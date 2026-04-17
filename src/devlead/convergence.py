"""Convergence math layer for DevLead.

Computes the five scalars that quantify Business Convergence:
  C(τ)  convergence ratio    — fraction of weighted goal closed
  α(k)  intent alignment      — does this TTO pull on the right axes?
  φ(k)  realisation fidelity  — did the work deliver what it promised?
  ε(k)  convergence efficiency— did the work pull toward the goal as planned?
  G(τ)  project gravity       — magnitude-weighted mean of realised alignment

Plus a Gram matrix for conflict detection between TTO intents.

Stdlib only — vectors are short (one component per BO, typically ≤ 8) and the
math is undergraduate. Inputs are sequences of floats; outputs are floats.
Numpy not pulled in; can be added later if PCA / eigendecomposition land.

Conventions
-----------
- Each BO axis is normalised so progress = (current - baseline) / (target - baseline)
  lives in [0, 1] at expected operating range, can exceed 1 on overshoot.
- BO weights w_i are importance allocations summing to 1.0.
- Goal vector g = (w_1, ..., w_n). State vector s = per-axis normalised progress.

References:
  docs/devlead-vision-2026-04-16.html Tab 4 (math derivation)
  docs/devlead-vision-2026-04-16.html Tab 5 (worked example, real numbers)

Note on C(τ) formula: Tab 4 wrote C = (s·g) / (g·g) which is a scalar
projection that overshoots 1 at full convergence. The correct convergence
ratio is the weighted progress C = s·g (with sum(w) = 1, this gives
C ∈ [0, 1] at expected range). Implemented here is the corrected form.
Tab 4 to be updated in a doc-cleanup pass.
"""
from __future__ import annotations

from math import sqrt
from typing import Sequence

Vector = Sequence[float]

__all__ = [
    "dot", "norm", "cosine",
    "compute_g", "compute_s",
    "compute_C", "compute_alpha", "compute_phi", "compute_epsilon",
    "compute_gravity", "compute_gram",
]


# --- primitives -------------------------------------------------------------

def dot(a: Vector, b: Vector) -> float:
    """Dot product of two equal-length sequences."""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    return sum(x * y for x, y in zip(a, b))


def norm(v: Vector) -> float:
    """Euclidean (L2) norm."""
    return sqrt(sum(x * x for x in v))


def cosine(a: Vector, b: Vector) -> float:
    """Cosine of angle between two vectors. Returns 0.0 if either is zero."""
    na, nb = norm(a), norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot(a, b) / (na * nb)


# --- goal vector and state -------------------------------------------------

def compute_g(bo_weights: Vector) -> tuple[float, ...]:
    """Goal vector g — the BO weight vector itself.

    Each axis is normalised so target-baseline = 1.0; the weight is the
    importance allocation. Sum of weights should equal 1.0 in v1.
    """
    return tuple(bo_weights)


def compute_s(currents: Vector, baselines: Vector, targets: Vector) -> tuple[float, ...]:
    """State vector s(τ) — per-axis normalised progress.

    Returns (current_i - baseline_i) / (target_i - baseline_i) for each axis.
    Result can exceed 1.0 on overshoot, go negative on regression.

    Edge case: when target == baseline (zero-displacement axis), returns 1.0
    if current == target else 0.0.
    """
    if not (len(currents) == len(baselines) == len(targets)):
        raise ValueError("axis count mismatch in compute_s")
    out = []
    for c, b, t in zip(currents, baselines, targets):
        denom = t - b
        if denom == 0.0:
            out.append(1.0 if c == t else 0.0)
        else:
            out.append((c - b) / denom)
    return tuple(out)


# --- the five scalars ------------------------------------------------------

def compute_C(s: Vector, g: Vector) -> float:
    """Convergence ratio C(τ) — weighted progress toward the goal.

    C = Σ wᵢ × sᵢ where g = (w_1, ..., w_n) and Σ w_i = 1.

    At s = (0,...,0): C = 0 (baseline).
    At s = (1,...,1): C = 1.0 (full convergence on every axis).
    Can exceed 1.0 if any axis overshoots its target.
    """
    return dot(s, g)


def compute_alpha(intent: Vector, g: Vector) -> float:
    """Intent alignment α(k) — cosine of TTO intent with goal vector.

    Range [-1, 1]. Negative = anti-goal work. Zero = orthogonal/no overlap.
    """
    return cosine(intent, g)


def compute_phi(realised: Vector, intent: Vector) -> float:
    """Realisation fidelity φ(k) — did the work deliver what it promised?

    Scalar projection of realised onto intent direction:
      φ = (r · i) / (i · i)

    At r = i (perfect realisation): φ = 1.0.
    At r = 0 (nothing happened): φ = 0.0.
    Exceeds 1.0 on over-delivery; negative if reality moved opposite intent.
    Returns 0.0 when intent is zero (no promise to evaluate).
    """
    denom = dot(intent, intent)
    if denom == 0.0:
        return 0.0
    return dot(realised, intent) / denom


def compute_epsilon(realised: Vector, intent: Vector, g: Vector) -> float:
    """Convergence efficiency ε(k) — did the work pull toward the goal as planned?

    ε = (r · g) / (i · g)

    Combines α and φ: high ε ⇒ both intent was goal-aligned AND realisation
    matched intent. Low ε ⇒ either mis-targeted (low α) or under-delivered (low φ).
    Returns 0.0 when intent is orthogonal to goal (i · g == 0).
    """
    denom = dot(intent, g)
    if denom == 0.0:
        return 0.0
    return dot(realised, g) / denom


def compute_gravity(realised_list: list[Vector], g: Vector) -> float:
    """Project gravity score G(τ) — magnitude-weighted mean of cos(rₖ, g).

    G = Σ ‖rₖ‖ × cos(rₖ, g) / Σ ‖rₖ‖

    Range [-1, 1]. High = realised work pulls hard toward the goal direction.
    Returns 0.0 if no realised work or all realisations are zero vectors.
    """
    if not realised_list:
        return 0.0
    total_mag = 0.0
    weighted = 0.0
    for r in realised_list:
        m = norm(r)
        if m == 0.0:
            continue
        weighted += m * cosine(r, g)
        total_mag += m
    if total_mag == 0.0:
        return 0.0
    return weighted / total_mag


# --- conflict detection ----------------------------------------------------

def compute_gram(intents: list[Vector]) -> list[list[float]]:
    """Gram matrix O = I · I^T for conflict detection across TTO intents.

    O[i][j] = intent_i · intent_j
    - positive off-diagonal → synergy (TTOs pull in same direction)
    - zero off-diagonal     → orthogonal (independent legitimate work)
    - negative off-diagonal → silent conflict (TTOs pull against each other)
    """
    n = len(intents)
    return [[dot(intents[i], intents[j]) for j in range(n)] for i in range(n)]

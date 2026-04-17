"""Unit tests for src/devlead/convergence.py.

Pin every formula against the worked numbers from Tab 4 of the vision doc
(docs/devlead-vision-2026-04-16.html). If a formula drifts, these tests
break and the math diverges from the documented design.
"""
from __future__ import annotations

import math
import pytest

from devlead.convergence import (
    dot, norm, cosine,
    compute_g, compute_s,
    compute_C, compute_alpha, compute_phi, compute_epsilon,
    compute_gravity, compute_gram,
)


# --- primitive math --------------------------------------------------------

def test_dot_basic():
    assert dot([1, 2, 3], [4, 5, 6]) == 32

def test_dot_length_mismatch_raises():
    with pytest.raises(ValueError):
        dot([1, 2], [1, 2, 3])

def test_norm_pythagorean():
    assert norm([3, 4]) == 5.0

def test_norm_zero_vector():
    assert norm([0, 0, 0]) == 0.0

def test_cosine_parallel():
    assert cosine([1, 0], [1, 0]) == 1.0

def test_cosine_orthogonal():
    assert math.isclose(cosine([1, 0], [0, 1]), 0.0, abs_tol=1e-12)

def test_cosine_anti_parallel():
    assert cosine([1, 0], [-1, 0]) == -1.0

def test_cosine_zero_vector_returns_zero():
    assert cosine([0, 0], [1, 1]) == 0.0


# --- goal vector and state -------------------------------------------------

def test_compute_g_returns_weights():
    assert compute_g((0.30, 0.20, 0.30, 0.20)) == (0.30, 0.20, 0.30, 0.20)

def test_compute_s_at_baseline_is_zero():
    s = compute_s(currents=(0, 0, 0, 0), baselines=(0, 0, 0, 0), targets=(1, 1, 1, 1))
    assert s == (0.0, 0.0, 0.0, 0.0)

def test_compute_s_at_target_is_one():
    # All four BOs reached target simultaneously
    s = compute_s(
        currents=(0.95, 60, 24, 1.0),
        baselines=(0.30, 600, 168, 0),
        targets=(0.95, 60, 24, 1.0),
    )
    assert all(math.isclose(x, 1.0, abs_tol=1e-12) for x in s)

def test_compute_s_partial_progress_inverted_axis():
    # Tab 4 BO-2 worked example: smaller-is-better metric
    # baseline=600s, target=60s, current=240s
    # progress = (current - baseline) / (target - baseline) = (240 - 600) / (60 - 600) = -360 / -540 = 0.667
    s = compute_s(currents=(240,), baselines=(600,), targets=(60,))
    assert math.isclose(s[0], 360 / 540, abs_tol=1e-12)

def test_compute_s_zero_displacement_at_target():
    # Edge: target equals baseline; current at target counts as converged
    s = compute_s(currents=(5,), baselines=(5,), targets=(5,))
    assert s == (1.0,)

def test_compute_s_axis_mismatch_raises():
    with pytest.raises(ValueError):
        compute_s(currents=(1, 2), baselines=(0,), targets=(2, 3))


# --- C(τ) convergence ratio ------------------------------------------------

def test_C_at_zero_state_is_zero():
    g = compute_g((0.30, 0.20, 0.30, 0.20))
    assert compute_C((0, 0, 0, 0), g) == 0.0

def test_C_at_full_convergence_is_one():
    # With weights summing to 1.0, full convergence on every axis ⇒ C = 1.0
    g = compute_g((0.30, 0.20, 0.30, 0.20))
    assert math.isclose(compute_C((1, 1, 1, 1), g), 1.0, abs_tol=1e-12)

def test_C_partial_convergence_weighted():
    # BO-1 fully closed, others at zero ⇒ C = w_1 = 0.30
    g = compute_g((0.30, 0.20, 0.30, 0.20))
    assert math.isclose(compute_C((1, 0, 0, 0), g), 0.30, abs_tol=1e-12)

def test_C_can_exceed_one_on_overshoot():
    g = compute_g((0.30, 0.20, 0.30, 0.20))
    # All axes at 1.5x target
    assert compute_C((1.5, 1.5, 1.5, 1.5), g) > 1.0


# --- α(k) intent alignment -------------------------------------------------

def test_alpha_pure_axis_intent():
    # Intent purely on highest-weighted axis
    g = (0.30, 0.20, 0.30, 0.20)
    intent = (0.40, 0, 0, 0)
    # cosine reduces to w_1 / ‖g‖
    expected = 0.30 / norm(g)
    assert math.isclose(compute_alpha(intent, g), expected, abs_tol=1e-12)

def test_alpha_orthogonal_to_goal():
    g = (1, 0, 0, 0)
    intent = (0, 1, 0, 0)
    assert math.isclose(compute_alpha(intent, g), 0.0, abs_tol=1e-12)

def test_alpha_anti_aligned_to_goal():
    g = (1, 1, 1, 1)
    intent = (-1, -1, -1, -1)
    assert math.isclose(compute_alpha(intent, g), -1.0, abs_tol=1e-12)


# --- φ(k) realisation fidelity ---------------------------------------------

def test_phi_perfect_realisation():
    intent = (0, 0.74, 0, 0)
    realised = (0, 0.74, 0, 0)
    assert math.isclose(compute_phi(realised, intent), 1.0, abs_tol=1e-12)

def test_phi_under_delivery_tab5_worked_example():
    # Tab 5 worked example: TTO-2.1.1 stop-hook regenerates _resume.md
    # Promised i = (0, 0.74, 0, 0); realised r = (0, 0.667, 0, 0)
    # φ = (r·i) / (i·i) = (0.667 × 0.74) / (0.74 × 0.74) ≈ 0.9014
    intent = (0, 0.74, 0, 0)
    realised = (0, 0.667, 0, 0)
    expected = (0.667 * 0.74) / (0.74 * 0.74)
    assert math.isclose(compute_phi(realised, intent), expected, abs_tol=1e-12)
    assert math.isclose(expected, 0.9014, abs_tol=1e-3)

def test_phi_zero_intent_returns_zero():
    assert compute_phi((1, 1), (0, 0)) == 0.0

def test_phi_negative_realisation_means_anti_progress():
    intent = (0, 1, 0, 0)
    realised = (0, -0.5, 0, 0)
    assert compute_phi(realised, intent) == -0.5


# --- ε(k) convergence efficiency -------------------------------------------

def test_epsilon_perfect():
    g = (0.30, 0.20, 0.30, 0.20)
    intent = (0.40, 0, 0, 0)
    realised = (0.40, 0, 0, 0)
    assert math.isclose(compute_epsilon(realised, intent, g), 1.0, abs_tol=1e-12)

def test_epsilon_under_delivery_tab5_worked_example():
    # Same Tab 5 example: ε = (r·g) / (i·g)
    g = (0.30, 0.20, 0.30, 0.20)
    intent = (0, 0.74, 0, 0)
    realised = (0, 0.667, 0, 0)
    expected = (0.667 * 0.20) / (0.74 * 0.20)  # = 0.667/0.74 ≈ 0.9014
    assert math.isclose(compute_epsilon(realised, intent, g), expected, abs_tol=1e-12)

def test_epsilon_zero_when_intent_orthogonal_to_goal():
    g = (1, 0, 0, 0)
    intent = (0, 1, 0, 0)  # i·g == 0
    realised = (0, 0.5, 0, 0)
    assert compute_epsilon(realised, intent, g) == 0.0


# --- G(τ) project gravity --------------------------------------------------

def test_gravity_no_realised_work():
    g = (0.30, 0.20, 0.30, 0.20)
    assert compute_gravity([], g) == 0.0

def test_gravity_single_aligned_realisation():
    # Realisation perfectly along goal direction ⇒ G = 1.0
    g = (0.30, 0.20, 0.30, 0.20)
    assert math.isclose(compute_gravity([g], g), 1.0, abs_tol=1e-12)

def test_gravity_single_anti_aligned():
    g = (0.30, 0.20, 0.30, 0.20)
    r = tuple(-x for x in g)
    assert math.isclose(compute_gravity([r], g), -1.0, abs_tol=1e-12)

def test_gravity_zero_magnitude_realisations_skipped():
    g = (0.30, 0.20, 0.30, 0.20)
    assert compute_gravity([(0, 0, 0, 0), (0, 0, 0, 0)], g) == 0.0

def test_gravity_weighted_by_magnitude():
    # Bigger r dominates the weighted average
    g = (1, 0)
    big_aligned = (10, 0)
    small_anti = (-1, 0)
    G = compute_gravity([big_aligned, small_anti], g)
    # weighted = 10*1 + 1*(-1) = 9; total_mag = 11; G = 9/11
    assert math.isclose(G, 9 / 11, abs_tol=1e-12)


# --- Gram matrix conflict detection ----------------------------------------

def test_gram_synergy_positive_off_diagonal():
    intents = [(0.40, 0, 0, 0), (0.20, 0, 0, 0)]
    O = compute_gram(intents)
    assert O[0][1] > 0
    assert O[1][0] > 0
    assert O[0][1] == O[1][0]  # symmetric

def test_gram_orthogonal_zero():
    intents = [(1, 0, 0, 0), (0, 1, 0, 0)]
    O = compute_gram(intents)
    assert O[0][1] == 0.0

def test_gram_conflict_negative_off_diagonal():
    # Tab 4 / Tab 5 hypothetical: TTO-X "drop metric_source" undoes foundation
    intents = [(0.40, 0, 0.05, 0), (-0.30, 0, 0, 0)]
    O = compute_gram(intents)
    assert O[0][1] < 0  # silent conflict surfaced

def test_gram_diagonal_is_squared_norm():
    intents = [(3, 4, 0)]
    O = compute_gram(intents)
    assert O[0][0] == 25  # 3² + 4²


# --- Tab 4 / Tab 5 worked example pinning ----------------------------------

def test_tab4_tto_111_alpha_matches_doc():
    """Tab 4: TTO-1.1.1 Gate exit-2 = (0.40, 0, 0.05, 0), g = (0.30, 0.20, 0.30, 0.20).
    Expected α ≈ 0.657."""
    g = (0.30, 0.20, 0.30, 0.20)
    intent = (0.40, 0, 0.05, 0)
    a = compute_alpha(intent, g)
    assert math.isclose(a, 0.657, abs_tol=0.01)

def test_tab4_tto_211_alpha_matches_doc():
    """Tab 4: TTO-2.1.1 = (0, 0.74, 0, 0), g = (0.30, 0.20, 0.30, 0.20).
    Expected α ≈ 0.392."""
    g = (0.30, 0.20, 0.30, 0.20)
    intent = (0, 0.74, 0, 0)
    a = compute_alpha(intent, g)
    assert math.isclose(a, 0.392, abs_tol=0.01)

def test_tab4_tto_311_alpha_matches_doc():
    """Tab 4: TTO-3.1.1 multi-axis = (0, 0, 0.30, 0.10), g = (0.30, 0.20, 0.30, 0.20).
    Expected α ≈ 0.683."""
    g = (0.30, 0.20, 0.30, 0.20)
    intent = (0, 0, 0.30, 0.10)
    a = compute_alpha(intent, g)
    assert math.isclose(a, 0.683, abs_tol=0.01)

import numpy as np
from src.siad03_extensions.explain import permute_within


def test_permutation_preserves_month_membership_and_input():
    x = np.arange(20); original = x.copy(); group = np.repeat([6,7],10)
    p = permute_within(x,group,np.random.default_rng(42))
    assert np.array_equal(x,original)
    for g in [6,7]: assert set(x[group==g]) == set(p[group==g])
    assert not np.array_equal(x,p)

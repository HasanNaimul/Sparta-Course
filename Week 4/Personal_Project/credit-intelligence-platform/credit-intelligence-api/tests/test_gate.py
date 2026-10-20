import gate


def test_exact_match_always_passes():
    assert gate.is_usable({"score": 0.10, "exact_match": True}, 0.35)


def test_score_above_floor_passes():
    assert gate.is_usable({"score": 0.60, "exact_match": False}, 0.35)


def test_score_below_floor_fails():
    assert not gate.is_usable({"score": 0.20, "exact_match": False}, 0.35)


def test_missing_score_fails():
    assert not gate.is_usable({"score": None, "exact_match": False}, 0.35)
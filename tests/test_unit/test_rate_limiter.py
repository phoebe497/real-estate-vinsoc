from src.services.rate_limiter import BoundedSlidingWindowLimiter


def test_limiter_blocks_after_limit() -> None:
    limiter = BoundedSlidingWindowLimiter(max_keys=10)

    assert limiter.is_limited("client", 2) is False
    assert limiter.is_limited("client", 2) is False
    assert limiter.is_limited("client", 2) is True


def test_limiter_bounds_attacker_controlled_keys() -> None:
    limiter = BoundedSlidingWindowLimiter(max_keys=3)

    for index in range(10):
        assert limiter.is_limited(f"attacker-{index}", 1) is False

    assert len(limiter._events) == 3


from datetime import UTC, datetime, timedelta

ART_33_WINDOW = timedelta(hours=72)


def _require_aware(dt: datetime, name: str) -> None:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError(f"{name} must be timezone-aware")


def notification_deadline(
    became_aware_at: datetime,
    window: timedelta = ART_33_WINDOW,
    *,
    start_at_next_full_hour: bool = False,
) -> datetime:
    _require_aware(became_aware_at, "became_aware_at")
    if window <= timedelta(0):
        raise ValueError("window must be positive")

    start_utc = became_aware_at.astimezone(UTC)
    if start_at_next_full_hour:
        hour_began = became_aware_at.replace(minute=0, second=0, microsecond=0)
        start_utc = hour_began.astimezone(UTC) + timedelta(hours=1)

    return (start_utc + window).astimezone(became_aware_at.tzinfo)


def is_late(
    became_aware_at: datetime,
    notified_at: datetime,
    window: timedelta = ART_33_WINDOW,
    *,
    start_at_next_full_hour: bool = False,
) -> bool:
    _require_aware(notified_at, "notified_at")

    deadline = notification_deadline(
        became_aware_at, window, start_at_next_full_hour=start_at_next_full_hour
    )
    return notified_at.astimezone(UTC) > deadline.astimezone(UTC)


def time_remaining(
    became_aware_at: datetime,
    now: datetime,
    window: timedelta = ART_33_WINDOW,
    *,
    start_at_next_full_hour: bool = False,
) -> timedelta:
    _require_aware(now, "now")

    deadline = notification_deadline(
        became_aware_at, window, start_at_next_full_hour=start_at_next_full_hour
    )
    return deadline.astimezone(UTC) - now.astimezone(UTC)

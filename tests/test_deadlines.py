from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from legal_eng_lab.deadlines import (
    ART_33_WINDOW,
    is_late,
    notification_deadline,
    time_remaining,
)

IST = ZoneInfo("Asia/Kolkata")
BRUSSELS = ZoneInfo("Europe/Brussels")


@pytest.mark.parametrize(
    ("became_aware_at", "expected_deadline"),
    [
        pytest.param(
            datetime(2026, 11, 16, 9, 0, tzinfo=UTC),
            datetime(2026, 11, 19, 9, 0, tzinfo=UTC),
            id="plain-utc",
        ),
        pytest.param(
            datetime(2026, 11, 16, 14, 30, tzinfo=IST),
            datetime(2026, 11, 19, 14, 30, tzinfo=IST),
            id="india-half-hour-offset",
        ),
        pytest.param(
            datetime(2026, 3, 27, 10, 0, tzinfo=BRUSSELS),
            datetime(2026, 3, 30, 11, 0, tzinfo=BRUSSELS),
            id="clocks-go-forward-inside-window",
        ),
        pytest.param(
            datetime(2026, 10, 23, 10, 0, tzinfo=BRUSSELS),
            datetime(2026, 10, 26, 9, 0, tzinfo=BRUSSELS),
            id="clocks-go-back-inside-window",
        ),
        pytest.param(
            datetime(2026, 12, 30, 18, 0, tzinfo=UTC),
            datetime(2027, 1, 2, 18, 0, tzinfo=UTC),
            id="crosses-new-year",
        ),
        pytest.param(
            datetime(2028, 2, 27, 12, 0, tzinfo=UTC),
            datetime(2028, 3, 1, 12, 0, tzinfo=UTC),
            id="leap-year-29-feb",
        ),
        pytest.param(
            datetime(2026, 11, 20, 17, 0, tzinfo=BRUSSELS),
            datetime(2026, 11, 23, 17, 0, tzinfo=BRUSSELS),
            id="weekend-counts",
        ),
    ],
)
def test_deadline_is_72_real_hours(became_aware_at: datetime, expected_deadline: datetime) -> None:
    deadline = notification_deadline(became_aware_at)
    assert deadline == expected_deadline
    # Subtract in UTC: two times in the SAME zone subtract by wall clock and hide DST.
    assert deadline.astimezone(UTC) - became_aware_at.astimezone(UTC) == ART_33_WINDOW
    assert deadline.tzinfo == became_aware_at.tzinfo


@pytest.mark.parametrize(
    ("notified_at", "late"),
    [
        pytest.param(datetime(2026, 11, 19, 9, 0, tzinfo=UTC), False, id="exactly-72h-on-time"),
        pytest.param(datetime(2026, 11, 19, 9, 0, 1, tzinfo=UTC), True, id="one-second-late"),
        pytest.param(datetime(2026, 11, 17, 9, 0, tzinfo=UTC), False, id="early"),
        pytest.param(
            datetime(2026, 11, 19, 10, 0, tzinfo=BRUSSELS), False, id="same-instant-other-zone"
        ),
    ],
)
def test_is_late(notified_at: datetime, late: bool) -> None:
    became_aware_at = datetime(2026, 11, 16, 14, 30, tzinfo=IST)  # = 09:00 UTC
    assert is_late(became_aware_at, notified_at) is late


@pytest.mark.parametrize(
    ("became_aware_at", "expected_deadline"),
    [
        pytest.param(
            datetime(2026, 11, 16, 10, 17, tzinfo=UTC),
            datetime(2026, 11, 19, 11, 0, tzinfo=UTC),
            id="mid-hour-starts-next-hour",
        ),
        pytest.param(
            datetime(2026, 11, 16, 10, 0, tzinfo=UTC),
            datetime(2026, 11, 19, 11, 0, tzinfo=UTC),
            id="on-the-hour-still-excluded",
        ),
        pytest.param(
            datetime(2026, 11, 16, 14, 30, tzinfo=IST),
            datetime(2026, 11, 19, 15, 0, tzinfo=IST),
            id="next-hour-in-local-time",
        ),
    ],
)
def test_reg_1182_71_next_full_hour(became_aware_at: datetime, expected_deadline: datetime) -> None:
    deadline = notification_deadline(became_aware_at, start_at_next_full_hour=True)
    assert deadline == expected_deadline


def test_time_remaining_is_real_time_across_dst() -> None:
    aware = datetime(2026, 3, 27, 10, 0, tzinfo=BRUSSELS)
    assert time_remaining(aware, now=aware) == timedelta(hours=72)
    one_hour_later = datetime(2026, 3, 27, 11, 0, tzinfo=BRUSSELS)
    assert time_remaining(aware, now=one_hour_later) == timedelta(hours=71)


@pytest.mark.parametrize(
    "bad_input",
    [
        pytest.param(datetime(2026, 11, 16, 9, 0), id="naive-datetime"),
    ],
)
def test_naive_datetime_is_rejected(bad_input: datetime) -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        notification_deadline(bad_input)


@pytest.mark.parametrize(
    "window",
    [
        pytest.param(timedelta(0), id="zero"),
        pytest.param(timedelta(hours=-1), id="negative"),
    ],
)
def test_non_positive_window_is_rejected(window: timedelta) -> None:
    with pytest.raises(ValueError, match="window must be positive"):
        notification_deadline(datetime(2026, 11, 16, 9, 0, tzinfo=UTC), window)

from datetime import date

import pytest
from nldate import parse

TODAY = date(2025, 12, 1)  # Monday


class TestSimpleReferences:
    def test_today(self) -> None:
        assert parse("today", today=TODAY) == TODAY

    def test_yesterday(self) -> None:
        assert parse("yesterday", today=TODAY) == date(2025, 11, 30)

    def test_tomorrow(self) -> None:
        assert parse("tomorrow", today=TODAY) == date(2025, 12, 2)

    def test_now(self) -> None:
        assert parse("now", today=TODAY) == TODAY


class TestAbsoluteDates:
    def test_month_name_with_ordinal(self) -> None:
        assert parse("December 1st, 2025") == date(2025, 12, 1)

    def test_abbreviated_month(self) -> None:
        assert parse("Dec 1, 2025") == date(2025, 12, 1)

    def test_day_month_year(self) -> None:
        assert parse("1st December 2025") == date(2025, 12, 1)

    def test_iso_format(self) -> None:
        assert parse("2025-12-01") == date(2025, 12, 1)

    def test_iso_with_slash(self) -> None:
        assert parse("2025/12/01") == date(2025, 12, 1)

    def test_us_format(self) -> None:
        assert parse("12/01/2025") == date(2025, 12, 1)

    def test_month_and_day_only(self) -> None:
        assert parse("December 1, 2025") == date(2025, 12, 1)


class TestRelativeDays:
    def test_before_fixed_date(self) -> None:
        assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)

    def test_after_fixed_date(self) -> None:
        assert parse("3 days after December 1st, 2025") == date(2025, 12, 4)

    def test_in_days(self) -> None:
        assert parse("in 5 days", today=TODAY) == date(2025, 12, 6)

    def test_days_from_today(self) -> None:
        assert parse("10 days from today", today=TODAY) == date(2025, 12, 11)

    def test_from_tomorrow(self) -> None:
        assert parse("2 weeks from tomorrow", today=TODAY) == date(2025, 12, 16)

    def test_before_yesterday(self) -> None:
        assert parse("3 days before yesterday", today=TODAY) == date(2025, 11, 27)

    def test_a_week_from_today(self) -> None:
        assert parse("a week from today", today=TODAY) == date(2025, 12, 8)

    def test_after_tomorrow(self) -> None:
        assert parse("a day after tomorrow", today=TODAY) == date(2025, 12, 3)


class TestCompoundOffsets:
    def test_year_and_months_after_fixed(self) -> None:
        assert parse("1 year and 2 months after December 1st, 2025") == date(2027, 2, 1)

    def test_year_and_months_after_ref(self) -> None:
        assert parse("1 year and 2 months after yesterday", today=TODAY) == date(2027, 1, 30)

    def test_year_before_fixed(self) -> None:
        assert parse("1 year before December 1st, 2025") == date(2024, 12, 1)

    def test_week_and_days_after(self) -> None:
        assert parse("1 week and 3 days after December 1st, 2025") == date(2025, 12, 11)


class TestWeekdayReferences:
    def test_next_tuesday(self) -> None:
        assert parse("next Tuesday", today=TODAY) == date(2025, 12, 2)

    def test_next_monday(self) -> None:
        assert parse("next Monday", today=TODAY) == date(2025, 12, 8)

    def test_last_friday(self) -> None:
        assert parse("last Friday", today=TODAY) == date(2025, 11, 28)

    def test_last_monday(self) -> None:
        assert parse("last Monday", today=TODAY) == date(2025, 11, 24)

    def test_this_friday(self) -> None:
        assert parse("this Friday", today=TODAY) == date(2025, 12, 5)

    def test_this_monday(self) -> None:
        assert parse("this Monday", today=TODAY) == TODAY

    def test_next_wednesday(self) -> None:
        assert parse("next Wednesday", today=TODAY) == date(2025, 12, 3)


class TestPeriodReferences:
    def test_next_week(self) -> None:
        assert parse("next week", today=TODAY) == date(2025, 12, 8)

    def test_last_week(self) -> None:
        assert parse("last week", today=TODAY) == date(2025, 11, 24)

    def test_next_month(self) -> None:
        assert parse("next month", today=TODAY) == date(2026, 1, 1)

    def test_last_month(self) -> None:
        assert parse("last month", today=TODAY) == date(2025, 11, 1)

    def test_next_year(self) -> None:
        assert parse("next year", today=TODAY) == date(2026, 12, 1)

    def test_this_week(self) -> None:
        assert parse("this week", today=TODAY) == TODAY


class TestEdgeCases:
    def test_in_a_week(self) -> None:
        assert parse("in a week", today=TODAY) == date(2025, 12, 8)

    def test_two_weeks_from_now(self) -> None:
        assert parse("2 weeks from now", today=TODAY) == date(2025, 12, 15)

    def test_in_two_weeks(self) -> None:
        assert parse("in two weeks", today=TODAY) == date(2025, 12, 15)

    def test_month_end_clamping(self) -> None:
        assert parse("1 month after January 31st, 2025") == date(2025, 2, 28)

    def test_default_today_returns_date(self) -> None:
        result = parse("today")
        assert isinstance(result, date)

    def test_invalid_input(self) -> None:
        with pytest.raises(ValueError):
            parse("not a date at all", today=TODAY)

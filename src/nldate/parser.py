import calendar
import re
from datetime import date, timedelta
from typing import Optional

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

MONTH_NAMES: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

NUMBER_WORDS: dict[str, int] = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "a": 1,
    "an": 1,
    "the": 1,
    "couple": 2,
    "few": 3,
}

UNIT_DAYS: dict[str, int] = {
    "day": 1,
    "days": 1,
    "week": 7,
    "weeks": 7,
    "fortnight": 14,
    "fortnights": 14,
}

UNIT_MONTHS: dict[str, int] = {
    "month": 1,
    "months": 1,
    "year": 12,
    "years": 12,
    "yr": 12,
    "yrs": 12,
}

_ALL_UNITS = set(UNIT_DAYS) | set(UNIT_MONTHS)


def _parse_number(s: str) -> int:
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    if s in NUMBER_WORDS:
        return NUMBER_WORDS[s]
    msg = f"Cannot parse number: {s}"
    raise ValueError(msg)


def _apply_offset(d: date, years: int = 0, months: int = 0, days: int = 0) -> date:
    total_months = d.month + months + years * 12
    new_year = d.year + (total_months - 1) // 12
    new_month = ((total_months - 1) % 12) + 1
    max_day = calendar.monthrange(new_year, new_month)[1]
    new_day = min(d.day, max_day)
    result = date(new_year, new_month, new_day)
    if days:
        result += timedelta(days=days)
    return result


def _parse_quantity(s: str) -> tuple[int, int, int]:
    s = s.strip().lower()
    total_days = 0
    total_months = 0
    total_years = 0

    parts = re.split(r"\s+and\s+|\s*,\s*", s)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"(\S+)\s+(" + "|".join(_ALL_UNITS) + r")$", part)
        if m:
            num_str, unit = m.groups()
            num = _parse_number(num_str)
            if unit in UNIT_DAYS:
                total_days += num * UNIT_DAYS[unit]
            elif unit in UNIT_MONTHS:
                months_added = num * UNIT_MONTHS[unit]
                total_years += months_added // 12
                total_months += months_added % 12
        else:
            msg = f"Cannot parse quantity: {part}"
            raise ValueError(msg)

    total_years += total_months // 12
    total_months = total_months % 12

    return total_days, total_months, total_years


def _parse_absolute_date(s: str, today: Optional[date] = None) -> Optional[date]:
    s = s.strip()
    s = re.sub(r"\bon\s+", "", s, flags=re.IGNORECASE)
    s = s.replace(",", "")
    s = s.replace(".", "")
    s = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s)

    year = today.year if today is not None else date.today().year

    m = re.match(r"([a-zA-Z]+)\s+(\d+)\s+(\d{4})$", s)
    if m:
        month_name, day_str, year_str = m.groups()
        if month_name.lower() in MONTH_NAMES:
            return date(int(year_str), MONTH_NAMES[month_name.lower()], int(day_str))

    m = re.match(r"(\d+)\s+([a-zA-Z]+)\s+(\d{4})$", s)
    if m:
        day_str, month_name, year_str = m.groups()
        if month_name.lower() in MONTH_NAMES:
            return date(int(year_str), MONTH_NAMES[month_name.lower()], int(day_str))

    m = re.match(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})$", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    m = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", s)
    if m:
        month, day, year_val = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return date(year_val, month, day)

    m = re.match(r"([a-zA-Z]+)\s+(\d{1,2})$", s)
    if m:
        month_name, day_str = m.groups()
        if month_name.lower() in MONTH_NAMES:
            return date(year, MONTH_NAMES[month_name.lower()], int(day_str))

    m = re.match(r"(\d{1,2})\s+([a-zA-Z]+)$", s)
    if m:
        day_str, month_name = m.groups()
        if month_name.lower() in MONTH_NAMES:
            return date(year, MONTH_NAMES[month_name.lower()], int(day_str))

    return None


def _parse_date_reference(s: str, today: date) -> date:
    s = s.strip().lower()

    if s == "today":
        return today
    if s == "yesterday":
        return today - timedelta(days=1)
    if s == "tomorrow":
        return today + timedelta(days=1)
    if s == "now":
        return today

    m = re.match(
        r"(next|last|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
        s,
    )
    if m:
        modifier, weekday = m.groups()
        target = WEEKDAYS.index(weekday)
        if modifier == "next":
            days_ahead = target - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        elif modifier == "last":
            days_behind = today.weekday() - target
            if days_behind <= 0:
                days_behind += 7
            return today - timedelta(days=days_behind)
        elif modifier == "this":
            days_ahead = target - today.weekday()
            if days_ahead < 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)

    m = re.match(r"(next|last|this)\s+(week|month|year)$", s)
    if m:
        modifier, period = m.groups()
        if modifier == "next":
            if period == "week":
                return today + timedelta(days=7)
            elif period == "month":
                return _apply_offset(today, months=1)
            elif period == "year":
                return _apply_offset(today, years=1)
        elif modifier == "last":
            if period == "week":
                return today - timedelta(days=7)
            elif period == "month":
                return _apply_offset(today, months=-1)
            elif period == "year":
                return _apply_offset(today, years=-1)
        elif modifier == "this":
            return today

    result = _parse_absolute_date(s, today)
    if result is not None:
        return result

    msg = f"Unknown date reference: {s}"
    raise ValueError(msg)


def parse(s: str, today: Optional[date] = None) -> date:
    if today is None:
        today = date.today()

    s = s.strip()
    if not s:
        msg = "Empty string"
        raise ValueError(msg)

    s = re.sub(r"^on\s+", "", s, flags=re.IGNORECASE)

    m = re.match(r"in\s+(.+)$", s, re.IGNORECASE)
    if m:
        quantity_str = m.group(1)
        days, months, years = _parse_quantity(quantity_str)
        return _apply_offset(today, years=years, months=months, days=days)

    m = re.match(r"(.+?)\s+from\s+(.+)$", s, re.IGNORECASE)
    if m:
        quantity_str = m.group(1).strip()
        reference_str = m.group(2).strip()
        days, months, years = _parse_quantity(quantity_str)
        base = _parse_date_reference(reference_str, today)
        return _apply_offset(base, years=years, months=months, days=days)

    m = re.match(r"(.+?)\s+(before|after)\s+(.+)$", s, re.IGNORECASE)
    if m:
        quantity_str = m.group(1).strip()
        direction = m.group(2).lower()
        reference_str = m.group(3).strip()
        days, months, years = _parse_quantity(quantity_str)
        if direction == "before":
            days, months, years = -days, -months, -years
        base = _parse_date_reference(reference_str, today)
        return _apply_offset(base, years=years, months=months, days=days)

    m = re.match(r"(.+?)\s+ago$", s, re.IGNORECASE)
    if m:
        quantity_str = m.group(1).strip()
        days, months, years = _parse_quantity(quantity_str)
        return _apply_offset(today, years=-years, months=-months, days=-days)

    return _parse_date_reference(s, today)

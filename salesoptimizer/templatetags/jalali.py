"""
jalali.py
---------
Django template filters for converting Gregorian dates to Jalali (Shamsi).

Usage in templates:
    {% load jalali %}
    {{ voucher.voucher_date|jalali }}             → 1403/07/20
    {{ voucher.voucher_date|jalali:"short" }}     → 1403/07/20
    {{ voucher.voucher_date|jalali:"long" }}      → ۲۰ مهر ۱۴۰۳
    {{ voucher.voucher_date|jalali:"datetime" }}  → 1403/07/20 14:30
    {{ voucher.voucher_date|jalali:"full" }}      → شنبه ۲۰ مهر ۱۴۰۳
"""

from datetime import date, datetime

import jdatetime
from django import template
from django.utils import timezone

register = template.Library()


# Persian month names
JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند",
]

# Persian weekday names (Saturday = 0 in jdatetime)
JALALI_WEEKDAYS = [
    "شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه",
    "چهارشنبه", "پنج‌شنبه", "جمعه",
]


def _to_jalali(value):
    """
    Convert a Gregorian date/datetime to a jdatetime object.
    Returns None if input is None or invalid.
    """
    if value is None:
        return None

    # Convert timezone-aware datetimes to local time first
    if isinstance(value, datetime) and timezone.is_aware(value):
        value = timezone.localtime(value)

    # If it's a datetime, split into date and time parts
    if isinstance(value, datetime):
        return jdatetime.datetime.fromgregorian(
            year=value.year,
            month=value.month,
            day=value.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second,
        )

    # If it's a date
    if isinstance(value, date):
        return jdatetime.date.fromgregorian(
            year=value.year,
            month=value.month,
            day=value.day,
        )

    return None


@register.filter(name="jalali")
def jalali(value, style="short"):
    """
    Convert a Gregorian date/datetime to Jalali string.

    Styles:
        short     → 1403/07/20              (default)
        long      → 20 مهر 1403
        full      → شنبه 20 مهر 1403
        datetime  → 1403/07/20 14:30
        iso       → 1403-07-20
        time      → 14:30
        year      → 1403
        month     → مهر
        day       → 20

    Persian digits are NOT applied by default — the output uses ASCII digits.
    Use the `jalali_fa` filter below if you want Persian digits.
    """
    jd = _to_jalali(value)
    if jd is None:
        return "—"

    style = (style or "short").lower()

    if style == "short" or style == "":
        return jd.strftime("%Y/%m/%d")

    if style == "iso":
        return jd.strftime("%Y-%m-%d")

    if style == "long":
        return f"{jd.day} {JALALI_MONTHS[jd.month - 1]} {jd.year}"

    if style == "full":
        # jdatetime weekday() returns 0 = Saturday
        weekday = JALALI_WEEKDAYS[jd.weekday()]
        return f"{weekday} {jd.day} {JALALI_MONTHS[jd.month - 1]} {jd.year}"

    if style == "datetime":
        return jd.strftime("%Y/%m/%d %H:%M")

    if style == "time":
        return jd.strftime("%H:%M")

    if style == "year":
        return str(jd.year)

    if style == "month":
        return JALALI_MONTHS[jd.month - 1]

    if style == "day":
        return str(jd.day)

    # Fallback
    return jd.strftime("%Y/%m/%d")


@register.filter(name="jalali_fa")
def jalali_fa(value, style="short"):
    """
    Same as `jalali` but converts all digits to Persian (۰۱۲۳۴۵۶۷۸۹).
    """
    result = jalali(value, style)
    if result == "—":
        return result

    translation_table = str.maketrans(
        "0123456789",
        "۰۱۲۳۴۵۶۷۸۹",
    )
    return result.translate(translation_table)


@register.filter(name="jalali_year")
def jalali_year(value):
    """Extract only the Jalali year. e.g. 1403"""
    jd = _to_jalali(value)
    return jd.year if jd else None


@register.filter(name="jalali_month")
def jalali_month(value):
    """Extract only the Jalali month number. e.g. 7"""
    jd = _to_jalali(value)
    return jd.month if jd else None


@register.filter(name="jalali_day")
def jalali_day(value):
    """Extract only the Jalali day. e.g. 20"""
    jd = _to_jalali(value)
    return jd.day if jd else None
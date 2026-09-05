"""DateTime wire formatting without importing the client or model packages."""

from datetime import datetime, timezone


def format_datetime_for_oanda(value: datetime, datetime_format: object = "RFC3339") -> str:
    """
    Format DateTime values according to Accept-Datetime-Format.

    OANDA applies Accept-Datetime-Format to DateTime fields in both requests and
    responses. Naive datetimes are treated as UTC for UNIX conversion.
    """
    if datetime_format != "UNIX":
        return value.isoformat()

    utc_value = value
    if utc_value.tzinfo is None:
        utc_value = utc_value.replace(tzinfo=timezone.utc)
    else:
        utc_value = utc_value.astimezone(timezone.utc)

    delta = utc_value - datetime(1970, 1, 1, tzinfo=timezone.utc)
    microseconds = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
    sign = "-" if microseconds < 0 else ""
    seconds, fraction = divmod(abs(microseconds), 1000000)
    return f"{sign}{seconds}.{fraction * 1000:09d}"

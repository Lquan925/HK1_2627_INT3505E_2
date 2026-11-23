import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import current_app, request

log = logging.getLogger("sunset")


def http_date(dt):
    return format_datetime(dt.astimezone(timezone.utc), usegmt=True)


def deprecate_at(sunset_date, replacement=None):
    if sunset_date.tzinfo is None or sunset_date.utcoffset() is None:
        raise ValueError("sunset_date must include a timezone")

    def wrap(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            if datetime.now(timezone.utc) >= sunset_date:
                result = ({
                    "error": "gone",
                    "sunset": http_date(sunset_date),
                    "use_instead": replacement,
                }, 410)
            else:
                result = fn(*args, **kwargs)
            # Preserve Flask response types, status codes and existing headers.
            response = current_app.make_response(result)
            response.headers["Sunset"] = http_date(sunset_date)
            response.headers["Deprecation"] = "true"
            if replacement:
                response.headers.add("Link", f'<{replacement}>; rel="successor-version"')
            return response

        return inner

    return wrap

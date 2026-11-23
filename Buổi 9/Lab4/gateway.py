import hashlib
import logging
import os

from flask import request

from handlers import v1_create_order, v2_create_order

V2_PERCENT = int(os.environ.get("V2_PERCENT", "5"))
if not 0 <= V2_PERCENT <= 100:
    raise ValueError("V2_PERCENT must be between 0 and 100")
V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}
log = logging.getLogger("gateway")


def route_to_v2(body):
    # Explicit cohorts and allow-listed accounts override the percentage.
    cohort = request.headers.get("X-Cohort", "").strip().lower()
    if cohort in V2_COHORTS:
        return True
    account = body.get("account_id", "")
    if account in V2_FORCE_ACCOUNTS:
        return True
    if V2_PERCENT == 0:
        return False
    # MD5 is used only for stable bucketing, not for security.
    bucket = int(hashlib.md5(account.encode("utf-8")).hexdigest(), 16) % 100
    return bucket < V2_PERCENT


def dispatch(body):
    which = "v2" if route_to_v2(body) else "v1"
    log.info("order_route account=%s handler=%s", body["account_id"], which)
    handler = v2_create_order if which == "v2" else v1_create_order
    return which, handler(body)

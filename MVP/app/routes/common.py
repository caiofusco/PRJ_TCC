from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def parse_money(value: str | None, default: str = "0") -> Decimal:
    if value is None or value == "":
        return Decimal(default)
    try:
        return Decimal(value.replace(".", "").replace(",", ".") if "," in value else value)
    except (InvalidOperation, AttributeError):
        return Decimal(default)


def parse_int(value: str | None, default: int = 0) -> int:
    try:
        return int(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def parse_datetime_local(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M")


def flash_errors(message: str):
    flash(message, "danger")

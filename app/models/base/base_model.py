import datetime
from typing import Any

from sqlalchemy import Date, DateTime, String, Time
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON

# Type aliasing agar tipe data memiliki makna semantik
type NomorTelepon = str
type Email = str


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON,
        datetime.datetime: DateTime,
        datetime.date: Date,
        datetime.time: Time,
        NomorTelepon: String(20),  # Max 15 digit, extra 5 digit untuk overhead
        Email: String(254),  # Max length berdasarkan RFC 3696 dan erratum EID 1690
    }
    """
    Mapping antara tipe native Python dengan tipe data SQL dari SQLAlchemy

    Sebagai contoh, pada definisi model, sebuah `dict[str, Any]` akan di-map menjadi
    JSON di database
    """

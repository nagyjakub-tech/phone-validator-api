"""
Phone Number Validator API — core validation logic.

Built on top of the `phonenumbers` library (a pure-Python port of Google's
libphonenumber). All metadata (numbering plans, carrier prefixes, timezone
mappings) ships bundled inside the library itself — there is no network
call, no external API, and no paid data source involved. Marginal cost per
request is essentially zero.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import phonenumbers
from phonenumbers import carrier as pn_carrier
from phonenumbers import geocoder as pn_geocoder
from phonenumbers import timezone as pn_timezone
from phonenumbers.phonenumberutil import NumberParseException

_TYPE_NAMES = {
    phonenumbers.PhoneNumberType.FIXED_LINE: "FIXED_LINE",
    phonenumbers.PhoneNumberType.MOBILE: "MOBILE",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_LINE_OR_MOBILE",
    phonenumbers.PhoneNumberType.TOLL_FREE: "TOLL_FREE",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
    phonenumbers.PhoneNumberType.SHARED_COST: "SHARED_COST",
    phonenumbers.PhoneNumberType.VOIP: "VOIP",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "PERSONAL_NUMBER",
    phonenumbers.PhoneNumberType.PAGER: "PAGER",
    phonenumbers.PhoneNumberType.UAN: "UAN",
    phonenumbers.PhoneNumberType.VOICEMAIL: "VOICEMAIL",
    phonenumbers.PhoneNumberType.UNKNOWN: "UNKNOWN",
}


@dataclass
class ValidationResult:
    input: str
    valid: bool
    possible: bool
    e164: str | None = None
    international: str | None = None
    national: str | None = None
    rfc3966: str | None = None
    country_calling_code: int | None = None
    region_code: str | None = None
    national_number: str | None = None
    number_type: str | None = None
    description: str | None = None
    carrier: str | None = None
    timezones: list[str] | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def validate(raw_number: str, default_region: str | None = None) -> dict:
    raw_number = (raw_number or "").strip()
    region = default_region.strip().upper() if default_region else None

    try:
        parsed = phonenumbers.parse(raw_number, region)
    except NumberParseException as exc:
        return ValidationResult(
            input=raw_number,
            valid=False,
            possible=False,
            error=str(exc),
        ).to_dict()

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)

    if not is_possible:
        return ValidationResult(
            input=raw_number,
            valid=False,
            possible=False,
            country_calling_code=parsed.country_code,
            error="Number is not a possible phone number for this country.",
        ).to_dict()

    number_type = phonenumbers.number_type(parsed)
    timezones = list(pn_timezone.time_zones_for_number(parsed))
    carrier_name = pn_carrier.name_for_number(parsed, "en") or None
    description = pn_geocoder.description_for_number(parsed, "en") or None

    return ValidationResult(
        input=raw_number,
        valid=is_valid,
        possible=is_possible,
        e164=phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        international=phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ),
        national=phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.NATIONAL
        ),
        rfc3966=phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.RFC3966
        ),
        country_calling_code=parsed.country_code,
        region_code=phonenumbers.region_code_for_number(parsed),
        national_number=str(parsed.national_number),
        number_type=_TYPE_NAMES.get(number_type, "UNKNOWN") if is_valid else None,
        description=description,
        carrier=carrier_name,
        timezones=timezones or None,
    ).to_dict()


def format_number(raw_number: str, default_region: str | None = None) -> dict:
    raw_number = (raw_number or "").strip()
    region = default_region.strip().upper() if default_region else None

    try:
        parsed = phonenumbers.parse(raw_number, region)
    except NumberParseException as exc:
        return {"input": raw_number, "error": str(exc)}

    if not phonenumbers.is_possible_number(parsed):
        return {
            "input": raw_number,
            "error": "Number is not a possible phone number for this country.",
        }

    return {
        "input": raw_number,
        "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        "international": phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ),
        "national": phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.NATIONAL
        ),
        "rfc3966": phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.RFC3966
        ),
        "error": None,
    }


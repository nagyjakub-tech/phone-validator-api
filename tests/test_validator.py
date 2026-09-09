import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.validator import format_number, validate

# Well-known publicly documented example numbers (the kind used in
# libphonenumber's own docs / reserved fictional ranges like NANP 555) —
# not real subscriber numbers.


def test_valid_international_number_no_region_needed():
    result = validate("+14155552671")
    assert result["valid"] is True
    assert result["possible"] is True
    assert result["region_code"] == "US"
    assert result["country_calling_code"] == 1
    assert result["e164"] == "+14155552671"
    assert result["error"] is None


def test_uk_fixed_line_detected():
    result = validate("+442083661177")
    assert result["valid"] is True
    assert result["region_code"] == "GB"
    assert result["number_type"] == "FIXED_LINE"


def test_german_mobile_detected():
    result = validate("+491701234567")
    assert result["valid"] is True
    assert result["region_code"] == "DE"
    assert result["number_type"] == "MOBILE"


def test_us_toll_free_detected():
    result = validate("+18005551234")
    assert result["valid"] is True
    assert result["region_code"] == "US"
    assert result["number_type"] == "TOLL_FREE"


def test_national_format_requires_default_region():
    result = validate("0908338077", "SK")
    assert result["valid"] is True
    assert result["region_code"] == "SK"
    assert result["number_type"] == "MOBILE"
    assert result["e164"] == "+421908338077"


def test_national_format_without_region_returns_error():
    result = validate("0908338077")
    assert result["valid"] is False
    assert result["error"] is not None


def test_garbage_input_returns_error():
    result = validate("not-a-number")
    assert result["valid"] is False
    assert result["error"] is not None


def test_too_short_to_be_possible():
    result = validate("+1234", "US")
    assert result["valid"] is False
    assert result["possible"] is False


def test_format_endpoint_returns_all_formats():
    result = format_number("+421908338077")
    assert result["error"] is None
    assert result["e164"] == "+421908338077"
    assert result["national"] == "0908 338 077"
    assert result["international"].startswith("+421")
    assert result["rfc3966"].startswith("tel:")


def test_format_endpoint_invalid_number_returns_error():
    result = format_number("not-a-number")
    assert result["error"] is not None


"""
Phone Number Validator API — validate phone numbers worldwide (E.164
parsing, country/region detection, line-type detection, carrier and
timezone lookup) using Google's public libphonenumber numbering-plan data
via the `phonenumbers` Python port.

This is a pure offline lookup against bundled public numbering-plan data —
it never sends the number anywhere else, never contacts a telecom network,
and never stores input. Marginal cost per request is essentially zero.

Auth model: same as our other APIs — RapidAPI's proxy forwards every
request with an `X-RapidAPI-Proxy-Secret` header. We validate that header
so nobody can call this service directly and skip RapidAPI's billing.
Set the expected value via the RAPIDAPI_PROXY_SECRET environment variable.
If unset (local dev), auth is skipped.
"""
from __future__ import annotations

import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.validator import format_number, validate

PROXY_SECRET = os.environ.get("RAPIDAPI_PROXY_SECRET")

app = FastAPI(
    title="Phone Number Validator API",
    description=(
        "Validate phone numbers for any country — E.164 parsing, "
        "country/region detection, line-type (mobile/fixed/toll-free/VoIP) "
        "detection, carrier and timezone lookup. Offline numbering-plan "
        "data, no telecom network contact, no data stored."
    ),
    version="1.0.0",
)


class NumberRequest(BaseModel):
    number: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description=(
            "Phone number, ideally in international format with a leading "
            "'+'. If it has no country code, supply `country`."
        ),
        examples=["+421908338077"],
    )
    country: str | None = Field(
        None,
        min_length=2,
        max_length=2,
        description=(
            "ISO 3166-1 alpha-2 default region (e.g. 'US', 'SK'), used only "
            "when `number` has no leading '+' / country code."
        ),
        examples=["SK"],
    )


class ValidateResponse(BaseModel):
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


class FormatResponse(BaseModel):
    input: str
    e164: str | None = None
    international: str | None = None
    national: str | None = None
    rfc3966: str | None = None
    error: str | None = None


@app.middleware("http")
async def verify_rapidapi_proxy(request: Request, call_next):
    if request.url.path in ("/health", "/docs", "/openapi.json", "/"):
        return await call_next(request)
    if PROXY_SECRET:
        incoming = request.headers.get("x-rapidapi-proxy-secret")
        if incoming != PROXY_SECRET:
            return JSONResponse(
                status_code=403,
                content={"detail": "Missing/invalid RapidAPI proxy secret."},
            )
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = str(round((time.time() - start) * 1000, 2))
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/validate", response_model=ValidateResponse)
def validate_number(req: NumberRequest):
    return validate(req.number, req.country)


@app.post("/v1/format", response_model=FormatResponse)
def format_number_endpoint(req: NumberRequest):
    return format_number(req.number, req.country)

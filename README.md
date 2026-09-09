# Phone Number Validator API

API na overenie telefónnych čísel — parsovanie podľa E.164, rozpoznanie
krajiny/regiónu, typu čísla (mobil, pevná linka, bezplatné číslo, VoIP...),
operátora a časového pásma. Funguje pre celý svet, nie len jednu krajinu.
Postavené na knižnici `phonenumbers` (Python port Google-ovho
libphonenumber) — všetky číslovacie plány sú súčasťou knižnice, žiadne
volania na platené AI API ani telekomunikačné siete, takže náklad na jedno
použitie je prakticky nulový.

**Dôležité:** toto API nekontaktuje žiadnu telekomunikačnú sieť ani
operátora naživo, neukladá žiadne vstupy. Overuje formát a vyhľadáva vo
verejne publikovaných číslovacích plánoch — presne to, čo bežne robí každý
registračný formulár pri zadávaní telefónneho čísla.

## Čo to robí

- **`POST /v1/validate`** — overí platnosť čísla, rozpozná krajinu, typ
  čísla (MOBILE, FIXED_LINE, TOLL_FREE, VOIP, ...), operátora (ak je
  dostupný) a časové pásmo, vráti aj naformátované verzie (E.164,
  medzinárodný, národný, RFC3966 formát).
- **`POST /v1/format`** — ľahší endpoint, ktorý pre zadané číslo vráti len
  preformátované verzie (E.164 / medzinárodný / národný / RFC3966) bez
  plnej validácie.

### Príklad

```bash
curl -X POST http://127.0.0.1:8000/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"number": "+421908338077"}'
```

Odpoveď:
```json
{
  "input": "+421908338077",
  "valid": true,
  "possible": true,
  "e164": "+421908338077",
  "international": "+421 908 338 077",
  "national": "0908 338 077",
  "rfc3966": "tel:+421-908-338-077",
  "country_calling_code": 421,
  "region_code": "SK",
  "national_number": "908338077",
  "number_type": "MOBILE",
  "description": "Slovakia",
  "carrier": "Orange",
  "timezones": ["Europe/Bratislava"],
  "error": null
}
```

Ak číslo nemá medzinárodnú predvoľbu, treba doplniť `country`
(ISO 3166-1 alpha-2, napr. `"SK"`):

```bash
curl -X POST http://127.0.0.1:8000/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"number": "0908338077", "country": "SK"}'
```

## Lokálne spustenie

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest -v
```

## Nasadenie na verejný server

Rovnaký postup ako pri predchádzajúcich appkách — Render.com, free plán, Docker:

1. Nahraj repozitár na GitHub.
2. Na Rendri: "New" → "Web Service" → napoj repozitár → "Docker" build.
3. Over: `curl https://tvoja-url.onrender.com/health` → `{"status":"ok"}`.

## Napojenie na RapidAPI

Rovnaký postup ako pri predchádzajúcich API — nová API v RapidAPI Studiu,
Base URL na Render adresu, `X-RapidAPI-Proxy-Secret` do premennej
`RAPIDAPI_PROXY_SECRET` v Renderi, endpointy `/v1/validate` a
`/v1/format`, kategória napr. "Tools" alebo "Communication".

## Štruktúra projektu

```
app/
  main.py       - FastAPI server, endpointy, autentifikácia
  validator.py  - parsovanie a validácia čísel (phonenumbers knižnica)
tests/          - automatizované testy (pytest)
Dockerfile      - build a spustenie servera
```

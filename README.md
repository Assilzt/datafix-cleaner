# DataFix Cleaner

[![CI](https://github.com/Assilzt/datafix-cleaner/actions/workflows/ci.yml/badge.svg)](https://github.com/Assilzt/datafix-cleaner/actions) [![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org) [![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](LICENSE)

DataFix Cleaner is a privacy-first MVP that turns messy CSV/Excel files into profiled, cleaned data and reproducible pandas code. It handles Arabic-Indic digits, currency text, duplicate rows, numeric casting, and null filling through explicit JSON operations.

## Features
- Profile row counts, nulls, unique values, duplicates, types, and samples.
- Suggest cleaning operations from the uploaded data.
- Previewable, deterministic operations with a clean CSV download.
- Export the approved operation list as pandas code.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://localhost:8000/docs`.

## API example
```bash
curl -F 'file=@sample/sales.csv' http://localhost:8000/profile
curl -X POST http://localhost:8000/code -H 'Content-Type: application/json' \
  -d '{"operations":[{"op":"drop_duplicates","cols":[]}]}'
```

## Architecture
`Upload → Parse → Profile → Suggest operations → Approve/apply → Export CSV or pandas code`. The core module is independent of FastAPI so it can later power a web UI, background workers, or a CLI.

## Docker
```bash
docker build -t datafix-cleaner . && docker run --rm -p 8000:8000 datafix-cleaner
```

## License
MIT

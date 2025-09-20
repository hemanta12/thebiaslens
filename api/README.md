# API Server

## Installation

```bash
pip install -r requirements.txt
```

## Run Commands

### Local Development

```bash
uvicorn api.main:app --reload
```

### Production Deploy

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

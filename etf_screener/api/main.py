"""Aplicação FastAPI do ETF Screener."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from etf_screener.api.routes import router
from etf_screener.database.db import Database

app = FastAPI(
    title="ETF Screener API",
    description="API de leitura para composição e métricas fundamentais de ETFs.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    Database().init_schema()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

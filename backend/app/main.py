from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .logging_config import configure_logging

logger = configure_logging()
app = FastAPI(title="Mini SIEM Backend", version="1.0.0")


class OrderCreate(BaseModel):
    customer_id: str = Field(..., examples=["cust-1001"])
    amount: float = Field(..., gt=0)
    currency: str = Field(default="TRY", min_length=3, max_length=3)


def compact(data: Any) -> Any:
    if isinstance(data, dict):
        cleaned = {key: compact(value) for key, value in data.items()}
        return {
            key: value
            for key, value in cleaned.items()
            if value not in ("", None, [], {})
        }
    if isinstance(data, list):
        return [item for item in (compact(value) for value in data) if item not in ("", None, [], {})]
    return data


def request_payload(
    request: Request,
    request_id: str,
    duration_ms: float | None = None,
    status_code: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "event": {
            "dataset": "mini-siem.backend",
            "kind": "event",
            "category": ["web"],
        },
        "trace": {"id": request_id},
        "http": {
            "request": {"method": request.method},
            "response": {"status_code": status_code},
        },
        "url": {
            "path": request.url.path,
            "query": request.url.query or None,
        },
        "client": {
            "ip": request.client.host if request.client else None,
        },
        "user_agent": {
            "original": request.headers.get("user-agent"),
        },
        "labels": {
            "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
        },
    }
    return compact(payload)


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = (time.perf_counter() - started_at) * 1000
        payload = request_payload(request, request_id, duration_ms=duration_ms, status_code=500)
        payload["event"]["category"] = ["error"]
        payload["event"]["type"] = ["exception"]
        payload["event"]["outcome"] = "failure"
        payload["error"] = {
            "message": str(exc),
            "type": exc.__class__.__name__,
        }
        logger.error("Unhandled application error", extra={"payload": payload}, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )

    duration_ms = (time.perf_counter() - started_at) * 1000
    payload = request_payload(
        request,
        request_id,
        duration_ms=duration_ms,
        status_code=response.status_code,
    )
    payload["event"]["type"] = ["access"]
    payload["event"]["outcome"] = "success" if response.status_code < 400 else "failure"

    if response.status_code >= 500:
        payload["event"]["category"] = ["error"]
        logger.error("Request completed with server error", extra={"payload": payload})
    elif response.status_code >= 400:
        logger.warning("Request completed with client error", extra={"payload": payload})
    else:
        logger.info("Request completed", extra={"payload": payload})

    response.headers["X-Request-ID"] = request_id
    return response


@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "Application started",
        extra={
            "payload": {
                "event": {
                    "dataset": "mini-siem.lifecycle",
                    "kind": "event",
                    "category": ["process"],
                    "type": ["start"],
                }
            }
        },
    )


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Mini SIEM backend is running"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/products/{product_id}")
async def get_product(product_id: int) -> dict[str, Any]:
    if product_id == 13:
        return JSONResponse(status_code=404, content={"detail": "Product not found"})

    return {"product_id": product_id, "name": f"product-{product_id}"}


@app.post("/orders", status_code=201)
async def create_order(order: OrderCreate, request: Request) -> dict[str, Any]:
    order_id = f"ord-{uuid.uuid4().hex[:8]}"
    logger.info(
        "Order created",
        extra={
            "payload": {
                "event": {
                    "dataset": "mini-siem.orders",
                    "kind": "event",
                    "category": ["application"],
                    "type": ["info"],
                },
                "trace": {"id": request.state.request_id},
                "order": {
                    "id": order_id,
                    "customer_id": order.customer_id,
                    "amount": order.amount,
                    "currency": order.currency,
                },
                "labels": {"business_event": "order_created"},
            }
        },
    )
    return {"order_id": order_id, "status": "created"}


@app.get("/simulate/error")
async def simulate_error() -> dict[str, str]:
    raise RuntimeError("Synthetic failure for dashboard testing")


@app.get("/simulate/slow")
async def simulate_slow() -> dict[str, str]:
    await asyncio.sleep(1.2)
    return {"message": "Slow request completed"}

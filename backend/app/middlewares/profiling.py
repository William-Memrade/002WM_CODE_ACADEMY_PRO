"""
CodeAcademy Pro — Query Profiling Middleware
Tracks SQL query count and total DB time per request.
Reports via response headers (X-Query-Count, X-DB-Time-Ms).
"""

import time
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import event

from app.db.session import engine

# Context variables for per-request tracking
_query_count: ContextVar[int] = ContextVar("query_count", default=0)
_query_time: ContextVar[float] = ContextVar("query_time", default=0.0)
_query_start: ContextVar[float] = ContextVar("query_start", default=0.0)


def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    _query_start.set(time.perf_counter())


def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    elapsed = time.perf_counter() - _query_start.get(0.0)
    _query_count.set(_query_count.get(0) + 1)
    _query_time.set(_query_time.get(0.0) + elapsed)


def setup_query_profiling():
    """Attach SQLAlchemy event listeners for query counting."""
    event.listen(engine.sync_engine, "before_cursor_execute", _before_cursor_execute)
    event.listen(engine.sync_engine, "after_cursor_execute", _after_cursor_execute)


class QueryProfilingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that reports query metrics in response headers.
    Headers added:
        X-Query-Count: number of SQL queries executed
        X-DB-Time-Ms: total database time in milliseconds
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Reset counters for this request
        _query_count.set(0)
        _query_time.set(0.0)

        response: Response = await call_next(request)

        # Inject metrics headers
        count = _query_count.get(0)
        db_time_ms = round(_query_time.get(0.0) * 1000, 2)
        response.headers["X-Query-Count"] = str(count)
        response.headers["X-DB-Time-Ms"] = str(db_time_ms)

        return response

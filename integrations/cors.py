"""CORS allowlist for the KALATRACE API."""
from __future__ import annotations

import os
from collections.abc import Mapping

_LOCAL_DEVELOPMENT_ORIGINS = (
    "http://127.0.0.1:5500",
    "http://localhost:5500",
)
_DEPLOYED_FRONTEND_ORIGINS = (
    # GitHub Pages origin for /kalatrace_desenvolvimento/.
    "https://turkista.github.io",
)


def get_cors_origins(environ: Mapping[str, str] | None = None) -> list[str]:
    """Return configured origins plus the explicitly deployed frontend origin.

    KALATRACE_CORS_ORIGINS can add or replace local development origins, but it
    cannot accidentally remove the published frontend from the API allowlist.
    """
    env = os.environ if environ is None else environ
    configured = env.get("KALATRACE_CORS_ORIGINS")
    if configured is None:
        configured = ",".join(_LOCAL_DEVELOPMENT_ORIGINS)

    origins = list(dict.fromkeys(
        origin.strip()
        for origin in configured.split(",")
        if origin.strip()
    ))
    for origin in _DEPLOYED_FRONTEND_ORIGINS:
        if origin not in origins:
            origins.append(origin)
    return origins

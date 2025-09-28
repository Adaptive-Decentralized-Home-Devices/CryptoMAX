"""Simple script to collect crypto staking interest rates from public APIs.

The script queries a handful of well known staking providers and prints the
latest advertised APY or APR figures.  Each provider exposes its data through a
small REST endpoint, so the script only depends on the standard library and the
`requests` package for HTTP requests.

The goal of this program is to provide a very small example of how someone can
pull staking information from the wider internet in a repeatable way.
"""

from __future__ import annotations

import dataclasses
import json
import sys
from typing import Callable, Dict, Iterable, List, Optional

import requests


@dataclasses.dataclass
class RateRecord:
    """Normalized representation of a staking rate."""

    provider: str
    network: str
    rate: float
    metric: str  # "apy" or "apr"
    source_url: str
    raw: Dict[str, object]


class RateFetchError(RuntimeError):
    """Raised when a provider cannot be queried successfully."""


ProviderFetcher = Callable[[], Iterable[RateRecord]]


def _fetch_json(url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    response = requests.get(url, headers=headers or {"User-Agent": "CryptoMAX Staking Bot"}, timeout=15)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:  # pragma: no cover - defensive logging path
        raise RateFetchError(f"HTTP error {response.status_code} from {url}") from exc

    try:
        return response.json()
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive logging path
        raise RateFetchError(f"Invalid JSON payload from {url}") from exc


def fetch_lido() -> Iterable[RateRecord]:
    """Fetch staking APY values from Lido's public API."""

    url = "https://stake.lido.fi/api/networks"
    payload = _fetch_json(url)

    # The payload is a dictionary keyed by network names.
    networks = payload.get("data") or payload
    if not isinstance(networks, dict):
        raise RateFetchError("Unexpected Lido payload format")

    for network_name, details in networks.items():
        if not isinstance(details, dict):
            continue
        metric_name = "apy" if "apy" in details else "apr"
        raw_rate = details.get(metric_name)
        if raw_rate is None:
            continue
        try:
            rate_value = float(raw_rate)
        except (TypeError, ValueError):
            continue
        yield RateRecord(
            provider="Lido",
            network=str(details.get("displayName") or network_name).title(),
            rate=rate_value,
            metric=metric_name,
            source_url=url,
            raw=details,
        )


def fetch_rocket_pool() -> Iterable[RateRecord]:
    """Fetch Rocket Pool staking APR."""

    url = "https://api.rocketpool.net/api/apr"
    payload = _fetch_json(url)

    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise RateFetchError("Unexpected Rocket Pool payload format")

    staking_rate = data.get("staking") or data.get("total")
    if staking_rate is None:
        raise RateFetchError("Rocket Pool response missing staking rate")

    yield RateRecord(
        provider="Rocket Pool",
        network="Ethereum",
        rate=float(staking_rate),
        metric="apr",
        source_url=url,
        raw=data,
    )


def fetch_kraken() -> Iterable[RateRecord]:
    """Fetch staking rates from Kraken."""

    url = "https://api.kraken.com/0/public/Staking/Assets"
    payload = _fetch_json(url)

    result = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(result, dict):
        raise RateFetchError("Unexpected Kraken payload format")

    for asset_code, details in result.items():
        if not isinstance(details, dict):
            continue
        network = details.get("staking_asset") or asset_code
        apr = details.get("apy") or details.get("apr") or details.get("reward_apr")
        if apr is None:
            continue
        try:
            rate_value = float(apr)
        except (TypeError, ValueError):
            continue
        yield RateRecord(
            provider="Kraken",
            network=str(network),
            rate=rate_value,
            metric="apr",
            source_url=url,
            raw=details,
        )


PROVIDERS: Dict[str, ProviderFetcher] = {
    "lido": fetch_lido,
    "rocket_pool": fetch_rocket_pool,
    "kraken": fetch_kraken,
}


def collect_rates() -> List[RateRecord]:
    records: List[RateRecord] = []
    for name, fetcher in PROVIDERS.items():
        try:
            records.extend(fetcher())
        except Exception as exc:
            print(f"⚠️  Failed to fetch rates from {name}: {exc}", file=sys.stderr)
    return records


def format_table(records: Iterable[RateRecord]) -> str:
    headers = ("Provider", "Network", "Rate", "Metric", "Source")
    rows = [headers]
    for record in records:
        rows.append(
            (
                record.provider,
                record.network,
                f"{record.rate:.2f}%",
                record.metric.upper(),
                record.source_url,
            )
        )

    if len(rows) == 1:
        return "No staking rates available."

    column_widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]

    def render_row(row: Iterable[str]) -> str:
        return " | ".join(cell.ljust(column_widths[i]) for i, cell in enumerate(row))

    separator = "-+-".join("-" * width for width in column_widths)
    lines = [render_row(rows[0]), separator]
    lines.extend(render_row(row) for row in rows[1:])
    return "\n".join(lines)


def main() -> None:
    records = collect_rates()
    print(format_table(records))


if __name__ == "__main__":
    main()

"""Simple script to collect crypto staking interest rates from public APIs.

The script queries a collection of well known staking providers (Lido, Rocket
Pool, Kraken, Coinbase, Crypto.com, KuCoin, Binance, and Nexo), normalizes the
responses, persists the data as JSON, and prints an ASCII table so you can
quickly inspect the advertised APR or APY for each network. Pass ``--low-risk``
to label the output for a "Low Risk" button or option and filter the table to
listings that reference well known stablecoins.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence

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


DEFAULT_HEADERS = {
    "User-Agent": "CryptoMAX Staking Bot",
    "Accept": "application/json",
}

STABLECOIN_KEYWORDS = {
    "USDC",
    "USDT",
    "DAI",
    "BUSD",
    "TUSD",
    "USDP",
    "GUSD",
    "USDD",
    "USTC",
    "EURT",
    "FRAX",
    "EURS",
    "LUSD",
}


def _fetch_json(url: str, headers: Optional[Dict[str, str]] = None) -> object:
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)
    response = requests.get(url, headers=merged_headers, timeout=15)
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


def _normalize_percentage(raw_value: object) -> Optional[float]:
    """Convert a raw numeric rate to a human friendly percentage."""

    if raw_value is None:
        return None
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    if value <= 1:
        value *= 100
    return value


def _pick_first(mapping: Mapping[str, object], keys: Sequence[str]) -> Optional[object]:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def fetch_coinbase() -> Iterable[RateRecord]:
    """Fetch staking APYs from Coinbase's staking product catalog."""

    url = "https://api.coinbase.com/v2/staking/products"
    payload = _fetch_json(url, headers={"CB-VERSION": "2024-01-01"})
    products = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(products, list):
        raise RateFetchError("Unexpected Coinbase payload format")

    for product in products:
        if not isinstance(product, dict):
            continue
        rate_value = _normalize_percentage(
            _pick_first(
                product,
                ("apy", "apr", "rewards_apy", "estimated_apy", "rewardRate", "rewardsRate"),
            )
        )
        if rate_value is None:
            continue
        network = _pick_first(
            product,
            ("asset_name", "asset", "name", "asset_symbol"),
        )
        yield RateRecord(
            provider="Coinbase",
            network=str(network or "Unknown"),
            rate=rate_value,
            metric="apy",
            source_url=url,
            raw=product,
        )


def fetch_crypto_com() -> Iterable[RateRecord]:
    """Fetch staking rates from Crypto.com's Earn product catalog."""

    url = "https://crypto.com/earn/api/v2/products"
    payload = _fetch_json(url)
    data = payload.get("data") if isinstance(payload, dict) else None
    products = data.get("items") if isinstance(data, dict) else None
    if not isinstance(products, list):
        raise RateFetchError("Unexpected Crypto.com payload format")

    for product in products:
        if not isinstance(product, dict):
            continue
        rate_value = _normalize_percentage(
            _pick_first(
                product,
                ("rate", "apy", "apr", "reward_rate"),
            )
        )
        if rate_value is None:
            continue
        network = _pick_first(
            product,
            ("displayName", "asset", "symbol", "name"),
        )
        yield RateRecord(
            provider="Crypto.com",
            network=str(network or "Unknown"),
            rate=rate_value,
            metric="apy",
            source_url=url,
            raw=product,
        )


def fetch_kucoin() -> Iterable[RateRecord]:
    """Fetch staking rates from KuCoin's Earn catalog."""

    url = "https://www.kucoin.com/_api/earning/earn/product/list?page=1&pageSize=200&status=ALL&type=ALL"
    payload = _fetch_json(url)
    data = payload.get("data") if isinstance(payload, dict) else None
    products = data.get("items") if isinstance(data, dict) else None
    if not isinstance(products, list):
        raise RateFetchError("Unexpected KuCoin payload format")

    for product in products:
        if not isinstance(product, dict):
            continue
        rate_value = _normalize_percentage(
            _pick_first(
                product,
                ("apr", "apy", "yieldRate", "rate"),
            )
        )
        if rate_value is None:
            continue
        network = _pick_first(
            product,
            ("currency", "name", "displayName"),
        )
        yield RateRecord(
            provider="KuCoin",
            network=str(network or "Unknown"),
            rate=rate_value,
            metric="apr",
            source_url=url,
            raw=product,
        )


def fetch_binance() -> Iterable[RateRecord]:
    """Fetch flexible staking (BNB) rates from Binance."""

    url = "https://www.binance.com/bapi/earn/v2/friendly/pos/product/list"
    payload = _fetch_json(url)
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise RateFetchError("Unexpected Binance payload format")
    products = data.get("result") or data.get("data") or []
    if not isinstance(products, list):
        raise RateFetchError("Unexpected Binance product payload")

    for product in products:
        if not isinstance(product, dict):
            continue
        rate_value = _normalize_percentage(
            _pick_first(
                product,
                ("configAnnualInterestRate", "apr", "apy", "maxApy"),
            )
        )
        if rate_value is None:
            continue
        network = _pick_first(
            product,
            ("asset", "productName", "displayName"),
        )
        yield RateRecord(
            provider="Binance",
            network=str(network or "Unknown"),
            rate=rate_value,
            metric="apr",
            source_url=url,
            raw=product,
        )


def fetch_nexo() -> Iterable[RateRecord]:
    """Fetch staking (earn) rates from Nexo."""

    url = "https://platform.nexo.io/api/v2/earn/rates"
    payload = _fetch_json(url)
    data = payload.get("data") if isinstance(payload, dict) else None
    products = data.get("rates") if isinstance(data, dict) else None
    if not isinstance(products, list):
        raise RateFetchError("Unexpected Nexo payload format")

    for product in products:
        if not isinstance(product, dict):
            continue
        base_rate = _normalize_percentage(
            _pick_first(
                product,
                ("rate", "apy", "apr", "baseRate"),
            )
        )
        if base_rate is None:
            continue
        network = _pick_first(
            product,
            ("currency", "symbol", "name"),
        )
        yield RateRecord(
            provider="Nexo",
            network=str(network or "Unknown"),
            rate=base_rate,
            metric="apy",
            source_url=url,
            raw=product,
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
    "coinbase": fetch_coinbase,
    "crypto_com": fetch_crypto_com,
    "kucoin": fetch_kucoin,
    "binance": fetch_binance,
    "nexo": fetch_nexo,
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


def save_rates(records: Iterable[RateRecord], output_path: Path) -> None:
    """Persist normalized staking rates to disk for later processing."""

    serialized = [dataclasses.asdict(record) for record in records]
    output_path.write_text(json.dumps(serialized, indent=2) + "\n")


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch staking rates from major exchanges and optionally focus on "
            "stablecoin-oriented, lower-risk listings."
        )
    )
    parser.add_argument(
        "--low-risk",
        action="store_true",
        help=(
            "Filter results to listings whose network name references a known "
            "stablecoin (for example USDC, USDT, or DAI)."
        ),
    )
    return parser.parse_args(argv)


def _is_stablecoin_network(name: str) -> bool:
    normalized = name.upper()
    return any(keyword in normalized for keyword in STABLECOIN_KEYWORDS)


def filter_low_risk(records: Iterable[RateRecord]) -> List[RateRecord]:
    """Return only records that appear to reference stablecoin staking products."""

    return [record for record in records if _is_stablecoin_network(record.network)]


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = _parse_args(argv)
    records = collect_rates()
    if args.low_risk:
        records = filter_low_risk(records)
    save_rates(records, Path("staking_rates.json"))
    if args.low_risk:
        print("Low-Risk Stablecoin View\n")
    print(format_table(records))


if __name__ == "__main__":
    main()

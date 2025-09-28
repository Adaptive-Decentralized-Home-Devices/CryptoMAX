# CryptoMAX

CryptoMAX is a lightweight Python script that compares staking yields across a broad set of centralized providers. It queries public APIs for Lido, Rocket Pool, Kraken, Coinbase, Crypto.com, KuCoin, Binance, and Nexo, normalizes the responses, stores the normalized payloads on disk, and prints a console table so you can quickly spot the advertised APR or APY for each network. A dedicated **Low-Risk Stablecoin view** is available when you want to focus on exchanges that list well-known stablecoins.

## Prerequisites

- Python 3.9 or newer.
- Internet access to reach the provider APIs.

> **Tip:** Create and activate a virtual environment before installing dependencies to keep them isolated from the rest of your system.

## Installation

Install the single runtime dependency with `pip`:

```bash
pip install -r requirements.txt
```

## Usage

After installing dependencies, run the script directly:

```bash
python staking_rates.py
```

To label the output as the “Low Risk” option and restrict it to stablecoin-oriented listings, pass the `--low-risk` flag:

```bash
python staking_rates.py --low-risk
```

Each execution produces two outputs:

1. A JSON snapshot saved to `staking_rates.json` containing normalized rate entries for every successful provider query. You can feed this file into other automation later without refetching the upstream APIs.
2. A console table summarizing the most recent rates. The table includes the following columns:

- **Provider** – The staking platform (for example Lido, Coinbase, Binance).
- **Network** – The blockchain or asset associated with the rate.
- **Rate** – The advertised percentage formatted to two decimals.
- **Metric** – Whether the rate is expressed as APR or APY.
- **Source** – The endpoint that supplied the data so you can verify the results.

If no rates can be retrieved, the script prints `No staking rates available.` instead of the table. Network or parsing errors from individual providers are caught and reported as warnings on standard error, and the script continues processing the remaining providers.

## Data Sources

| Provider     | Endpoint                                                             | Notes |
|--------------|----------------------------------------------------------------------|-------|
| Lido         | `https://stake.lido.fi/api/networks`                                  | Returns APY or APR per supported Lido network. |
| Rocket Pool  | `https://api.rocketpool.net/api/apr`                                  | Supplies the current Ethereum staking APR. |
| Kraken       | `https://api.kraken.com/0/public/Staking/Assets`                      | Lists supported staking assets with APR/APY figures. |
| Coinbase     | `https://api.coinbase.com/v2/staking/products`                        | Catalog of Coinbase staking assets and their quoted APYs. |
| Crypto.com   | `https://crypto.com/earn/api/v2/products`                             | Earn product inventory with reward rates. |
| KuCoin       | `https://www.kucoin.com/_api/earning/earn/product/list`               | KuCoin Earn listings including flexible and fixed terms. |
| Binance      | `https://www.binance.com/bapi/earn/v2/friendly/pos/product/list`      | Binance savings and staking rates for supported tokens. |
| Nexo         | `https://platform.nexo.io/api/v2/earn/rates`                          | Nexo earn rates for supported assets. |

## Script Structure

The core logic is organized into a few small, composable helpers:

### Data fetching helpers

`_fetch_json` centralizes HTTP requests using `requests.get`, applies a user-agent header, enforces a 15 second timeout, and raises `RateFetchError` if a response fails or the JSON payload cannot be parsed.

### Provider-specific collectors

`fetch_lido`, `fetch_rocket_pool`, `fetch_kraken`, `fetch_coinbase`, `fetch_crypto_com`, `fetch_kucoin`, `fetch_binance`, and `fetch_nexo` wrap `_fetch_json`, interpret the provider-specific payloads, and yield standardized `RateRecord` instances. Each function isolates any response shape quirks so failures in one provider do not affect the others.

### Normalization

`RateRecord` is a dataclass that captures the provider name, network, percentage value, rate metric (APR or APY), and the originating URL along with the raw payload snippet. The `collect_rates` function iterates through all registered providers, aggregating the resulting `RateRecord` items while printing a warning if any provider raises an exception. The `save_rates` helper writes the normalized list to `staking_rates.json` so other tooling can reuse the snapshot without hitting the upstream APIs again.

### Table rendering

`format_table` takes the aggregated records and builds an ASCII table with padded columns. It also produces a friendly fallback string when the list of records is empty. `filter_low_risk` screens the normalized records for stablecoin keywords (USDC, USDT, DAI, and others) so the script can power a “Low Risk” button or option in a UI. `_parse_args` reads the optional `--low-risk` flag, and `main` ties everything together by collecting the rates, applying the requested view, and printing the formatted output.

## License

This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.

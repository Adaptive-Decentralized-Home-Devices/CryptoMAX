# CryptoMAX

CryptoMAX is a lightweight Python script that compares staking yields across a few well known Ethereum staking providers. It queries public APIs for Lido, Rocket Pool, and Kraken, normalizes the responses, and prints a console table so you can quickly spot the advertised APR or APY for each network.

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

The script fetches rates from each provider and renders a table with the following columns:

- **Provider** – The staking platform (Lido, Rocket Pool, Kraken).
- **Network** – The blockchain or asset associated with the rate.
- **Rate** – The advertised percentage formatted to two decimals.
- **Metric** – Whether the rate is expressed as APR or APY.
- **Source** – The endpoint that supplied the data so you can verify the results.

If no rates can be retrieved, the script prints `No staking rates available.` instead of the table. Network or parsing errors from individual providers are caught and reported as warnings on standard error, and the script continues processing the remaining providers.

## Data Sources

| Provider     | Endpoint                                                  | Notes |
|--------------|-----------------------------------------------------------|-------|
| Lido         | `https://stake.lido.fi/api/networks`                       | Returns APY or APR per supported Lido network. |
| Rocket Pool  | `https://api.rocketpool.net/api/apr`                       | Supplies the current Ethereum staking APR. |
| Kraken       | `https://api.kraken.com/0/public/Staking/Assets`           | Lists supported staking assets with APR/APY figures. |

## Script Structure

The core logic is organized into a few small, composable helpers:

### Data fetching helpers

`_fetch_json` centralizes HTTP requests using `requests.get`, applies a user-agent header, enforces a 15 second timeout, and raises `RateFetchError` if a response fails or the JSON payload cannot be parsed.

### Provider-specific collectors

`fetch_lido`, `fetch_rocket_pool`, and `fetch_kraken` wrap `_fetch_json`, interpret the provider-specific payloads, and yield standardized `RateRecord` instances. Each function isolates any response shape quirks so failures in one provider do not affect the others.

### Normalization

`RateRecord` is a dataclass that captures the provider name, network, percentage value, rate metric (APR or APY), and the originating URL along with the raw payload snippet. The `collect_rates` function iterates through all registered providers, aggregating the resulting `RateRecord` items while printing a warning if any provider raises an exception.

### Table rendering

`format_table` takes the aggregated records and builds an ASCII table with padded columns. It also produces a friendly fallback string when the list of records is empty. `main` ties everything together by collecting the rates and printing the formatted output.

## License

This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.

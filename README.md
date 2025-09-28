
---This Android app helps users explore and compare **staking interest rates** for cryptocurrencies across reputable exchanges based on their **risk tolerance** (Low, Medium, High).
--+CryptoMAX provides a multithreaded Java data ingestion pipeline that gathers exchange listings, 
--+current gas fee estimates, and staking APR/APY snapshots. The scraper persists the normalized 
--+information to a lightweight SQLite database so that future Android or desktop clients can reuse 
--+the aggregated data without having to make direct network calls.
-- 
---Built for crypto investors who want to **beat inflation** and generate **passive income** through **staking** and **yield farming** strategies 💸
--+The program prefers live public APIs but gracefully falls back to bundled sample datasets when 
--+network access is unavailable or rate limited. This makes the tool ideal for prototyping user 
--+interfaces or verifying database integrations offline.
-- 
------
--+## Features
-- 
---## 🚀 Features
--+- 🧵 **Multithreaded scraping** – Exchange, gas fee, and staking tasks run concurrently using an
--+  `ExecutorService` to reduce total scraping time.
--+- 🌐 **HTTP scraping helpers** – A shared HTTP client (powered by Jsoup) applies sensible headers
--+  and timeouts to play nicely with public APIs.
--+- 💾 **SQLite persistence** – All datasets are written to `cryptomax.db`, ready for consumption by
--+  Android Room, desktop applications, or analytics scripts.
--+- 🛟 **Offline fallbacks** – Curated JSON samples ensure the database can still be populated when
--+  the network is unavailable or remote services block automated requests.
-- 
---- ✅ **Low Risk**: Stablecoin staking (USDC, USDT, DAI) with positive APY from trusted sources
---- ✅ **Medium Risk**: Mix of high-volume cryptos (BTC, ETH, SOL) with staking options
---- ✅ **High Risk**: ⚠️ Advanced mode with gas fee optimization and high-yield assets
---- ✅ Real-time data aggregation using:
---  - DeFi Llama API (primary)
---  - HTML scraping for exchanges like Nexo
---- ✅ Links to exchanges and staking products
---- ✅ User-friendly interface with risk warning system
--+## Project Layout
-- 
------
--+```
--+CryptoMAX/
--+├── build.gradle               # Gradle configuration with dependencies
--+├── settings.gradle            # Declares the Gradle root project name
--+├── src/main/java/com/cryptomax/
--+│   ├── CryptoDataScraper.java # Main entry point orchestrating the scraping workflow
--+│   ├── DatabaseManager.java   # SQLite helper that creates tables and stores results
--+│   ├── ExchangeInfo.java      # Data model for centralized exchanges
--+│   ├── GasFeeInfo.java        # Data model for gas fee snapshots
--+│   ├── HttpFetcher.java       # Shared HTTP utility with timeouts/user agent headers
--+│   └── StakingPoolInfo.java   # Data model for staking pool yields
--+└── src/main/resources/fallback/
--+    ├── exchanges.json         # Sample exchange list used when live calls fail
--+    ├── gas-fees.json          # Sample gas fee metrics for multiple chains
--+    └── staking-pools.json     # Sample staking APR/APY data
--+```
-- 
---## 🎥 Preview
--+## Getting Started
-- 
---| Risk Option | Data View | Warning |
---|-------------|-----------|---------|
---| ![Risk Selection](screenshots/risk_options.png) | ![Results](screenshots/staking_data.png) | ![High Risk](screenshots/high_risk_warning.png) |
--+### Prerequisites
-- 
---> 📸 *Add your screenshots to a `/screenshots` folder in your repo for these previews to work.*
--+- Java 17 or newer (managed automatically via the Gradle toolchain)
--+- Gradle (the project uses the Gradle wrapper once it has been generated)
-- 
------
--+### Build the Project
-- 
---## 🧱 Architecture
--+```bash
--+./gradlew build
--+```
-- 
--+Gradle will download all required dependencies: Jsoup for HTTP access, Gson for JSON parsing, and
--+SQLite JDBC for database access.
--+
--+### Run the Scraper
--+
--+```bash
--+./gradlew run
--+```
--+
--+This command launches `CryptoDataScraper`. The scraper attempts to contact the following public
--+endpoints:
--+
--+- `https://api.coingecko.com/api/v3/exchanges?per_page=20&page=1`
--+- `https://api.gasprice.io/v1/estimates`
--+- `https://yields.llama.fi/pools`
--+
--+If any request fails, CryptoMAX automatically loads the equivalent bundled fallback dataset so that
--+the resulting `cryptomax.db` file is always populated with representative data.
--+
--+### Database Schema
--+
--+The SQLite database contains three tables:
--+
--+| Table           | Description                                     |
--+|-----------------|-------------------------------------------------|
--+| `exchanges`     | Basic metadata about centralized exchanges      |
--+| `gas_fees`      | Slow/standard/fast gas fee estimates per chain  |
--+| `staking_rates` | APR/APY metrics for curated staking pools       |
--+
--+All tables include unique constraints to prevent duplicate records on subsequent runs. Developers
--+can inspect the generated database with any SQLite browser or with the `sqlite3` CLI.
--+
--+### Using the Data in Android
--+
--+Because Android supports SQLite natively, you can copy `cryptomax.db` into your Android project (for
--+example under `src/main/assets/`) and access the pre-populated tables via Room or the Android SQLite
--+APIs. Alternatively, bundle the scraper as part of your backend stack to refresh the database on a
--+schedule and deliver updates to clients.
--+
--+## Extending the Scraper
--+
--+- Add new scraping tasks by creating a model class, update the database schema, and submit another
--+  callable to the executor.
--+- Replace the fallback JSON files with your own curated datasets or a company API stub.
--+- Integrate scheduling (e.g., using Quartz or Spring) to refresh the database periodically.
--+
--+## License
--+
--+This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.
-- 
--EOF
--)
-+# CryptoMAX
-+
-+CryptoMAX is a Java command-line tool that aggregates stablecoin APY offers from popular centralized
-+exchanges such as Coinbase, Binance, KuCoin, Crypto.com, and Nexo. The scraper tries to pull the most
-+recent rates directly from the exchanges. When a site blocks automated requests or the network is not
-+available, CryptoMAX falls back to curated sample datasets so the pipeline always produces a
-+reference snapshot.
-+
-+## Features
-+
-+- **Pluggable scrapers** – Each exchange has a dedicated parser that knows how to extract stablecoin
-+  yields from JSON or HTML payloads.
-+- **Resilient HTTP client** – A shared `HttpFetcher` applies user-agent headers and reasonable
-+  timeouts to behave like a regular browser.
-+- **Concurrent execution** – All exchange scrapers run in parallel using an `ExecutorService` to keep
-+  runtime short.
-+- **Structured exports** – Results are printed as a formatted table and persisted to
-+  `build/stablecoin-offers.json` for later consumption.
-+- **Offline fallbacks** – JSON fixtures under `src/main/resources/fallback/` guarantee that you still
-+  get a useful dataset even when live scraping fails.
-+
-+## Getting Started
-+
-+### Prerequisites
-+
-+- Java 21 (the Gradle build configures the toolchain automatically).
-+- The included Gradle wrapper (`./gradlew`).
-+
-+### Build
-+
-+```bash
-+./gradlew build
-+```
-+
-+### Run the scraper
-+
-+```bash
-+./gradlew run
-+```
-+
-+Running the scraper prints a table summarizing the available stablecoin APYs and writes the same data
-+as JSON to `build/stablecoin-offers.json`.
-+
-+## Project Layout
-+
-+```
-+CryptoMAX/
-+├── build.gradle
-+├── settings.gradle
-+├── src/main/java/com/cryptomax/
-+│   ├── CryptoDataScraper.java      # Main entry point
-+│   ├── http/HttpFetcher.java       # Shared HTTP helper
-+│   ├── model/StablecoinOffer.java  # Immutable representation of an offer
-+│   ├── scraper/                    # Exchange-specific scraper implementations
-+│   └── util/                       # Serialization helpers
-+└── src/main/resources/fallback/    # Offline datasets used when live scraping fails
-+```
-+
-+## Extending
-+
-+1. Create a new class in `src/main/java/com/cryptomax/scraper/` that extends `BaseJsonScraper` and
-+   implements the parsing logic for the new exchange.
-+2. Drop a fallback JSON file in `src/main/resources/fallback/` that follows the same format as the
-+   existing fixtures.
-+3. Register the scraper in `CryptoDataScraper` so it runs alongside the others.
-+
-+## License
-+
-+This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.
+CryptoMAX is a lightweight Python script that compares staking yields across a few well known Ethereum staking providers. It queries public APIs for Lido, Rocket Pool, and Kraken, normalizes the responses, and prints a console table so you can quickly spot the advertised APR or APY for each network.
+
+## Prerequisites
+
+- Python 3.9 or newer.
+- Internet access to reach the provider APIs.
+
+> **Tip:** Create and activate a virtual environment before installing dependencies to keep them isolated from the rest of your system.
+
+## Installation
+
+Install the single runtime dependency with `pip`:
+
+```bash
+pip install -r requirements.txt
+```
+
+## Usage
+
+After installing dependencies, run the script directly:
+
+```bash
+python staking_rates.py
+```
+
+The script fetches rates from each provider and renders a table with the following columns:
+
+- **Provider** – The staking platform (Lido, Rocket Pool, Kraken).
+- **Network** – The blockchain or asset associated with the rate.
+- **Rate** – The advertised percentage formatted to two decimals.
+- **Metric** – Whether the rate is expressed as APR or APY.
+- **Source** – The endpoint that supplied the data so you can verify the results.
+
+If no rates can be retrieved, the script prints `No staking rates available.` instead of the table. Network or parsing errors from individual providers are caught and reported as warnings on standard error, and the script continues processing the remaining providers.
+
+## Data Sources
+
+| Provider     | Endpoint                                                  | Notes |
+|--------------|-----------------------------------------------------------|-------|
+| Lido         | `https://stake.lido.fi/api/networks`                       | Returns APY or APR per supported Lido network. |
+| Rocket Pool  | `https://api.rocketpool.net/api/apr`                       | Supplies the current Ethereum staking APR. |
+| Kraken       | `https://api.kraken.com/0/public/Staking/Assets`           | Lists supported staking assets with APR/APY figures. |
+
+## Script Structure
+
+The core logic is organized into a few small, composable helpers:
+
+### Data fetching helpers
+
+`_fetch_json` centralizes HTTP requests using `requests.get`, applies a user-agent header, enforces a 15 second timeout, and raises `RateFetchError` if a response fails or the JSON payload cannot be parsed.
+
+### Provider-specific collectors
+
+`fetch_lido`, `fetch_rocket_pool`, and `fetch_kraken` wrap `_fetch_json`, interpret the provider-specific payloads, and yield standardized `RateRecord` instances. Each function isolates any response shape quirks so failures in one provider do not affect the others.
+
+### Normalization
+
+`RateRecord` is a dataclass that captures the provider name, network, percentage value, rate metric (APR or APY), and the originating URL along with the raw payload snippet. The `collect_rates` function iterates through all registered providers, aggregating the resulting `RateRecord` items while printing a warning if any provider raises an exception.
+
+### Table rendering
+
+`format_table` takes the aggregated records and builds an ASCII table with padded columns. It also produces a friendly fallback string when the list of records is empty. `main` ties everything together by collecting the rates and printing the formatted output.
+
+## License
+
+This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.

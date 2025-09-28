-This Android app helps users explore and compare **staking interest rates** for cryptocurrencies across reputable exchanges based on their **risk tolerance** (Low, Medium, High).
+CryptoMAX provides a multithreaded Java data ingestion pipeline that gathers exchange listings, 
+current gas fee estimates, and staking APR/APY snapshots. The scraper persists the normalized 
+information to a lightweight SQLite database so that future Android or desktop clients can reuse 
+the aggregated data without having to make direct network calls.
 
-Built for crypto investors who want to **beat inflation** and generate **passive income** through **staking** and **yield farming** strategies 💸
+The program prefers live public APIs but gracefully falls back to bundled sample datasets when 
+network access is unavailable or rate limited. This makes the tool ideal for prototyping user 
+interfaces or verifying database integrations offline.
 
----
+## Features
 
-## 🚀 Features
+- 🧵 **Multithreaded scraping** – Exchange, gas fee, and staking tasks run concurrently using an
+  `ExecutorService` to reduce total scraping time.
+- 🌐 **HTTP scraping helpers** – A shared HTTP client (powered by Jsoup) applies sensible headers
+  and timeouts to play nicely with public APIs.
+- 💾 **SQLite persistence** – All datasets are written to `cryptomax.db`, ready for consumption by
+  Android Room, desktop applications, or analytics scripts.
+- 🛟 **Offline fallbacks** – Curated JSON samples ensure the database can still be populated when
+  the network is unavailable or remote services block automated requests.
 
-- ✅ **Low Risk**: Stablecoin staking (USDC, USDT, DAI) with positive APY from trusted sources
-- ✅ **Medium Risk**: Mix of high-volume cryptos (BTC, ETH, SOL) with staking options
-- ✅ **High Risk**: ⚠️ Advanced mode with gas fee optimization and high-yield assets
-- ✅ Real-time data aggregation using:
-  - DeFi Llama API (primary)
-  - HTML scraping for exchanges like Nexo
-- ✅ Links to exchanges and staking products
-- ✅ User-friendly interface with risk warning system
+## Project Layout
 
----
+```
+CryptoMAX/
+├── build.gradle               # Gradle configuration with dependencies
+├── settings.gradle            # Declares the Gradle root project name
+├── src/main/java/com/cryptomax/
+│   ├── CryptoDataScraper.java # Main entry point orchestrating the scraping workflow
+│   ├── DatabaseManager.java   # SQLite helper that creates tables and stores results
+│   ├── ExchangeInfo.java      # Data model for centralized exchanges
+│   ├── GasFeeInfo.java        # Data model for gas fee snapshots
+│   ├── HttpFetcher.java       # Shared HTTP utility with timeouts/user agent headers
+│   └── StakingPoolInfo.java   # Data model for staking pool yields
+└── src/main/resources/fallback/
+    ├── exchanges.json         # Sample exchange list used when live calls fail
+    ├── gas-fees.json          # Sample gas fee metrics for multiple chains
+    └── staking-pools.json     # Sample staking APR/APY data
+```
 
-## 🎥 Preview
+## Getting Started
 
-| Risk Option | Data View | Warning |
-|-------------|-----------|---------|
-| ![Risk Selection](screenshots/risk_options.png) | ![Results](screenshots/staking_data.png) | ![High Risk](screenshots/high_risk_warning.png) |
+### Prerequisites
 
-> 📸 *Add your screenshots to a `/screenshots` folder in your repo for these previews to work.*
+- Java 17 or newer (managed automatically via the Gradle toolchain)
+- Gradle (the project uses the Gradle wrapper once it has been generated)
 
----
+### Build the Project
 
-## 🧱 Architecture
+```bash
+./gradlew build
+```
 
+Gradle will download all required dependencies: Jsoup for HTTP access, Gson for JSON parsing, and
+SQLite JDBC for database access.
+
+### Run the Scraper
+
+```bash
+./gradlew run
+```
+
+This command launches `CryptoDataScraper`. The scraper attempts to contact the following public
+endpoints:
+
+- `https://api.coingecko.com/api/v3/exchanges?per_page=20&page=1`
+- `https://api.gasprice.io/v1/estimates`
+- `https://yields.llama.fi/pools`
+
+If any request fails, CryptoMAX automatically loads the equivalent bundled fallback dataset so that
+the resulting `cryptomax.db` file is always populated with representative data.
+
+### Database Schema
+
+The SQLite database contains three tables:
+
+| Table           | Description                                     |
+|-----------------|-------------------------------------------------|
+| `exchanges`     | Basic metadata about centralized exchanges      |
+| `gas_fees`      | Slow/standard/fast gas fee estimates per chain  |
+| `staking_rates` | APR/APY metrics for curated staking pools       |
+
+All tables include unique constraints to prevent duplicate records on subsequent runs. Developers
+can inspect the generated database with any SQLite browser or with the `sqlite3` CLI.
+
+### Using the Data in Android
+
+Because Android supports SQLite natively, you can copy `cryptomax.db` into your Android project (for
+example under `src/main/assets/`) and access the pre-populated tables via Room or the Android SQLite
+APIs. Alternatively, bundle the scraper as part of your backend stack to refresh the database on a
+schedule and deliver updates to clients.
+
+## Extending the Scraper
+
+- Add new scraping tasks by creating a model class, update the database schema, and submit another
+  callable to the executor.
+- Replace the fallback JSON files with your own curated datasets or a company API stub.
+- Integrate scheduling (e.g., using Quartz or Spring) to refresh the database periodically.
+
+## License
+
+This project is released under the terms of the MIT License. See [LICENSE](LICENSE) for details.
 
EOF
)

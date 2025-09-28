 # 🚀 CryptoMAX

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

**CryptoMAX** is a lightweight Python script that compares staking yields across well-known Ethereum staking providers.  
It queries public APIs for **Lido**, **Rocket Pool**, and **Kraken**, normalizes the responses, and prints a clean console table so you can quickly spot advertised **APR/APY** rates.

---

## ✨ Features

- 🔍 **Aggregates staking yields** from multiple providers in real time.  
- 🛡️ **Resilient data fetching** with error handling and clear warnings.  
- 📊 **Console table output** with neatly aligned columns.  
- 🌐 **Public API integrations** (Lido, Rocket Pool, Kraken).  
- ⚠️ **Graceful fallback** – if a provider fails, the script continues with remaining sources.  

---

## 📦 Prerequisites

- Python **3.9+**
- Internet access to reach provider APIs

> 💡 **Tip:** Create and activate a virtual environment before installing dependencies to keep them isolated.

---

## 🔧 Installation

Install the single runtime dependency with `pip`:

```bash
pip install -r requirements.txt

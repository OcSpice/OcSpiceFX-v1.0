# OcSpiceFX v1.0 - Strategy Laboratory

A professional-grade Strategy Laboratory built with a Node.js data pipeline, FastAPI backend, and React frontend. This system downloads 20+ years of Dukascopy data, converts it to ultra-fast Parquet files, and runs backtests against the V19 Strategy Engine with strict Prop Firm Rule enforcement.

## Project Structure

```
oscipicex-lab/
├── data-pipeline/          # Node.js data pipeline
│   ├── package.json
│   ├── download.js         # Download M5 data from Dukascopy
│   ├── merge.js            # Merge yearly CSVs
│   └── convert.js          # Convert CSV to Parquet
├── data/                   # Data storage
│   ├── raw/               # Individual year CSVs
│   ├── merged/            # Merged CSVs per symbol
│   └── parquet/           # Converted Parquet files
├── backend/               # FastAPI backend
│   ├── prop_firm_engine.py      # Prop Firm Rule Engine
│   ├── strategy_engine.py       # V19 M5 Driver Strategy
│   ├── requirements.txt
│   └── main.py            # (Coming in Step 3)
└── frontend/              # React frontend (Coming in Step 3)
```

## Step 1: Project Scaffolding & Data Pipeline

### Prerequisites
- Node.js 16+ with npm
- Python 3.9+

### Setup

```bash
# Create root folder
mkdir oscipicex-lab
cd oscipicex-lab

# Create directories
mkdir backend frontend data-pipeline data

# Navigate to data-pipeline
cd data-pipeline
npm init -y
npm install dukascopy-node fs-extra csv-parser parquets
```

### Running the Data Pipeline

```bash
# Download M5 data from Dukascopy (2005-2024)
npm run download

# Merge yearly CSVs into master CSVs per symbol
npm run merge

# Convert CSVs to compressed Parquet files
npm run convert

# Or run all at once
npm run pipeline
```

### Supported Assets (Tier 1, 2, 3)
- **Tier 1 (Majors):** EURUSD, GBPUSD, USDJPY
- **Tier 2 (Exotics):** GBPJPY, EURJPY, AUDJPY, NZDJPY, NZDUSD
- **Tier 3 (Indices & Commodities):** XAUUSD, USA30IDXUSD, DOLLARIDXUSD

## Step 2: FastAPI Backend & Prop Firm Rule Engine

### Setup

```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Key Components

#### PropFirmEngine (`prop_firm_engine.py`)
Production-ready rule engine that enforces:
- **Profit Target:** % gain needed to pass the evaluation
- **Daily Drawdown Limit:** Max daily loss allowed
- **Total Drawdown Limit:** Max cumulative loss allowed
- **Minimum Trading Days:** Minimum days active to be eligible

#### StrategyEngine (`strategy_engine.py`)
V19 M5 Driver strategy featuring:
- **H1 Bias Filter:** Uses 50-period EMA on 1-hour timeframe
- **Break of Structure:** Detects key support/resistance levels
- **Smart Entry Logic:** Confirms entry with specific candle patterns
- **Dynamic Position Sizing:** 1% risk per trade based on current balance
- **Risk Management:** 2:1 Risk-Reward ratio on all trades
- **Exit Rules:** Time stop (120 M5 candles = 10 hours), SL, TP

**Supported Broker Configurations:**
- Configurable spread (pips)
- Configurable slippage (pips)
- Configurable commission (per lot)

## Step 3: FastAPI Server & React Frontend (Coming Next)

Once the data pipeline is complete and Parquet files are generated, we'll implement:
- FastAPI endpoints for backtest execution
- Real-time performance tracking
- React dashboard with TradingView widgets
- Interactive strategy parameters
- Performance analytics

## Running Backtests

After Step 3, run backtests:

```bash
python -m uvicorn main:app --reload
```

Then access the dashboard at `http://localhost:3000`

## Data Pipeline Stages

1. **Download Stage:** Downloads M5 OHLCV data from Dukascopy for 11 assets (2005-2024)
2. **Merge Stage:** Combines yearly CSVs into single master files per symbol
3. **Convert Stage:** Transforms CSVs into column-oriented Parquet format for 100x faster queries

## Performance Notes

- **Parquet Compression:** Reduces data size by 90%+ compared to raw CSV
- **Fast Query Performance:** Vectorized operations via NumPy/Pandas
- **Memory Efficient:** Lazy loading of data as needed
- **Scalable:** Can handle 20+ years of M5 data efficiently

## License

ISC

## Author

OcSpice

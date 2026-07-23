# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import uvicorn

# Import your engines and strategy logic
from prop_firm_engine import PropFirmEngine
from broker_engine import StandardBrokerEngine
from strategy_engine import load_data, ASSET_CONFIG, run_backtest

app = FastAPI(title="OcSpiceFX Strategy Lab")

# Enable CORS so Retool can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class BacktestRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    account_size: float
    risk_per_trade_pct: float
    
    # Broker Emulation
    broker_type: str # "prop_firm" or "standard"
    spread_pips: float
    slippage_pips: float
    commission_per_lot: float
    
    # Prop Firm Rules (Optional)
    profit_target_pct: Optional[float] = 0.10
    max_daily_dd_pct: Optional[float] = 0.05
    max_total_dd_pct: Optional[float] = 0.10
    min_trading_days: Optional[int] = 3
    
    # Standard Broker Rules (Optional)
    leverage: Optional[int] = 500
    margin_call_pct: Optional[float] = 0.60
    stop_out_pct: Optional[float] = 0.30

@app.get("/api/assets")
def get_available_assets():
    return {"assets": list(ASSET_CONFIG.keys())}

@app.post("/api/backtest")
def execute_backtest(req: BacktestRequest):
    # 1. Load Data (Passing dates to optimize memory on Render)
    df = load_data(req.symbol, req.start_date, req.end_date)
    if df is None:
        raise HTTPException(status_code=404, detail=f"Data for {req.symbol} not found in the selected range.")
        
    if len(df) < 100:
        raise HTTPException(status_code=400, detail="Not enough data in selected date range.")

    # 2. Initialize Broker Engine
    broker_config = {
        "spread_pips": req.spread_pips,
        "slippage_pips": req.slippage_pips,
        "commission_per_lot": req.commission_per_lot
    }
    
    if req.broker_type == "prop_firm":
        engine = PropFirmEngine(
            initial_balance=req.account_size,
            profit_target_pct=req.profit_target_pct,
            max_daily_dd_pct=req.max_daily_dd_pct,
            max_total_dd_pct=req.max_total_dd_pct,
            min_trading_days=req.min_trading_days
        )
    else:
        engine = StandardBrokerEngine(
            initial_balance=req.account_size,
            leverage=req.leverage,
            margin_call_pct=req.margin_call_pct,
            stop_out_pct=req.stop_out_pct
        )

    # 3. Run Backtest
    trades, final_engine = run_backtest(df, req.symbol, broker_config, engine, req.risk_per_trade_pct)
    
    # 4. Calculate Analytics
    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        return {
            "status": "No trades taken",
            "fail_reason": "Strategy generated 0 trades for this period.",
            "final_balance": req.account_size,
            "metrics": {
                "total_trades": 0,
                "win_rate": "0%",
                "net_pnl": 0.0,
                "profit_factor": 0.0,
                "max_drawdown": 0.0
            },
            "trades": []
        }

    wins = trades_df[trades_df['pnl'] > 0]
    losses = trades_df[trades_df['pnl'] < 0]
    
    # Calculate Max Drawdown safely
    cum_pnl = trades_df['pnl'].cumsum()
    peak = cum_pnl.cummax()
    drawdown = (peak - cum_pnl) / req.account_size
    max_dd = float(drawdown.max() * 100) if not drawdown.empty else 0.0
    
    metrics = {
        "total_trades": len(trades_df),
        "win_rate": f"{(len(wins) / len(trades_df)) * 100:.2f}%" if len(trades_df) > 0 else "0%",
        "net_pnl": float(trades_df['pnl'].sum()),
        "profit_factor": float(wins['pnl'].sum() / abs(losses['pnl'].sum())) if len(losses) > 0 and losses['pnl'].sum() != 0 else float('inf'),
        "max_drawdown": max_dd
    }
    
    # Prepare trades for frontend charting (limit to last 100 for payload size)
    chart_trades = trades_df.tail(100).to_dict(orient="records")
    for t in chart_trades:
        if isinstance(t['time'], pd.Timestamp):
            t['time'] = t['time'].isoformat()
        # Ensure PnL is a standard float for JSON
        t['pnl'] = float(t['pnl'])

    return {
        "status": final_engine.status,
        "fail_reason": getattr(final_engine, "fail_reason", getattr(final_engine, "event_reason", "")),
        "final_balance": float(final_engine.current_balance),
        "metrics": metrics,
        "trades": chart_trades
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

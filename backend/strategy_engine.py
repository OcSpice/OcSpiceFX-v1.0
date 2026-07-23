# backend/strategy_engine.py
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'parquet')

ASSET_CONFIG = {
    'xauusd': {'pip_size': 0.1, 'pip_value': 10.0},
    'gbpusd': {'pip_size': 0.0001, 'pip_value': 10.0},
    'gbpjpy': {'pip_size': 0.01, 'pip_value': 6.67},
    'usdjpy': {'pip_size': 0.01, 'pip_value': 6.67},
    'eurusd': {'pip_size': 0.0001, 'pip_value': 10.0},
    'eurjpy': {'pip_size': 0.01, 'pip_value': 6.67},
    'usa30idxusd': {'pip_size': 1.0, 'pip_value': 1.0},
    'dollaridxusd': {'pip_size': 0.01, 'pip_value': 10.0},
    'audjpy': {'pip_size': 0.01, 'pip_value': 6.67},
    'nzdusd': {'pip_size': 0.0001, 'pip_value': 10.0},
    'nzdjpy': {'pip_size': 0.01, 'pip_value': 6.67}
}

def load_data(symbol: str):
    file_path = os.path.join(DATA_DIR, f"{symbol}_m5.parquet")
    if not os.path.exists(file_path): return None
    df = pd.read_parquet(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    return df

def run_backtest(df: pd.DataFrame, symbol: str, broker_config: dict, engine, risk_pct: float):
    cfg = ASSET_CONFIG[symbol]
    pip = cfg['pip_size']
    
    spread_pips = broker_config['spread_pips']
    slippage_pips = broker_config['slippage_pips']
    commission_per_lot = broker_config['commission_per_lot']
    
    # Build H1 Bias
    df_h1 = df.resample('1h').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
    df_h1['EMA_50'] = df_h1['close'].ewm(span=50, adjust=False).mean()
    
    m5_t = df.index.values
    m5_o = df['open'].values
    m5_h = df['high'].values
    m5_l = df['low'].values
    m5_c = df['close'].values
    
    h1_t = df_h1.index.values
    h1_ema = df_h1['EMA_50'].values
    h1_c = df_h1['close'].values
    
    trade_active = False
    direction = ""
    entry_price = stop_price = target_price = initial_stop = 0.0
    entry_idx = 0
    state = "neutral"
    active_ob = None
    trades = []
    is_jpy = 'jpy' in symbol
    
    for i in range(60, len(df)):
        if trade_active:
            # Calculate floating PnL for standard broker margin checks
            if direction == "long":
                raw_pnl_pips = (m5_c[i] - entry_price) / pip
            else:
                raw_pnl_pips = (entry_price - m5_c[i]) / pip
                
            floating_pnl = (raw_pnl_pips * cfg['pip_value'] * size) - (commission_per_lot * size)
            
            if hasattr(engine, 'update_floating'):
                engine.update_floating(floating_pnl)
                if engine.status == "Blown":
                    trades.append({"time": pd.Timestamp(m5_t[i]), "pnl": floating_pnl, "reason": "stop_out"})
                    break

            # Check Time Stop (120 candles)
            if i - entry_idx >= 120:
                net_pnl_pips = raw_pnl_pips - (slippage_pips * 2 + spread_pips)
                pnl_usd = (net_pnl_pips * cfg['pip_value'] * size) - (commission_per_lot * size)
                trades.append({"time": pd.Timestamp(m5_t[i]), "pnl": pnl_usd, "reason": "time_stop"})
                
                if hasattr(engine, 'close_trade'):
                    if not engine.close_trade(pnl_usd, size, entry_price, is_jpy): break
                else:
                    if not engine.process_trade(pnl_usd, pd.Timestamp(m5_t[i])): break
                    
                trade_active = False; state = "neutral"; continue

            # Check Stop Loss
            if direction == "long" and m5_l[i] <= stop_price:
                net_pnl_pips = ((stop_price - entry_price) / pip) - (slippage_pips * 2 + spread_pips)
                pnl_usd = (net_pnl_pips * cfg['pip_value'] * size) - (commission_per_lot * size)
                trades.append({"time": pd.Timestamp(m5_t[i]), "pnl": pnl_usd, "reason": "stop_loss"})
                
                if hasattr(engine, 'close_trade'):
                    if not engine.close_trade(pnl_usd, size, entry_price, is_jpy): break
                else:
                    if not engine.process_trade(pnl_usd, pd.Timestamp(m5_t[i]))): break
                    
                trade_active = False; state = "neutral"; continue

            # Check Take Profit
            elif direction == "long" and m5_h[i] >= target_price:
                net_pnl_pips = ((target_price - entry_price) / pip) - (slippage_pips * 2 + spread_pips)
                pnl_usd = (net_pnl_pips * cfg['pip_value'] * size) - (commission_per_lot * size)
                trades.append({"time": pd.Timestamp(m5_t[i]), "pnl": pnl_usd, "reason": "take_profit"})
                
                if hasattr(engine, 'close_trade'):
                    if not engine.close_trade(pnl_usd, size, entry_price, is_jpy): break
                else:
                    if not engine.process_trade(pnl_usd, pd.Timestamp(m5_t[i]))): break
                    
                trade_active = False; state = "neutral"; continue

            # Short exits
            if direction == "short" and m5_h[i] >= stop_price:
                net_pnl_pips = ((entry_price - stop_price) / pip) - (slippage_pips * 2 + spread_pips)
                pnl_usd = (net_pnl_pips * cfg['pip_value'] * size) - (commission_per_lot * size)
                trades.append({"time": pd.Timestamp(m5_t[i]), "pnl": pnl_usd, "reason": "stop_loss"})
                
                if hasattr(engine, 'close_trade'):
                    if not engine.close_trade(pnl_usd, size, entry_price, is_jpy): break
                else:
                    if not engine.process_trade(pnl_usd, pd.Timestamp(m5_t[i]))): break
                    
                trade_active = False; state = "neutral"; continue

            elif direction == "short" and m5_l[i] <= target_price:
                net_pnl_pips = ((entry_price - target_price) / pip) - (slippage_pips * 2 + spread_pips)
                pnl_usd = (net_pnl_pips * cfg['pip_value'] * size) - (commission_per_lot * size)
                trades.append({"time": pd.Timestamp(m5_t[i]), "pnl": pnl_usd, "reason": "take_profit"})
                
                if hasattr(engine, 'close_trade'):
                    if not engine.close_trade(pnl_usd, size, entry_price, is_jpy): break
                else:
                    if not engine.process_trade(pnl_usd, pd.Timestamp(m5_t[i]))): break
                    
                trade_active = False; state = "neutral"; continue
            continue

        # Session Filter (7 AM to 4 PM UTC)
        py_time = pd.Timestamp(m5_t[i]).tz_convert('UTC')
        if py_time.hour < 7 or py_time.hour >= 16: continue

        h1i = np.searchsorted(h1_t, m5_t[i]) - 1
        if h1i < 0: continue
        is_h1_bull = h1_c[h1i] > h1_ema[h1i]
        is_h1_bear = h1_c[h1i] < h1_ema[h1i]

        if state == "neutral":
            if is_h1_bull:
                if m5_c[i] > np.max(m5_h[i-30:i-1]):
                    for j in range(i-1, max(i-60, -1), -1):
                        if m5_c[j] < m5_o[j]: active_ob = {'top': m5_o[j], 'bottom': m5_l[j]}; state = "bos_found"; break
            elif is_h1_bear:
                if m5_c[i] < np.min(m5_l[i-30:i-1]):
                    for j in range(i-1, max(i-60, -1), -1):
                        if m5_c[j] > m5_o[j]: active_ob = {'top': m5_h[j], 'bottom': m5_c[j]}; state = "bos_found"; break

        elif state == "bos_found" and active_ob:
            if is_h1_bull and m5_l[i] <= active_ob['top']:
                if m5_c[i-1] < m5_o[i-1] and m5_c[i] > m5_o[i] and m5_o[i] <= m5_c[i-1] and m5_c[i] >= m5_o[i-1]:
                    entry_price = m5_c[i]
                    stop_price = np.min(m5_l[i-1:i+1]) - (1 * pip)
                    initial_stop = stop_price
                    risk = max(entry_price - stop_price, 5 * pip)
                    target_price = entry_price + (risk * 2.0)
                    direction = "long"
                    
                    # Position Sizing
                    risk_usd = engine.current_balance * risk_pct
                    stop_dist_pips = abs(entry_price - stop_price) / pip
                    size = risk_usd / (stop_dist_pips * cfg['pip_value'])
                    
                    if hasattr(engine, 'open_trade'):
                        if not engine.open_trade(size, entry_price, is_jpy): continue
                        
                    trade_active = True; entry_idx = i; active_ob = None; state = "neutral"
                    
            elif is_h1_bear and m5_h[i] >= active_ob['bottom']:
                if m5_c[i-1] > m5_o[i-1] and m5_c[i] < m5_o[i] and m5_o[i] >= m5_c[i-1] and m5_c[i] <= m5_o[i-1]:
                    entry_price = m5_c[i]
                    stop_price = np.max(m5_h[i-1:i+1]) + (1 * pip)
                    initial_stop = stop_price
                    risk = max(stop_price - entry_price, 5 * pip)
                    target_price = entry_price - (risk * 2.0)
                    direction = "short"
                    
                    risk_usd = engine.current_balance * risk_pct
                    stop_dist_pips = abs(stop_price - entry_price) / pip
                    size = risk_usd / (stop_dist_pips * cfg['pip_value'])
                    
                    if hasattr(engine, 'open_trade'):
                        if not engine.open_trade(size, entry_price, is_jpy): continue
                        
                    trade_active = True; entry_idx = i; active_ob = None; state = "neutral"
                    
    return trades, engine

# backend/prop_firm_engine.py
from datetime import datetime, timedelta

class PropFirmEngine:
    def __init__(self, initial_balance: float, profit_target_pct: float, 
                 max_daily_dd_pct: float, max_total_dd_pct: float, min_trading_days: int):
        self.initial_balance = initial_balance
        self.profit_target_pct = profit_target_pct
        self.max_daily_dd_pct = max_daily_dd_pct
        self.max_total_dd_pct = max_total_dd_pct
        self.min_trading_days = min_trading_days
        
        self.current_balance = initial_balance
        self.peak_balance = initial_balance
        self.daily_start_balance = initial_balance
        
        self.current_day = None
        self.unique_trading_days = set()
        self.status = "Active"
        self.fail_reason = ""

    def update_day(self, trade_timestamp: datetime):
        trade_day = trade_timestamp.date()
        self.unique_trading_days.add(trade_day)
        
        if self.current_day is None:
            self.current_day = trade_day
        elif trade_day != self.current_day:
            self.current_day = trade_day
            self.daily_start_balance = self.current_balance # Reset daily limit at new day

    def process_trade(self, trade_pnl: float, trade_timestamp: datetime):
        if self.status != "Active": return False

        self.update_day(trade_timestamp)
        
        self.current_balance += trade_pnl
        self.peak_balance = max(self.peak_balance, self.current_balance)
        
        # Check Daily Drawdown
        daily_dd = (self.daily_start_balance - self.current_balance) / self.initial_balance
        if daily_dd >= self.max_daily_dd_pct:
            self.status = "Failed"
            self.fail_reason = f"Max Daily Drawdown Breached ({daily_dd*100:.2f}% >= {self.max_daily_dd_pct*100:.2f}%)"
            return False
            
        # Check Total Drawdown
        total_dd = (self.peak_balance - self.current_balance) / self.initial_balance
        if total_dd >= self.max_total_dd_pct:
            self.status = "Failed"
            self.fail_reason = f"Max Total Drawdown Breached ({total_dd*100:.2f}% >= {self.max_total_dd_pct*100:.2f}%)"
            return False
            
        # Check Profit Target
        current_profit_pct = (self.current_balance - self.initial_balance) / self.initial_balance
        if current_profit_pct >= self.profit_target_pct and len(self.unique_trading_days) >= self.min_trading_days:
            self.status = "Passed"
            self.fail_reason = "Profit target reached."
            return False
            
        return True

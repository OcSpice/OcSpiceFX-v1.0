# backend/broker_engine.py
from datetime import datetime

class StandardBrokerEngine:
    def __init__(self, initial_balance: float, leverage: int, 
                 margin_call_pct: float, stop_out_pct: float):
        """
        Emulates a standard retail broker (e.g., Exness, Deriv).
        :param leverage: e.g., 500 for 1:500
        :param margin_call_pct: e.g., 0.60 (60% margin level triggers warning)
        :param stop_out_pct: e.g., 0.30 (30% margin level triggers liquidation)
        """
        self.initial_balance = initial_balance
        self.leverage = leverage
        self.margin_call_pct = margin_call_pct
        self.stop_out_pct = stop_out_pct
        
        self.current_balance = initial_balance
        self.floating_pnl = 0.0
        self.used_margin = 0.0
        self.status = "Active"
        self.event_reason = ""
        
    @property
    def equity(self):
        return self.current_balance + self.floating_pnl
        
    @property
    def margin_level(self):
        if self.used_margin == 0: return float('inf')
        return (self.equity / self.used_margin) * 100

    def calculate_required_margin(self, position_size_lots: float, entry_price: float, is_jpy: bool = False):
        """
        Calculates margin required for a trade.
        Contract size for standard lot (1.0) is 100,000 units.
        """
        # Base currency is assumed USD. For USDJPY, base is USD. For GBPUSD, base is GBP.
        # To keep the math simple and universal for the backtest, we use contract value.
        contract_value = position_size_lots * 100_000 * entry_price
        
        # For pairs where USD is the base (e.g., USDJPY), contract value is just lots * 100,000
        # This is a slight simplification but highly accurate for retail margin sim.
        if is_jpy:
            contract_value = position_size_lots * 100_000
            
        return contract_value / self.leverage

    def open_trade(self, position_size_lots: float, entry_price: float, is_jpy: bool = False):
        if self.status != "Active": return False
        
        required_margin = self.calculate_required_margin(position_size_lots, entry_price, is_jpy)
        
        # Check if there is enough free margin to open the trade
        free_margin = self.equity - self.used_margin
        if required_margin > free_margin:
            self.event_reason = "Not enough free margin to open trade."
            return False # Trade rejected
            
        self.used_margin += required_margin
        return True

    def update_floating(self, floating_pnl: float):
        self.floating_pnl = floating_pnl
        
        # Check Stop Out / Margin Call
        if self.used_margin > 0:
            if self.margin_level <= self.stop_out_pct * 100:
                # In a real broker, this force-closes the largest losing trade.
                # For this engine, we flag the account as blown.
                self.status = "Blown"
                self.event_reason = f"Stop Out Executed (Margin Level: {self.margin_level:.2f}%)"
            elif self.margin_level <= self.margin_call_pct * 100:
                self.event_reason = "Margin Call Warning"
                
    def close_trade(self, pnl: float, position_size_lots: float, entry_price: float, is_jpy: bool = False):
        self.current_balance += pnl
        freed_margin = self.calculate_required_margin(position_size_lots, entry_price, is_jpy)
        self.used_margin -= freed_margin
        if self.used_margin < 0: self.used_margin = 0
        
        if self.current_balance <= 0:
            self.status = "Blown"
            self.event_reason = "Account balance hit zero."
            
        return self.status == "Active"

# backend/broker_presets.py
"""
Broker presets for common retail trading platforms.
Use these to quickly initialize StandardBrokerEngine with realistic settings.
"""

BROKER_PRESETS = {
    "exness": {
        "name": "Exness",
        "leverage": 2000,
        "margin_call_pct": 0.60,  # 60%
        "stop_out_pct": 0.0,      # 0% (Exness famous for this)
        "spread_pips": 0.1,       # Ultra-tight spreads on major pairs
        "commission_per_lot": 0.0,
        "description": "Unlimited leverage option available. 0% stop out policy."
    },
    "exness_conservative": {
        "name": "Exness (Conservative)",
        "leverage": 500,
        "margin_call_pct": 0.60,
        "stop_out_pct": 0.20,
        "spread_pips": 0.5,
        "commission_per_lot": 2.0,
        "description": "Standard Exness account with typical spreads."
    },
    "deriv": {
        "name": "Deriv",
        "leverage": 1000,
        "margin_call_pct": 1.0,   # 100%
        "stop_out_pct": 0.50,     # 50%
        "spread_pips": 1.0,
        "commission_per_lot": 3.0,
        "description": "Deriv's standard forex account."
    },
    "ic_markets": {
        "name": "IC Markets",
        "leverage": 500,
        "margin_call_pct": 0.60,
        "stop_out_pct": 0.20,
        "spread_pips": 0.0,       # ECN spreads (variable)
        "commission_per_lot": 7.0,
        "description": "ECN broker with commissions."
    },
    "pepperstone": {
        "name": "Pepperstone",
        "leverage": 400,
        "margin_call_pct": 0.60,
        "stop_out_pct": 0.20,
        "spread_pips": 0.2,
        "commission_per_lot": 6.0,
        "description": "ECN account with variable spreads."
    },
    "interactive_brokers": {
        "name": "Interactive Brokers",
        "leverage": 20,  # More conservative leverage
        "margin_call_pct": 1.0,
        "stop_out_pct": 0.30,
        "spread_pips": 0.1,
        "commission_per_lot": 10.0,
        "description": "Professional institutional broker, low leverage."
    },
    "prop_firm_funded": {
        "name": "Prop Firm (5K Challenge)",
        "leverage": 100,
        "margin_call_pct": 0.80,
        "stop_out_pct": 0.50,
        "spread_pips": 1.5,
        "commission_per_lot": 5.0,
        "description": "Typical prop firm challenge conditions."
    },
    "prop_firm_aggressive": {
        "name": "Prop Firm (Aggressive)",
        "leverage": 50,
        "margin_call_pct": 1.0,
        "stop_out_pct": 0.80,
        "spread_pips": 2.0,
        "commission_per_lot": 8.0,
        "description": "Strict prop firm evaluation account."
    }
}

def get_preset(broker_name: str) -> dict:
    """
    Get broker preset configuration.
    :param broker_name: Name of the broker (e.g., 'exness', 'deriv')
    :return: Dict with broker configuration
    """
    return BROKER_PRESETS.get(broker_name.lower(), BROKER_PRESETS["exness"])

def list_presets() -> dict:
    """Return all available presets."""
    return BROKER_PRESETS

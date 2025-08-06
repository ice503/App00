def scan_multi_timeframe(symbol: str):
    """Mock multi-timeframe signal. Extend with real data sources."""
    return {
        "M15": "BUY",
        "H1": "HOLD",
        "H4": "BUY",
        "Convergence": "BULLISH"
    }

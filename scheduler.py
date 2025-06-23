"""60-second price scheduler & toast notifications (stub)"""
import asyncio
from typing import Callable, List
try:
    import yfinance as yf
    from win10toast import ToastNotifier
except ImportError:
    yf = None
    ToastNotifier = None

toaster = ToastNotifier() if ToastNotifier else None

def _notify(msg: str):
    if toaster:
        toaster.show_toast("TraderCopilot", msg, duration=5, threaded=True)
    print("[NOTIFY]", msg)

async def price_loop(symbols: List[str], on_price: Callable[[str, float], None], interval: int = 60):
    """Polls Yahoo Finance every `interval` seconds and invokes `on_price`."""
    if yf is None:
        _notify("yfinance not installed; price loop disabled.")
        return
    while True:
        for sym in symbols:
            try:
                data = yf.Ticker(sym).history(period="1d", interval="1m").tail(1)
                price = float(data["Close"].iloc[-1])
                on_price(sym, price)
            except Exception as e:
                _notify(f"Price fetch error for {sym}: {e}")
        await asyncio.sleep(interval)

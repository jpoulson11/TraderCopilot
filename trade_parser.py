"""Simple natural‑language trade parser"""
import re

def parse_trade(text: str):
    pattern = re.compile(
        r"(?P<side>Long|Short)\s+(?P<qty>\d+)\s*[\u00D7xX]?\s*(?P<symbol>[A-Za-z0-9\$]+)\s*@?\s*(?P<entry>[0-9\.]+)(?:[^\d]+SL\s*(?P<sl>[0-9\.]+))?(?:[^\d]+TP\s*(?P<tp>[0-9\.]+))?",
        re.I,
    )
    m = pattern.search(text)
    if not m:
        return None
    d = m.groupdict()
    return {
        "side": d["side"].capitalize(),
        "qty": int(d["qty"]),
        "symbol": d["symbol"],
        "entry": float(d["entry"]),
        "sl": float(d["sl"]) if d["sl"] else None,
        "tp": float(d["tp"]) if d["tp"] else None,
    }

if __name__ == "__main__":
    test = "Long 5× TQQQ $42C @ 0.80 SL 0.55 TP 1.40"
    print(parse_trade(test))

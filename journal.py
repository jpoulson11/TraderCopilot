"""Daily PDF/CSV journal exporter (stub)"""
from datetime import datetime
from pathlib import Path
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    canvas = None

def export_pdf(trades: list[dict], out_dir: Path):
    """Writes a simple PDF summary of closed trades."""
    if canvas is None:
        print("reportlab not installed; skipping PDF export")
        return None
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"journal_{datetime.now().date()}.pdf"
    c = canvas.Canvas(str(fname), pagesize=letter)
    y = 750
    c.setFont("Helvetica", 12)
    c.drawString(30, 770, "TraderCopilot Daily Journal")
    for t in trades:
        line = f"{t.get('symbol')} {t.get('side')} {t.get('qty')} @ {t.get('entry')} P&L {t.get('pnl','')}"
        c.drawString(30, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return fname

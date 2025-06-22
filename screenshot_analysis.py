"""Screenshot analysis helper (stub)"""
import io, base64, asyncio
try:
    import mss, mss.tools
    import openai
except ImportError:
    mss = None
    openai = None

aSYNC_TIMEOUT = 60

async def analyze_screen() -> tuple[str, bytes]:
    """Captures the primary monitor, sends to GPT‑4o Vision.
    Returns (analysis_text, png_bytes)."""
    if mss is None:
        return "mss not installed", b""

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        png_bytes = mss.tools.to_png(img.rgb, img.size)

    if openai is None:
        return "openai SDK missing", png_bytes

    try:
        resp = await asyncio.wait_for(
            openai.ChatCompletion.acreate(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Analyze this trading chart for supply/demand, EMAs, VWAP, volume profile, candlesticks, sentiment, and propose a 5‑step trade plan."}],
                images=[{"type": "image/png", "data": base64.b64encode(png_bytes).decode()}],
                max_tokens=400,
            ),
            timeout=aSYNC_TIMEOUT,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        text = f"Error from OpenAI: {e}"
    return text, png_bytes

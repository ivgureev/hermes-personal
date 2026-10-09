from __future__ import annotations
import json
from pathlib import Path

_TEMPLATE = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{
 --gv-graphite:{{brand.graphite}};--gv-brand-teal:{{brand.teal}};--gv-teal-ui:{{teal.ui}};--gv-teal-text:{{teal.text}};
 --gv-teal-strong:{{teal.strong}};--gv-secondary:{{text.secondary}};--gv-input:{{border.input}};--gv-decor:{{border.decor}};
 --gv-base:{{bg.base}};--gv-subtle:{{bg.subtle}};--gv-radius:10px;
}
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:var(--gv-graphite)}
.stApp{background:var(--gv-base)}
[data-testid="stSidebar"]{background:var(--gv-subtle);border-right:1px solid var(--gv-decor)}
[data-testid="stSidebar"] img{max-width:32px!important;height:32px!important;object-fit:contain;margin:.2rem 0 1rem}
[data-testid="stSidebarNav"]{padding-top:.5rem}
[data-testid="stHeader"]{background:rgba(255,255,255,.94);border-bottom:1px solid var(--gv-decor)}
.block-container{max-width:1280px;padding-top:1.5rem;padding-bottom:4rem}
h1,h2,h3{color:var(--gv-graphite);font-weight:700;letter-spacing:-.02em}
h1{font-size:clamp(1.55rem,2.5vw,2.1rem)!important} h2{font-size:1.25rem!important} h3{font-size:1.05rem!important}
p,li,label{font-size:1rem;line-height:1.55}
a{color:var(--gv-teal-text)!important}
[data-testid="stCaptionContainer"],.stCaption{color:var(--gv-secondary)!important}
.stButton>button,.stDownloadButton>button{border-radius:8px;border:1px solid var(--gv-teal-text);min-height:44px;font-weight:600}
.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{background:var(--gv-teal-text);color:white;border-color:var(--gv-teal-text)}
.stButton>button[kind="primary"]:hover,.stDownloadButton>button[kind="primary"]:hover{background:var(--gv-teal-strong);border-color:var(--gv-teal-strong)}
.stButton>button[kind="secondary"]:hover{color:var(--gv-teal-strong);border-color:var(--gv-teal-strong);background:var(--gv-subtle)}
[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div{border-color:var(--gv-input)!important;border-radius:8px!important}
[data-testid="stFileUploaderDropzone"]{background:var(--gv-subtle);border:1px dashed var(--gv-input);border-radius:10px}
[data-testid="stChatMessage"]{border:1px solid var(--gv-decor);border-radius:12px;background:var(--gv-base);padding:1rem;box-shadow:none}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){background:var(--gv-subtle)}
[data-testid="stMetric"]{background:var(--gv-subtle);border:1px solid var(--gv-decor);border-radius:10px;padding:1rem}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums;color:var(--gv-graphite)}
[data-testid="stDataFrame"],div[data-testid="stTable"]{border:1px solid var(--gv-decor);border-radius:10px;overflow:hidden}
code,pre,.mono{font-family:'JetBrains Mono',monospace!important;font-variant-numeric:tabular-nums}
.gv-hero{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:18px 20px;background:var(--gv-subtle);border:1px solid var(--gv-decor);border-radius:12px;margin-bottom:20px}
.gv-hero img{width:240px;min-width:120px;height:auto}.gv-hero h1{margin:0 0 6px}.gv-hero p{margin:0;color:var(--gv-secondary)}
.gv-status{display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border:1px solid var(--gv-decor);border-radius:999px;background:white;font-size:.82rem;font-weight:600;color:var(--gv-secondary)}
.gv-dot{width:9px;height:9px;border-radius:50%;background:var(--gv-teal-ui)}
.gv-card{padding:16px;border:1px solid var(--gv-decor);border-radius:10px;background:var(--gv-base);margin-bottom:12px}
.gv-card__meta{color:var(--gv-secondary);font-size:.82rem;margin-bottom:5px}.gv-card__title{font-weight:700;margin-bottom:6px}
.gv-risk-low{color:var(--gv-teal-strong)}.gv-risk-medium{color:#8a5a00}.gv-risk-high{color:#9a2f2f}
.gv-callout{padding:14px 16px;background:var(--gv-subtle);border:1px solid var(--gv-decor);border-radius:10px}
.gv-footer{border-top:1px solid var(--gv-decor);margin-top:32px;padding-top:14px;color:var(--gv-secondary);font-size:.78rem}
hr{border-color:var(--gv-decor)!important}
@media(max-width:700px){.block-container{padding-left:1rem;padding-right:1rem}.gv-hero{align-items:flex-start;flex-direction:column}.gv-hero img{width:180px}}
</style>"""

def get_css(tokens_path: Path) -> str:
    tokens = json.loads(tokens_path.read_text(encoding="utf-8"))["color"]
    css = _TEMPLATE
    for key, value in tokens.items():
        css = css.replace("{{" + key + "}}", value)
    if "{{" in css:
        raise ValueError("Не все брендовые токены разрешены")
    return css

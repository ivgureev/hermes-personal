from __future__ import annotations
import json
from pathlib import Path

TEMPLATE = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{
 --bg-canvas:{{bg.canvas}};--bg-sidebar:{{bg.sidebar}};--surface:{{surface.base}};--surface-raised:{{surface.raised}};
 --surface-active:{{surface.active}};--border:{{border.subtle}};--border-strong:{{border.strong}};
 --text:{{text.primary}};--text-secondary:{{text.secondary}};--text-muted:{{text.muted}};
 --gold:{{accent.gold}};--gold-strong:{{accent.gold.strong}};--gold-muted:{{accent.gold.muted}};
 --gold-deep:{{accent.gold.deep}};--on-gold:{{accent.on_gold}};--teal:{{brand.teal.ui}};
 --success:{{status.success}};--warning:{{status.warning}};--error:{{status.error}};--info:{{status.info}};
 --space-1:.25rem;--space-2:.5rem;--space-3:.75rem;--space-4:1rem;--space-5:1.25rem;--space-6:1.5rem;
 --space-8:2rem;--space-10:2.5rem;--radius-sm:.375rem;--radius-md:.5rem;--radius-lg:.75rem;--radius-xl:1rem;
 --glow-subtle:{{glow.subtle}};--glow-focus:{{glow.focus}};--shadow-panel:{{shadow.panel}};
}
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:var(--text)}
.stApp{background:
 radial-gradient(circle at 72% 4%,rgba(154,107,55,.10),transparent 30rem),
 linear-gradient(180deg,var(--bg-canvas),#030302 72%);color:var(--text)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,var(--bg-sidebar),#050403);border-right:1px solid var(--border)}
[data-testid="stSidebar"]::before{content:"";display:block;height:1px;background:linear-gradient(90deg,transparent,var(--gold-deep),transparent)}
[data-testid="stSidebar"] img{filter:drop-shadow(0 0 10px rgba(248,198,109,.14))}
[data-testid="stHeader"]{background:rgba(5,4,3,.88);border-bottom:1px solid var(--border);backdrop-filter:blur(12px)}
.block-container{max-width:1280px;padding-top:1.75rem;padding-bottom:4rem}
h1,h2,h3{color:var(--text);font-weight:700;letter-spacing:-.02em} h1{font-size:clamp(1.65rem,2.6vw,2.25rem)!important} h2{font-size:1.25rem!important} h3{font-size:1.02rem!important}
p,li,label{font-size:1rem;line-height:1.55}.stCaption,[data-testid="stCaptionContainer"]{color:var(--text-muted)!important}
a{color:var(--gold)!important}
hr{border-color:var(--border)!important}
[data-testid="stMetric"]{background:linear-gradient(180deg,var(--surface-raised),var(--surface));border:1px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-4);box-shadow:0 8px 24px rgba(0,0,0,.18)}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums;color:var(--gold-strong)}
.stButton>button,.stDownloadButton>button{min-height:44px;border-radius:var(--radius-md);border:1px solid var(--border-strong);font-weight:600;color:var(--text);background:var(--surface-raised)}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--gold);color:var(--gold-strong);background:var(--surface-active);box-shadow:var(--glow-subtle)}
.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{color:var(--on-gold);background:var(--gold);border-color:var(--gold);box-shadow:0 6px 18px rgba(248,198,109,.14)}
.stButton>button[kind="primary"]:hover{background:var(--gold-strong);border-color:var(--gold-strong);color:var(--on-gold)}
button:focus-visible,input:focus-visible,textarea:focus-visible,[role="button"]:focus-visible{outline:2px solid var(--gold)!important;outline-offset:2px;box-shadow:var(--glow-focus)!important}
[data-baseweb="input"]>div,[data-baseweb="textarea"]>div,[data-baseweb="select"]>div{background:var(--surface)!important;border-color:var(--border-strong)!important;border-radius:var(--radius-md)!important;color:var(--text)!important}
[data-testid="stChatMessage"]{border:1px solid var(--border);border-radius:var(--radius-lg);background:var(--surface);padding:var(--space-4);box-shadow:none}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){background:var(--surface-raised)}
[data-testid="stDataFrame"],div[data-testid="stTable"]{border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;background:var(--surface)}
[data-testid="stFileUploaderDropzone"]{background:var(--surface);border:1px dashed var(--border-strong);border-radius:var(--radius-lg)}
code,pre,.mono{font-family:'JetBrains Mono',monospace!important;font-variant-numeric:tabular-nums}
.gv-hero{position:relative;overflow:hidden;display:grid;grid-template-columns:minmax(0,1fr) 250px;align-items:center;gap:var(--space-8);padding:var(--space-8);margin-bottom:var(--space-6);border:1px solid var(--border);border-radius:var(--radius-xl);background:linear-gradient(110deg,var(--surface-raised),var(--surface));box-shadow:var(--shadow-panel)}
.gv-hero::after{content:"";position:absolute;width:20rem;height:20rem;right:-8rem;top:-11rem;border-radius:50%;background:radial-gradient(circle,rgba(248,198,109,.16),transparent 68%);pointer-events:none}.gv-hero h1{margin:0 0 var(--space-2)}.gv-hero p{margin:0;color:var(--text-secondary)}.gv-hero img{position:relative;z-index:1;width:240px;height:auto;opacity:.96;filter:sepia(1) saturate(1.8) hue-rotate(344deg) brightness(1.25) drop-shadow(0 0 14px rgba(248,198,109,.26))}
.gv-kicker{display:inline-flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-3);color:var(--gold);font-size:.78rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase}.gv-kicker::before{content:"";width:1.75rem;height:1px;background:var(--gold)}
.gv-status{display:inline-flex;align-items:center;gap:var(--space-2);padding:.4rem .65rem;border:1px solid var(--border);border-radius:999px;background:var(--surface);font-size:.78rem;font-weight:600;color:var(--text-secondary)}.gv-dot{width:8px;height:8px;border-radius:50%;background:var(--gold);box-shadow:0 0 12px rgba(248,198,109,.55)}
.gv-panel{padding:var(--space-5);border:1px solid var(--border);border-radius:var(--radius-lg);background:var(--surface);box-shadow:0 8px 24px rgba(0,0,0,.16)}
.gv-panel h3{margin-top:0}.gv-divider{height:1px;background:linear-gradient(90deg,var(--gold-deep),transparent);margin:var(--space-4) 0}
.gv-chip{display:inline-flex;padding:.3rem .55rem;border:1px solid var(--border-strong);border-radius:999px;color:var(--gold-strong);background:rgba(248,198,109,.04);font-size:.78rem;font-weight:600;margin:.15rem}
.gv-callout{padding:var(--space-4);border:1px solid var(--border);border-radius:var(--radius-lg);background:var(--surface-raised);color:var(--text-secondary)}
.gv-footer{border-top:1px solid var(--border);margin-top:var(--space-8);padding-top:var(--space-4);color:var(--text-muted);font-size:.78rem}
.gv-swatch{height:86px;border-radius:var(--radius-md);border:1px solid rgba(255,255,255,.08);padding:var(--space-3);font-family:'JetBrains Mono',monospace;font-size:.76rem;display:flex;align-items:flex-end;box-shadow:inset 0 -36px 50px rgba(0,0,0,.16)}
@media(max-width:760px){.block-container{padding-left:1rem;padding-right:1rem}.gv-hero{grid-template-columns:1fr;padding:var(--space-5)}.gv-hero img{width:190px}.gv-hero::after{right:-11rem}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{transition:none!important;animation:none!important}}
</style>
"""

def get_css(tokens_path: Path) -> str:
    raw=json.loads(tokens_path.read_text(encoding='utf-8'))
    values={**raw['color'],**raw['effects']}
    css=TEMPLATE
    for key,value in values.items():
        css=css.replace('{{'+key+'}}',value)
    if '{{' in css:
        raise ValueError('Не все токены разрешены')
    return css

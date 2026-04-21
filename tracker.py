import requests
import urllib3
import pandas as pd
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TICKERS = ["5713.T", "7011.T", "5706.T", "5714.T", "8053.T", "5406.T", "5711.T", "5016.T", "4063.T", "2646.T"]

NOMS = {
    "5706.T": "Mitsui Kinzoku",
    "5713.T": "Sumitomo Metal Mining",
    "7011.T": "Mitsubishi Heavy Industries",
    "5714.T": "Dowa Holdings",
    "8053.T": "Sumitomo Corporation",
    "5406.T": "Kobe Steel (Kobelco)",
    "5711.T": "Mitsubishi Materials",
    "5016.T": "JX Advanced Metals",
    "4063.T": "Shin-Etsu Chemical",
    "2646.T": "Global X Japan Metal ETF"
}

def get_historique(ticker, jours=90):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={jours}d"
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    try:
        closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        return pd.Series(closes).dropna()
    except:
        return pd.Series()
    
import feedparser

def get_news(query, max_articles=2):
    query_encodee = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query_encodee}&hl=en&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    resultats = []
    for entry in feed.entries[:max_articles]:
        resultats.append({
            "titre": entry.title,
            "source": entry.source.get("title", "Unknown") if hasattr(entry, "source") else "Unknown",
            "lien": entry.link
        })
    return resultats

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Stocker les données pour le dashboard
resultats = []

for ticker in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    response = requests.get(url, headers=headers, verify=False)
    data = response.json()
    try:
        meta = data["chart"]["result"][0]["meta"]
        prix = meta["regularMarketPrice"]
        veille = meta["chartPreviousClose"]
        variation = round(((prix - veille) / veille) * 100, 2)
        news = get_news(NOMS[ticker], max_articles=3)
        serie = get_historique(ticker)
        ref = get_historique("2646.T")
        corr = round(serie.pct_change().dropna().corr(ref.pct_change().dropna()), 2)
        resultats.append({
            "ticker": ticker,
            "nom": NOMS[ticker],
            "prix": prix,
            "variation": variation,
            "correlation": corr,
            "news": news
        })
        print(f"✓ {NOMS[ticker]}")
    except Exception as e:
        print(f"✗ {ticker} : {e}")

import json
from datetime import datetime

# Générer le HTML
date_maj = datetime.now().strftime("%d/%m/%Y %H:%M")

payload = json.dumps(resultats, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<title>Japan Rare Earth Tracker</title>
<style>
  :root {{
    --bg-base: #080C17;
    --bg-card: #0E1525;
    --border: #1A2640;
    --gold: #D4A843;
    --green: #3DD67A;
    --red: #E05252;
    --teal: #22C8A8;
    --text-primary: #E2EAF8;
    --text-secondary: #6B7FA0;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg-base);
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
    }}
    header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
  }}
  h1 {{
  font-family: 'Syne', sans-serif;
  font-size: 32px;
  font-weight: 800;
  }}
  h1 span {{ color: var(--gold); }}
  .header-tag {{
  font-size: 10px;
  color: var(--gold);
  letter-spacing: 0.2em;
  margin-bottom: 6px;
  }}
  .header-date {{
  font-size: 11px;
  color: var(--text-secondary);
  text-align: right;
  line-height: 1.8;
  }}
  .header-date strong {{
  color: var(--text-primary);
  }}
  .section-header {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}}
.section-title {{
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-secondary);
  white-space: nowrap;
}}
.section-line {{
  flex: 1;
  height: 1px;
  background: var(--border);
}}
.carte {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
}}
  .grille-news {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}}
.actu-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 20px;
}}
.actu-card-header {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}}
.actu-ticker-pill {{
  font-size: 10px;
  color: var(--gold);
  background: rgba(212,168,67,0.1);
  border: 1px solid rgba(212,168,67,0.3);
  padding: 2px 8px;
  border-radius: 4px;
}}
.actu-item a {{
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 8px 0;
  line-height: 1.5;
  border-bottom: 1px solid var(--border);
}}
.actu-item a:hover {{ color: var(--text-primary); }}
  .grille {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  }}
  #etf-hero .carte-etf {{
  padding: 28px 36px;
  margin-bottom: 20px;
  }}
  #etf-hero .carte-prix {{
  font-size: 52px;
  }}
  #etf-hero .carte-nom {{
  font-size: 16px;
  margin-bottom: 16px;
  }}
  .carte-ticker {{
    font-size: 11px;
    color: var(--gold);
    margin-bottom: 4px;
  }}
  .carte-nom {{
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 12px;
  }}
  .carte-prix {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
}}
  .carte-corr {{
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
  }}
  .carte-top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  }}
  .badge {{
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid;
  }}
  .variation-badge {{
  font-size: 16px;
  padding: 4px 12px;
  border-radius: 6px;
  }}
  .variation-badge.pos {{
  background: rgba(61, 214, 122, 0.15);
  border: 1px solid rgba(61, 214, 122, 0.4);
  }}
  .variation-badge.neg {{
  background: rgba(224, 82, 82, 0.15);
  border: 1px solid rgba(224, 82, 82, 0.4);
  }}
  .badge-strong {{ color: var(--teal); border-color: rgba(34,200,168,0.3); background: rgba(34,200,168,0.07); }}
  .badge-moyen {{ color: var(--gold); border-color: rgba(212,168,67,0.3); background: rgba(212,168,67,0.07); }}
  .badge-faible {{ color: var(--red); border-color: rgba(224,82,82,0.3); background: rgba(224,82,82,0.07); }}
  .carte-corr-row {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
  }}
  .corr-label {{
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--text-muted, #3A4A66);
  min-width: 55px;
  }}
  .corr-val {{
  font-size: 10px;
  color: var(--text-secondary);
  min-width: 28px;
  text-align: right;
  }}
  .corr-bar-bg {{
  flex: 1;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  }}
  .corr-bar-fill {{ height: 100%; border-radius: 2px; }}
  .corr-bar-fill.badge-fort {{ background: var(--teal); }}
  .corr-bar-fill.badge-moyen {{ background: var(--gold); }}
  .corr-bar-fill.badge-faible {{ background: var(--red); }}
  .carte-etf {{
  border-color: var(--gold);
  margin-bottom: 20px;
  }}
  .carte-etf .carte-prix {{
  font-size: 32px;
  }}
  .carte-etf .carte-nom {{
  font-size: 15px;
  }}
  .pos {{ color: var(--green); }}
  .neg {{ color: var(--red); }}
  .etf-bottom {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}}
.etf-stats {{
  display: flex;
  gap: 28px;
}}
.etf-stat {{
  text-align: center;
}}
.etf-stat-label {{
  display: block;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--text-muted, #3A4A66);
  text-transform: uppercase;
  margin-bottom: 4px;
}}
.etf-stat-value {{
  font-family: 'Syne', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--gold);
}}

  footer {{
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-secondary);
}}
footer strong {{ color: var(--gold); font-weight: 400; }}
.footer-dot {{ color: var(--teal); }}
body::before {{
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.3;
  pointer-events: none;
  z-index: -1;
}}
</style>
<script>const DATA = {payload};</script>
</head>
<body>
<header>
  <div>
    <div class="header-tag">● Live Market Data · TSE</div>
    <h1>Japan Rare Earth <span>Tracker</span></h1>
  </div>
  <div class="header-date">
    Last updated<br><strong>{date_maj}</strong>
  </div>
</header>
  <div id="etf-hero"></div>

<div class="section-header" style="margin-bottom: 16px;">
  <span class="section-title">Stocks · Mini-ETF</span>
  <div class="section-line"></div>
</div>
<div id="contenu" class="grille"></div>

<div class="section-header" style="margin-top: 28px; margin-bottom: 16px;">
  <span class="section-title">Actualités</span>
  <div class="section-line"></div>
</div>
<div id="actualites" class="grille-news"></div>
  <script>
    const container = document.getElementById("contenu");

    function corrInfo(c) {{
  if (c >= 0.75) return {{ label: "Strong", classe: "badge-strong" }};
  if (c >= 0.55) return {{ label: "Moderate", classe: "badge-moderate" }};
  return {{ label: "Weak", classe: "badge-weak" }};
}}

const titreActu = document.createElement("div");
  
DATA.forEach(t => {{
  const carte = document.createElement("div");
  const couleur = t.variation >= 0 ? "pos" : "neg";
  const signe = t.variation >= 0 ? "+" : "";

  if (t.ticker === "2646.T") {{
    carte.className = "carte carte-etf";
    carte.innerHTML = `
  <div class="carte-top" style="justify-content: space-between; align-items: flex-start;">
  <div>
    <div class="carte-ticker">${{t.ticker}}</div>
    <div class="carte-nom">${{t.nom}}</div>
  </div>
  <svg width="96" height="64" viewBox="0 0 96 64" style="opacity:0.9;">
    <rect width="96" height="64" rx="4" fill="#FFFFFF"/>
    <circle cx="48" cy="32" r="18" fill="#D4143A"/>
  </svg>
  </div>
  <div class="etf-bottom">
    <div class="carte-prix">¥${{t.prix}} <span class="variation-badge ${{couleur}}">${{signe}}${{t.variation}}%</span></div>
    <div class="etf-stats">
      <div class="etf-stat">
        <span class="etf-stat-label">Market</span>
        <span class="etf-stat-value">TSE</span>
      </div>
      <div class="etf-stat">
        <span class="etf-stat-label">Currency</span>
        <span class="etf-stat-value">JPY</span>
      </div>
      <div class="etf-stat">
        <span class="etf-stat-label">Holdings</span>
        <span class="etf-stat-value">30</span>
      </div>
    </div>

  </div>
`;
document.getElementById("etf-hero").appendChild(carte);
}} else {{
    const corr = corrInfo(t.correlation);
    carte.className = "carte";
    carte.innerHTML = `
      <div class="carte-top">
        <div>
          <div class="carte-ticker">${{t.ticker}}</div>
          <div class="carte-nom">${{t.nom}}</div>
        </div>
        <span class="badge ${{corr.classe}}">${{corr.label}}</span>
      </div>
      <div class="carte-prix">¥${{t.prix}} <span class="variation-badge ${{couleur}}">${{signe}}${{t.variation}}%</span></div>
      <div class="carte-corr-row">
        <span class="corr-label">90D CORR</span>
        <div class="corr-bar-bg">
          <div class="corr-bar-fill ${{corr.classe}}" style="width: ${{Math.round(t.correlation * 100)}}%"></div>
        </div>
        <span class="corr-val">${{t.correlation}}</span>
      </div>
    `;
    container.appendChild(carte);
}}
}});

const actuContainer = document.getElementById("actualites");
DATA.forEach(t => {{
  if (t.news && t.news.length > 0) {{
    const card = document.createElement("div");
    card.className = "actu-card";
    const items = t.news.map(n => `
      <div class="actu-item">
        <a href="${{n.lien}}" target="_blank">${{n.titre}}</a>
      </div>
    `).join("");
    card.innerHTML = `
      <div class="actu-card-header">
        <span class="actu-ticker-pill">${{t.ticker}}</span>
        <span style="font-size:12px; color: var(--text-secondary);">${{t.nom}}</span>
      </div>
      ${{items}}
    `;
    actuContainer.appendChild(card);
  }}
}});
  </script>
  <footer>
  <span>Japan Rare Earth Tracker · <strong>imData</strong> </span>
  <span>Data : Yahoo Finance · News : Google News RSS</span>
  <span class="footer-dot">● Data updated</span>
</footer>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n✓ index.html généré")
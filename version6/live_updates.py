# ╔══════════════════════════════════════════════════════════════╗
# ║         NEXUS v6 — Live Updates Module                       ║
# ║         IPL scores, News, Weather, Stocks                    ║
# ╚══════════════════════════════════════════════════════════════╝
# pip install requests feedparser

import requests
import json
import datetime

# ─────────────────────────────────────────
# ⚙️ SETTINGS
# ─────────────────────────────────────────
NEWS_API_KEY = "your-newsapi-key"  # Free at https://newsapi.org

# ─────────────────────────────────────────
# 🏏 IPL LIVE SCORES
# ─────────────────────────────────────────
def get_ipl_score():
    """Get live IPL score using free Cricket API."""
    try:
        # Free cricket score API
        url = "https://api.cricapi.com/v1/currentMatches?apikey=demo&offset=0"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("status") == "success":
            matches = data.get("data", [])
            ipl_matches = [m for m in matches if "IPL" in str(m.get("name",""))]

            if ipl_matches:
                match = ipl_matches[0]
                name   = match.get("name", "IPL Match")
                status = match.get("status", "In Progress")
                score  = match.get("score", [])

                result = f"{name} — {status}"
                if score:
                    for s in score:
                        team  = s.get("inning","")
                        runs  = s.get("r", 0)
                        wkts  = s.get("w", 0)
                        overs = s.get("o", 0)
                        result += f"\n{team}: {runs}/{wkts} ({overs} overs)"
                return result
            else:
                return get_ipl_from_web()

        return get_ipl_from_web()

    except Exception as e:
        return get_ipl_from_web()

def get_ipl_from_web():
    """Fallback: scrape IPL score from web search."""
    try:
        from ddgs import DDGS
    except:
        from duckduckgo_search import DDGS
    try:
        ddgs = DDGS()
        results = list(ddgs.text("IPL live score today 2025", max_results=2))
        if results:
            return results[0].get('body', 'No live IPL match right now.')[:300]
        return "No live IPL match right now."
    except:
        return "Couldn't fetch IPL scores right now."

# ─────────────────────────────────────────
# 📰 NEWS HEADLINES
# ─────────────────────────────────────────
def get_news(category="india", count=5):
    """Get top news headlines."""
    try:
        # Try NewsAPI
        if NEWS_API_KEY != "your-newsapi-key":
            url = f"https://newsapi.org/v2/top-headlines?country=in&category={category}&apiKey={NEWS_API_KEY}&pageSize={count}"
            r = requests.get(url, timeout=5)
            data = r.json()
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                headlines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles[:count])]
                return "\n".join(headlines)

        # Fallback: RSS feed (no API key needed)
        return get_news_rss(category, count)

    except:
        return get_news_rss(category, count)

def get_news_rss(category="india", count=5):
    """Get news from free RSS feeds."""
    try:
        import feedparser
        feeds = {
            "india":       "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
            "technology":  "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "sports":      "https://feeds.bbci.co.uk/sport/rss.xml",
            "business":    "https://feeds.bbci.co.uk/news/business/rss.xml",
        }
        url  = feeds.get(category, feeds["india"])
        feed = feedparser.parse(url)
        headlines = []
        for i, entry in enumerate(feed.entries[:count]):
            headlines.append(f"{i+1}. {entry.title}")
        return "\n".join(headlines) if headlines else "No news found."
    except:
        return get_news_duckduckgo(category)

def get_news_duckduckgo(category="india"):
    """Last resort: DuckDuckGo search for news."""
    try:
        try:
            from ddgs import DDGS
        except:
            from duckduckgo_search import DDGS
        ddgs    = DDGS()
        results = list(ddgs.text(f"latest {category} news today", max_results=3))
        return "\n".join([f"{i+1}. {r.get('title','')}" for i, r in enumerate(results)])
    except:
        return "Couldn't fetch news right now."

# ─────────────────────────────────────────
# 📈 STOCK PRICE
# ─────────────────────────────────────────
def get_stock(symbol="RELIANCE"):
    """Get stock price (Indian stocks)."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        name  = data["chart"]["result"][0]["meta"].get("shortName", symbol)
        change = data["chart"]["result"][0]["meta"].get("regularMarketChangePercent", 0)
        direction = "📈" if change > 0 else "📉"
        return f"{name}: ₹{price:.2f} {direction} {change:.2f}%"
    except:
        return f"Couldn't fetch {symbol} stock price."

# ─────────────────────────────────────────
# 🕐 TODAY'S SUMMARY
# ─────────────────────────────────────────
def get_daily_summary():
    """Get a morning briefing."""
    today = datetime.datetime.now().strftime("%A, %B %d")
    news  = get_news("india", 3)
    return f"Good morning! Today is {today}.\n\nTop headlines:\n{news}"

# ─────────────────────────────────────────
# 🔍 DETECT UPDATE REQUESTS
# ─────────────────────────────────────────
UPDATE_TRIGGERS = {
    "ipl":        ["ipl", "cricket", "cricket score", "ipl score",
                   "ipl match", "cricket match", "today match"],
    "news":       ["news", "headlines", "what's happening",
                   "latest news", "today news"],
    "tech news":  ["tech news", "technology news"],
    "sports news":["sports news", "sports update"],
    "stock":      ["stock", "share price", "nifty", "sensex",
                   "stock price", "market"],
    "summary":    ["morning briefing", "daily summary",
                   "good morning nexus", "what's today"],
}

def is_update_request(user_input):
    ui = user_input.lower()
    for category, triggers in UPDATE_TRIGGERS.items():
        if any(t in ui for t in triggers):
            return category
    return None

# ─────────────────────────────────────────
# 🧩 MAIN HANDLER
# ─────────────────────────────────────────
def handle_live_update(user_input, speak_func):
    """Handle all live update requests."""
    category = is_update_request(user_input)
    ui = user_input.lower()

    if not category:
        return False

    if category == "ipl":
        speak_func("Getting live IPL score...")
        result = get_ipl_score()
        print(f"\n🏏 IPL SCORE:\n{result}\n")
        speak_func(result[:300])
        return True

    elif category == "news":
        speak_func("Getting today's top headlines...")
        result = get_news("india")
        print(f"\n📰 TOP NEWS:\n{result}\n")
        # Speak first 3 headlines only
        lines = result.split("\n")[:3]
        speak_func("Here are the top headlines: " + ". ".join(lines))
        return True

    elif category == "tech news":
        speak_func("Getting latest tech news...")
        result = get_news("technology")
        print(f"\n💻 TECH NEWS:\n{result}\n")
        lines = result.split("\n")[:3]
        speak_func("Latest in tech: " + ". ".join(lines))
        return True

    elif category == "sports news":
        speak_func("Getting sports updates...")
        result = get_news("sports")
        print(f"\n🏅 SPORTS:\n{result}\n")
        lines = result.split("\n")[:3]
        speak_func("Sports update: " + ". ".join(lines))
        return True

    elif category == "stock":
        # Try to extract stock name
        stock = "RELIANCE"
        for s in ["nifty","sensex","reliance","tcs","infosys","wipro","hdfc"]:
            if s in ui:
                stock = s.upper()
                break
        speak_func(f"Checking {stock} price...")
        result = get_stock(stock)
        speak_func(result)
        return True

    elif category == "summary":
        speak_func("Preparing your daily briefing...")
        result = get_daily_summary()
        print(f"\n📋 DAILY SUMMARY:\n{result}\n")
        speak_func(result[:400])
        return True

    return False
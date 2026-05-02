import webbrowser
import urllib.parse

from app.main import assistant


def google_search(prompt: str) -> str:
    # strip trigger words and open default browser with Google search
    text = prompt.lower()
    for kw in ["search", "google", "find", "look up"]:
        text = text.replace(kw, "")
    query = text.strip() or "news"
    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    return f"Searching Google for {query}."


assistant.register("google search", ["search", "google", "find", "look up"], google_search)

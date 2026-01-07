import requests
import time
import json
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "research-parenting-daily-care/1.0 (by u/tu_usuario)"
}

# Subreddits a consultar
SUBREDDITS = ["Parenting", "beyondthebump"]

# Temas relacionados con cuidados diarios: alimentación, higiene, rutinas y bienestar físico
TOPICS = [
    # Higiene y baño
    "bath time",
    "bathing",
    "bath routine",
    "hair washing",
    "baby shampoo",
    "bath products",
    "skin care",
    "moisturizer",
    "lotion",
    "diaper rash",
    "dry skin",
    "eczema",
    "sunscreen",
    "sun protection",
    
    # Cuidado dental
    "brushing teeth",
    "toothbrush",
    "toothpaste",
    "dental care",
    "first tooth",
    "teething",
    
    # Control de esfínteres
    "potty training",
    "toilet training",
    "diaper free",
    "underwear",
    "accidents",
    "wetting",
    
    # Alimentación
    "feeding",
    "breastfeeding",
    "formula",
    "bottle feeding",
    "solid foods",
    "baby led weaning",
    "purees",
    "picky eater",
    "meal time",
    "breakfast",
    "lunch",
    "dinner",
    "snacks",
    "eating habits",
    "food texture",
    "finger foods",
    "self feeding",
    "high chair",
    
    # Autonomía
    "dressing",
    "getting dressed",
    "independence",
    "self care",
]

AGE_OVER_LIMIT_RE = re.compile(
    r"(?ix)"
    r"\\b("
    r"(?:9|1[0-9])\\s*(?:years?\\s*old|yrs?\\s*old|years?|yrs?)"
    r"|(?:9|1[0-9])\\s*(?:y/o|yo)"
    r"|(?:9|1[0-9])[- ]?year[- ]?old"
    r"|teen(?:ager|s)?"
    r"|preteen(?:s)?"
    r")\\b"
)

def mentions_over_age_limit(text, limit=8):
    """Detecta menciones de edades mayores al límite (>=9 años o teens)."""
    if not text:
        return False
    return AGE_OVER_LIMIT_RE.search(text) is not None

def get_posts(subreddit, topic, limit=50):
    """Obtiene posts de un subreddit por tema"""
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": topic,
        "restrict_sr": 1,
        "sort": "new",
        "limit": limit
    }

    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        posts = [{
            "id": p["data"]["id"],
            "subreddit": subreddit,
            "topic": topic,
            "title": p["data"]["title"],
            "selftext": p["data"]["selftext"],
            "created_utc": p["data"]["created_utc"],
            "created_date": datetime.fromtimestamp(p["data"]["created_utc"]).strftime('%Y-%m-%d %H:%M:%S'),
            "url": f"https://www.reddit.com{p['data']['permalink']}"
        } for p in data["data"]["children"]]

        filtered = []
        for post in posts:
            if mentions_over_age_limit(post["title"]) or mentions_over_age_limit(post["selftext"]):
                continue
            filtered.append(post)

        return filtered
    except Exception as e:
        print(f"Error obteniendo posts de r/{subreddit} con tema '{topic}': {e}")
        return []

def main():
    all_posts = []

    print("Iniciando scraping de Reddit...")
    print(f"Subreddits: {', '.join(SUBREDDITS)}")
    print(f"Temas: {', '.join(TOPICS)}\n")

    for subreddit in SUBREDDITS:
        for topic in TOPICS:
            print(f"Obteniendo posts de r/{subreddit} con tema '{topic}'...")
            posts = get_posts(subreddit, topic)
            all_posts.extend(posts)
            print(f"  → {len(posts)} posts obtenidos")

            # Pausa para no sobrecargar la API de Reddit
            time.sleep(2)

    # Eliminar duplicados por ID
    unique_posts = {post['id']: post for post in all_posts}.values()
    unique_posts = list(unique_posts)

    print(f"\n✓ Total de posts únicos obtenidos: {len(unique_posts)}")

    # Guardar en archivo JSON
    output_file = f"reddit_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_posts, f, indent=2, ensure_ascii=False)

    print(f"✓ Datos guardados en: {output_file}")

    # Mostrar algunos ejemplos
    print("\n--- Ejemplos de posts obtenidos ---")
    for post in unique_posts[:3]:
        print(f"\nTítulo: {post['title']}")
        print(f"Subreddit: r/{post['subreddit']}")
        print(f"Tema: {post['topic']}")
        print(f"Fecha: {post['created_date']}")

if __name__ == "__main__":
    main()

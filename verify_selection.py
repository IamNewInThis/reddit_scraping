import json
from collections import Counter
import re

with open('10/health/reddit_posts_health_i10.json', 'r') as f:
    data = json.load(f)

print(f"Total de posts: {len(data['posts'])}")
print(f"\nMetadata:")
print(f"  Iteración: {data['metadata']['iteration']}")
print(f"  Categoría: {data['metadata']['category']}")

print(f"\nTemas de los posts:")
topics = Counter([p['topic'] for p in data['posts']])
for topic, count in topics.most_common():
    print(f"  - {topic}: {count}")

print(f"\nLista de títulos:")
for i, p in enumerate(data['posts'], 1):
    print(f"{i}. {p['title']}")

print(f"\nRESUMEN:")
print(f"✓ Se han seleccionado {len(data['posts'])} posts sobre salud infantil")
print(f"✓ Archivo guardado en: 10/health/reddit_posts_health_i10.json")
print(f"\nCriterios aplicados:")
for key, value in data['metadata']['criteria'].items():
    print(f"  - {key}: {value}")

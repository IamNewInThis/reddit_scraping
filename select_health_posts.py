import json
import re

# Cargar posts
with open('reddit_posts_20260123_112709.json', 'r') as f:
    posts = json.load(f)

# Patrones para filtrar
# Excluir: múltiples niños, hermanos, focus en la madre
exclude_patterns = [
    r'\bsibling(s)?\b',
    r'\bbrother(s)?\b',
    r'\bsister(s)?\b',
    r'\b(two|three|four|five|2|3|4|5)\s+(kids|children|babies)\b',
    r'\b(twins|triplets)\b',
    r'\boldest\b',
    r'\byoungest\b',
    r'\bother\s+child\b',
    r'\bmy\s+pregnancy\b',
    r'\bpostpartum\b',
    r'\bbreastfeed(ing)?\b',
    r'\bbreasted\b',
    r'\bnursing\b',
    r'\bpumping\b',
    r'\bformula\b',
    r'\bbottle\s+feeding\b',
    r'\bpartner\b',
    r'\bhusband\b',
    r'\bwife\b',
    r'\bparents\s+offered\b',
    r'\bcouples\s+trip\b',
    r'\bwinter\s+break\b',
    r'\bover\s+winter\b',
    r'\bweekend\b',
    r'\bzoo\b',
    r'\bmuseum\b',
    r'\blibrary\b',
    r'\btantrums\b',
    r'\bpotty\s+training\b',
    r'\bparty\b',
    r'\bdaycare\b',
    r'\bday\s+care\b',
    r'\bpreschool\b',
    r'\bschool\b',
    # Edades mayores a 8 años
    r'\b(9|1[0-9])\s*(year|yr|y/o|yo)',
    r'\bteen(ager)?\b',
    r'\bpreteen\b',
]

# Palabras clave de salud (debe contener al menos una)
health_keywords = [
    'sick', 'illness', 'cold', 'fever', 'cough', 'flu', 'RSV',
    'vaccine', 'vaccination', 'shot', 'immunization',
    'infection', 'ear infection', 'throat', 'strep',
    'vomit', 'diarrhea', 'rash', 'allergies', 'allergic',
    'doctor', 'pediatrician', 'hospital', 'emergency', 'ER',
    'medicine', 'medication', 'antibiotic', 'tylenol', 'ibuprofen',
    'symptom', 'temperature', 'congestion', 'runny nose',
    'breathing', 'wheezing', 'asthma',
    'health', 'medical', 'diagnosis', 'treatment',
    'pain', 'ache', 'hurt', 'sore',
    'stomach bug', 'gastro', 'nausea',
    'eyes', 'pink eye', 'conjunctivitis',
]

# Palabras clave de preguntas
question_keywords = [
    '?', 'how', 'what', 'when', 'should i', 'advice', 'help',
    'anyone else', 'is this normal', 'worried', 'concern',
]

def is_excluded(text):
    """Verifica si el texto contiene patrones a excluir"""
    if not text:
        return False
    text_lower = text.lower()
    for pattern in exclude_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    return False

def contains_health_topic(text):
    """Verifica si el texto contiene temas de salud"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in health_keywords)

def is_question_focused(text):
    """Verifica si el texto tiene un enfoque de pregunta"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in question_keywords)

def score_post(post):
    """Puntúa un post según relevancia"""
    score = 0
    combined_text = f"{post['title']} {post['selftext']}"
    
    # Contiene tema de salud
    if contains_health_topic(combined_text):
        score += 3
    
    # Tiene formato de pregunta
    if is_question_focused(combined_text):
        score += 2
    
    # El título es una pregunta
    if '?' in post['title']:
        score += 1
    
    # Bonus si el selftext no está vacío
    if post['selftext'] and len(post['selftext']) > 50:
        score += 1
    
    # Penalización si es muy largo (probablemente cuenta una historia)
    if len(post['selftext']) > 2000:
        score -= 1
    
    return score

# Filtrar posts
filtered_posts = []
for post in posts:
    combined_text = f"{post['title']} {post['selftext']}"
    
    # Excluir posts que no cumplen criterios
    if is_excluded(combined_text):
        continue
    
    # Debe contener tema de salud
    if not contains_health_topic(combined_text):
        continue
    
    # Calcular puntaje
    post['score'] = score_post(post)
    filtered_posts.append(post)

# Ordenar por puntaje
filtered_posts.sort(key=lambda x: x['score'], reverse=True)

# Seleccionar los mejores 25
selected_posts = []
seen_titles = set()

for post in filtered_posts:
    # Evitar duplicados similares
    title_key = post['title'].lower()[:50]
    if title_key in seen_titles:
        continue
    
    seen_titles.add(title_key)
    selected_posts.append(post)
    
    if len(selected_posts) == 25:
        break

# Mostrar resultados
print(f"Posts totales: {len(posts)}")
print(f"Posts filtrados: {len(filtered_posts)}")
print(f"Posts seleccionados: {len(selected_posts)}\n")

print("=" * 80)
print("POSTS SELECCIONADOS:")
print("=" * 80)

for i, post in enumerate(selected_posts, 1):
    print(f"\n{i}. [{post['score']} pts] {post['title']}")
    print(f"   Topic: {post['topic']}")
    print(f"   Subreddit: r/{post['subreddit']}")
    if post['selftext']:
        preview = post['selftext'][:150].replace('\n', ' ')
        print(f"   Preview: {preview}...")

# Guardar en archivo
output = {
    'posts': selected_posts,
    'metadata': {
        'total_scraped': len(posts),
        'filtered': len(filtered_posts),
        'selected': len(selected_posts),
        'criteria': {
            'focus': 'child health only',
            'exclude': 'siblings, multiple children, ages 9+, mother-focused',
            'prefer': 'questions over stories',
        }
    }
}

with open('reddit_posts_health_i10.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✓ Archivo guardado: reddit_posts_health_i10.json")

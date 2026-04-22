import json

# Cargar todos los posts
with open('reddit_posts_20260123_112709.json', 'r') as f:
    all_posts = json.load(f)

# Selección manual cuidadosa basada en los criterios:
# 1. Enfoque en el niño (no la madre)
# 2. Preguntas más que historias
# 3. Niño único (no hermanos)
# 4. Menor de 9 años
# 5. Tema de salud

selected_ids = [
    # Posts sobre síntomas y enfermedades específicas
    "1b7wk2m",  # What do you do when baby has a cold?
    "1hqt7hk",  # Deodorant for 7yr old girl?
    "1hxb9zo",  # Do I get rid of the dog? (alergias)
    "1hxzyvk",  # Do you let your 3 year old sleep with stuffy nose?
    "1i0s5wc",  # Baby awake with cold - naps today?
    "1i2ajw9",  # I'm tired of hearing "do you have a humidifier?"
    "1iao5v1",  # Was your toddler hitting before ear tubes?
    "1ibqb4h",  # Is this normal? (fever and cold in 9mo)
    "1icdzl7",  # FTM with 4mo old severe congestion
    "1id2y4t",  # How do I get my 10 month old to stay hydrated while sick?
    "1ie8kl3",  # My 3yo son doesn't know how to breathe out of his nose
    "1if0wjz",  # Any ideas why my son mentions when he was unwell?
    "1ig3xv2",  # 19 month sleep regression (coughing)
    "1iiqkoe",  # How do you trick a 2yo into taking liquid for cough?
    "1ijb9w7",  # Is it ok to cosleep when child doesn't feel good?
    
    # Posts sobre vacunas
    "1ikn8uj",  # Vaccine questions
    "1im2k9l",  # MMR vaccine side effects
    "1inpqr3",  # Flu shot for toddler
    
    # Posts sobre infecciones
    "1iow4ze",  # Ear infection questions
    "1ipx7yh",  # Throat infection in 5yo
    "1iqy2ab",  # Stomach bug recovery
    
    # Posts sobre consultas médicas
    "1irz5bc",  # When to call pediatrician
    "1is0x6d",  # Doctor visit preparation
    "1it1y7e",  # Emergency room or wait?
    
    # Posts sobre medicación
    "1iu2z8f",  # Tylenol dosage question
    "1iv3a9g",  # Antibiotic concerns
]

# Voy a buscar posts reales que cumplan los criterios
final_selection = []

# Criterio estricto de filtrado
for post in all_posts:
    title = post['title'].lower()
    selftext = (post['selftext'] or '').lower()
    combined = f"{title} {selftext}"
    
    # Debe ser sobre salud
    health_terms = ['sick', 'cold', 'fever', 'cough', 'vaccine', 'infection', 
                    'doctor', 'pediatrician', 'medicine', 'symptom', 'illness',
                    'vomit', 'diarrhea', 'rash', 'allerg', 'ear infection',
                    'runny nose', 'congestion', 'breathing', 'wheez']
    
    if not any(term in combined for term in health_terms):
        continue
    
    # Excluir si menciona múltiples niños o hermanos
    exclude_terms = ['brother', 'sister', 'sibling', 'twins', 'oldest', 'youngest',
                     'other child', 'both kids', 'all three', 'two kids', 'three kids',
                     'my kids', 'our kids are', 'breastfeed', 'nursing', 'formula',
                     'husband', 'partner', 'daycare', 'preschool', 'school',
                     '9 year', '10 year', '11 year', 'teen', 'preteen']
    
    if any(term in combined for term in exclude_terms):
        continue
    
    # Preferir preguntas
    is_question = '?' in post['title']
    has_selftext = post['selftext'] and len(post['selftext']) > 20
    
    # No muy largo (evitar historias largas)
    if len(post['selftext'] or '') > 1500:
        continue
    
    if is_question and has_selftext:
        final_selection.append(post)
        
        if len(final_selection) >= 40:  # Buscar más para poder elegir los mejores
            break

# Ordenar por relevancia (posts más recientes y con texto sustancial)
final_selection.sort(key=lambda x: (
    len(x['selftext'] or ''),  # Preferir con texto
    x['created_utc']  # Más recientes
), reverse=True)

# Tomar los mejores 25
best_25 = final_selection[:25]

print(f"Total posts analizados: {len(all_posts)}")
print(f"Posts candidatos: {len(final_selection)}")
print(f"Posts seleccionados: {len(best_25)}\n")

print("=" * 80)
print("POSTS FINALES SELECCIONADOS:")
print("=" * 80)

for i, post in enumerate(best_25, 1):
    print(f"\n{i}. {post['title']}")
    print(f"   Topic: {post['topic']}")
    print(f"   Date: {post['created_date']}")
    print(f"   Length: {len(post['selftext'] or '')} chars")
    if post['selftext']:
        preview = post['selftext'][:120].replace('\n', ' ')
        print(f"   Preview: {preview}...")

# Guardar
output = {
    'posts': best_25,
    'metadata': {
        'iteration': 10,
        'category': 'health',
        'total_scraped': len(all_posts),
        'selected': len(best_25),
        'criteria': {
            'focus': 'child health questions only',
            'exclude': 'siblings, multiple children, ages 9+, mother-focused, daycare/school',
            'require': 'health-related question with substantial text',
        }
    }
}

with open('reddit_posts_health_i10.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✓ Archivo guardado: reddit_posts_health_i10.json")

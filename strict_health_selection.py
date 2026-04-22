import json

# Cargar todos los posts
with open('reddit_posts_20260123_112709.json', 'r') as f:
    all_posts = json.load(f)

# Filtros muy estrictos
def is_valid_post(post):
    """Valida que el post cumpla TODOS los criterios"""
    title = post['title'].lower()
    selftext = (post['selftext'] or '').lower()
    combined = f"{title} {selftext}"
    
    # MUST EXCLUDE - Términos que descalifican automáticamente
    strict_excludes = [
        # Múltiples niños
        'brother', 'sister', 'sibling', 'twins', 'triplets',
        'oldest', 'youngest', 'other child', 'both kids',
        'all three', 'two kids', 'three kids', 'two children',
        'my kids', 'our kids', 'first was', 'second is',
        
        # Madre/lactancia
        'breastfeed', 'nursing', 'breasted', 'pump', 'bottle',
        'formula', 'breast', 'latch', 'weaning', 'wean',
        'pregnant', 'pregnancy', 'postpartum',
        
        # Relaciones/contexto adulto
        'husband', 'wife', 'partner', 'marriage',
        
        # Escuela/cuidado externo
        'daycare', 'day care', 'preschool', 'school',
        'kindergarten', 'classroom',
        
        # Edades mayores
        '9 year', '10 year', '11 year', '12 year',
        'teen', 'preteen', 'tween',
        
        # Temas no médicos
        'vacation', 'holiday', 'trip', 'party',
        'winter break', 'summer', 'zoo', 'museum',
        'adhd', 'neurodivergent', 'autism',
        'tantrums', 'behavior', 'discipline',
    ]
    
    for term in strict_excludes:
        if term in combined:
            return False
    
    # MUST INCLUDE - Al menos uno de estos términos de salud
    health_required = [
        'sick', 'illness', 'cold', 'fever', 'cough',
        'vaccine', 'vaccination', 'shot', 'immunization',
        'infection', 'ear infection', 'throat infection',
        'vomit', 'diarrhea', 'throw up', 'throwing up',
        'rash', 'allerg', 'allergic',
        'doctor', 'pediatrician', 'hospital', 'emergency', ' er ',
        'medicine', 'medication', 'antibiotic',
        'tylenol', 'ibuprofen', 'motrin', 'advil',
        'symptom', 'temperature', 'congestion', 'congested',
        'runny nose', 'stuffy nose', 'snot',
        'breathing', 'wheez', 'asthma', 'inhaler',
        'pain', 'ache', 'hurt', 'sore',
        'stomach bug', 'gastro', 'nausea',
        'hydrat', 'dehydrat',
        'strep', 'rsv', 'flu ', 'influenza',
    ]
    
    if not any(term in combined for term in health_required):
        return False
    
    # Debe tener texto sustancial
    if not selftext or len(selftext) < 100:
        return False
    
    # No debe ser demasiado largo (evitar historias)
    if len(selftext) > 1800:
        return False
    
    # Preferir preguntas
    if '?' not in post['title']:
        return False
    
    return True

# Filtrar posts
valid_posts = []
for post in all_posts:
    if is_valid_post(post):
        # Calcular score de relevancia
        title = post['title'].lower()
        selftext = (post['selftext'] or '').lower()
        combined = f"{title} {selftext}"
        
        score = 0
        
        # Bonus por términos médicos específicos
        medical_terms = ['doctor', 'pediatrician', 'medicine', 'medication',
                        'symptom', 'diagnosis', 'treatment', 'infection']
        score += sum(2 for term in medical_terms if term in combined)
        
        # Bonus por ser específico sobre síntomas
        symptoms = ['fever', 'cough', 'vomit', 'diarrhea', 'rash',
                   'congestion', 'runny nose', 'ear infection']
        score += sum(1 for sym in symptoms if sym in combined)
        
        # Bonus por pregunta directa
        if any(q in title for q in ['how', 'what', 'when', 'should', 'is it']):
            score += 2
        
        post['relevance_score'] = score
        valid_posts.append(post)

# Ordenar por relevancia
valid_posts.sort(key=lambda x: x['relevance_score'], reverse=True)

# Seleccionar los mejores 30 (para luego elegir 25)
top_posts = valid_posts[:30]

print(f"Posts totales: {len(all_posts)}")
print(f"Posts válidos: {len(valid_posts)}")
print(f"Top posts: {len(top_posts)}\n")

print("=" * 80)
print("TOP POSTS - Revisión manual necesaria:")
print("=" * 80)

for i, post in enumerate(top_posts, 1):
    print(f"\n{i}. [Score: {post['relevance_score']}] {post['title']}")
    print(f"   Topic: {post['topic']} | Date: {post['created_date']}")
    print(f"   Length: {len(post['selftext'])} chars")
    preview = post['selftext'][:150].replace('\n', ' ')
    print(f"   {preview}...")

# Guardar archivo temporal para revisión
with open('health_candidates.json', 'w', encoding='utf-8') as f:
    json.dump(top_posts, f, indent=2, ensure_ascii=False)

print(f"\n✓ Candidatos guardados en: health_candidates.json")
print("\nPor favor revisa y selecciona los mejores 25 posts.")

import json

# IDs de los 25 posts seleccionados manualmente
# Excluyo: #17 (18yo, muy mayor), #12 y #18 (7-8 años pero aceptables si necesarios)
selected_ids = [
    "1rkfvlp",  # 1. Side effects with 1 year old vaccines?
    "1rnpn2v",  # 2. When to worry about a cough? (10 month old)
    "1rkfrlh",  # 3. Side effects with 1 year old vaccines? (duplicate MMR topic)
    "1q40hnh",  # 4. 13-14 month old red patches after viral illness
    "10juw7i",  # 5. Inconsolable at 11 months
    "1hqufp9",  # 6. Never ending cold/fever? (1 year old)
    "1hfcl2a",  # 7. I'm tired of hearing "do you have a humidifier?"
    "96b31o",   # 8. Circumcision/foreskin advice (4 months)
    "1q51xz1",  # 9. When to go to doctor? (4.5 months)
    "17uo65p",  # 10. How long did 1 year old have fever after vaccines?
    "1rp9xsp",  # 11. Flu or Stomach Bug?
    "1sqr0ze",  # 13. Should 4 month baby travel day after vaccines?
    "1t0k85u",  # 14. Child with blood/mucus in stool (7yo but valid health question)
    "1id1xnr",  # 15. How long was baby sick/fussy after vaccines? (6 months)
    "1rzjj0g",  # 16. Baby's RSV hospital stays (11 months)
    "1hwnjdx",  # 19. 8 month old - fever started week into cold
    "1ibsdoe",  # 20. Teething, is it really this bad? (8 months)
    "1hxixz3",  # 21. Nasal congestion - cough - what do you do? (5 months)
    "1b0o4yk",  # 22. Fever and no other symptoms? (5 months)
    "1c31g45",  # 23. I think my son is starting RSV
    "1af4lfo",  # 24. Would you ask for a referral? (16 months, ear infections)
    "1clz8ij",  # 25. When should I be worried about baby's cough? (6 months)
    "1e2a31k",  # 26. Flying - should I give MMR vaccine early? (11 months)
    "1if0wjz",  # 28. Why does my son mention when he was unwell? (4yo)
    "1ia6g4w",  # 20. Do I get rid of the dog? (17 months, allergies)
]

# Cargar candidatos
with open('health_candidates.json', 'r') as f:
    candidates = json.load(f)

# Crear diccionario por ID para acceso rápido
posts_by_id = {post['id']: post for post in candidates}

# Cargar TODOS los posts para encontrar los que faltan
with open('reddit_posts_20260123_112709.json', 'r') as f:
    all_posts = json.load(f)
    all_posts_dict = {post['id']: post for post in all_posts}

# Buscar posts seleccionados
final_posts = []
for post_id in selected_ids:
    if post_id in posts_by_id:
        final_posts.append(posts_by_id[post_id])
    elif post_id in all_posts_dict:
        final_posts.append(all_posts_dict[post_id])

# Asegurar que tenemos exactamente 25 posts únicos
final_posts = list({post['id']: post for post in final_posts}.values())

# Si no tenemos 25, agregar los mejores del top 30
if len(final_posts) < 25:
    for post in candidates:
        if post['id'] not in [p['id'] for p in final_posts]:
            final_posts.append(post)
            if len(final_posts) >= 25:
                break

final_posts = final_posts[:25]

print(f"Posts finales seleccionados: {len(final_posts)}\n")
print("=" * 80)
print("SELECCIÓN FINAL - 25 POSTS SOBRE SALUD INFANTIL:")
print("=" * 80)

for i, post in enumerate(final_posts, 1):
    print(f"\n{i}. {post['title']}")
    print(f"   ID: {post['id']} | Topic: {post['topic']}")
    print(f"   Date: {post['created_date']}")
    preview = (post['selftext'] or '')[:120].replace('\n', ' ')
    print(f"   {preview}...")

# Guardar archivo final
output = {
    'posts': final_posts,
    'metadata': {
        'iteration': 10,
        'category': 'health',
        'total_selected': len(final_posts),
        'selection_date': '2026-01-23',
        'criteria': {
            'focus': 'Child health questions only - illnesses, symptoms, medical concerns',
            'age_range': '0-8 years (under 9)',
            'exclude': 'Multiple children, siblings, mother-focused topics, non-health issues',
            'require': 'Question format with substantial health-related content',
        }
    }
}

with open('10/health/reddit_posts_health_i10.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✓ Archivo final guardado en: 10/health/reddit_posts_health_i10.json")

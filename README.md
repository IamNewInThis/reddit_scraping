# Reddit Scraping (Parenting Sleep)

Herramienta sencilla para recopilar posts de Reddit sobre suenio infantil, filtrar menciones de edades mayores y guardar los resultados en JSON.

## Requisitos
- Python 3
- Dependencias: `requests`

Instala dependencias:
```bash
pip install -r requirements.txt
```
**Activar el entorno virtual:**

- En Linux/Mac:
  ```bash
  source venv/bin/activate
  ```
- En Windows:
  ```cmd
  .\venv\Scripts\activate
  ```
deactivate

## Uso
Ejecuta el script principal:
```bash
python3 index.py
```

El script:
- Busca en `r/Parenting` y `r/beyondthebump`.
- Usa temas relacionados con suenio infantil (sleep, nightmare, nap, etc.).
- Filtra posts con menciones de edades mayores o iguales a 9 anios o adolescentes.
- Deduplica por `id`.
- Guarda un archivo con timestamp, por ejemplo: `reddit_posts_YYYYMMDD_HHMMSS.json`.

## Formato de salida
Cada objeto del JSON tiene esta estructura:
```json
{
  "id": "...",
  "subreddit": "Parenting",
  "topic": "sleep",
  "title": "...",
  "selftext": "...",
  "created_utc": 1234567890,
  "created_date": "YYYY-MM-DD HH:MM:SS",
  "url": "https://www.reddit.com/..."
}
```

## Filtro de edad
El filtro actual excluye posts que mencionan edades de 9 anios o mas, ademas de referencias a adolescentes. Esto se hace con una expresion regular en `index.py`.

## Reescritura para LLM
Las instrucciones para reescritura y normalizacion de posts estan en `AGENTS.MD`.

## Notas
- Se usa un `User-Agent` fijo en el header de requests. Si vas a publicar o escalar el uso, ajusta este valor.
- La pausa entre requests es de 2 segundos para evitar sobrecargar la API.

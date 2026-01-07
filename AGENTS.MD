## Objetivo
Generar `title` y `selftext` nuevos e inspirados en los posts de Reddit
producidos por `index.py`, pero orientados a un LLM. Las preguntas deben
ser claras, autocontenidas y relevantes para un modelo (no para una comunidad).

## Alcance
- Entrada: objetos con `title` y `selftext` (y cualquier metadato adicional).
- Salida: nuevos objetos con solo `title` y `selftext`.
- Idioma de salida: igual al idioma solicitado por el flujo actual.

## Principios
- Autocontenido: no depender de contexto del subreddit o comunidad.
- Relevante para LLM: preguntas que un modelo pueda responder con sentido.
- Natural: tono humano y coherente; evitar traducciones literales raras.

## Reglas de reescritura
1) Eliminar referencias a Reddit, subreddits, usuarios, votos, "OP", hilos,
   reglas comunitarias o "en este subreddit".
2) Reemplazar menciones de "la comunidad", "aquí", "en este foro" por un
   contexto general ("en mi situación", "en mi caso", "en mi familia").
3) Convertir preguntas demasiado generales o sociales en preguntas prácticas
   para un LLM (p. ej. pedir consejos, pasos, explicaciones).
4) Mantener el significado central, pero aclarar ambigüedades.
5) Preservar saltos de línea cuando ayudan a la lectura.
6) Evitar detalles irrelevantes para el LLM (karma, moderación, flair, etc.).

## Formato de salida
JSON por objeto:
{
  "title": "<titulo claro>",
  "selftext": "<pregunta o contexto autocontenido>"
}

## Guía para generar JSON desde Reddit (posts personalizados)
- Objetivo: usar posts de Reddit como inspiración, pero producir prompts autocontenidos para un LLM.
- Selección: elegir N posts relevantes y coherentes con el tema solicitado; evitar duplicados y casos demasiado similares.
- Perfil: si se incluye un campo `profile`, debe ser coherente con la edad/etapa mencionada en `selftext` (p. ej., si dice “2 meses”, el `profile` no puede ser “5 años”).
- Reescritura: eliminar cualquier mención a Reddit o comunidades, y convertir la pregunta en una solicitud práctica que un LLM pueda responder.
- Claridad: si hay ambigüedad, resolverla en el texto final (sin inventar datos críticos).
- Salida: cada objeto debe tener solo `title` y `selftext` (y `profile` si el flujo actual lo requiere), en el idioma del flujo.
- Nota adicional: en flujos de `sleep_and_rest`, los archivos `en.json` y `pt.json` deben incluir un campo `"es"` con `{ "title": "...", "selftext": "..." }` para facilitar la revisión.

## Ejemplos
- Antes (comunidad):
  title: "Pregunta para quien esté criando (o haya criado)"
  selftext: "Hola r/Parenting, ¿a alguien más le pasa que...?"
  Después (LLM):
  title: "Consejos para manejar X durante la crianza"
  selftext: "Estoy en situación X con mi hijo/a. ¿Qué pasos prácticos
  recomiendas y por qué?"

- Antes (Reddit):
  title: "Upvotes no importan, pero..."
  selftext: "Sé que en este subreddit no se permite..."
  Después (LLM):
  title: "Necesito una guía clara para X"
  selftext: "Quiero una guía paso a paso para X, con pros y contras."

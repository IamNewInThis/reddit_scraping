# 🎯 Lumi Response Listener

Servidor listener que captura las respuestas del chat de Lumi y las envía a n8n/Google Sheets.

## 📋 Descripción

Este servicio actúa como un **webhook receiver** que:
1. ✅ Escucha las respuestas del endpoint `/api/chat` de `lumi-llm`
2. ✅ Captura solo la respuesta de Lumi
3. ✅ Reenvía los datos a n8n
4. ✅ n8n procesa y guarda en Google Sheets

## 🚀 Instalación

### 1. Instalar dependencias

```bash
cd reddit_scraping
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Edita el archivo `.env` y agrega tu webhook URL de n8n:

```env
# Configuración del Listener Server
LISTENER_PORT=5001
LISTENER_HOST=0.0.0.0

# N8N Webhook URL - IMPORTANTE: Configura esto con tu webhook de n8n
N8N_WEBHOOK_URL=https://tu-n8n.com/webhook/lumi-responses
```

### 3. Iniciar el servidor listener

```bash
python listener_server.py
```

Deberías ver:

```
============================================================
🚀 Listener Server Starting on http://0.0.0.0:5001
============================================================

📋 Endpoints disponibles:
   • GET  /health                  - Health check
   • POST /webhook/chat-response   - Recibe respuestas de Lumi
   • POST /test                    - Endpoint de prueba

============================================================
```

## 🔧 Configuración de lumi-llm

Para que `lumi-llm` envíe las respuestas al listener, necesitas:

### 1. Copiar el servicio de webhook

Copia el archivo `webhook_service_example.py` a `lumi-llm`:

```bash
cp webhook_service_example.py ../lumi-llm/src/services/webhook_service.py
```

### 2. Agregar variables de entorno a lumi-llm

Edita `lumi-llm/.env` y agrega:

```env
# Webhook Configuration
ENABLE_WEBHOOKS=true
LISTENER_WEBHOOK_URL=http://localhost:5001/webhook/chat-response
WEBHOOK_TIMEOUT=5
```

### 3. Modificar el endpoint /api/chat

En `lumi-llm/src/routes/chat.py`, agrega:

```python
from ..services.webhook_service import send_chat_response_to_listener

@router.post("/api/chat")
async def chat_openai(payload: ChatRequest, user=Depends(get_current_user)):
    """
    Endpoint principal de chat. Delega toda la lógica a chat_service.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="message required")
    
    try:
        result = await process_chat(payload, user)
        
        # 🔥 NUEVO: Enviar respuesta al listener (asíncrono, no bloquea)
        if result.get('response'):
            await send_chat_response_to_listener(
                user_id=user.get('id'),
                baby_id=payload.baby_id,
                message=payload.message,
                response=result['response'],
                session_id=payload.session_id
            )
        
        return result
    except Exception as e:
        print(f"❌ Error en chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 🧪 Testing

### Test 1: Verificar que el listener está corriendo

```bash
curl http://localhost:5001/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "service": "lumi-listener",
  "timestamp": "2026-01-08T10:30:00",
  "n8n_configured": true
}
```

### Test 2: Enviar datos de prueba

```bash
curl -X POST http://localhost:5001/test \
  -H "Content-Type: application/json" \
  -d '{
    "test": "hola mundo"
  }'
```

### Test 3: Simular respuesta de Lumi

```bash
curl -X POST http://localhost:5001/webhook/chat-response \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-08T10:30:00",
    "user_id": "test-user-123",
    "baby_id": "test-baby-456",
    "message": "¿Cómo hacer que mi bebé duerma mejor?",
    "response": "Para mejorar el sueño de tu bebé, te recomiendo establecer una rutina nocturna consistente...",
    "session_id": "session-789"
  }'
```

## 📊 Configuración de n8n

### Crear el workflow en n8n:

1. **Webhook Node** (Trigger)
   - Method: POST
   - Path: `/webhook/lumi-responses`
   - Authentication: None (o Basic Auth si prefieres)

2. **Set Node** (Opcional - Procesar datos)
   - Extraer campos que necesites
   - Formatear timestamp

3. **Google Sheets Node**
   - Operation: Append
   - Mapear campos:
     - `timestamp` → Columna A
     - `lumi_response` → Columna B
     - `user_id` → Columna C (opcional)
     - `baby_id` → Columna D (opcional)

### URL del webhook:
Copia la URL del webhook de n8n y pégala en el `.env`:

```env
N8N_WEBHOOK_URL=https://tu-n8n.com/webhook-test/lumi-responses
```

## 📁 Estructura de datos enviados

El listener envía este payload a n8n:

```json
{
  "timestamp": "2026-01-08T10:30:00.123456",
  "lumi_response": "Respuesta completa de Lumi aquí...",
  "user_id": "uuid-del-usuario",
  "baby_id": "uuid-del-bebe",
  "session_id": "session-uuid",
  "user_message": "Mensaje original del usuario"
}
```

## 🔒 Seguridad

Si deseas agregar autenticación al listener:

1. Genera un token secreto
2. Agrégalo al `.env`:
```env
WEBHOOK_SECRET_TOKEN=tu-token-super-secreto
```

3. Modifica `listener_server.py` para validar el token en los headers

## 🐛 Troubleshooting

### El listener no recibe datos

1. Verifica que `lumi-llm` tenga configurado `ENABLE_WEBHOOKS=true`
2. Verifica que `LISTENER_WEBHOOK_URL` apunte a `http://localhost:5001/webhook/chat-response`
3. Revisa los logs de ambos servidores

### n8n no recibe los datos

1. Verifica que `N8N_WEBHOOK_URL` esté correctamente configurada
2. Prueba la URL con curl:
```bash
curl -X POST https://tu-n8n.com/webhook/lumi-responses \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Timeout errors

Aumenta el timeout en `lumi-llm/.env`:
```env
WEBHOOK_TIMEOUT=10
```

## 📝 Logs

El listener imprime logs detallados:

```
📨 [LISTENER] Respuesta recibida:
   ⏰ Timestamp: 2026-01-08T10:30:00
   👤 User ID: abc-123
   👶 Baby ID: def-456
   💬 Response: Para mejorar el sueño de tu bebé...

📤 [LISTENER] Enviando a n8n...
✅ [LISTENER] Enviado exitosamente a n8n
```

## 🚀 Producción

Para producción, considera usar:

- **Gunicorn** para servir la app Flask
- **Nginx** como reverse proxy
- **Systemd** para mantener el servicio corriendo
- **Docker** para containerización

Ejemplo con Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 listener_server:app
```

## 📞 Soporte

Si tienes problemas, revisa:
1. Logs del listener server
2. Logs de lumi-llm
3. Logs de n8n
4. Conexión de red entre servicios

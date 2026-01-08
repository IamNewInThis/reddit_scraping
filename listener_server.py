"""
Listener Server para capturar respuestas de Lumi y enviarlas a n8n/Google Sheets

Este servidor escucha las respuestas del endpoint /api/chat de lumi-llm
y las reenvía a n8n para su procesamiento y almacenamiento en Google Sheets.
"""

from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración desde .env
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
LISTENER_PORT = int(os.getenv('LISTENER_PORT', 5001))
LISTENER_HOST = os.getenv('LISTENER_HOST', '0.0.0.0')

# Log de configuración
print(f"🎯 Listener Server Iniciando...")
print(f"📍 Puerto: {LISTENER_PORT}")
print(f"🔗 N8N Webhook: {N8N_WEBHOOK_URL if N8N_WEBHOOK_URL else '❌ NO CONFIGURADO'}")


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({
        "status": "healthy",
        "service": "lumi-listener",
        "timestamp": datetime.now().isoformat(),
        "n8n_configured": bool(N8N_WEBHOOK_URL)
    }), 200


@app.route('/webhook/chat-response', methods=['POST'])
def receive_chat_response():
    """
    Recibe las respuestas del chat de Lumi y las procesa.
    
    Payload esperado:
    {
        "timestamp": "2026-01-08T10:30:00",
        "user_id": "uuid",
        "baby_id": "uuid", 
        "message": "mensaje del usuario",
        "response": "respuesta de Lumi",
        "session_id": "session_uuid"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Log de recepción
        print(f"\n📨 [LISTENER] Respuesta recibida:")
        print(f"   ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"   📩 User Message: {data.get('user_message', 'N/A')[:100]}...")
        
        # Extraer respuesta de Lumi y mensaje del usuario
        lumi_response = data.get('lumi_response', '')
        user_message = data.get('user_message', '')
        
        if not lumi_response:
            print("⚠️  [LISTENER] No se encontró respuesta de Lumi")
            print(f"   Datos recibidos: {list(data.keys())}")
            return jsonify({"error": "No lumi_response found"}), 400
        
        print(f"   💬 Lumi Response: {lumi_response[:100]}...")
        
        # Preparar payload para n8n (timestamp, mensaje usuario y respuesta Lumi)
        n8n_payload = {
            "timestamp": data.get('timestamp', datetime.now().isoformat()),
            "user_message": user_message,
            "lumi_response": lumi_response
        }
        
        # Enviar a n8n si está configurado
        if N8N_WEBHOOK_URL:
            try:
                print(f"📤 [LISTENER] Enviando a n8n...")
                response = requests.post(
                    N8N_WEBHOOK_URL,
                    json=n8n_payload,
                    timeout=10,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code in [200, 201]:
                    print(f"✅ [LISTENER] Enviado exitosamente a n8n")
                    return jsonify({
                        "success": True,
                        "message": "Data sent to n8n successfully",
                        "n8n_status": response.status_code
                    }), 200
                else:
                    print(f"⚠️  [LISTENER] n8n respondió con status {response.status_code}")
                    return jsonify({
                        "success": False,
                        "message": f"n8n responded with status {response.status_code}",
                        "n8n_response": response.text
                    }), 500
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ [LISTENER] Error enviando a n8n: {e}")
                return jsonify({
                    "success": False,
                    "message": f"Error sending to n8n: {str(e)}"
                }), 500
        else:
            # Si no hay webhook configurado, solo loguear
            print(f"⚠️  [LISTENER] N8N_WEBHOOK_URL no configurado. Datos recibidos:")
            print(json.dumps(n8n_payload, indent=2, ensure_ascii=False))
            return jsonify({
                "success": True,
                "message": "Data received but n8n webhook not configured",
                "data": n8n_payload
            }), 200
            
    except Exception as e:
        print(f"❌ [LISTENER] Error procesando webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/test', methods=['POST'])
def test_endpoint():
    """Endpoint de prueba para verificar que el listener funciona"""
    data = request.get_json()
    print(f"🧪 [TEST] Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
    return jsonify({
        "success": True,
        "message": "Test successful",
        "received_data": data
    }), 200


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🚀 Listener Server Starting on http://{LISTENER_HOST}:{LISTENER_PORT}")
    print(f"{'='*60}\n")
    print(f"📋 Endpoints disponibles:")
    print(f"   • GET  /health                  - Health check")
    print(f"   • POST /webhook/chat-response   - Recibe respuestas de Lumi")
    print(f"   • POST /test                    - Endpoint de prueba")
    print(f"\n{'='*60}\n")
    
    app.run(
        host=LISTENER_HOST,
        port=LISTENER_PORT,
        debug=True
    )

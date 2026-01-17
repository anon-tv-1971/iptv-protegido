#!/usr/bin/env python3
"""
🎬 SERVIDOR IPTV COMPLETO - Render + Televizo
Versión funcional con autenticación y rutas completas
"""

import os
import random
import hashlib
from datetime import datetime
from flask import Flask, Response, jsonify, render_template_string, send_from_directory
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

app = Flask(__name__)
auth = HTTPBasicAuth()

# 🔐 CREDENCIALES FIJAS (más fácil para pruebas)
USUARIO = "anon"
CONTRASEÑA = "tv1971"

USERS = {
    USUARIO: generate_password_hash(CONTRASEÑA)
}

# 📁 CARPETA DE LISTAS
PLAYLISTS_FOLDER = "playlists"
os.makedirs(PLAYLISTS_FOLDER, exist_ok=True)

# ============================================================================
# AUTENTICACIÓN
# ============================================================================

@auth.verify_password
def verify_password(username, password):
    """Verificación de credenciales"""
    if username in USERS and check_password_hash(USERS.get(username), password):
        return username
    return None

def generar_id_unico(nombre_archivo):
    """Genera ID único para cada archivo"""
    return hashlib.md5(nombre_archivo.encode()).hexdigest()[:10]

def get_playlists_info():
    """Obtiene información de todas las listas"""
    archivos = []
    
    if not os.path.exists(PLAYLISTS_FOLDER):
        return archivos
    
    for filename in sorted(os.listdir(PLAYLISTS_FOLDER)):
        if filename.lower().endswith('.m3u8'):
            filepath = os.path.join(PLAYLISTS_FOLDER, filename)
            
            try:
                # Tamaño
                size = os.path.getsize(filepath)
                
                # Contar canales
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    channels = content.count('#EXTINF:')
                
                # ID único
                file_id = generar_id_unico(filename)
                
                archivos.append({
                    'nombre': filename,
                    'id': file_id,
                    'tamano_mb': round(size / (1024 * 1024), 2),
                    'canales': channels,
                    'url_protegida': f"/stream/{file_id}/playlist",
                    'url_directa': f"/direct/{filename}",
                    'url_simple': f"/playlists/{filename}",
                    'modificado': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%d/%m %H:%M")
                })
            except Exception as e:
                print(f"⚠️ Error con {filename}: {e}")
    
    return archivos

# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
@auth.login_required
def index():
    """Página principal"""
    playlists = get_playlists_info()
    total_canales = sum(p['canales'] for p in playlists)
    total_tamano = sum(p['tamano_mb'] for p in playlists)
    
    # URL base
    base_url = "https://" + os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'tu-app.onrender.com')
    
    html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎬 IPTV Server</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #0f172a; color: #e2e8f0;
                min-height: 100vh; padding: 20px; line-height: 1.6;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                padding: 30px; border-radius: 15px; text-align: center;
                margin-bottom: 30px; box-shadow: 0 10px 30px rgba(30, 64, 175, 0.3);
            }}
            .header h1 {{ font-size: 2rem; margin-bottom: 10px; color: white; }}
            .stats-grid {{
                display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px; margin-bottom: 30px;
            }}
            .stat-card {{
                background: rgba(30, 41, 59, 0.8); padding: 20px;
                border-radius: 10px; text-align: center; border: 1px solid #334155;
            }}
            .stat-number {{ font-size: 2rem; font-weight: bold; color: #60a5fa; }}
            .stat-label {{ font-size: 0.9rem; color: #94a3b8; }}
            .playlists-grid {{
                display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px; margin-bottom: 30px;
            }}
            .playlist-card {{
                background: rgba(30, 41, 59, 0.9); padding: 20px;
                border-radius: 10px; border: 1px solid #334155;
            }}
            .playlist-name {{ font-size: 1.2rem; font-weight: bold; color: #e2e8f0; }}
            .btn {{
                display: block; width: 100%; padding: 10px; margin: 10px 0;
                background: #3b82f6; color: white; border: none; border-radius: 5px;
                text-decoration: none; text-align: center; cursor: pointer;
            }}
            .btn:hover {{ background: #2563eb; }}
            .url-box {{
                background: #0f172a; border: 1px solid #334155; border-radius: 5px;
                padding: 10px; font-family: monospace; color: #60a5fa;
                word-break: break-all; margin: 10px 0; font-size: 0.9rem;
            }}
            .credentials {{
                background: rgba(30, 41, 59, 0.8); padding: 15px;
                border-radius: 10px; margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎬 IPTV Server</h1>
                <p>Servidor funcional para Televizo y apps IPTV</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(playlists)}</div>
                    <div class="stat-label">Listas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_canales}</div>
                    <div class="stat-label">Canales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_tamano:.1f}</div>
                    <div class="stat-label">MB</div>
                </div>
            </div>
    '''
    
    if playlists:
        for playlist in playlists:
            simple_url = f"{base_url}/playlists/{playlist['nombre']}"
            
            html += f'''
            <div class="playlist-card">
                <div class="playlist-name">📺 {playlist['nombre']}</div>
                <div style="color: #94a3b8; font-size: 0.9rem; margin: 10px 0;">
                    Canales: {playlist['canales']} | Tamaño: {playlist['tamano_mb']} MB
                </div>
                
                <div class="url-box" id="url_{playlist['id']}">
                    {simple_url}
                </div>
                
                <a href="{playlist['url_simple']}" class="btn">
                    🔗 URL para Televizo
                </a>
                <button onclick="copyToClipboard('{playlist['id']}')" class="btn">
                    📋 Copiar URL
                </button>
            </div>
            '''
    else:
        html += '''
            <div style="text-align: center; padding: 40px 20px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">📂</div>
                <h3 style="color: #94a3b8;">No hay listas disponibles</h3>
                <p style="color: #64748b;">Sube archivos .m3u8 a la carpeta playlists/</p>
            </div>
        '''
    
    html += f'''
            <div class="credentials">
                <h3 style="color: #60a5fa; margin-bottom: 15px;">🔐 Credenciales:</h3>
                <p><strong>Usuario:</strong> <code>{USUARIO}</code></p>
                <p><strong>Contraseña:</strong> <code>{CONTRASEÑA}</code></p>
                <p style="margin-top: 15px; color: #94a3b8; font-size: 0.9rem;">
                    Para Televizo: usa la URL simple (no requiere auth en esta versión)
                </p>
            </div>
            
            <script>
                function copyToClipboard(playlistId) {{
                    const urlBox = document.getElementById(`url_${{playlistId}}`);
                    const url = urlBox.textContent.trim();
                    navigator.clipboard.writeText(url)
                        .then(() => alert('✅ URL copiada'))
                        .catch(err => alert('❌ Error: ' + err));
                }}
            </script>
        </div>
    </body>
    </html>
    '''
    
    return html

# ============================================================================
# RUTAS PARA SERVIR ARCHIVOS M3U8 (¡IMPORTANTE!)
# ============================================================================

@app.route('/stream/<file_id>/playlist')
@auth.login_required
def stream_playlist(file_id):
    """Sirve archivo por ID (con auth)"""
    if os.path.exists(PLAYLISTS_FOLDER):
        for filename in os.listdir(PLAYLISTS_FOLDER):
            if filename.lower().endswith('.m3u8'):
                current_id = generar_id_unico(filename)
                if current_id == file_id:
                    return serve_m3u8_file(filename)
    return jsonify({'error': 'No encontrado'}), 404

@app.route('/direct/<filename>')
@auth.login_required
def direct_playlist(filename):
    """Sirve archivo por nombre (con auth)"""
    return serve_m3u8_file(filename)

@app.route('/raw/<filename>')
def raw_playlist(filename):
    """Sirve archivo SIN autenticación"""
    return serve_m3u8_file(filename)

@app.route('/playlists/<filename>')
def simple_playlist(filename):
    """Ruta SIMPLE para Televizo (sin auth)"""
    return serve_m3u8_file(filename)

def serve_m3u8_file(filename):
    """Función común para servir archivos M3U8"""
    if '..' in filename or filename.startswith('/'):
        return jsonify({'error': 'Nombre inválido'}), 400
    
    filepath = os.path.join(PLAYLISTS_FOLDER, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'Archivo no encontrado'}), 404
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        response = Response(content, mimetype='application/vnd.apple.mpegurl')
        response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Access-Control-Allow-Origin'] = '*'
        
        return response
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Endpoint de salud"""
    playlists_count = len([f for f in os.listdir(PLAYLISTS_FOLDER) 
                          if f.endswith('.m3u8')]) if os.path.exists(PLAYLISTS_FOLDER) else 0
    
    return jsonify({
        'status': 'ok',
        'service': 'IPTV Server',
        'version': '2.0',
        'playlists': playlists_count,
        'timestamp': datetime.now().isoformat()
    })

# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🎬 Servidor IPTV iniciando en puerto {port}")
    print(f"🔐 Credenciales: {USUARIO}:{CONTRASEÑA}")
    print(f"📁 Listas en: {PLAYLISTS_FOLDER}/")
    app.run(host='0.0.0.0', port=port, debug=False)
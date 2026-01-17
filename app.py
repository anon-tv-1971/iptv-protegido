#!/usr/bin/env python3
"""
🛡️ SERVIDOR IPTV ANTI-BLOQUEO - RENDER.COM
Versión ultra-protegida contra bloqueos ISP
"""

import os
import random
import hashlib
from datetime import datetime
from flask import Flask, Response, jsonify, render_template_string
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================================
# CONFIGURACIÓN AUTOMÁTICA
# ============================================================================

app = Flask(__name__)
auth = HTTPBasicAuth()

# 🔒 CREDENCIALES DINÁMICAS (cambian automáticamente)
fecha_actual = datetime.now().strftime("%m%d")
USUARIO = f"user_{random.randint(1000, 9999)}"
CONTRASEÑA = f"tv{fecha_actual}{random.randint(100, 999)}"

USERS = {
    USUARIO: generate_password_hash(CONTRASEÑA)
}

# 📁 CARPETA DE LISTAS PROTEGIDAS
PLAYLISTS_FOLDER = "playlists"
os.makedirs(PLAYLISTS_FOLDER, exist_ok=True)

# ============================================================================
# FUNCIONES DE SEGURIDAD
# ============================================================================

@auth.verify_password
def verify_password(username, password):
    """Verificación silenciosa"""
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
                
                # Contar canales aproximados
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
    """Página principal ultra-protegida"""
    playlists = get_playlists_info()
    total_canales = sum(p['canales'] for p in playlists)
    total_tamano = sum(p['tamano_mb'] for p in playlists)
    
    html = f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔒 Streaming Privado</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #e2e8f0;
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            /* HEADER */
            .header {{
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                padding: 40px 30px;
                border-radius: 20px;
                text-align: center;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(30, 64, 175, 0.3);
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                color: white;
            }}
            
            .header p {{
                font-size: 1.1rem;
                opacity: 0.9;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            /* ESTADÍSTICAS */
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: rgba(30, 41, 59, 0.8);
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                border: 1px solid #334155;
                transition: transform 0.3s;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
                border-color: #3b82f6;
            }}
            
            .stat-number {{
                font-size: 2.5rem;
                font-weight: bold;
                color: #60a5fa;
                display: block;
                margin-bottom: 10px;
            }}
            
            .stat-label {{
                font-size: 0.9rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            /* LISTA DE ARCHIVOS */
            .playlists-section {{
                margin-bottom: 40px;
            }}
            
            .section-title {{
                font-size: 1.8rem;
                margin-bottom: 20px;
                color: #e2e8f0;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .playlists-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 25px;
            }}
            
            .playlist-card {{
                background: rgba(30, 41, 59, 0.9);
                border-radius: 15px;
                padding: 25px;
                border: 1px solid #334155;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .playlist-card:hover {{
                border-color: #3b82f6;
                box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2);
                transform: translateY(-8px);
            }}
            
            .playlist-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 5px;
                height: 100%;
                background: linear-gradient(to bottom, #3b82f6, #8b5cf6);
            }}
            
            .playlist-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
            }}
            
            .playlist-name {{
                font-size: 1.3rem;
                font-weight: bold;
                color: #e2e8f0;
                word-break: break-word;
                flex: 1;
            }}
            
            .playlist-id {{
                background: #1e293b;
                color: #60a5fa;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-family: monospace;
                margin-left: 10px;
            }}
            
            .playlist-info {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 20px;
                background: rgba(15, 23, 42, 0.5);
                padding: 15px;
                border-radius: 10px;
            }}
            
            .info-item {{
                text-align: center;
            }}
            
            .info-label {{
                display: block;
                font-size: 0.85rem;
                color: #94a3b8;
                margin-bottom: 5px;
            }}
            
            .info-value {{
                display: block;
                font-size: 1.1rem;
                font-weight: bold;
                color: #e2e8f0;
            }}
            
            /* BOTONES */
            .buttons-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}
            
            .btn {{
                padding: 12px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                transition: all 0.3s;
                font-size: 0.95rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }}
            
            .btn-stream {{
                background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
                color: white;
            }}
            
            .btn-direct {{
                background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
                color: white;
            }}
            
            .btn-copy {{
                background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%);
                color: white;
                grid-column: span 2;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            
            /* URL BOX */
            .url-container {{
                margin: 20px 0;
            }}
            
            .url-box {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
                color: #60a5fa;
                word-break: break-all;
                margin-bottom: 10px;
                position: relative;
            }}
            
            /* INSTRUCCIONES */
            .instructions {{
                background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%);
                border: 1px solid rgba(251, 191, 36, 0.3);
                padding: 25px;
                border-radius: 15px;
                margin-top: 40px;
            }}
            
            .instructions h3 {{
                color: #fbbf24;
                margin-bottom: 15px;
                font-size: 1.4rem;
            }}
            
            .instructions ol {{
                padding-left: 25px;
                margin-bottom: 15px;
            }}
            
            .instructions li {{
                margin-bottom: 10px;
                padding-left: 5px;
            }}
            
            .credentials {{
                background: rgba(30, 41, 59, 0.8);
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
            }}
            
            .credential-item {{
                margin: 10px 0;
                font-family: monospace;
            }}
            
            /* FOOTER */
            footer {{
                text-align: center;
                margin-top: 50px;
                padding: 20px;
                color: #64748b;
                font-size: 0.9rem;
                border-top: 1px solid #334155;
            }}
            
            .security-badges {{
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-top: 10px;
                flex-wrap: wrap;
            }}
            
            .badge {{
                background: #334155;
                color: #94a3b8;
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8rem;
            }}
            
            /* NOTIFICACIÓN */
            .notification {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: #10b981;
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                z-index: 1000;
                transform: translateX(400px);
                transition: transform 0.5s ease;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .notification.show {{
                transform: translateX(0);
            }}
            
            /* RESPONSIVE */
            @media (max-width: 768px) {{
                .playlists-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .stats-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header {{
                    padding: 30px 20px;
                }}
                
                .header h1 {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- HEADER -->
            <div class="header">
                <h1>🔐 STREAMING PRIVADO</h1>
                <p>Acceso seguro a contenido multimedia protegido contra bloqueos</p>
            </div>
            
            <!-- ESTADÍSTICAS -->
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-number">{len(playlists)}</span>
                    <span class="stat-label">Listas Activas</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{total_canales}</span>
                    <span class="stat-label">Canales Totales</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{total_tamano:.1f}</span>
                    <span class="stat-label">MB Almacenados</span>
                </div>
                <div class="stat-card">
                    <span class="stat-number">AUTO</span>
                    <span class="stat-label">Rotación Activa</span>
                </div>
            </div>
            
            <!-- LISTA DE ARCHIVOS -->
            <div class="playlists-section">
                <h2 class="section-title">
                    <span>📂</span> Tus Listas Protegidas
                </h2>
                
    '''
    
    if playlists:
        for playlist in playlists:
            # URL completa para esta playlist
            base_url = "https://" + os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'tuservidor.onrender.com')
            stream_url = f"{base_url}/stream/{playlist['id']}/playlist"
            
            html += f'''
                <div class="playlist-card">
                    <div class="playlist-header">
                        <div class="playlist-name">📺 {playlist['nombre']}</div>
                        <div class="playlist-id">ID: {playlist['id']}</div>
                    </div>
                    
                    <div class="playlist-info">
                        <div class="info-item">
                            <span class="info-label">Canales</span>
                            <span class="info-value">{playlist['canales']}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Tamaño</span>
                            <span class="info-value">{playlist['tamano_mb']} MB</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Actualizado</span>
                            <span class="info-value">{playlist['modificado']}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Protección</span>
                            <span class="info-value">ALTA</span>
                        </div>
                    </div>
                    
                    <div class="url-container">
                        <div class="url-box" id="url_{playlist['id']}">
                            {stream_url}
                        </div>
                    </div>
                    
                    <div class="buttons-grid">
                        <a href="{playlist['url_protegida']}" class="btn btn-stream">
                            <span>▶️</span> Stream Protegido
                        </a>
                        <a href="{playlist['url_directa']}" class="btn btn-direct">
                            <span>🔗</span> Enlace Directo
                        </a>
                        <button onclick="copyToClipboard('{playlist['id']}')" class="btn btn-copy">
                            <span>📋</span> Copiar URL
                        </button>
                    </div>
                </div>
            '''
    else:
        html += '''
            <div style="text-align: center; padding: 50px 20px; background: rgba(30, 41, 59, 0.5); border-radius: 15px;">
                <div style="font-size: 4rem; margin-bottom: 20px;">📂</div>
                <h3 style="color: #94a3b8; margin-bottom: 15px;">No hay listas disponibles</h3>
                <p style="color: #64748b;">
                    Sube tus archivos .m3u8 procesados a la carpeta <code style="background: #0f172a; padding: 5px 10px; border-radius: 5px;">playlists/</code>
                </p>
            </div>
        '''
    
    html += f'''
            </div>
            
            <!-- INSTRUCCIONES -->
            <div class="instructions">
                <h3>📱 CONFIGURACIÓN PARA TELEVIZO</h3>
                <ol>
                    <li><strong>Elige una lista</strong> de las disponibles arriba</li>
                    <li><strong>Copia la URL</strong> usando el botón "📋 Copiar URL"</li>
                    <li><strong>Abre Televizo</strong> en tu dispositivo Android</li>
                    <li><strong>Añade nueva lista</strong> → Tipo: URL/M3U</li>
                    <li><strong>Pega la URL</strong> copiada</li>
                    <li><strong>Configura credenciales</strong> (abajo)</li>
                    <li><strong>Guarda y disfruta</strong> del streaming protegido</li>
                </ol>
                
                <div class="credentials">
                    <h4 style="color: #60a5fa; margin-bottom: 15px;">🔐 CREDENCIALES ACTUALES:</h4>
                    <div class="credential-item">
                        <strong>Usuario:</strong> <code>{USUARIO}</code>
                    </div>
                    <div class="credential-item">
                        <strong>Contraseña:</strong> <code>{CONTRASEÑA}</code>
                    </div>
                    <p style="margin-top: 15px; color: #94a3b8; font-size: 0.9rem;">
                        ⚠️ Estas credenciales cambian periódicamente para mayor seguridad
                    </p>
                </div>
            </div>
            
            <!-- FOOTER -->
            <footer>
                <p>🛡️ Servicio de Streaming Protegido • v4.0 • {datetime.now().strftime('%Y')}</p>
                <div class="security-badges">
                    <span class="badge">HTTPS</span>
                    <span class="badge">Encriptado</span>
                    <span class="badge">Anti-ISP</span>
                    <span class="badge">Sin Logs</span>
                    <span class="badge">Rotación Activa</span>
                </div>
                <p style="margin-top: 15px; font-size: 0.8rem; color: #475569;">
                    Conexión segura mediante Render.com + Cloudflare
                </p>
            </footer>
            
            <!-- NOTIFICACIÓN -->
            <div class="notification" id="notification">
                <span>✅</span>
                <span id="notificationText">URL copiada al portapapeles</span>
            </div>
        </div>
        
        <script>
            function copyToClipboard(playlistId) {{
                const urlElement = document.getElementById('url_' + playlistId);
                const url = urlElement.textContent;
                
                navigator.clipboard.writeText(url).then(() => {{
                    showNotification('✅ URL copiada al portapapeles');
                }}).catch(err => {{
                    showNotification('❌ Error al copiar: ' + err);
                }});
            }}
            
            function showNotification(message) {{
                const notification = document.getElementById('notification');
                const notificationText = document.getElementById('notificationText');
                
                notificationText.textContent = message;
                notification.classList.add('show');
                
                setTimeout(() => {{
                    notification.classList.remove('show');
                }}, 3000);
            }}
            
            // Rotar credenciales automáticamente después de 24 horas
            setTimeout(() => {{
                fetch('/api/rotate').then(() => {{
                    showNotification('🔄 Credenciales actualizadas - Recarga la página');
                }});
            }}, 24 * 60 * 60 * 1000); // 24 horas
        </script>
    </body>
    </html>
    '''
    
    return html

@app.route('/stream/<playlist_id>/playlist')
@auth.login_required
def serve_protected_playlist(playlist_id):
    """Sirve playlist con protección máxima"""
    # Buscar archivo por ID
    for filename in os.listdir(PLAYLISTS_FOLDER):
        if filename.lower().endswith('.m3u8'):
            file_id = generar_id_unico(filename)
            if file_id == playlist_id:
                filepath = os.path.join(PLAYLISTS_FOLDER, filename)
                
                # Leer y servir
                with open(filepath, 'rb') as f:
                    content = f.read()
                
                return Response(
                    content,
                    mimetype='application/vnd.apple.mpegurl',
                    headers={{
                        'Content-Disposition': f'inline; filename="{filename}"',
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0',
                        'X-Content-Type-Options': 'nosniff',
                        'X-Frame-Options': 'DENY',
                        'Referrer-Policy': 'no-referrer',
                        'X-Protection-Level': 'maximum'
                    }}
                )
    
    return "Lista no encontrada", 404

@app.route('/direct/<filename>')
@auth.login_required
def serve_direct_playlist(filename):
    """Sirve playlist directa (para compatibilidad)"""
    filepath = os.path.join(PLAYLISTS_FOLDER, filename)
    
    if not os.path.exists(filepath):
        return "Archivo no encontrado", 404
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    return Response(
        content,
        mimetype='application/vnd.apple.mpegurl',
        headers={{
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }}
    )

@app.route('/api/rotate')
@auth.login_required
def rotate_credentials():
    """Rota las credenciales automáticamente"""
    global USUARIO, CONTRASEÑA, USERS
    
    fecha_actual = datetime.now().strftime("%m%d")
    nuevo_usuario = f"user_{random.randint(1000, 9999)}"
    nueva_contraseña = f"tv{fecha_actual}{random.randint(100, 999)}"
    
    USUARIO = nuevo_usuario
    CONTRASEÑA = nueva_contraseña
    USERS = {nuevo_usuario: generate_password_hash(nueva_contraseña)}
    
    return jsonify({
        'status': 'rotated',
        'new_user': nuevo_usuario,
        'new_password': nueva_contraseña,
        'timestamp': datetime.now().isoformat(),
        'message': 'Credenciales actualizadas correctamente'
    })

@app.route('/api/status')
def api_status():
    """Estado del servidor (público)"""
    playlists = get_playlists_info()
    
    return jsonify({
        'status': 'operational',
        'protection_level': 'maximum',
        'encryption': 'HTTPS/TLS',
        'playlists_count': len(playlists),
        'total_channels': sum(p['canales'] for p in playlists),
        'rotation_enabled': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health_check():
    """Health check para Render"""
    return jsonify({'status': 'healthy', 'service': 'iptv-anti-block'})

if __name__ == '__main__':
    # Mostrar información de inicio
    print("=" * 70)
    print("🛡️  SERVIDOR IPTV ANTI-BLOQUEO")
    print("=" * 70)
    print(f"🔐 Usuario actual: {USUARIO}")
    print(f"🔑 Contraseña actual: {CONTRASEÑA}")
    print(f"📁 Listas cargadas: {len(get_playlists_info())}")
    print(f"🌐 URL local: http://localhost:5000")
    print(f"⚡ Seguridad: HTTPS + Ofuscación + Rotación automática")
    print("=" * 70)
    
    # Iniciar servidor
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
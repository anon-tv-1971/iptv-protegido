#!/usr/bin/env python3
"""
🔥 PROCESADOR ANTI-BLOQUEO ISP
Convierte listas M3U8 normales en ultra-protegidas
"""

import os
import re
import random
import hashlib
from datetime import datetime
import sys

def ofuscar_url_streaming(url_original):
    """
    Convierte URLs sospechosas en URLs normales
    """
    url = url_original
    
    # 🔥 PASO 1: Eliminar parámetros peligrosos
    if '?' in url:
        base, query = url.split('?', 1)
        
        # Convertir parámetros a nombres genéricos
        query = query.replace('username=', 'u=')
        query = query.replace('password=', 'p=')
        query = query.replace('token=', 't=')
        query = query.replace('id=', 'i=')
        query = query.replace('type=', 'f=')
        query = query.replace('output=', 'o=')
        
        # Eliminar parámetros específicos
        parametros_peligrosos = ['token', 'signature', 'secret', 'key', 'mac']
        for param in parametros_peligrosos:
            query = re.sub(f'{param}=[^&]*&?', '', query)
        
        url = base + '?' + query if query else base
    
    # 🔥 PASO 2: Cambiar extensiones sospechosas
    reemplazos = {
        '.php': '.json',
        '.ts': '.vid',
        '.m3u8': '.stream',
        'get.php': 'data.json',
        'live/': 'video/',
        'stream/': 'media/'
    }
    
    for viejo, nuevo in reemplazos.items():
        url = url.replace(viejo, nuevo)
    
    # 🔥 PASO 3: Cambiar dominios conocidos
    dominios_iptv = ['iptv', 'stream', 'live', 'tvserver', 'm3u']
    for dominio in dominios_iptv:
        if dominio in url:
            # Reemplazar con algo genérico
            url = url.replace(dominio, 'media')
    
    # 🔥 PASO 4: Añadir parámetros anti-cache
    timestamp = int(datetime.now().timestamp())
    random_num = random.randint(1000, 9999)
    
    if '?' in url:
        url += f"&_t={timestamp}&_r={random_num}"
    else:
        url += f"?_t={timestamp}&_r={random_num}"
    
    return url

def procesar_lista_m3u8(archivo_entrada, archivo_salida):
    """
    Procesa un archivo M3U8 para hacerlo anti-bloqueo
    """
    print(f"🔄 Procesando: {os.path.basename(archivo_entrada)}")
    
    with open(archivo_entrada, 'r', encoding='utf-8', errors='ignore') as f:
        lineas = f.readlines()
    
    resultado = []
    canal_numero = 1
    urls_procesadas = {}
    
    # Asegurar cabecera M3U
    resultado.append("#EXTM3U\n")
    resultado.append("#EXT-X-VERSION:3\n")
    
    i = 0
    while i < len(lineas):
        linea = lineas[i].strip()
        
        # 🔥 LÍNEA #EXTINF: - Limpiar METADATOS
        if linea.startswith("#EXTINF:"):
            # Eliminar TODO metadata
            linea_limpia = re.sub(r'tvg-[^=]*="[^"]*"', '', linea)
            linea_limpia = re.sub(r'group-title="[^"]*"', '', linea_limpia)
            linea_limpia = re.sub(r'parent-code="[^"]*"', '', linea_limpia)
            linea_limpia = re.sub(r'audio-track="[^"]*"', '', linea_limpia)
            linea_limpia = re.sub(r'\s+', ' ', linea_limpia).strip()
            
            # Asegurar formato correcto
            if not linea_limpia.endswith(','):
                if 'tvg' in linea or 'group' in linea:
                    # Quedó sin coma, añadir
                    linea_limpia = "#EXTINF:-1,"
                else:
                    # Mantener lo que haya
                    pass
            
            # 🔥 NOMBRE GENÉRICO
            nombre_generico = f"Canal {canal_numero:03d}"
            linea_final = f"{linea_limpia}{nombre_generico}"
            
            # 🔥 BUSCAR URL SIGUIENTE
            if i + 1 < len(lineas):
                url_line = lineas[i + 1].strip()
                
                if url_line and '://' in url_line:
                    # Ofuscar URL
                    if url_line in urls_procesadas:
                        url_ofuscada = urls_procesadas[url_line]
                    else:
                        url_ofuscada = ofuscar_url_streaming(url_line)
                        urls_procesadas[url_line] = url_ofuscada
                    
                    # Añadir a resultado
                    resultado.append(linea_final + "\n")
                    resultado.append(url_ofuscada + "\n")
                    
                    canal_numero += 1
                    i += 1  # Saltar línea URL
        
        i += 1
    
    # 🔥 AÑADIR METADATOS DE SEGURIDAD
    resultado.append("#EXT-X-ENDLIST\n")
    resultado.append(f"# Procesado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    resultado.append("# Protection: Anti-ISP v3.0\n")
    
    # 🔥 GUARDAR
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.writelines(resultado)
    
    print(f"✅ Guardado: {os.path.basename(archivo_salida)}")
    print(f"   Canales: {canal_numero-1}")
    
    return canal_numero - 1

def procesar_carpeta_completa():
    """
    Procesa TODOS los archivos .m3u8 de una carpeta
    """
    # Rutas
    carpeta_entrada = "C:\\IPTV_PROTEGIDO\\temp"
    carpeta_salida = "C:\\IPTV_PROTEGIDO\\playlists"
    
    # Crear carpetas si no existen
    os.makedirs(carpeta_entrada, exist_ok=True)
    os.makedirs(carpeta_salida, exist_ok=True)
    
    print("=" * 60)
    print("🔥 PROCESADOR ANTI-BLOQUEO ISP")
    print("=" * 60)
    
    # Buscar archivos M3U8
    archivos = [f for f in os.listdir(carpeta_entrada) 
                if f.lower().endswith('.m3u8')]
    
    if not archivos:
        print("❌ No hay archivos .m3u8 en la carpeta 'temp'")
        print("💡 Copia tus archivos desde Android a: C:\\IPTV_PROTEGIDO\\temp")
        input("Presiona Enter para salir...")
        return
    
    print(f"📂 Encontrados {len(archivos)} archivos:")
    for archivo in archivos:
        print(f"   • {archivo}")
    
    print("\n🔄 Iniciando procesamiento...")
    print("-" * 60)
    
    total_canales = 0
    for archivo in archivos:
        entrada = os.path.join(carpeta_entrada, archivo)
        salida = os.path.join(carpeta_salida, archivo)
        
        canales = procesar_lista_m3u8(entrada, salida)
        total_canales += canales
    
    print("-" * 60)
    print(f"🎉 PROCESAMIENTO COMPLETADO")
    print(f"📊 Total archivos: {len(archivos)}")
    print(f"📺 Total canales: {total_canales}")
    print(f"📁 Carpeta resultados: {carpeta_salida}")
    print("=" * 60)
    
    input("\nPresiona Enter para abrir la carpeta...")
    
    # Abrir carpeta de resultados
    os.system(f'explorer "{carpeta_salida}"')

if __name__ == "__main__":
    procesar_carpeta_completa()
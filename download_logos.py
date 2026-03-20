import os
import sqlite3
import requests
import time

# Rutas dinámicas
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'backend', 'transparency.db')
LOGOS_DIR = os.path.join(BASE_DIR, 'frontend', 'logos')

def download_logos():
    print("Iniciando descarga y reemplazo de logos de partidos políticos a local...")
    
    # Paso 1: Crear la carpeta ./frontend/logos/ si no existe
    if not os.path.exists(LOGOS_DIR):
        os.makedirs(LOGOS_DIR)
        print(f"[OK] Carpeta creada u obtenida en: {LOGOS_DIR}")
        
    # Paso 2: Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, logo_url FROM parties")
    parties = cursor.fetchall()
    
    for party in parties:
        p_id = party["id"]
        p_name = party["name"]
        url = party["logo_url"]
        
        # Ignorar perfiles que no sean URLs válidas externas (http/https)
        if not url or not url.startswith('http'):
            continue
            
        print(f"\nProcesando a: {p_name}\n  -> URL Externa: {url}")
        
        try:
            # Paso 3: Descargar la imagen
            # Añadimos un header User-Agent para evitar que algunos hosts bloqueen descargas automatizadas.
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, stream=True, timeout=45, headers=headers)
            
            if response.status_code == 200:
                # Extraemos posible extensión o forzamos .png en general
                ext = ".png"
                if ".jpg" in url.lower() or ".jpeg" in url.lower():
                    ext = ".jpg"
                
                # Asignar un nombre limpio (ej. logo_5.png)
                filename = f"logo_{p_id}{ext}"
                filepath = os.path.join(LOGOS_DIR, filename)
                
                # Guardar el binario de la imagen fisicamente
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                # Paso 4: Actualizar la BD con la nueva ruta estática relativa
                new_url = f"/logos/{filename}"
                cursor.execute("UPDATE parties SET logo_url = ? WHERE id = ?", (new_url, p_id))
                print(f"  [OK] Descargado y guardado como {new_url}")
            else:
                print(f"  [!] HTTP Error {response.status_code}. No se pudo descargar.")
                
        except Exception as e:
            print(f"  [X] Error fatal con la descarga: {e}")
            
        # Pausa táctica de 3 segundos para no saturar al servidor del JNE
        time.sleep(3)
            
    # Finalmente confirmar transacción y cerrar BD
    conn.commit()
    conn.close()
    print("\n¡Descarga terminada! Tus logos ahora se sirven localmente y tu Base de Datos está actualizada.")

if __name__ == "__main__":
    download_logos()

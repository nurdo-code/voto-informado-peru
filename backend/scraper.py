import requests
import time
import urllib3
import os
import sqlite3

# Deshabilitar advertencias SSL si se usa verify=False
urllib3.disable_warnings()

BASE_URL = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/listarCanditatos"
PROCESO_ELECTORAL = 124

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Content-Type": "application/json"
}

import sys

def fetch_candidatos(tipo_eleccion, ubigeo="", cargo_label="Desconocido"):
    """
    Realiza la petición POST al JNE inyectando el tipo de elección y ubigeo.
    """
    payload = {
        "idProcesoElectoral": PROCESO_ELECTORAL,
        "idTipoEleccion": tipo_eleccion,
        "strUbiDepartamento": ubigeo
    }
    
    print(f"Realizando petición POST para {cargo_label} (Ubigeo: '{ubigeo}')...")
    
    try:
        res = requests.post(BASE_URL, json=payload, headers=HEADERS, verify=False, timeout=20)
        res.raise_for_status()
        
        # Extraer la lista de la llave "data"
        datos = res.json().get('data', [])
        return datos
    except Exception as e:
        print(f"Error extrayendo {cargo_label} ubigeo '{ubigeo}': {e}")
        
    return []

def run_scraper():
    all_candidates_raw = []
    
    print("Iniciando extracción masiva de candidatos del JNE...")
    
    # 1. Plancha Presidencial (idTipoEleccion: 1, sin ubigeo)
    cands_pres = fetch_candidatos(1, "", "Plancha Presidencial")
    all_candidates_raw.extend([(cand, "Presidente/Vicepresidente") for cand in cands_pres])
    time.sleep(1.5)
    
    # 2. Senadores - Distrito Único (idTipoEleccion: 20, sin ubigeo)
    cands_sen = fetch_candidatos(20, "", "Senadores")
    all_candidates_raw.extend([(cand, "Senador") for cand in cands_sen])
    time.sleep(1.5)
    
    # 3. Diputados - Por Región (idTipoEleccion: 15, iterar 25 regiones)
    # Los ubigeos de departamentos en Perú van del 010000 al 250000
    ubigeos = [f"{str(i).zfill(2)}0000" for i in range(1, 26)]
    
    for ubi in ubigeos:
        cands_dip = fetch_candidatos(15, ubi, f"Diputados Región {ubi}")
        all_candidates_raw.extend([(cand, "Diputado") for cand in cands_dip])
        time.sleep(1.5)
        
    print(f"\nTotal registros en crudo extraídos: {len(all_candidates_raw)}")
    print("Procesando datos y guardando en SQLite...")
    
    # CONEXIÓN A BASE DE DATOS LOCAL
    db_path = os.path.join(os.path.dirname(__file__), 'transparency.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Borrar todos los datos antiguos para empezar desde cero
    cursor.execute("DELETE FROM score_reasons")
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM candidates")
    cursor.execute("DELETE FROM parties")
    
    # 2. Extraer una lista única de todas las Organizaciones Políticas de la data en crudo
    partidos_unicos = {}
    for cand_raw, _ in all_candidates_raw:
        nombre_partido = cand_raw.get("strOrganizacionPolitica", cand_raw.get("organizacionPolitica", "General"))
        id_partido = cand_raw.get("idOrganizacionPolitica")
        
        if id_partido:
            logo_url = f"https://sroppublico.jne.gob.pe/Consulta/Simbolo/GetSimbolo/{id_partido}"
        else:
            logo_url = ""
            
        if nombre_partido and nombre_partido not in partidos_unicos:
            partidos_unicos[nombre_partido] = logo_url
            
    # 3. Insertar los partidos en BD
    for nombre_partido, logo in partidos_unicos.items():
        cursor.execute("INSERT INTO parties (name, logo_url, score) VALUES (?, ?, 100)", (nombre_partido, logo))
        
    # Crear diccionario de mapeo desde la BD
    cursor.execute("SELECT id, name FROM parties")
    mapa_partidos = {row[1]: row[0] for row in cursor.fetchall()}
        
    # 4. Iterar y estructurar a los candidatos mapeando el nombre del partido por su nuevo ID
    candidatos_insert_batch = []
    
    for cand_raw, pseudo_cargo in all_candidates_raw:
        nombre_completo = f"{cand_raw.get('strNombres', '')} {cand_raw.get('strApellidoPaterno', '')} {cand_raw.get('strApellidoMaterno', '')}".strip()
        nombre_partido = cand_raw.get('strOrganizacionPolitica', 'General')
        cargo = cand_raw.get('strCargo', pseudo_cargo)
        
        if not nombre_completo or not nombre_partido:
            continue
            
        id_del_partido = mapa_partidos.get(nombre_partido)
        
        if id_del_partido is not None:
            candidatos_insert_batch.append((nombre_completo, id_del_partido, cargo))

    # 5. Ejecutar la inserción masiva en tabla candidates
    if candidatos_insert_batch:
        print(f"Intentando insertar {len(candidatos_insert_batch)} candidatos...")
        try:
            cursor.executemany(
                "INSERT INTO candidates (name, party_id, cargo) VALUES (?, ?, ?)", 
                candidatos_insert_batch
            )
        except sqlite3.Error as e:
            print(f"Error de SQLite al insertar candidatos: {e}")
            raise
    else:
        print("ADVERTENCIA: candidatos_insert_batch está vacía. Es probable que las claves de los nombres (strCandidato) no se encuentren en la respuesta de la API.")

    # 6. Guardar cambios
    try:
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error de SQLite al hacer commit de los datos: {e}")
        raise
    finally:
        conn.close()
    
    print("¡Extracción JNE completada y Base de Datos guardada exitosamente!")

if __name__ == "__main__":
    run_scraper()


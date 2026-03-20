import os
import sqlite3
import time
import re
from gnews import GNews
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Conéctate a transparency.db usando os.path.join (ruta absoluta)
DB_PATH = os.path.join(os.path.dirname(__file__), 'transparency.db')

# Inicializar OpenAI leyendo la clave oculta
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluar_noticias_con_ia_batch(candidato, noticias, google_news):
    """
    Envía un solo prompt al auditor con todos los titulares y contenidos, y retorna los índices aprobados.
    """
    if not client or not noticias:
        return []
        
    titulares_str = ""
    for i, noticia in enumerate(noticias):
        titulo = noticia.get('title', '')
        url = noticia.get('url', '')
        contenido = ""
        try:
            articulo = google_news.get_full_article(url)
            if articulo and articulo.text:
                contenido = articulo.text[:2500]
        except Exception:
            pass
        titulares_str += f"Noticia {i+1}: {titulo} - Contenido: {contenido}\n\n"
        
    prompt = f"Analiza estas noticias sobre el candidato {candidato}. Devuelve ÚNICAMENTE una lista separada por comas con los NÚMEROS de las noticias que mencionen:\nInvestigaciones, denuncias o procesos fiscales/judiciales (INCLUSO si fueron archivados por \"blindaje\" político).\nCasos de \"blindaje\" en el Congreso, Comisiones de Ética o impunidad.\nUso indebido de recursos del Estado, policías o funcionarios para favorecer su campaña.\nVínculos con corrupción, mafias, lavado de activos o creación de leyes cuestionables con nombre propio (ej. buscar beneficiarse a sí mismo).\nIGNORA solo si es una promesa de campaña genérica o si el candidato simplemente está opinando sobre la coyuntura. Usa tu criterio: si la noticia mancha seriamente el historial ético o legal del candidato, inclúyela.\nSi ninguna noticia es relevante bajo estos criterios, responde exactamente \"NINGUNO\".\n\nNoticias a evaluar:\n{titulares_str}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un analista investigador especializado en transparencia política peruana. Tu objetivo es detectar noticias que representen un riesgo ético, legal o de idoneidad sobre un candidato."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        text_response = response.choices[0].message.content.strip().upper()
        
        if "NINGUNO" in text_response:
            return []
            
        # Extraer números usando regex por seguridad
        numeros = re.findall(r'\d+', text_response)
        
        # Validar índices reales (1-indexed en el prompt a 0-indexed en Python), ignorar duplicados
        indices = []
        for n in numeros:
            idx = int(n)
            if 0 < idx <= len(noticias):
                indices.append(idx - 1)
                
        return list(set(indices))
        
    except Exception as e:
        print(f"      [!] Excepción consultando a OpenAI en modo BATCH: {e}")
        return []

def run_analyzer():
    print("Iniciando análisis semántico de antecedentes con GNews + OpenAI (BATCH PROMPTING) (Modo Producción)...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Modo Producción: Solo analizar a los candidatos sin procesar
    cursor.execute("SELECT * FROM candidates WHERE id NOT IN (SELECT DISTINCT candidate_id FROM score_reasons) AND score = 100")
    candidates = cursor.fetchall()
    total_candidates = len(candidates)
    
    print(f"Total candidatos restantes por analizar: {total_candidates}\n")
    
    # Configuración de Google News
    google_news = GNews(language='es', country='PE', max_results=10)
    
    for idx_cand, cand in enumerate(candidates, start=1):
        cand_id = cand["id"]
        cand_name = cand["name"]
        
        print(f"\n[*] Analizando a: {cand_name} ({idx_cand} de {total_candidates})")
        
        # Búsqueda general
        query = f'"{cand_name}" (investigación OR denuncia OR ética OR escándalo OR fiscalía OR blindaje)'
        
        articulos_validos = []
        
        try:
            noticias = google_news.get_news(query)
            
            if noticias:
                print(f"    -> Se encontraron {len(noticias)} noticias en GNews. Enviando lote a Inteligencia Artificial...")
                
                # Evaluación masiva (1 petición por candidato en total)
                indices_detectados = evaluar_noticias_con_ia_batch(cand_name, noticias, google_news)
                
                if indices_detectados:
                    print(f"       [!] IA detecta antecedentes en {len(indices_detectados)} titulares. Guardando alertas.")
                    for idx in indices_detectados:
                        articulo = noticias[idx]
                        title = articulo.get('title', 'Sin título')
                        url = articulo.get('url', '')
                        source = articulo.get('publisher', {}).get('title', 'Google News')
                        
                        articulos_validos.append({
                            "title": title,
                            "url": url,
                            "source": source
                        })
                else:
                    print("       [OK] Múltiples titulares validados en un ciclo. 0 detecciones. Limpio o falso positivo.")
            else:
                print("    -> Cero menciones en GNews.")
                
        except Exception as e:
            # Si Gnews falla
            print(f"[!] Error procesando noticias para {cand_name}: {e}")
            print(f"    -> Dejando a {cand_name} con 100 puntos y pasando al siguiente.")
            
            cursor.execute("DELETE FROM articles WHERE candidate_id = ?", (cand_id,))
            cursor.execute("DELETE FROM score_reasons WHERE candidate_id = ?", (cand_id,))
            cursor.execute("UPDATE candidates SET score = 100, news_count = 0 WHERE id = ?", (cand_id,))
            
            time.sleep(5)
            continue
            
        # Calcula el descuento con la lista purificada final
        cantidad_noticias = len(articulos_validos)
        descuento = 0
        
        if 1 <= cantidad_noticias <= 2:
            descuento = 5
        elif 3 <= cantidad_noticias <= 5:
            descuento = 10
        elif cantidad_noticias >= 6:
            descuento = 20
            
        nuevo_score = 100 - descuento
        
        # Limpiar entradas anteriores del candidato
        cursor.execute("DELETE FROM articles WHERE candidate_id = ?", (cand_id,))
        cursor.execute("DELETE FROM score_reasons WHERE candidate_id = ?", (cand_id,))
        
        # Guardar noticias váliss validadas
        for art in articulos_validos:
            cursor.execute("""
                INSERT INTO articles (title, url, source, candidate_id)
                VALUES (?, ?, ?, ?)
            """, (art["title"], art["url"], art["source"], cand_id))
                
        # Actualiza el puntaje y el contador del candidato
        cursor.execute("UPDATE candidates SET score = ?, news_count = ? WHERE id = ?", 
                       (nuevo_score, cantidad_noticias, cand_id))
        
        if cantidad_noticias > 0:
            print(f"    -> Noticias filtradas válidas: {cantidad_noticias}. Nuevo puntaje: {nuevo_score}")
            cursor.execute("""
                INSERT INTO score_reasons (candidate_id, reason, deduction)
                VALUES (?, ?, ?)
            """, (cand_id, f"Descuento de lote por {cantidad_noticias} reportes (Batch IA)", descuento))
        else:
            print(f"    -> Puntaje inalterado: 100")
            
        # Descanso ESTRATÉGICO de 5 segundos solo después de cada candidato procesado completamente
        print("    -> Esperando 5 segundos por el límite de quota de OpenAI...")
        time.sleep(5)
        conn.commit()
        
    print("\nActualizando puntaje acumulativo e implacable de los Partidos Políticos...")
    
    # 1. Cálculo de Puntaje de los Partidos (Acumulativo)
    cursor.execute("""
        UPDATE parties 
        SET score = 100 - (
            SELECT COALESCE(SUM(100 - score), 0) 
            FROM candidates 
            WHERE party_id = parties.id AND score < 100
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("¡Análisis de Inteligencia Batch completado y datos guardados exitosamente!")

if __name__ == "__main__":
    run_analyzer()

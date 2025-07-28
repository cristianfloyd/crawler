import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any

def generar_id_chunk(contenido: str, materia: str, indice: int) -> str:
    """Genera un ID único para cada chunk"""
    content_hash = hashlib.md5(f"{materia}_{indice}_{contenido}".encode()).hexdigest()[:8]
    return f"materia_{content_hash}"

def limpiar_contenido(texto: str) -> str:
    """Limpia y normaliza el contenido del chunk"""
    # Eliminar espacios en blanco excesivos
    texto = ' '.join(texto.split())
    
    # Eliminar caracteres especiales problemáticos
    texto = texto.replace('\n', ' ').replace('\r', ' ')
    texto = texto.replace('\t', ' ')
    
    # Asegurar que termine con punto si es necesario
    if texto and not texto.endswith(('.', '!', '?')):
        texto += '.'
    
    return texto.strip()

def agregar_metadatos_materia(materia: Dict[str, Any]) -> Dict[str, Any]:
    """Agrega metadatos útiles para el RAG"""
    # Detectar tipo de contenido básico
    contenido_completo = ' '.join(materia['chunks']).lower()
    
    metadatos = {
        'es_carrera': 'carrera' in contenido_completo or 'licenciatura' in contenido_completo,
        'es_materia': 'materia' in contenido_completo or 'asignatura' in contenido_completo,
        'tiene_horarios': 'horario' in contenido_completo or 'lunes' in contenido_completo,
        'tiene_correlativas': 'correlativa' in contenido_completo or 'prerequisito' in contenido_completo,
        'tiene_programa': 'programa' in contenido_completo or 'contenido' in contenido_completo,
        'total_chunks': len(materia['chunks']),
        'palabras_total': sum(len(chunk.split()) for chunk in materia['chunks']),
        'fecha_scraping': datetime.now().isoformat()
    }
    
    return metadatos

def preparar_documentos_rag(archivo_materias: str = "materias_rag.json") -> List[Dict[str, Any]]:
    """
    Convierte los datos scrapeados en documentos optimizados para RAG
    """
    with open(archivo_materias, 'r', encoding='utf-8') as f:
        materias = json.load(f)
    
    documentos_rag = []
    
    for materia in materias:
        metadatos_materia = agregar_metadatos_materia(materia)
        
        for i, chunk in enumerate(materia['chunks']):
            if not chunk.strip():  # Skip chunks vacíos
                continue
                
            contenido_limpio = limpiar_contenido(chunk)
            
            if len(contenido_limpio.split()) < 5:  # Skip chunks muy cortos
                continue
            
            documento = {
                'id': generar_id_chunk(contenido_limpio, materia['nombre'], i),
                'contenido': contenido_limpio,
                'metadatos': {
                    'materia_nombre': materia['nombre'],
                    'materia_url': materia['url'],
                    'chunk_index': i,
                    'chunk_size': len(contenido_limpio.split()),
                    **metadatos_materia
                },
                'tipo_documento': 'materia_universitaria',
                'fuente': 'lcd.exactas.uba.ar'
            }
            
            documentos_rag.append(documento)
    
    return documentos_rag

def guardar_documentos_rag(documentos: List[Dict[str, Any]], archivo_salida: str = "documentos_rag_final.json"):
    """Guarda los documentos preparados para RAG"""
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(documentos)} documentos preparados para RAG guardados en: {archivo_salida}")
    
    # Estadísticas
    total_palabras = sum(doc['metadatos']['chunk_size'] for doc in documentos)
    materias_unicas = len(set(doc['metadatos']['materia_nombre'] for doc in documentos))
    
    print(f"📊 Estadísticas:")
    print(f"   - Total documentos: {len(documentos)}")
    print(f"   - Total materias: {materias_unicas}")
    print(f"   - Total palabras: {total_palabras}")
    print(f"   - Promedio palabras por documento: {total_palabras/len(documentos):.1f}")

def main():
    print("🔄 Preparando datos para RAG...")
    documentos = preparar_documentos_rag()
    guardar_documentos_rag(documentos)

if __name__ == "__main__":
    main()
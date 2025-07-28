#!/usr/bin/env python3
"""
Pipeline completo para crear un RAG de materias universitarias

Pasos:
1. Scrapear datos (scrap_materias_rag_corregido.py)
2. Preparar documentos (preparar_datos_rag.py) 
3. Crear sistema de embeddings (sistema_embeddings.py)
4. Probar el sistema
"""

import asyncio
import os
import sys
from datetime import datetime

async def paso_1_scraping():
    """Ejecuta el scraping de materias"""
    print("=" * 60)
    print("🕷️  PASO 1: SCRAPING DE MATERIAS")
    print("=" * 60)
    
    # Importar y ejecutar el scraper
    from scrap_materias_rag_corregido import main as scraper_main
    await scraper_main()
    
    # Verificar que se creó el archivo
    if os.path.exists("materias_rag.json"):
        print("✅ Scraping completado exitosamente")
        return True
    else:
        print("❌ Error en el scraping")
        return False

def paso_2_preparar_datos():
    """Prepara los datos para RAG"""
    print("\n" + "=" * 60)
    print("📊 PASO 2: PREPARACIÓN DE DATOS PARA RAG")
    print("=" * 60)
    
    from preparar_datos_rag import main as preparar_main
    preparar_main()
    
    # Verificar que se creó el archivo
    if os.path.exists("documentos_rag_final.json"):
        print("✅ Preparación de datos completada")
        return True
    else:
        print("❌ Error en la preparación de datos")
        return False

def paso_3_crear_embeddings():
    """Crea el sistema de embeddings"""
    print("\n" + "=" * 60)
    print("🤖 PASO 3: CREACIÓN DE SISTEMA DE EMBEDDINGS")
    print("=" * 60)
    
    from crawler.src.sistema_embeddings import main as embeddings_main
    embeddings_main()
    
    # Verificar que se creó el directorio del sistema
    if os.path.exists("rag_sistema") and os.path.exists("rag_sistema/indice.faiss"):
        print("✅ Sistema de embeddings creado exitosamente")
        return True
    else:
        print("❌ Error en la creación del sistema de embeddings")
        return False

def paso_4_probar_sistema():
    """Prueba el sistema RAG completo"""
    print("\n" + "=" * 60)
    print("🧪 PASO 4: PRUEBAS DEL SISTEMA RAG")
    print("=" * 60)
    
    try:
        from crawler.src.sistema_embeddings import SistemaEmbeddings
        
        # Cargar sistema
        sistema = SistemaEmbeddings()
        sistema.cargar_sistema("rag_sistema")
        
        # Consultas de prueba específicas para universidad
        consultas_prueba = [
            "horarios de análisis matemático",
            "correlativas de algoritmos",
            "programa de la materia de bases de datos",
            "carrera de licenciatura en computación",
            "requisitos para cursar física",
            "contenido de álgebra lineal",
            "¿cuándo se dicta programación?",
            "materias del primer año"
        ]
        
        print(f"🔍 Probando {len(consultas_prueba)} consultas de ejemplo:")
        print("-" * 60)
        
        for i, consulta in enumerate(consultas_prueba, 1):
            print(f"\n{i}. 🔎 '{consulta}'")
            
            try:
                resultados = sistema.buscar_similares(consulta, k=3)
                
                if resultados:
                    for j, (doc, score) in enumerate(resultados[:2], 1):
                        materia = doc['metadatos']['materia_nombre']
                        contenido = doc['contenido'][:120] + "..."
                        print(f"   📄 {j}. [{score:.3f}] {materia}")
                        print(f"      {contenido}")
                else:
                    print("   ❌ No se encontraron resultados")
                    
            except Exception as e:
                print(f"   ❌ Error en consulta: {e}")
        
        print("\n" + "=" * 60)
        print("✅ SISTEMA RAG COMPLETADO Y FUNCIONANDO")
        print("=" * 60)
        
        # Estadísticas finales
        print(f"📊 Estadísticas finales:")
        print(f"   • Total documentos: {len(sistema.documentos)}")
        print(f"   • Dimensión vectores: {sistema.dimension}")
        print(f"   • Materias únicas: {len(set(doc['metadatos']['materia_nombre'] for doc in sistema.documentos))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        return False

def mostrar_archivos_generados():
    """Muestra los archivos generados en el proceso"""
    print("\n" + "=" * 60)
    print("📁 ARCHIVOS GENERADOS")
    print("=" * 60)
    
    archivos_esperados = [
        ("materias_rag.json", "Datos scrapeados originales"),
        ("documentos_rag_final.json", "Documentos preparados para RAG"),
        ("rag_sistema/", "Directorio del sistema RAG"),
        ("rag_sistema/indice.faiss", "Índice vectorial FAISS"),
        ("rag_sistema/documentos.json", "Documentos del sistema"),
        ("rag_sistema/metadatos.json", "Metadatos del sistema")
    ]
    
    for archivo, descripcion in archivos_esperados:
        if os.path.exists(archivo):
            if os.path.isdir(archivo):
                tamaño = "directorio"
            else:
                tamaño = f"{os.path.getsize(archivo) / 1024:.1f} KB"
            print(f"✅ {archivo:<30} | {tamaño:<15} | {descripcion}")
        else:
            print(f"❌ {archivo:<30} | {'FALTANTE':<15} | {descripcion}")

async def main():
    """Ejecuta el pipeline completo"""
    inicio = datetime.now()
    
    print("🚀 INICIANDO PIPELINE RAG COMPLETO")
    print(f"⏰ Hora de inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Paso 1: Scraping
        if not await paso_1_scraping():
            print("❌ Pipeline detenido en el paso 1")
            return False
        
        # Paso 2: Preparar datos
        if not paso_2_preparar_datos():
            print("❌ Pipeline detenido en el paso 2")
            return False
        
        # Paso 3: Crear embeddings
        if not paso_3_crear_embeddings():
            print("❌ Pipeline detenido en el paso 3")
            return False
        
        # Paso 4: Probar sistema
        if not paso_4_probar_sistema():
            print("❌ Pipeline detenido en el paso 4")
            return False
        
        # Mostrar resumen
        mostrar_archivos_generados()
        
        fin = datetime.now()
        duracion = fin - inicio
        
        print("\n" + "🎉" * 20)
        print("🎉 PIPELINE RAG COMPLETADO EXITOSAMENTE")
        print("🎉" * 20)
        print(f"⏱️  Duración total: {duracion}")
        print(f"📅 Finalizado: {fin.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n💡 Próximos pasos sugeridos:")
        print("   1. Usar sistema_embeddings.py para hacer consultas")
        print("   2. Integrar con tu chatbot favorito")
        print("   3. Crear API REST para el RAG")
        print("   4. Añadir interfaz web (Streamlit/Gradio)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error crítico en el pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import sentence_transformers
        import faiss
        import numpy as np
    except ImportError as e:
        print("❌ Dependencias faltantes. Instala con:")
        print("pip install sentence-transformers faiss-cpu numpy")
        sys.exit(1)
    
    # Ejecutar pipeline
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

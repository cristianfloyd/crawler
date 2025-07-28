#!/usr/bin/env python3
"""
Script para hacer consultas al sistema RAG desde línea de comandos
"""

import argparse
import sys
import os
from crawler.src.sistema_embeddings import SistemaEmbeddings

def consultar_interactivo(sistema):
    """Modo interactivo para hacer consultas"""
    print("🤖 Modo interactivo del RAG - Escribe 'salir' para terminar")
    print("=" * 60)
    
    while True:
        try:
            consulta = input("\n🔍 Tu consulta: ").strip()
            
            if consulta.lower() in ['salir', 'exit', 'quit', '']:
                print("👋 ¡Hasta luego!")
                break
            
            # Buscar resultados
            resultados = sistema.buscar_similares(consulta, k=5)
            
            if not resultados:
                print("❌ No se encontraron resultados relevantes")
                continue
            
            print(f"\n📊 Encontré {len(resultados)} resultados relevantes:")
            print("-" * 40)
            
            for i, (doc, score) in enumerate(resultados, 1):
                materia = doc['metadatos']['materia_nombre']
                contenido = doc['contenido']
                palabras = doc['metadatos']['chunk_size']
                
                print(f"\n{i}. 📚 {materia} (Score: {score:.3f})")
                print(f"   📄 {contenido}")
                print(f"   ℹ️  {palabras} palabras | Chunk {doc['metadatos']['chunk_index']}")
                
                if i >= 3:  # Mostrar solo los 3 más relevantes por defecto
                    if len(resultados) > 3:
                        mostrar_mas = input(f"\n¿Mostrar los otros {len(resultados)-3} resultados? (s/n): ")
                        if mostrar_mas.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
                            break
                    
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def consultar_simple(sistema, consulta, k=3, mostrar_detalle=False):
    """Hace una consulta simple y muestra resultados"""
    print(f"🔍 Consulta: '{consulta}'")
    print("-" * 60)
    
    resultados = sistema.buscar_similares(consulta, k=k)
    
    if not resultados:
        print("❌ No se encontraron resultados relevantes")
        return
    
    for i, (doc, score) in enumerate(resultados, 1):
        materia = doc['metadatos']['materia_nombre']
        contenido = doc['contenido']
        
        print(f"\n{i}. 📚 {materia} (Score: {score:.3f})")
        
        if mostrar_detalle:
            print(f"   📄 {contenido}")
            print(f"   🔗 {doc['metadatos']['materia_url']}")
            print(f"   ℹ️  {doc['metadatos']['chunk_size']} palabras")
        else:
            # Mostrar solo los primeros 150 caracteres
            contenido_corto = contenido[:150] + "..." if len(contenido) > 150 else contenido
            print(f"   📄 {contenido_corto}")

def estadisticas_sistema(sistema):
    """Muestra estadísticas del sistema RAG"""
    print("📊 ESTADÍSTICAS DEL SISTEMA RAG")
    print("=" * 40)
    
    total_docs = len(sistema.documentos)
    materias_unicas = set(doc['metadatos']['materia_nombre'] for doc in sistema.documentos)
    total_palabras = sum(doc['metadatos']['chunk_size'] for doc in sistema.documentos)
    
    print(f"📚 Total documentos: {total_docs}")
    print(f"🎓 Materias únicas: {len(materias_unicas)}")
    print(f"📝 Total palabras: {total_palabras:,}")
    print(f"📊 Promedio palabras/doc: {total_palabras/total_docs:.1f}")
    print(f"🤖 Dimensión vectores: {sistema.dimension}")
    
    print(f"\n📋 Materias disponibles:")
    for i, materia in enumerate(sorted(materias_unicas), 1):
        docs_materia = len([d for d in sistema.documentos if d['metadatos']['materia_nombre'] == materia])
        print(f"   {i:2d}. {materia} ({docs_materia} documentos)")

def main():
    parser = argparse.ArgumentParser(description="Consultar sistema RAG de materias universitarias")
    parser.add_argument("--consulta", "-c", type=str, help="Consulta específica")
    parser.add_argument("--k", "-k", type=int, default=3, help="Número de resultados (default: 3)")
    parser.add_argument("--detalle", "-d", action="store_true", help="Mostrar información detallada")
    parser.add_argument("--interactivo", "-i", action="store_true", help="Modo interactivo")
    parser.add_argument("--stats", "-s", action="store_true", help="Mostrar estadísticas del sistema")
    parser.add_argument("--directorio", type=str, default="rag_sistema", help="Directorio del sistema RAG")
    
    args = parser.parse_args()
    
    # Verificar que existe el sistema RAG
    if not os.path.exists(args.directorio):
        print(f"❌ No se encontró el sistema RAG en: {args.directorio}")
        print("💡 Ejecuta primero: python pipeline_rag_completo.py")
        sys.exit(1)
    
    # Cargar sistema
    print(f"📂 Cargando sistema RAG desde: {args.directorio}")
    try:
        sistema = SistemaEmbeddings()
        sistema.cargar_sistema(args.directorio)
    except Exception as e:
        print(f"❌ Error cargando sistema: {e}")
        sys.exit(1)
    
    # Mostrar estadísticas si se solicita
    if args.stats:
        estadisticas_sistema(sistema)
        if not (args.consulta or args.interactivo):
            return
        print("\n")
    
    # Modo interactivo
    if args.interactivo:
        consultar_interactivo(sistema)
        return
    
    # Consulta específica
    if args.consulta:
        consultar_simple(sistema, args.consulta, args.k, args.detalle)
        return
    
    # Si no se especifica nada, mostrar ayuda
    parser.print_help()
    print("\n💡 Ejemplos de uso:")
    print("  python consultar_rag.py -c 'horarios de análisis matemático'")
    print("  python consultar_rag.py -i  # Modo interactivo")
    print("  python consultar_rag.py -s  # Estadísticas")

if __name__ == "__main__":
    main()

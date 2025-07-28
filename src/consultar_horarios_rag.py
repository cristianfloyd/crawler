#!/usr/bin/env python3
"""
Interfaz CLI para Consultas de Horarios - Día 4
Sistema RAG especializado en consultas académicas de horarios

Autor: Sistema RAG MVP
Fecha: 2025-07-27
"""

import argparse
import sys
import os
from typing import List, Dict, Any
import re
from datetime import datetime
import logging
try:
    from .sistema_embeddings_horarios import SistemaEmbeddingsHorarios
except ImportError:
    from sistema_embeddings_horarios import SistemaEmbeddingsHorarios

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConsultorHorarios:
    """Interfaz de consulta especializada para horarios académicos"""
    
    def __init__(self, directorio_sistema: str = "rag_sistema_horarios"):
        """
        Inicializa el consultor de horarios
        
        Args:
            directorio_sistema: Directorio donde está guardado el sistema RAG
        """
        self.sistema = SistemaEmbeddingsHorarios()
        self.directorio_sistema = directorio_sistema
        self.sistema_cargado = False
        
        # Comandos especiales
        self.comandos_especiales = {
            '/help': self.mostrar_ayuda,
            '/stats': self.mostrar_estadisticas,
            '/examples': self.mostrar_ejemplos,
            '/materias': self.listar_materias,
            '/departamentos': self.listar_departamentos,
            '/dias': self.buscar_por_dia,
            '/mañana': lambda: self.buscar_por_franja('mañana'),
            '/tarde': lambda: self.buscar_por_franja('tarde'),
            '/noche': lambda: self.buscar_por_franja('noche'),
            '/exit': self.salir,
            '/quit': self.salir
        }

    def cargar_sistema(self) -> bool:
        """Carga el sistema RAG de horarios"""
        try:
            if not os.path.exists(self.directorio_sistema):
                print(f"❌ No se encontró el sistema RAG en: {self.directorio_sistema}")
                print("💡 Ejecuta primero: python sistema_embeddings_horarios.py")
                return False
            
            print("🔄 Cargando sistema RAG de horarios...")
            self.sistema.cargar_sistema_horarios(self.directorio_sistema)
            self.sistema_cargado = True
            print("✅ Sistema RAG de horarios cargado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando el sistema: {e}")
            return False

    def procesar_consulta(self, consulta: str, k: int = 5) -> List[Dict]:
        """Procesa una consulta y devuelve resultados estructurados"""
        if not self.sistema_cargado:
            return []
        
        try:
            # Buscar similitudes
            resultados = self.sistema.buscar_similares_horarios(consulta, k=k)
            
            resultados_estructurados = []
            for doc, score in resultados:
                materia = doc['materia_original']
                metadatos = doc['metadatos']
                
                # Estructura resultado
                resultado = {
                    'score': score,
                    'nombre': metadatos['materia_nombre'],
                    'nombre_normalizado': metadatos['materia_normalizada'],
                    'departamento': metadatos['departamento_nombre'],
                    'codigo_dept': metadatos['departamento_codigo'],
                    'tiene_horarios': metadatos['tiene_horarios'],
                    'horarios': [],
                    'docentes': [],
                    'periodo': metadatos.get('periodo', {})
                }
                
                # Procesar horarios
                if materia.get('horarios'):
                    for horario in materia['horarios']:
                        resultado['horarios'].append({
                            'dia': horario.get('dia', ''),
                            'hora_inicio': horario.get('hora_inicio', ''),
                            'hora_fin': horario.get('hora_fin', ''),
                            'tipo': horario.get('tipo_actividad', ''),
                            'comision': horario.get('comision', ''),
                            'aula': horario.get('aula', '')
                        })
                
                # Procesar docentes
                if materia.get('docentes'):
                    for docente in materia['docentes']:
                        if isinstance(docente, dict):
                            resultado['docentes'].append({
                                'nombre': docente.get('nombre', ''),
                                'rol': docente.get('rol', '')
                            })
                        else:
                            resultado['docentes'].append({'nombre': str(docente), 'rol': ''})
                
                resultados_estructurados.append(resultado)
            
            return resultados_estructurados
            
        except Exception as e:
            print(f"❌ Error procesando consulta: {e}")
            return []

    def mostrar_resultado(self, resultado: Dict, indice: int):
        """Muestra un resultado de forma estructurada"""
        score = resultado['score']
        nombre = resultado['nombre']
        dept = resultado['codigo_dept']
        
        # Encabezado
        print(f"\n📚 {indice}. [{score:.3f}] {nombre} ({dept})")
        
        # Horarios
        if resultado['horarios']:
            print("   🕐 Horarios:")
            for horario in resultado['horarios']:
                dia = horario['dia']
                inicio = horario['hora_inicio']
                fin = horario['hora_fin']
                tipo = horario['tipo']
                comision = horario['comision']
                aula = horario['aula']
                
                texto_horario = f"      • {dia}: {inicio} - {fin}"
                if tipo and tipo != 'general':
                    texto_horario += f" ({tipo})"
                if comision:
                    texto_horario += f" - Comisión {comision}"
                if aula:
                    texto_horario += f" - {aula}"
                
                print(texto_horario)
        else:
            print("   ❌ Sin horarios definidos")
        
        # Docentes
        if resultado['docentes']:
            docentes_texto = []
            for docente in resultado['docentes']:
                nombre_doc = docente['nombre']
                rol = docente['rol']
                if rol:
                    docentes_texto.append(f"{nombre_doc} ({rol})")
                else:
                    docentes_texto.append(nombre_doc)
            
            if docentes_texto:
                print(f"   👨‍🏫 Docentes: {', '.join(docentes_texto)}")
        
        # Período
        periodo = resultado['periodo']
        if periodo:
            info_periodo = []
            if periodo.get('cuatrimestre'):
                info_periodo.append(f"{periodo['cuatrimestre']}° cuatrimestre")
            if periodo.get('bimestre'):
                info_periodo.append(f"{periodo['bimestre']}° bimestre")
            if periodo.get('año'):
                info_periodo.append(f"{periodo['año']}")
            
            if info_periodo:
                print(f"   📅 Período: {' '.join(info_periodo)}")

    def buscar_por_dia(self, dia: str = None):
        """Busca materias por día específico"""
        if not dia:
            dia = input("📅 Ingresa el día (lunes, martes, etc.): ").strip().lower()
        
        if not dia:
            print("❌ Debe especificar un día")
            return
        
        consulta = f"materias clases {dia} cursada"
        print(f"\n🔍 Buscando materias que se dictan los {dia}...")
        
        resultados = self.procesar_consulta(consulta, k=10)
        
        # Filtrar por día específico
        resultados_filtrados = []
        for resultado in resultados:
            for horario in resultado['horarios']:
                if horario['dia'].lower() == dia.lower():
                    resultados_filtrados.append(resultado)
                    break
        
        if resultados_filtrados:
            print(f"\n📚 Materias que se dictan los {dia}:")
            for i, resultado in enumerate(resultados_filtrados[:8], 1):
                self.mostrar_resultado(resultado, i)
        else:
            print(f"❌ No se encontraron materias para los {dia}")

    def buscar_por_franja(self, franja: str):
        """Busca materias por franja horaria (mañana, tarde, noche)"""
        consulta = f"materias clases {franja} horarios cursada"
        print(f"\n🔍 Buscando materias de {franja}...")
        
        resultados = self.procesar_consulta(consulta, k=10)
        
        if resultados:
            print(f"\n📚 Materias de {franja}:")
            for i, resultado in enumerate(resultados[:6], 1):
                self.mostrar_resultado(resultado, i)
        else:
            print(f"❌ No se encontraron materias de {franja}")

    def listar_materias(self):
        """Lista todas las materias disponibles"""
        if not self.sistema_cargado:
            print("❌ Sistema no cargado")
            return
        
        print("\n📚 Materias disponibles en el sistema:")
        
        materias_por_dept = {}
        for doc in self.sistema.documentos:
            dept = doc['metadatos']['departamento_codigo']
            nombre = doc['metadatos']['materia_nombre']
            tiene_horarios = doc['metadatos']['tiene_horarios']
            
            if dept not in materias_por_dept:
                materias_por_dept[dept] = []
            
            materias_por_dept[dept].append((nombre, tiene_horarios))
        
        for dept, materias in sorted(materias_por_dept.items()):
            print(f"\n🏢 {dept}:")
            for nombre, tiene_horarios in sorted(materias):
                icono = "🕐" if tiene_horarios else "❌"
                print(f"   {icono} {nombre}")

    def listar_departamentos(self):
        """Lista departamentos y estadísticas"""
        if not self.sistema_cargado:
            print("❌ Sistema no cargado")
            return
        
        print("\n🏢 Departamentos disponibles:")
        
        stats_dept = {}
        for doc in self.sistema.documentos:
            codigo = doc['metadatos']['departamento_codigo']
            nombre = doc['metadatos']['departamento_nombre']
            tiene_horarios = doc['metadatos']['tiene_horarios']
            
            if codigo not in stats_dept:
                stats_dept[codigo] = {
                    'nombre': nombre,
                    'total': 0,
                    'con_horarios': 0
                }
            
            stats_dept[codigo]['total'] += 1
            if tiene_horarios:
                stats_dept[codigo]['con_horarios'] += 1
        
        for codigo, stats in sorted(stats_dept.items()):
            total = stats['total']
            con_horarios = stats['con_horarios']
            porcentaje = (con_horarios / total * 100) if total > 0 else 0
            
            print(f"   • {codigo}: {stats['nombre']}")
            print(f"     📊 {total} materias, {con_horarios} con horarios ({porcentaje:.1f}%)")

    def mostrar_estadisticas(self):
        """Muestra estadísticas del sistema"""
        if not self.sistema_cargado:
            print("❌ Sistema no cargado")
            return
        
        total_docs = len(self.sistema.documentos)
        con_horarios = sum(1 for d in self.sistema.documentos if d['metadatos']['tiene_horarios'])
        sin_horarios = total_docs - con_horarios
        
        print(f"\n📊 Estadísticas del Sistema RAG de Horarios:")
        print(f"   📚 Total materias: {total_docs}")
        print(f"   🕐 Con horarios: {con_horarios} ({con_horarios/total_docs*100:.1f}%)")
        print(f"   ❌ Sin horarios: {sin_horarios} ({sin_horarios/total_docs*100:.1f}%)")
        
        # Estadísticas por día
        dias_count = {}
        for doc in self.sistema.documentos:
            for dia in doc['metadatos']['dias_semana']:
                dias_count[dia] = dias_count.get(dia, 0) + 1
        
        if dias_count:
            print(f"\n📅 Materias por día:")
            for dia, count in sorted(dias_count.items()):
                print(f"   • {dia}: {count} materias")

    def mostrar_ejemplos(self):
        """Muestra ejemplos de consultas"""
        print("""
🔍 Ejemplos de consultas que puedes hacer:

📚 Consultas básicas:
   • "¿Cuándo se dicta Análisis Matemático?"
   • "Horarios de Algoritmos y Estructuras de Datos"
   • "¿Qué materias hay los lunes?"

⏰ Consultas por horario:
   • "¿Materias por la mañana?"
   • "¿Qué hay los viernes por la tarde?"
   • "¿Clases de noche?"

🏢 Consultas por departamento:
   • "Materias del Departamento de Computación"
   • "¿Qué dicta el Instituto de Cálculo?"
   • "Horarios de matemática"

🔧 Comandos especiales:
   • /help - Muestra esta ayuda
   • /stats - Estadísticas del sistema
   • /materias - Lista todas las materias
   • /departamentos - Lista departamentos
   • /dias lunes - Materias de un día específico
   • /mañana, /tarde, /noche - Por franja horaria
   • /exit - Salir del programa
        """)

    def mostrar_ayuda(self):
        """Muestra ayuda del sistema"""
        print("""
🤖 Sistema RAG de Consulta de Horarios Académicos

Este sistema te permite consultar horarios de materias universitarias
de manera natural. Puedes hacer preguntas como si le hablaras a una persona.

📝 Tipos de consultas soportadas:
   • Horarios de materias específicas
   • Materias por día de la semana
   • Materias por franja horaria
   • Información de docentes
   • Datos de departamentos

💡 Consejos:
   • Usa lenguaje natural: "¿Cuándo se dicta...?"
   • Especifica el día: "los lunes", "martes por la tarde"
   • Menciona la materia: "Análisis", "Algoritmos"
   • Usa comandos /help para más opciones

🔧 Comandos disponibles:
   • /examples - Ver ejemplos de consultas
   • /stats - Estadísticas del sistema
   • /materias - Listar todas las materias
   • /departamentos - Información de departamentos
   • /dias [día] - Buscar por día específico
   • /exit - Salir
        """)

    def salir(self):
        """Sale del programa"""
        print("\n👋 ¡Hasta luego! Gracias por usar el Sistema RAG de Horarios")
        sys.exit(0)

    def procesar_comando_especial(self, entrada: str) -> bool:
        """Procesa comandos especiales. Retorna True si fue un comando."""
        entrada = entrada.strip().lower()
        
        if entrada in self.comandos_especiales:
            self.comandos_especiales[entrada]()
            return True
        
        # Comandos con parámetros
        if entrada.startswith('/dias '):
            dia = entrada[6:].strip()
            self.buscar_por_dia(dia)
            return True
        
        return False

    def ejecutar_consulta_individual(self, consulta: str, k: int = 5):
        """Ejecuta una consulta individual y muestra resultados"""
        if not self.cargar_sistema():
            return
        
        print(f"\n🔍 Consulta: {consulta}")
        print("=" * 60)
        
        resultados = self.procesar_consulta(consulta, k=k)
        
        if resultados:
            print(f"\n📚 Encontrados {len(resultados)} resultados:")
            for i, resultado in enumerate(resultados, 1):
                self.mostrar_resultado(resultado, i)
        else:
            print("❌ No se encontraron resultados para tu consulta")
            print("💡 Intenta reformular la pregunta o usa /examples para ver ejemplos")

    def iniciar_modo_interactivo(self):
        """Inicia el modo interactivo de consultas"""
        print("🤖 Sistema RAG de Consulta de Horarios Académicos")
        print("=" * 60)
        
        if not self.cargar_sistema():
            return
        
        self.mostrar_ayuda()
        
        print("\n✅ Sistema listo para consultas. Escribe tu pregunta o /help para ayuda.")
        
        while True:
            try:
                entrada = input("\n📝 Tu consulta: ").strip()
                
                if not entrada:
                    continue
                
                # Procesar comandos especiales
                if self.procesar_comando_especial(entrada):
                    continue
                
                # Procesar consulta normal
                print(f"\n🔍 Buscando: {entrada}")
                print("=" * 40)
                
                resultados = self.procesar_consulta(entrada, k=5)
                
                if resultados:
                    print(f"\n📚 Encontrados {len(resultados)} resultados:")
                    for i, resultado in enumerate(resultados, 1):
                        self.mostrar_resultado(resultado, i)
                else:
                    print("❌ No se encontraron resultados para tu consulta")
                    print("💡 Intenta reformular la pregunta o usa /examples para ver ejemplos")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Sistema RAG de Consulta de Horarios Académicos")
    parser.add_argument("--consulta", "-c", type=str, help="Consulta específica a realizar")
    parser.add_argument("--resultados", "-k", type=int, default=5, help="Número de resultados (default: 5)")
    parser.add_argument("--sistema", "-s", type=str, default="rag_sistema_horarios", help="Directorio del sistema RAG")
    parser.add_argument("--interactivo", "-i", action="store_true", help="Modo interactivo")
    
    args = parser.parse_args()
    
    consultor = ConsultorHorarios(args.sistema)
    
    if args.consulta:
        # Modo consulta única
        consultor.ejecutar_consulta_individual(args.consulta, args.resultados)
    else:
        # Modo interactivo (default)
        consultor.iniciar_modo_interactivo()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
PUNTO DE ENTRADA UNIFICADO - DESCUBRIMIENTO COMPLETO DE MATERIAS LCD
Ejecuta toda la cadena: extracción → normalización → archivo final con nombre fijo
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, Optional


class DescubridorMateriasCompleto:
    def __init__(self):
        self.archivo_final = "materias_lcd_descubiertas.json"  # Nombre fijo
        self.ruta_final = None
        self.estadisticas = {
            "inicio": None,
            "fin": None,
            "duracion_segundos": 0,
            "materias_extraidas": 0,
            "materias_normalizadas": 0,
            "cambios_normalizacion": 0,
            "exito": False
        }

    async def ejecutar_descubrimiento_completo(self) -> str:
        """
        Ejecuta toda la cadena de descubrimiento y normalización
        Returns: Ruta del archivo JSON final con nombre fijo
        """
        print("🚀 DESCUBRIDOR COMPLETO DE MATERIAS LCD")
        print("=" * 60)
        print("Ejecutando cadena completa:")
        print("  1️⃣ Extracción de materias (identificar_materias_lcd.py)")
        print("  2️⃣ Normalización automática de nombres")
        print("  3️⃣ Generación de archivo final con nombre fijo")
        print()
        
        self.estadisticas["inicio"] = datetime.now()
        
        try:
            # PASO 1: Extracción de materias
            print("🔄 PASO 1: Ejecutando extracción de materias...")
            archivo_extraido = await self.ejecutar_extraccion()
            print(f"   ✅ Extracción completada: {os.path.basename(archivo_extraido)}")
            
            # PASO 2: Normalización de nombres
            print("\n🔄 PASO 2: Ejecutando normalización de nombres...")
            archivo_normalizado = await self.ejecutar_normalizacion(archivo_extraido)
            print(f"   ✅ Normalización completada: {os.path.basename(archivo_normalizado)}")
            
            # PASO 3: Generar archivo final con nombre fijo
            print("\n🔄 PASO 3: Generando archivo final con nombre fijo...")
            self.ruta_final = self.generar_archivo_final(archivo_normalizado)
            print(f"   ✅ Archivo final generado: {os.path.basename(self.ruta_final)}")
            
            # PASO 4: Validar resultado
            print("\n🔄 PASO 4: Validando resultado final...")
            self.validar_archivo_final()
            print("   ✅ Validación exitosa")
            
            self.estadisticas["fin"] = datetime.now()
            self.estadisticas["duracion_segundos"] = (
                self.estadisticas["fin"] - self.estadisticas["inicio"]
            ).total_seconds()
            self.estadisticas["exito"] = True
            
            self.generar_resumen_final()
            return self.ruta_final
            
        except Exception as e:
            print(f"\n❌ ERROR EN DESCUBRIMIENTO: {e}")
            self.estadisticas["exito"] = False
            raise

    async def ejecutar_extraccion(self) -> str:
        """Ejecuta la extracción de materias usando el identificador LCD"""
        # Importar dinámicamente para evitar problemas de dependencias
        sys.path.append(os.path.dirname(__file__))
        
        try:
            from identificar_materias_lcd import ExtractorMateriasLCD
            
            # Usar el esquema LCD estructurado que ya funciona
            extractor = ExtractorMateriasLCD("lcd_css_schema_generado_por_llm_ccode.json")
            
            # Ejecutar extracción
            await extractor.ejecutar_extraccion_final()
            
            # Encontrar el archivo generado (buscar el más reciente)
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            archivos_lcd = []
            
            for archivo in os.listdir(data_dir):
                if archivo.startswith("materias_lcd_css_final") and archivo.endswith(".json"):
                    ruta_completa = os.path.join(data_dir, archivo)
                    archivos_lcd.append((ruta_completa, os.path.getmtime(ruta_completa)))
            
            if not archivos_lcd:
                raise FileNotFoundError("No se encontró archivo de materias extraídas")
            
            # Devolver el más reciente
            archivo_mas_reciente = max(archivos_lcd, key=lambda x: x[1])[0]
            
            # Actualizar estadísticas
            with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                self.estadisticas["materias_extraidas"] = datos.get("metadata", {}).get("total_materias", 0)
            
            return archivo_mas_reciente
            
        except ImportError as e:
            raise Exception(f"Error importando extractor LCD: {e}")

    async def ejecutar_normalizacion(self, archivo_entrada: str) -> str:
        """Ejecuta la normalización de nombres"""
        try:
            from fase2_normalizar_nombres_automatico import NormalizadorNombresLCD
            
            # Crear normalizador usando el archivo extraído
            normalizador = NormalizadorNombresLCD()
            
            # Ejecutar normalización completa
            archivo_normalizado = normalizador.ejecutar_fase2_completa(os.path.basename(archivo_entrada))
            
            # Actualizar estadísticas
            stats_normalizacion = normalizador.estadisticas
            self.estadisticas["materias_normalizadas"] = stats_normalizacion.get("materias_procesadas", 0)
            self.estadisticas["cambios_normalizacion"] = stats_normalizacion.get("cambios_realizados", 0)
            
            return archivo_normalizado
            
        except ImportError as e:
            raise Exception(f"Error importando normalizador: {e}")

    def generar_archivo_final(self, archivo_normalizado: str) -> str:
        """Genera el archivo final con nombre fijo para consumo externo"""
        # Leer archivo normalizado
        with open(archivo_normalizado, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Enriquecer metadata para consumo externo
        datos["metadata"]["punto_entrada"] = "descubrir_materias_completo.py"
        datos["metadata"]["archivo_consumible"] = True
        datos["metadata"]["version_api"] = "1.0"
        datos["metadata"]["formato_estable"] = True
        datos["metadata"]["descripcion"] = "Materias LCD extraídas y normalizadas para consumo por scrapers"
        
        # Convertir datetime objects a strings para JSON serialization
        estadisticas_serializables = self.estadisticas.copy()
        if estadisticas_serializables.get("inicio"):
            estadisticas_serializables["inicio"] = estadisticas_serializables["inicio"].isoformat()
        if estadisticas_serializables.get("fin"):
            estadisticas_serializables["fin"] = estadisticas_serializables["fin"].isoformat()
        
        datos["metadata"]["estadisticas_proceso"] = estadisticas_serializables
        
        # Ruta del archivo final con nombre fijo
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        ruta_final = os.path.join(data_dir, self.archivo_final)
        
        # Guardar con nombre fijo
        with open(ruta_final, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        return ruta_final

    def validar_archivo_final(self):
        """Valida que el archivo final sea correcto y consumible"""
        if not os.path.exists(self.ruta_final):
            raise FileNotFoundError(f"Archivo final no existe: {self.ruta_final}")
        
        # Validar estructura JSON
        with open(self.ruta_final, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Validaciones críticas
        if "cbc" not in datos:
            raise ValueError("Falta sección CBC en archivo final")
        
        if "segundo_ciclo" not in datos:
            raise ValueError("Falta sección segundo_ciclo en archivo final")
        
        if "tercer_ciclo" not in datos:
            raise ValueError("Falta sección tercer_ciclo en archivo final")
        
        if "metadata" not in datos:
            raise ValueError("Falta metadata en archivo final")
        
        # Validar que haya materias
        total_materias = len(datos["cbc"]) + len(datos["segundo_ciclo"]) + len(datos["tercer_ciclo"])
        if total_materias == 0:
            raise ValueError("No se encontraron materias en archivo final")
        
        print(f"     📊 Validación: {total_materias} materias en archivo final")
        print(f"     📊 CBC: {len(datos['cbc'])} materias")
        print(f"     📊 Segundo Ciclo: {len(datos['segundo_ciclo'])} materias")
        print(f"     📊 Tercer Ciclo: {len(datos['tercer_ciclo'])} caminos")

    def generar_resumen_final(self):
        """Genera resumen final del proceso"""
        print("\n" + "=" * 60)
        print("🎉 DESCUBRIMIENTO COMPLETO EXITOSO")
        print("=" * 60)
        
        print(f"📁 Archivo final: {os.path.basename(self.ruta_final)}")
        print(f"🗂️ Ruta completa: {self.ruta_final}")
        print(f"⏱️ Duración total: {self.estadisticas['duracion_segundos']:.1f} segundos")
        print(f"📊 Materias extraídas: {self.estadisticas['materias_extraidas']}")
        print(f"🔧 Materias normalizadas: {self.estadisticas['materias_normalizadas']}")
        print(f"✨ Cambios aplicados: {self.estadisticas['cambios_normalizacion']}")
        
        print("\n✅ ARCHIVO LISTO PARA CONSUMO EXTERNO")
        print("   • Nombre fijo para integración con scrapers")
        print("   • Estructura JSON validada")
        print("   • Metadata completa incluida")
        print("   • Nombres normalizados y limpios")
        
        print(f"\n🔗 INTEGRACIÓN CON SCRAPERS:")
        print(f"   import json")
        print(f"   with open('{self.archivo_final}', 'r') as f:")
        print(f"       materias_lcd = json.load(f)")
        print(f"   # Acceder a: materias_lcd['cbc'], materias_lcd['segundo_ciclo'], etc.")

    def obtener_ruta_archivo_final(self) -> Optional[str]:
        """Devuelve la ruta del archivo final generado"""
        return self.ruta_final


async def main():
    """Función principal - punto de entrada unificado"""
    descubridor = DescubridorMateriasCompleto()
    
    try:
        ruta_final = await descubridor.ejecutar_descubrimiento_completo()
        
        print(f"\n🚀 ÉXITO: Archivo final disponible en:")
        print(f"   {ruta_final}")
        print(f"\n💡 Para usar en otros scrapers:")
        print(f"   archivo = '{os.path.basename(ruta_final)}'")
        
        return ruta_final
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nVerifica que:")
        print("  • Los archivos de extracción y normalización estén disponibles")
        print("  • El directorio data/ sea accesible")
        print("  • Crawl4AI esté funcionando correctamente")
        return None


if __name__ == "__main__":
    result = asyncio.run(main())
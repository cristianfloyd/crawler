#!/usr/bin/env python3
"""
Script de ejecución rápida del Scraper MVP
Ejecuta scraping y muestra resultados inmediatos

Autor: Sistema RAG MVP
Fecha: 2025-07-26
"""

import os
import json
import sys
from datetime import datetime
from scraper_materias_obligatorias import ScraperMateriasObligatorias

def mostrar_banner():
    """Muestra banner inicial"""
    print("🕷️" + "=" * 60)
    print("   SCRAPER MVP - MATERIAS OBLIGATORIAS LCD")
    print("   Sistema RAG con Horarios - Día 2")
    print("=" * 62)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def mostrar_resumen_detallado(materias_por_periodo, stats):
    """Muestra resumen detallado de los resultados"""
    print("📊 RESUMEN DETALLADO")
    print("-" * 30)
    
    print(f"📚 Total materias extraídas: {stats['total_materias']}")
    print(f"📅 Períodos académicos: {stats['total_periodos']}")
    print(f"🏢 Departamentos únicos: {len(stats['departamentos_unicos'])}")
    print(f"🔗 Materias con URLs: {stats['urls_horarios']['con_url']}")
    print()
    
    # Detalles por período
    print("📋 MATERIAS POR PERÍODO:")
    for periodo, cantidad in stats['materias_por_periodo'].items():
        print(f"   • {periodo}: {cantidad} materias")
    print()
    
    # Departamentos detectados
    print("🏢 DEPARTAMENTOS DETECTADOS:")
    for dept in sorted(stats['departamentos_unicos']):
        print(f"   • {dept}")
    print()
    
    # Tipos de materia
    print("📖 TIPOS DE MATERIA:")
    for tipo, cantidad in stats['tipos_materia'].items():
        if cantidad > 0:
            print(f"   • {tipo.title()}: {cantidad}")
    print()

def mostrar_ejemplos_materias(materias_por_periodo):
    """Muestra ejemplos de materias extraídas"""
    print("🔍 EJEMPLOS DE MATERIAS EXTRAÍDAS")
    print("-" * 35)
    
    count = 0
    for periodo, materias in materias_por_periodo.items():
        if count >= 3:  # Mostrar máximo 3 ejemplos
            break
            
        for materia in materias[:2]:  # 2 por período
            if count >= 3:
                break
                
            print(f"\n📝 Ejemplo {count + 1}:")
            print(f"   Nombre: {materia['nombre']}")
            print(f"   Tipo: {materia['tipo']}")
            print(f"   Departamento: {materia['departamento']['codigo']} - {materia['departamento']['nombre']}")
            print(f"   Período: {materia['periodo']['periodo_completo']}")
            print(f"   ID: {materia['id']}")
            if materia['departamento']['url_horarios']:
                print(f"   URL Horarios: {materia['departamento']['url_horarios'][:50]}...")
            count += 1
    print()

def verificar_calidad_datos(stats):
    """Verifica y reporta la calidad de los datos"""
    print("✅ VERIFICACIÓN DE CALIDAD")
    print("-" * 28)
    
    # Checks de calidad
    checks = {
        "materias_suficientes": stats['total_materias'] >= 20,
        "periodos_2025": stats['total_periodos'] >= 2,
        "departamentos_multiples": len(stats['departamentos_unicos']) >= 3,
        "urls_disponibles": stats['urls_horarios']['con_url'] > 0,
        "sin_errores_criticos": len(stats['errores']) == 0
    }
    
    for check, resultado in checks.items():
        status = "✅" if resultado else "❌"
        descripcion = {
            "materias_suficientes": f"Materias suficientes (≥20): {stats['total_materias']}",
            "periodos_2025": f"Períodos 2025 detectados: {stats['total_periodos']}",
            "departamentos_multiples": f"Múltiples departamentos: {len(stats['departamentos_unicos'])}",
            "urls_disponibles": f"URLs de horarios: {stats['urls_horarios']['con_url']}",
            "sin_errores_criticos": f"Sin errores críticos: {len(stats['errores'])} errores"
        }
        print(f"   {status} {descripcion[check]}")
    
    calidad_general = sum(checks.values()) / len(checks) * 100
    print(f"\n🎯 Calidad general: {calidad_general:.1f}%")
    
    if calidad_general >= 80:
        print("🎉 ¡Datos de alta calidad! Listos para RAG")
    elif calidad_general >= 60:
        print("⚠️  Datos de calidad media. Revisar problemas")
    else:
        print("🚨 Datos de baja calidad. Requiere ajustes")
    
    print()
    return calidad_general

def generar_reporte_markdown(materias_por_periodo, stats, archivos):
    """Genera reporte en Markdown"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""# 📊 Reporte Scraping - Materias Obligatorias LCD

**Fecha:** {timestamp}  
**Sistema:** MVP RAG con Horarios  
**Fuente:** https://lcd.exactas.uba.ar/materias-obligatorias/

## 🎯 Resumen Ejecutivo

- **Total materias:** {stats['total_materias']}
- **Períodos académicos:** {stats['total_periodos']} (año 2025)
- **Departamentos:** {len(stats['departamentos_unicos'])}
- **URLs con horarios:** {stats['urls_horarios']['con_url']}

## 📅 Materias por Período

"""
    
    for periodo, cantidad in stats['materias_por_periodo'].items():
        markdown += f"- **{periodo}:** {cantidad} materias\n"
    
    markdown += f"""
## 🏢 Departamentos Detectados

"""
    for dept in sorted(stats['departamentos_unicos']):
        markdown += f"- {dept}\n"
    
    markdown += f"""
## 📁 Archivos Generados

- **Datos:** `{archivos[0]}`
- **Estadísticas:** `{archivos[1]}`
- **Reporte:** `reporte_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md`

## 🔍 Ejemplo de Datos Extraídos

```json
{json.dumps(list(materias_por_periodo.values())[0][0] if materias_por_periodo else {}, indent=2, ensure_ascii=False)[:500]}...
```

## 🎯 Próximos Pasos

1. ✅ Scraping materias obligatorias completado
2. 🔄 Desarrollar enriquecimiento con horarios detallados
3. 🔄 Scraper materias optativas 2025
4. 🔄 Integración con sistema RAG
5. 🔄 Testing y validación

---
*Generado automáticamente por Scraper MVP*
"""
    
    archivo_reporte = f"reporte_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    return archivo_reporte

def main():
    """Función principal de ejecución rápida"""
    mostrar_banner()
    
    try:
        # 1. Crear e inicializar scraper
        print("🔧 Inicializando scraper...")
        scraper = ScraperMateriasObligatorias()
        
        # 2. Ejecutar scraping completo
        print("🕷️  Ejecutando scraping...")
        exito = scraper.ejecutar_scraping_completo()
        
        if not exito:
            print("❌ Error en el scraping. Revisa los logs.")
            return 1
        
        # 3. Leer resultados generados
        print("📖 Leyendo resultados...")
        
        # Buscar archivos más recientes
        archivos_json = [f for f in os.listdir('.') if f.startswith('materias_obligatorias_') and f.endswith('.json')]
        if not archivos_json:
            print("❌ No se encontraron archivos de resultados.")
            return 1
        
        archivo_mas_reciente = sorted(archivos_json)[-1]
        archivo_stats = archivo_mas_reciente.replace('materias_obligatorias_', 'stats_obligatorias_')
        
        with open(archivo_mas_reciente, 'r', encoding='utf-8') as f:
            materias_por_periodo = json.load(f)
        
        with open(archivo_stats, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        # 4. Mostrar resultados detallados
        mostrar_resumen_detallado(materias_por_periodo, stats)
        mostrar_ejemplos_materias(materias_por_periodo)
        calidad = verificar_calidad_datos(stats)
        
        # 5. Generar reporte
        print("📝 Generando reporte...")
        archivo_reporte = generar_reporte_markdown(materias_por_periodo, stats, [archivo_mas_reciente, archivo_stats])
        
        # 6. Resumen final
        print("🎉 SCRAPING COMPLETADO EXITOSAMENTE")
        print("=" * 40)
        print(f"📊 {stats['total_materias']} materias extraídas")
        print(f"📁 Archivos generados:")
        print(f"   • {archivo_mas_reciente}")
        print(f"   • {archivo_stats}")
        print(f"   • {archivo_reporte}")
        print(f"🎯 Calidad: {calidad:.1f}%")
        
        if calidad >= 80:
            print("\n✅ ¡Listos para el Día 3: Procesamiento de Datos!")
            print("💡 Próximo paso: Desarrollar enriquecimiento con horarios")
        else:
            print("\n⚠️  Revisar calidad antes de continuar")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
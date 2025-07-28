#!/usr/bin/env python3
"""
Validador usando el HTML real de materias obligatorias
Usa el HTML proporcionado para validar el scraper

Autor: Sistema RAG MVP
Fecha: 2025-07-26
"""

import json
from datetime import datetime
from scraper_materias_obligatorias import ScraperMateriasObligatorias

# HTML real proporcionado (simplificado para el test)
HTML_REAL = '''
<h2>Verano 2025</h2>
<table class="table">
    <tbody>
        <tr>
            <th>Materia</th>
            <th>Departamento</th>
            <th>Página web</th>
        </tr>
        <tr>
            <td>Algebra I</td>
            <td>Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=v"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Análisis I</td>
            <td>Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=v"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Laboratorio de Datos</td>
            <td>Departamento de Computación</td>
            <td><a href="https://www.dc.uba.ar/cursada-de-grado/"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
    </tbody>
</table>

<h2>1er cuatrimestre 2025</h2>
<table class="table">
    <tbody>
        <tr>
            <th>Materia</th>
            <th>Departamento</th>
            <th>Página web</th>
        </tr>
        <tr>
            <td>Álgebra I</td>
            <td>Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=1"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Algebra Lineal Computacional</td>
            <td>Departamento de Computación, Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=1"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Algoritmos y Estructuras de Datos I</td>
            <td>Departamento de Computación</td>
            <td><a href="https://www.dc.uba.ar/cursada-de-grado/"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Algoritmos y Estructuras de Datos II</td>
            <td>Departamento de Computación</td>
            <td><a href="https://www.dc.uba.ar/cursada-de-grado/"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Algoritmos y Estructuras de Datos III</td>
            <td>Departamento de Computación</td>
            <td><a href="https://www.dc.uba.ar/cursada-de-grado/"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Intr. a la Estadística y Ciencia de Datos</td>
            <td>Instituto de Cálculo</td>
            <td><a href="https://ic.fcen.uba.ar/actividades-academicas/formacion/materias"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Física 1 (Q) - Electiva de Intro. a las Cs. Naturales</td>
            <td>Departamento de Física</td>
            <td><a href="https://www.df.uba.ar/es/docentes/distribucion-de-horarios-y-docentes"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Probabilidad</td>
            <td>Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=1"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Tesis de Licenciatura</td>
            <td>Instituto de Cálculo</td>
            <td><a href="https://ic.fcen.uba.ar/actividades-academicas/formacion/materias"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
    </tbody>
</table>

<h2>2do cuatrimestre 2025</h2>
<table class="table">
    <tbody>
        <tr>
            <th>Materia</th>
            <th>Departamento</th>
            <th>Página web</th>
        </tr>
        <tr>
            <td>Análisis II</td>
            <td>Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=2"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Intr. a la Investigación Operativa y Optimización</td>
            <td>Departamento de Matemática</td>
            <td><a href="https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=2"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
        <tr>
            <td>Laboratorio de Datos</td>
            <td>Departamento de Computación, Departamento de Física, Instituto de Cálculo</td>
            <td><a href="https://www.ic.fcen.uba.ar/actividades-academicas/formacion/cursos"><img src="/programs/imagenes/website.png" width="24px"></a></td>
        </tr>
    </tbody>
</table>
'''

def ejecutar_validacion_completa():
    """Ejecuta validación completa con HTML real"""
    print("🔍 VALIDACIÓN CON HTML REAL")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Crear scraper
    scraper = ScraperMateriasObligatorias()
    
    # 2. Procesar HTML real
    print("🕷️  Procesando HTML real...")
    materias_por_periodo = scraper.extraer_materias_por_periodo(HTML_REAL)
    
    # 3. Validar resultados
    print("✅ Validando resultados...")
    stats = scraper.validar_materias_extraidas(materias_por_periodo)
    
    # 4. Mostrar resumen
    print("📊 RESULTADOS DE LA VALIDACIÓN")
    print("-" * 35)
    print(f"✅ Períodos detectados: {stats['total_periodos']}")
    print(f"✅ Total materias: {stats['total_materias']}")
    print(f"✅ Departamentos únicos: {len(stats['departamentos_unicos'])}")
    print(f"✅ Materias con URLs: {stats['urls_horarios']['con_url']}")
    print()
    
    # 5. Detalles por período
    print("📋 MATERIAS POR PERÍODO:")
    for periodo, cantidad in stats['materias_por_periodo'].items():
        print(f"   • {periodo}: {cantidad} materias")
    print()
    
    # 6. Departamentos detectados
    print("🏢 DEPARTAMENTOS DETECTADOS:")
    for dept in sorted(stats['departamentos_unicos']):
        codigo_dept = dept
        nombre_completo = {
            'DM': 'Departamento de Matemática',
            'DC': 'Departamento de Computación', 
            'DF': 'Departamento de Física',
            'IC': 'Instituto de Cálculo'
        }.get(dept, 'Desconocido')
        print(f"   • {codigo_dept}: {nombre_completo}")
    print()
    
    # 7. Mostrar ejemplos de materias
    print("🔍 EJEMPLOS DE MATERIAS PROCESADAS:")
    print("-" * 40)
    
    count = 0
    for periodo, materias in materias_por_periodo.items():
        if count >= 5:  # Mostrar máximo 5 ejemplos
            break
            
        print(f"\n📚 {periodo}:")
        for i, materia in enumerate(materias[:3]):  # 3 por período
            if count >= 5:
                break
            print(f"   {i+1}. {materia['nombre']}")
            print(f"      Tipo: {materia['tipo']}")
            print(f"      Depto: {materia['departamento']['codigo']}")
            print(f"      ID: {materia['id']}")
            count += 1
    print()
    
    # 8. Verificar casos específicos importantes
    print("🎯 VERIFICACIONES ESPECÍFICAS:")
    print("-" * 32)
    
    # Buscar materias específicas importantes
    materias_importantes = [
        "Algoritmos y Estructuras de Datos I",
        "Álgebra I", 
        "Probabilidad",
        "Tesis de Licenciatura",
        "Laboratorio de Datos"
    ]
    
    todas_las_materias = []
    for materias in materias_por_periodo.values():
        todas_las_materias.extend(materias)
    
    for materia_importante in materias_importantes:
        encontrada = False
        for materia in todas_las_materias:
            if materia_importante.lower() in materia['nombre'].lower():
                print(f"   ✅ {materia_importante}: ENCONTRADA")
                encontrada = True
                break
        if not encontrada:
            print(f"   ❌ {materia_importante}: NO ENCONTRADA")
    print()
    
    # 9. Verificar URLs de departamentos principales
    print("🔗 VERIFICACIÓN DE URLs:")
    print("-" * 25)
    
    urls_encontradas = set()
    for materias in materias_por_periodo.values():
        for materia in materias:
            url = materia['departamento']['url_horarios']
            if url:
                urls_encontradas.add(url)
    
    urls_esperadas = [
        "dc.uba.ar",
        "web.dm.uba.ar", 
        "ic.fcen.uba.ar",
        "df.uba.ar"
    ]
    
    for url_esperada in urls_esperadas:
        encontrada = any(url_esperada in url for url in urls_encontradas)
        status = "✅" if encontrada else "❌"
        print(f"   {status} {url_esperada}")
    print()
    
    # 10. Calcular puntuación de calidad
    puntuacion = 0
    total_checks = 6
    
    if stats['total_materias'] >= 10: puntuacion += 1
    if stats['total_periodos'] >= 3: puntuacion += 1  
    if len(stats['departamentos_unicos']) >= 3: puntuacion += 1
    if stats['urls_horarios']['con_url'] >= 10: puntuacion += 1
    if len([m for materias in materias_por_periodo.values() for m in materias if m['tipo'] == 'obligatoria']) >= 8: puntuacion += 1
    if len(urls_encontradas) >= 3: puntuacion += 1
    
    calidad = (puntuacion / total_checks) * 100
    
    print("🎯 PUNTUACIÓN FINAL:")
    print("-" * 20)
    print(f"   Puntuación: {puntuacion}/{total_checks}")
    print(f"   Calidad: {calidad:.1f}%")
    
    if calidad >= 85:
        print("   🎉 ¡EXCELENTE! Scraper funcionando perfectamente")
        print("   ✅ Listo para usar en producción")
    elif calidad >= 70:
        print("   👍 BUENO. Scraper funcionando bien")
        print("   ⚠️  Algunos ajustes menores recomendados")
    else:
        print("   🚨 REQUIERE MEJORAS. Problemas detectados")
        print("   ❌ Revisar lógica de extracción")
    
    print()
    
    # 11. Guardar resultados de validación
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_validacion = f"validacion_html_real_{timestamp}.json"
    
    resultado_validacion = {
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "materias_por_periodo": materias_por_periodo,
        "calidad_porcentaje": calidad,
        "puntuacion": f"{puntuacion}/{total_checks}",
        "urls_encontradas": list(urls_encontradas),
        "materias_totales": len(todas_las_materias)
    }
    
    with open(archivo_validacion, 'w', encoding='utf-8') as f:
        json.dump(resultado_validacion, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Resultados guardados en: {archivo_validacion}")
    print()
    
    # 12. Recomendaciones para siguiente paso
    print("🚀 PRÓXIMOS PASOS RECOMENDADOS:")
    print("-" * 35)
    
    if calidad >= 85:
        print("   1. ✅ Scraper base funcionando excelente")
        print("   2. 🔄 Desarrollar enriquecimiento con horarios detallados")
        print("   3. 🔄 Crear scraper para optativas 2025")
        print("   4. 🔄 Integrar con sistema RAG")
    else:
        print("   1. 🔧 Ajustar lógica de extracción")
        print("   2. 🧪 Ejecutar más tests")
        print("   3. 🔄 Re-validar con HTML completo")
    
    return materias_por_periodo, stats, calidad

def main():
    """Función principal"""
    materias, stats, calidad = ejecutar_validacion_completa()
    
    print("=" * 60)
    print("🏁 VALIDACIÓN COMPLETADA")
    print(f"📊 {stats['total_materias']} materias procesadas correctamente")
    print(f"🎯 Calidad: {calidad:.1f}%")
    
    if calidad >= 85:
        print("🎉 ¡SCRAPER LISTO PARA PRODUCCIÓN!")
    
    return 0

if __name__ == "__main__":
    exit(main())
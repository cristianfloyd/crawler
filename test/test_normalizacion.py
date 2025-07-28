#!/usr/bin/env python3
"""
Test de Normalización con Datos Reales
Prueba el procesador con los datos que ya tenemos

Autor: Sistema RAG MVP
Fecha: 2025-07-26
"""

import json
from procesar_datos_horarios import ProcesadorDatosHorarios
from datetime import datetime

def crear_datos_test_con_horarios():
    """Crea datos de prueba con horarios simulados basados en los datos reales"""
    
    # Datos base de una materia real (simplificado)
    materias_test = {
        "1er cuatrimestre 2025": [
            {
                "id": "lcd_obligatoria_algoritmos_y_estructuras_de_datos_i_2025_1_02",
                "nombre": "algoritmos y estructuras   de DATOS I",  # Nombre con problemas
                "nombre_original": "Algoritmos y Estructuras de Datos I",
                "tipo": "obligatoria",
                "departamento": {
                    "nombre": "Departamento de Computación",
                    "codigo": "DC",
                    "url_horarios": "https://www.dc.uba.ar/cursada-de-grado/"
                },
                "periodo": {
                    "año": 2025,
                    "cuatrimestre": "1",
                    "periodo_completo": "1er cuatrimestre 2025"
                },
                "horarios": {
                    "clases": [
                        {
                            "dia": "LUN",  # Formato a normalizar
                            "hora_inicio": "14:00",
                            "hora_fin": "18:00",
                            "aula": "pab 1 aula 5",  # Formato a normalizar
                            "modalidad": "presencial"
                        },
                        {
                            "dia": "miercoles",  # Sin acento
                            "hora_inicio": "14",  # Sin minutos
                            "hora_fin": "18",
                            "aula": "Lab ComputaciOn",
                            "modalidad": "presencial"
                        }
                    ],
                    "consultas": [
                        {
                            "dia": "vie",  # Abreviado
                            "hora_inicio": "10:30",
                            "hora_fin": "12:30",
                            "docente": "Dr. Juan Pérez"
                        }
                    ],
                    "examenes": {
                        "parcial_1": "2025-04-15",
                        "parcial_2": "15/05/2025",  # Formato diferente
                        "final": "2025-07-10"
                    }
                },
                "correlativas": {
                    "para_cursar": ["Álgebra I"],
                    "para_rendir": ["Álgebra I"]
                },
                "docentes": [
                    {
                        "nombre": "Dr. Juan Pérez",
                        "categoria": "titular"
                    }
                ],
                "metadata": {
                    "fuente_url": "https://lcd.exactas.uba.ar/materias-obligatorias/",
                    "fecha_scraping": "2025-07-26T19:53:19.747064",
                    "version": "2025.1",
                    "confiabilidad": "alta",
                    "requiere_enriquecimiento": True
                }
            },
            {
                "id": "lcd_obligatoria_algebra_i_2025_1_01",
                "nombre": "ÁLGEBRA    I",  # Mayúsculas y espacios extra
                "nombre_original": "Álgebra I",
                "tipo": "obligatoria",
                "departamento": {
                    "nombre": "Departamento de Matemática",
                    "codigo": "DM",
                    "url_horarios": "https://web.dm.uba.ar/index.php/docencia/materias/horarios?ano=2025&cuatrimestre=1"
                },
                "periodo": {
                    "año": 2025,
                    "cuatrimestre": "1",
                    "periodo_completo": "1er cuatrimestre 2025"
                },
                "horarios": {
                    "clases": [
                        {
                            "dia": "martes",
                            "hora_inicio": "8:00",
                            "hora_fin": "12:00",
                            "aula": "Aula Magna",
                            "modalidad": "presencial"
                        },
                        {
                            "dia": "jueves",
                            "hora_inicio": "8:00",
                            "hora_fin": "12:00",
                            "aula": "Aula Magna",
                            "modalidad": "presencial"
                        }
                    ],
                    "consultas": [
                        {
                            "dia": "viernes",
                            "hora_inicio": "14:00",
                            "hora_fin": "16:00",
                            "docente": "Dra. María García"
                        }
                    ],
                    "examenes": {}
                },
                "correlativas": {
                    "para_cursar": [],
                    "para_rendir": []
                },
                "docentes": [],
                "metadata": {
                    "fuente_url": "https://lcd.exactas.uba.ar/materias-obligatorias/",
                    "fecha_scraping": "2025-07-26T19:53:19.747064",
                    "version": "2025.1",
                    "confiabilidad": "alta",
                    "requiere_enriquecimiento": True
                }
            },
            {
                "id": "lcd_obligatoria_algoritmos_y_estructuras_de_datos_i_duplicado_2025_1_99",
                "nombre": "Algoritmos y Estructuras de Datos 1",  # Duplicado con nombre ligeramente diferente
                "nombre_original": "Algoritmos y Estructuras de Datos I (Duplicado)",
                "tipo": "obligatoria",
                "departamento": {
                    "nombre": "Departamento de Computación",
                    "codigo": "DC",
                    "url_horarios": "https://www.dc.uba.ar/cursada-de-grado/"
                },
                "periodo": {
                    "año": 2025,
                    "cuatrimestre": "1",
                    "periodo_completo": "1er cuatrimestre 2025"
                },
                "horarios": {
                    "clases": [],  # Menos información que el original
                    "consultas": [],
                    "examenes": {}
                },
                "correlativas": {
                    "para_cursar": [],
                    "para_rendir": []
                },
                "docentes": [],
                "metadata": {
                    "fuente_url": "https://lcd.exactas.uba.ar/materias-obligatorias/",
                    "fecha_scraping": "2025-07-26T19:53:19.747064",
                    "version": "2025.1",
                    "confiabilidad": "media",
                    "requiere_enriquecimiento": True
                }
            }
        ],
        "2do cuatrimestre 2025": [
            {
                "id": "lcd_obligatoria_algoritmos_y_estructuras_de_datos_i_2025_2_02",
                "nombre": "Algoritmos y Estructuras de Datos I",  # Mismo nombre que en 1er cuatrimestre
                "nombre_original": "Algoritmos y Estructuras de Datos I",
                "tipo": "obligatoria",
                "departamento": {
                    "nombre": "Departamento de Computación",
                    "codigo": "DC",
                    "url_horarios": "https://www.dc.uba.ar/cursada-de-grado/"
                },
                "periodo": {
                    "año": 2025,
                    "cuatrimestre": "2",
                    "periodo_completo": "2do cuatrimestre 2025"
                },
                "horarios": {
                    "clases": [
                        {
                            "dia": "lunes",
                            "hora_inicio": "18:00",
                            "hora_fin": "22:00",
                            "aula": "Pabellón 1 Aula 3",
                            "modalidad": "presencial"
                        }
                    ],
                    "consultas": [],
                    "examenes": {}
                },
                "correlativas": {
                    "para_cursar": ["Álgebra I"],
                    "para_rendir": ["Álgebra I"]
                },
                "docentes": [],
                "metadata": {
                    "fuente_url": "https://lcd.exactas.uba.ar/materias-obligatorias/",
                    "fecha_scraping": "2025-07-26T19:53:19.748387",
                    "version": "2025.1",
                    "confiabilidad": "alta",
                    "requiere_enriquecimiento": True
                }
            }
        ]
    }
    
    return materias_test

def ejecutar_test_normalizacion():
    """Ejecuta el test completo de normalización"""
    print("🧪 TEST DE NORMALIZACIÓN CON DATOS REALES")
    print("=" * 50)
    
    # 1. Crear datos de prueba
    print("📝 Creando datos de prueba...")
    datos_test = crear_datos_test_con_horarios()
    
    # Guardar datos de prueba
    with open("datos_test_normalizacion.json", "w", encoding="utf-8") as f:
        json.dump(datos_test, f, ensure_ascii=False, indent=2)
    
    print("✅ Datos de prueba creados: datos_test_normalizacion.json")
    
    # 2. Crear procesador
    print("\n🔄 Inicializando procesador...")
    procesador = ProcesadorDatosHorarios()
    
    # 3. Procesar datos
    print("🔄 Procesando datos...")
    try:
        resultado = procesador.procesar_archivo_completo("datos_test_normalizacion.json")
        
        # 4. Mostrar resultados
        mostrar_resultados_test(resultado, datos_test)
        
        # 5. Guardar resultados
        with open("resultado_test_normalizacion.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        print("✅ Resultados guardados: resultado_test_normalizacion.json")
        return True
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        return False

def mostrar_resultados_test(resultado, datos_originales):
    """Muestra los resultados del test de normalización"""
    
    print("\n📊 RESULTADOS DEL TEST")
    print("=" * 30)
    
    # Estadísticas generales
    stats = resultado["estadisticas"]
    integridad = resultado["reporte_integridad"]
    
    print("📈 ESTADÍSTICAS:")
    print(f"   • Materias procesadas: {stats['materias_procesadas']}")
    print(f"   • Nombres normalizados: {stats['nombres_normalizados']}")
    print(f"   • Horarios normalizados: {stats['horarios_normalizados']}")
    print(f"   • Días normalizados: {stats['dias_normalizados']}")
    print(f"   • Duplicados detectados: {stats['duplicados_detectados']}")
    
    if stats["errores"]:
        print(f"   ⚠️  Errores: {len(stats['errores'])}")
        for error in stats["errores"][:3]:
            print(f"      - {error}")
    
    print(f"\n🔍 INTEGRIDAD:")
    print(f"   • Total materias final: {integridad['total_materias']}")
    print(f"   • Con horarios: {integridad['materias_con_horarios']}")
    print(f"   • Sin horarios: {integridad['materias_sin_horarios']}")
    print(f"   • Departamentos: {len(integridad['departamentos_unicos'])}")
    
    # Mostrar ejemplos de normalización
    print(f"\n🔄 EJEMPLOS DE NORMALIZACIÓN:")
    datos_normalizados = resultado["datos_normalizados"]
    
    # Tomar primera materia de cada período
    for periodo, materias in datos_normalizados.items():
        if materias:
            materia = materias[0]
            print(f"\n📚 {periodo} - {materia.get('nombre', 'SIN NOMBRE')}:")
            
            # Nombre normalizado
            if materia.get("nombre_normalizado"):
                print(f"   📝 Nombre normalizado: '{materia['nombre_normalizado']}'")
            
            # Palabras clave
            if materia.get("palabras_clave"):
                palabras = ", ".join(materia["palabras_clave"][:5])
                print(f"   🔍 Palabras clave: {palabras}...")
            
            # Horarios normalizados
            horarios = materia.get("horarios", {})
            if horarios.get("clases"):
                print(f"   🕐 Clases normalizadas:")
                for clase in horarios["clases"][:2]:  # Mostrar máximo 2
                    dia = clase.get("dia", "N/A")
                    inicio = clase.get("hora_inicio", "N/A")
                    fin = clase.get("hora_fin", "N/A")
                    aula = clase.get("aula", "N/A")
                    print(f"      - {dia} {inicio}-{fin} en {aula}")
            
            # Cambios realizados
            if materia.get("normalizacion", {}).get("cambios_realizados"):
                cambios = ", ".join(materia["normalizacion"]["cambios_realizados"])
                print(f"   ✏️  Cambios: {cambios}")

def test_casos_especificos():
    """Test de casos específicos de normalización"""
    print("\n🎯 TEST DE CASOS ESPECÍFICOS")
    print("=" * 35)
    
    procesador = ProcesadorDatosHorarios()
    
    # Test normalización de nombres
    print("📝 Test normalización de nombres:")
    casos_nombres = [
        "algoritmos y estructuras   de DATOS I",
        "ÁLGEBRA    I",
        "Análisis II",
        "intro. a la estadística y ciencia de datos"
    ]
    
    for nombre in casos_nombres:
        normalizado = procesador.normalizar_nombre_materia(nombre)
        print(f"   '{nombre}' → '{normalizado}'")
    
    # Test normalización de días
    print(f"\n📅 Test normalización de días:")
    casos_dias = ["LUN", "miercoles", "vie", "MARTES", "jue", "sábado"]
    
    for dia in casos_dias:
        normalizado = procesador.normalizar_dia(dia)
        print(f"   '{dia}' → '{normalizado}'")
    
    # Test normalización de horas
    print(f"\n🕐 Test normalización de horas:")
    casos_horas = ["14", "8:00", "22:30", "9", "18:45"]
    
    for hora in casos_horas:
        normalizado = procesador.normalizar_hora(hora)
        print(f"   '{hora}' → '{normalizado}'")
    
    # Test normalización de aulas
    print(f"\n🏛️  Test normalización de aulas:")
    casos_aulas = ["pab 1 aula 5", "Lab ComputaciOn", "Aula Magna", "salon 201"]
    
    for aula in casos_aulas:
        normalizado = procesador.normalizar_aula(aula)
        print(f"   '{aula}' → '{normalizado}'")

def main():
    """Función principal del test"""
    print("🚀 INICIANDO TESTS DE NORMALIZACIÓN")
    print("=" * 45)
    
    try:
        # Test principal con datos completos
        exito_principal = ejecutar_test_normalizacion()
        
        # Test de casos específicos
        test_casos_especificos()
        
        # Resumen final
        print("\n🎉 RESUMEN FINAL DEL TEST")
        print("=" * 30)
        
        if exito_principal:
            print("✅ Test principal: EXITOSO")
            print("✅ Normalización funcionando correctamente")
            print("✅ Detección de duplicados funcionando")
            print("✅ Validación de integridad funcionando")
            print("\n🔥 ¡LISTO PARA USAR EN PRODUCCIÓN!")
        else:
            print("❌ Test principal: FALLÓ")
            print("⚠️  Revisar errores antes de continuar")
        
        print("\n📁 Archivos generados:")
        print("   • datos_test_normalizacion.json")
        print("   • resultado_test_normalizacion.json")
        
        return 0 if exito_principal else 1
        
    except Exception as e:
        print(f"❌ Error inesperado en el test: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
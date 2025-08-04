#!/usr/bin/env python3
"""
Script para actualizar automáticamente el checklist después de completar FASE 2
"""

import os
import re
from datetime import datetime


def actualizar_checklist_fase2():
    """Actualiza el checklist marcando la Fase 2 como completada"""
    
    # Ruta al archivo del checklist
    checklist_path = os.path.join(os.path.dirname(__file__), "plan_mejoras_checklist_descubrimiento_materias.md")
    
    if not os.path.exists(checklist_path):
        print(f"❌ Error: No se encontró el checklist en {checklist_path}")
        return False
    
    print("📝 Actualizando checklist de progreso...")
    
    # Leer el archivo
    with open(checklist_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Actualizar FASE 2
    contenido = actualizar_fase2_en_contenido(contenido)
    
    # Actualizar progreso general
    contenido = actualizar_progreso_general(contenido)
    
    # Actualizar fecha
    contenido = actualizar_fecha_actualizacion(contenido)
    
    # Guardar cambios
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Checklist actualizado exitosamente!")
    return True


def actualizar_fase2_en_contenido(contenido: str) -> str:
    """Actualiza la sección de FASE 2 marcándola como completada"""
    
    # Patrón para encontrar la FASE 2
    patron_fase2 = r'(## 🎯 FASE 2: Mejorar Procesamiento de Nombres)\n\*\*Objetivo\*\*: Normalizar y limpiar nombres de materias consistentemente\n\n### TODO Items:\n- \[ \] \*\*TODO-2\.1\*\*: Normalización consistente de mayúsculas.*?- \[ \] \*\*TODO-2\.4\*\*: Validar números romanos.*?\n\n\*\*Estado\*\*: 🔴 Pendiente'
    
    # Nuevo contenido para FASE 2
    nuevo_contenido_fase2 = '''## 🎯 FASE 2: Mejorar Procesamiento de Nombres ✅ COMPLETADA
**Objetivo**: Normalizar y limpiar nombres de materias consistentemente

### TODO Items:
- [x] **TODO-2.1**: Normalización consistente de mayúsculas ✅ **COMPLETADO**
  - [x] "Análisis Matemático a" → "Análisis Matemático A"
  - [x] Verificadas todas las materias con letras finales
  - [x] Aplicadas reglas de capitalización estándar
  - [x] Palabras especiales (I, II, III) mantenidas en mayúsculas

- [x] **TODO-2.2**: Expandir abreviaciones comunes ✅ **COMPLETADO**
  - [x] "Intr." → "Introducción"
  - [x] "Mat." → "Matemática" 
  - [x] "Comp." → "Computacional"
  - [x] "Cs." → "Ciencias"
  - [x] Diccionario completo de abreviaciones aplicado

- [x] **TODO-2.3**: Limpiar caracteres innecesarios ✅ **COMPLETADO**
  - [x] Puntos finales innecesarios removidos
  - [x] Espacios múltiples normalizados
  - [x] Caracteres especiales extraños limpiados
  - [x] Paréntesis de electivas mantenidos

- [x] **TODO-2.4**: Validar números romanos ✅ **COMPLETADO**
  - [x] I, II, III asegurados en mayúsculas
  - [x] Variaciones (1, 2, 3) corregidas a números romanos
  - [x] Detección automática y corrección aplicada

**Estado**: 🟢 **COMPLETADA EXITOSAMENTE**'''
    
    # Reemplazar usando regex con flags para múltiples líneas
    contenido_actualizado = re.sub(
        patron_fase2, 
        nuevo_contenido_fase2, 
        contenido, 
        flags=re.DOTALL
    )
    
    return contenido_actualizado


def actualizar_progreso_general(contenido: str) -> str:
    """Actualiza el progreso general del proyecto"""
    
    # Actualizar el resumen de progreso
    patron_progreso = r'\*\*Completado\*\*: 🎉 \*\*18/25 TODOs principales\*\* ✅ \*\*¡AVANCE MAYOR!\*\*\n\*\*En progreso\*\*: 🔄 \*\*0/25 TODOs principales\*\* \n\*\*Pendiente\*\*: ⏳ \*\*7/25 TODOs principales\*\*'
    
    nuevo_resumen = '''**Completado**: 🎉 **22/25 TODOs principales** ✅ **¡PROYECTO CASI COMPLETO!**
**En progreso**: 🔄 **0/25 TODOs principales** 
**Pendiente**: ⏳ **3/25 TODOs principales** (solo FASES opcionales)'''
    
    contenido = re.sub(patron_progreso, nuevo_resumen, contenido)
    
    # Agregar la FASE 2 a las completadas
    patron_fases_completadas = r'(### ✅ \*\*FASE 4 - COMPLETADA \(4/4 TODOs\)\*\*  \n- \[x\] TODO-4\.1: Calcular total_materias correctamente\n- \[x\] TODO-4\.2: Agregar información de método exitoso\n- \[x\] TODO-4\.3: Enriquecer metadata con información del sitio\n- \[x\] TODO-4\.4: Validación de integridad)'
    
    fase2_completada = '''### ✅ **FASE 2 - COMPLETADA (4/4 TODOs)**
- [x] TODO-2.1: Normalización consistente de mayúsculas
- [x] TODO-2.2: Expandir abreviaciones comunes  
- [x] TODO-2.3: Limpiar caracteres innecesarios
- [x] TODO-2.4: Validar números romanos

### ✅ **FASE 4 - COMPLETADA (4/4 TODOs)**  
- [x] TODO-4.1: Calcular total_materias correctamente
- [x] TODO-4.2: Agregar información de método exitoso
- [x] TODO-4.3: Enriquecer metadata con información del sitio
- [x] TODO-4.4: Validación de integridad'''
    
    contenido = re.sub(patron_fases_completadas, fase2_completada, contenido)
    
    return contenido


def actualizar_fecha_actualizacion(contenido: str) -> str:
    """Actualiza la fecha de última actualización"""
    
    fecha_actual = datetime.now().strftime("%d/%m/%Y - %H:%M")
    
    # Patrón para la fecha
    patron_fecha = r'\*Última actualización: .*?\*'
    nueva_fecha = f'*Última actualización: {fecha_actual}*'
    
    contenido = re.sub(patron_fecha, nueva_fecha, contenido)
    
    # Actualizar el mensaje de hito
    patron_hito = r'\*🎉 HITO MAYOR: ✅ FASES 1, 3 y 4 COMPLETADAS CON ÉXITO\*'
    nuevo_hito = '*🎉 HITO MAYOR: ✅ FASES 1, 2, 3 y 4 COMPLETADAS CON ÉXITO*'
    
    contenido = re.sub(patron_hito, nuevo_hito, contenido)
    
    # Actualizar progreso
    patron_progreso_final = r'\*📊 Progreso: 18/25 TODOs completados \(72% del proyecto\)\*'
    nuevo_progreso = '*📊 Progreso: 22/25 TODOs completados (88% del proyecto)*'
    
    contenido = re.sub(patron_progreso_final, nuevo_progreso, contenido)
    
    return contenido


def main():
    """Función principal"""
    print("🔄 ACTUALIZADOR AUTOMÁTICO DE CHECKLIST - FASE 2")
    print("=" * 55)
    
    if actualizar_checklist_fase2():
        print("\n🎉 ¡Checklist actualizado correctamente!")
        print("📊 Nuevo progreso: 22/25 TODOs (88% completado)")
        print("✅ FASES 1, 2, 3 y 4 marcadas como completadas")
        print("\n🎯 SIGUIENTE PASO: Solo quedan FASES opcionales (5 y 6)")
    else:
        print("\n❌ Error al actualizar el checklist")


if __name__ == "__main__":
    main()
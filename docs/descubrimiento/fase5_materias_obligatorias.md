# FASE 5: Sistema de Enriquecimiento de Materias LCD

## Descripción

La Fase 5 enriquece los datos base de materias LCD extraídos en fases anteriores con información adicional sobre cuatrimestres, horarios y clasificaciones. Actualmente incluye la extracción de materias obligatorias y está diseñada para expandirse con otras clases de enriquecimiento.

## Arquitectura del Sistema

### Componentes Actuales
- **ExtractorMateriasObligatorias**: Extrae materias obligatorias por cuatrimestre
- **NormalizadorNombresMaterias**: Sistema de normalización inteligente integrado

### Componentes Futuros (Planificados)
- **ExtractorMateriasElectivas**: Materias electivas y opcionales
- **ExtractorHorarios**: Horarios específicos por materia
- **ClasificadorMaterias**: Clasificación automática por departamento/área

## Objetivos

- **Enriquecer** `data/materias_lcd_descubiertas.json` con datos de cuatrimestres y departamentos
- **Extraer** materias obligatorias de https://lcd.exactas.uba.ar/materias-obligatorias/
- **Organizar** datos por período académico (verano, primer, segundo cuatrimestre)
- **Normalizar** nombres usando sistema inteligente integrado
- **Validar** consistencia entre datos base y datos enriquecidos

## Estructura de Datos

### Archivo de Salida: `materias_obligatorias.json`

```json
{
  "cuatrimestres": {
    "verano_2025": [
      {
        "materia": "Nombre de la materia",
        "departamento": "Departamento responsable",
        "enlace": "URL del sitio de la materia"
      }
    ],
    "primer_cuatrimestre_2025": [...],
    "segundo_cuatrimestre_2025": [...]
  },
  "metadata": {
    "timestamp": "2025-08-05T...",
    "fuente": "https://lcd.exactas.uba.ar/materias-obligatorias/",
    "metodo": "crawl4ai_css_extraction",
    "version": "fase5_v2",
    "total_materias": 0
  }
}
```

### Datos de Entrada

**Archivo Principal**: `data/materias_lcd_descubiertas.json`
- Generado por `descubrir_materias_completo.py` (punto de entrada unificado)
- Contiene materias normalizadas por ciclo: CBC, segundo_ciclo, tercer_ciclo
- Formato estable con metadata completa y nombres ya normalizados

### Enriquecimiento de Datos Base

Las materias de `materias_lcd_descubiertas.json` se enriquecen con:
- **`cuatrimestre_disponible`**: Cuatrimestre donde se dicta la materia
- **`departamento_confirmado`**: Departamento oficial responsable
- **`enlace_horarios`**: URL para consultar horarios específicos
- **`categoria_materia`**: Obligatoria/Electiva/Optativa (futuro)
- **`prerrequisitos`**: Materias correlativas (futuro)

## Flujo de Ejecución

### Fase 5.1: Materias Obligatorias (Actual)
1. **Carga de Datos Base**: Lee `materias_lcd_descubiertas.json`
2. **Inicialización del Normalizador**: Carga sistema inteligente de normalización
3. **Extracción con CSS**: Usa `crawl4ai` con selectores CSS específicos
4. **Fallback HTML**: Análisis directo de HTML si falla CSS
5. **Normalización Inteligente**: Aplica normalización usando índice de materias base
6. **Validación**: Verifica integridad y consistencia de datos extraídos
7. **Guardado**: Genera `materias_obligatorias.json`
8. **Enriquecimiento**: Cruza datos con materias base usando matching inteligente
9. **Reporte**: Genera estadísticas detalladas de extracción y normalización

### Fases Futuras (Planificadas)
- **Fase 5.2**: Extracción de materias electivas y opcionales
- **Fase 5.3**: Extracción de horarios específicos por materia
- **Fase 5.4**: Clasificación automática y detección de prerrequisitos

## Uso

```bash
# Ejecutar Fase 5.1 completa (materias obligatorias)
python descubrimiento/enriquecer_materias_obligatorias.py

# Generar datos base actualizados (si es necesario)
python descubrimiento/descubrir_materias_completo.py

# Ejecutar normalización standalone (para testing)
python descubrimiento/normalizador_nombres_materias.py
```

## Archivos del Sistema

### Archivos de Entrada
- **`data/materias_lcd_descubiertas.json`**: Datos base normalizados (desde descubrir_materias_completo.py)
- **`data/materias.json`**: Archivo de referencia para normalización (usado por normalizador)

### Archivos Generados
- **`data/materias_obligatorias.json`**: Datos extraídos por cuatrimestre
- **`data/materias_enriquecidas.json`**: Materias base enriquecidas con datos de cuatrimestres
- **`debug_obligatorias.json`**: Debug de extracción CSS para troubleshooting

### Archivos Futuros (Planificados)
- **`data/materias_electivas.json`**: Materias electivas por departamento
- **`data/horarios_detallados.json`**: Horarios específicos por materia
- **`data/materias_completamente_enriquecidas.json`**: Dataset final consolidado

## Validaciones

- Campos requeridos: materia, departamento
- Longitud mínima de nombres
- Detección de datos incompletos
- Reporte de errores en consola

## Integración con el Sistema

### Integración Upstream
- **Entrada Principal**: `data/materias_lcd_descubiertas.json` (desde `descubrir_materias_completo.py`)
- **Normalizador**: `normalizador_nombres_materias.py` (sistema inteligente integrado)
- **Datos de Referencia**: `data/materias.json` (para índice de normalización)

### Integración Downstream
- **Salida Principal**: Datos enriquecidos para sistema RAG
- **Scrapers**: Información de cuatrimestres para scrapers específicos
- **Sistema de Horarios**: Base para extracción de horarios detallados

### Dependencias Técnicas
- **`crawl4ai`**: Motor de extracción web
- **Navegador Chromium**: Renderizado JavaScript
- **`normalizador_nombres_materias`**: Normalización inteligente de nombres
- **Python asyncio**: Ejecución asíncrona

## Roadmap y Expansión

### Fase 5.1 - Materias Obligatorias (✅ Completada - 5 Agosto 2025)
- ✅ Extracción por cuatrimestre
- ✅ Normalización inteligente integrada
- ✅ **Equivalencias CBC implementadas** (quimica, fisica, algebra, analisis)
- ✅ Enriquecimiento mejorado: 39.4% → **45.5%**
- ✅ 15/33 materias enriquecidas (+2 materias CBC)
- ✅ Validación y reportes completos

#### Mejoras de Normalización CBC:
- **`"quimica"` ↔ `"quimica general e inorganica"`**
- **`"fisica"` ↔ `"fisica i"`** 
- **`"algebra"` ↔ `"algebra i"`**
- **`"analisis matematico"` ↔ `"analisis matematico a"`**

#### Resultados Finales:
- **53 materias obligatorias** extraídas
- **15 materias LCD enriquecidas** con cuatrimestres
- **Matching bidireccional** CBC ↔ Obligatorias
- **Sistema listo para RAG** con datos consistentes

### Fase 5.2 - Materias Electivas (🔄 Planificada)
```python
class ExtractorMateriasElectivas:
    """Extrae materias electivas y opcionales por departamento"""
    def extraer_electivas_por_departamento(self):
        # Extraer de páginas específicas por departamento
        pass
```

### Fase 5.3 - Horarios Detallados (🔄 Planificada)
```python
class ExtractorHorariosDetallados:
    """Extrae horarios específicos por materia"""
    def extraer_horarios_por_materia(self, materia_id):
        # Seguir enlaces de materias_obligatorias.json
        pass
```

### Fase 5.4 - Clasificación Automática (🔄 Planificada)
```python
class ClasificadorMaterias:
    """Clasifica materias automáticamente"""
    def detectar_prerrequisitos(self):
        # Análisis de dependencias entre materias
        pass
```

## Estado Actual y Próximos Pasos

### 🏁 **CHECKPOINT - 5 Agosto 2025**
**Fase 5.1 COMPLETADA exitosamente**

#### ✅ Logros Alcanzados:
- Sistema de enriquecimiento funcional al 45.5%
- Equivalencias CBC implementadas y probadas
- Normalizador inteligente con 10 equivalencias activas
- Pipeline completo: Extracción → Normalización → Enriquecimiento
- Datos listos para integración con sistema RAG

#### 📊 Estadísticas Finales:
- **Materias procesadas**: 33/33 (100%)
- **Materias enriquecidas**: 15/33 (45.5%)
- **Equivalencias CBC**: 10 activas
- **Variaciones normalización**: 81 en índice

#### 📋 Archivos Generados:
- `materias_obligatorias.json`: 53 materias obligatorias
- `materias_lcd_enriquecidas.json`: Dataset final para RAG
- `test_equivalencias_cbc.py`: Suite de tests para equivalencias

### 🚀 **Próximos Pasos (Futuras Sesiones)**:
1. **Fase 5.2**: ExtractorMateriasElectivas 
2. **Fase 5.3**: ExtractorHorariosDetallados
3. **Optimización**: Mejorar matching al 60%+
4. **Integración RAG**: Conectar con sistema de consultas

## Mantenimiento

- **Periodicidad**: Ejecutar al inicio de cada cuatrimestre
- **Monitoreo**: Verificar cambios en estructura web de LCD
- **Actualización**: Ajustar selectores CSS si cambia el sitio
- **Validación**: Comprobar consistencia con `materias_lcd_descubiertas.json`
- **Normalizador**: Actualizar índice si se agregan nuevas materias base
- **Equivalencias**: Revisar y expandir equivalencias CBC según necesidad
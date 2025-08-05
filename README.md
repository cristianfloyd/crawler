# 🕷️ Crawler Universitario RAG - Sistema de Consultas Académicas

Sistema completo de web scraping y RAG (Retrieval-Augmented Generation) para extraer y consultar información académica de Licenciatura en Ciencias de Datos de la facultad de Exactas de la UBA.

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema integral que:
- **Descubre y mapea** sitios web académicos de diferentes departamentos
- **Extrae información** de materias, horarios y programas académicos
- **Crea un sistema RAG** para consultas inteligentes usando embeddings y FAISS
- **Proporciona una interfaz CLI** especializada para consultas de horarios

### 🎯 Estado Actual: MVP Funcional

TODO: refinar el descubrimiento


## 🏗️ Arquitectura del Sistema

```
│
├── 🗺️ DESCUBRIMIENTO     │ 🕷️ SCRAPING          │ 🔄 PROCESAMIENTO      │ 🤖 RAG SYSTEM
│   • Mapeo de sitios      │ • Scrapers específicos │ • Normalización       │ • Embeddings
│   • Análisis técnico     │ • Coordinación masiva  │ • Unificación         │ • FAISS indexing
│   • Priorización         │ • Validación           │ • Detección duplicados│ • CLI interface
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- 4GB RAM mínimo
- Conexión a internet estable

### Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd crawler

# Instalar dependencias
pip install -r requirements_scraper.txt

# Verificar instalación
python src/pipeline_rag_completo.py --help
```

### Dependencias Principales
- **crawl4ai>=0.3.0** - Web crawling con soporte AI y JavaScript
- **faiss-cpu>=1.7.4** - Base de datos vectorial para RAG
- **sentence-transformers>=2.2.2** - Embeddings de texto
- **beautifulsoup4>=4.12.0** - Parsing HTML
- **requests>=2.31.0** - HTTP requests

## 📚 Estructura del Proyecto

```
crawler/
├── 📁 descubrimiento/          # Descubrimiento y mapeo de sitios
│   ├── descubrir_sitios.py     # Script principal de descubrimiento
│   ├── analisis_links.py       # Análisis de enlaces y patrones
│   ├── enriquecer_materias_obligatorias.py # Extractor Fase 5 de materias por cuatrimestre
│   ├── normalizador_nombres_materias.py # Normalizador inteligente de nombres
│   └── inventario_sitios.json  # Mapeo completo de sitios
│
├── 🕷️ scrapers/                # Scrapers especializados
│   ├── scraper_horarios_dc.py      # Depto. Computación (46 materias)
│   ├── scraper_horarios_matematica.py # Depto. Matemática (40 materias)
│   ├── scraper_horarios_instituto_calculo.py # Instituto Cálculo (22 materias)
│   └── run_scraper.py          # Coordinador de scrapers
│
├── 📊 src/                     # Sistema RAG principal
│   ├── pipeline_rag_completo.py    # Pipeline end-to-end
│   ├── sistema_embeddings_horarios.py # Sistema de embeddings especializado
│   ├── consultar_horarios_rag.py   # CLI para consultas de horarios
│   ├── procesar_datos_unificado.py # Procesamiento y normalización
│   └── preparar_datos_rag.py       # Preparación para RAG
│
├── 🗃️ datos/                   # Datos procesados
│   ├── raw/                    # Datos crudos por scraper
│   └── procesados/             # Datos normalizados y unificados
│
├── 🤖 rag_sistema_horarios/    # Sistema RAG generado
│   ├── indice_horarios.faiss   # Índice vectorial FAISS
│   ├── documentos_horarios.json# Documentos procesados
│   └── metadatos_horarios.json # Metadatos y configuración
│
├── 🧪 tests/ y test/           # Suite de testing
│   ├── test_rag_horarios.py    # Tests del sistema RAG
│   ├── test_consultas_final.py # Tests de consultas
│   └── test_conflictos_horarios.py # Tests de detección de conflictos
│
├── 📋 reportes/                # Reportes y métricas
│   ├── reporte_testing_horarios_final.md # Reporte completo de testing
│   ├── metricas_mvp.json       # Métricas del MVP
│   └── reporte_procesamiento_*.md # Reportes de procesamiento
│
└── 📖 docs/                    # Documentación
    ├── plan_mvp_horarios.md    # Plan estratégico del MVP
    ├── plan_rag_materias.md    # Plan completo del sistema RAG
    ├── checklist_completo_mvp.md # Checklist de desarrollo
    └── descubrimiento/         # Documentación específica de descubrimiento
        └── fase5_materias_obligatorias.md # Documentación Fase 5
```

## 🎮 Uso del Sistema

### 1. Consultas de Horarios (Modo Interactivo)

```bash
# Iniciar modo interactivo
python src/consultar_horarios_rag.py

# Ejemplos de consultas:
> ¿Cuándo se dicta Análisis Matemático I?
> ¿Qué materias hay los martes por la tarde?
> ¿Horarios de Algoritmos y Estructuras de Datos?
> ¿Qué materias empiezan a las 14:00?
```

### 2. Comandos Especiales

```bash
# Dentro del modo interactivo:
/help       - Mostrar ayuda completa
/dias       - Buscar por día específico
/mañana     - Materias en horario matutino
/tarde      - Materias en horario vespertino
/noche      - Materias en horario nocturno
/stats      - Estadísticas del sistema
/materias   - Listar todas las materias
/examples   - Ejemplos de consultas
```

### 3. Consulta Única

```bash
# Consulta directa sin modo interactivo
python src/consultar_horarios_rag.py -q "¿Cuándo se dicta Álgebra I?"
```

### 4. Pipeline Completo

```bash
# Ejecutar todo el proceso desde cero
python src/pipeline_rag_completo.py

# Fases ejecutadas:
# 1. Scraping de materias
# 2. Procesamiento y normalización  
# 3. Generación de embeddings
# 4. Creación del índice FAISS
# 5. Testing automático
```

## 📊 Métricas y Performance

### Cobertura de Datos
- **108 materias** procesadas exitosamente (scrapers especializados)
- **53 materias obligatorias** extraídas por cuatrimestre (Fase 5)
- **32 materias base** normalizadas en sistema de matching
- **3 departamentos** principales cubiertos:
  - Departamento de Computación: 52% cobertura
  - Departamento de Matemática: 45% cobertura  
  - Instituto de Cálculo: 27% cobertura
- **3 cuatrimestres** disponibles: Verano 2025, 1er y 2do cuatrimestre 2025

### Performance del Sistema
- **18.2ms** tiempo promedio de respuesta
- **90% consultas exitosas** en testing
- **100% éxito** en casos críticos de prueba
- **<1 segundo** por consulta compleja

### Tipos de Información Extraída
- ✅ Horarios de cursada por comisión
- ✅ Días de la semana y rangos horarios
- ✅ Información de aulas y docentes
- ✅ Departamentos y períodos académicos
- ✅ Referencias cruzadas entre materias

## 🧪 Testing y Validación

### Ejecutar Tests

```bash
# Test completo del sistema RAG
python tests/test_rag_horarios.py

# Test de consultas específicas
python tests/test_consultas_final.py

# Test de detección de conflictos
python tests/test_conflictos_horarios.py
```

### Casos de Prueba Validados
- ✅ Consulta por materia específica (Score: 0.718)
- ✅ Búsqueda por día y horario (Score: 0.543)
- ✅ Consulta de algoritmos (Score: 0.738)
- ✅ Búsqueda por hora exacta (Score: 0.553)

## 🔄 Actualización y Mantenimiento

### Scraping Incremental

```bash
# Actualizar datos de un departamento específico
python scrapers/scraper_horarios_dc.py

# Extraer materias obligatorias por cuatrimestre (Fase 5)
python descubrimiento/enriquecer_materias_obligatorias.py

# Procesar y actualizar RAG
python src/procesar_datos_unificado.py
python src/sistema_embeddings_horarios.py
```

### Monitoreo de Calidad

```bash
# Generar reporte de calidad
python tests/validacion_manual_completa.py

# Verificar métricas actuales
python src/consultar_horarios_rag.py --stats
```

## 🛠️ Desarrollo y Extensión

### Agregar Nuevo Scraper

1. **Crear scraper específico** en `scrapers/`
2. **Implementar extractor** siguiendo el patrón existente
3. **Actualizar coordinador** en `run_scraper.py`
4. **Ejecutar procesamiento** con `procesar_datos_unificado.py`

### Normalización de Nombres de Materias

```python
# Usar el normalizador inteligente
from descubrimiento.normalizador_nombres_materias import NormalizadorNombresMaterias

normalizador = NormalizadorNombresMaterias()
resultado = normalizador.normalizar_nombre_web(
    "Física 1 (Lic. en Cs. Físicas) - Electiva de Intro..."
)
# Resultado: "Fisica I"
```

### Características del Normalizador
- **CamelCase sin acentos**: "análisis" → "Analisis"
- **Números arábigos → romanos**: "1" → "I", "2" → "II"
- **Limpieza inteligente**: Elimina texto descriptivo y paréntesis
- **Matching robusto**: 32 materias base con múltiples variaciones

### Configuración Avanzada

```python
# Archivo: src/config_paths.py
# Configurar rutas y parámetros del sistema
BASE_PATH = "ruta/personalizada"
EMBEDDING_MODEL = "modelo-embedding-personalizado"
```

## 📈 Roadmap y Expansión

### Próximas Características (Planificadas)
- ✅ **Extracción por cuatrimestre**: Fase 5 completada (53 materias obligatorias)
- ✅ **Normalizador inteligente**: Sistema de matching avanzado
- 🔜 **Más departamentos**: Física, Química, Ciencias de la Atmósfera
- 🔜 **API REST**: Interfaz programática para integraciones
- 🔜 **Interface Web**: Dashboard interactivo con React
- 🔜 **Detección automática** de cambios en sitios web
- 🔜 **Correlativas y dependencias** entre materias

### Expansión Técnica
- **Scrapers adicionales** para sistemas complejos (Drupal, Joomla)
- **Cache inteligente** para optimización de performance
- **Monitoreo automático** de calidad y freshness
- **Pipeline CI/CD** para despliegues automatizados

## 🐛 Troubleshooting

### Problemas Comunes

**Error: "No se encuentra el sistema RAG"**
```bash
# Verificar que existe el directorio
ls rag_sistema_horarios/
# Si no existe, ejecutar:
python src/sistema_embeddings_horarios.py
```

**Error: "Módulo no encontrado"**
```bash
# Instalar dependências faltantes
pip install -r requirements_scraper.txt
```

**Performance lenta en consultas**
```bash
# Verificar recursos del sistema
# RAM requerida: >4GB
# Regenerar índice optimizado:
python src/sistema_embeddings_horarios.py --optimize
```

### Logs y Debugging

```bash
# Activar logging detallado
export LOG_LEVEL=DEBUG
python src/consultar_horarios_rag.py -v
```

## 📞 Soporte y Contribución

### Reportar Issues
- Crear issue en el repositorio con:
  - Descripción del problema
  - Pasos para reproducir
  - Logs relevantes
  - Configuración del sistema

### Contribuir
1. Fork del repositorio
2. Crear branch para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo [licencia a definir]. Ver `LICENSE` para más detalles.

## 👥 Créditos

**Desarrollado para**: Facultad de Ciencias Exactas, Universidad de Buenos Aires
**Tecnologías**: Python, FAISS, SentenceTransformers, Crawl4AI
**Estado**: MVP Funcional - Versión 1.0
**Fecha**: Julio 2025

---

**🎯 Para consultas de horarios: `python src/consultar_horarios_rag.py`**
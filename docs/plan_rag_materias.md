# Plan de Acción: Sistema de scraping para RAG

## 📋 Resumen del Proyecto

**Objetivo**: Construir un sistema RAG (Retrieval Augmented Generation) completo para crear un chatbot que responda preguntas sobre materias universitarias del sitio web https://lcd.exactas.uba.ar/materias/

**Fuente de datos**: Aplicación WordPress con información de materias de la Facultad de Ciencias Exactas, UBA

**Tecnologías principales**: Python, Crawl4AI, SentenceTransformers, FAISS, BeautifulSoup

---

## 🎯 Estado Actual

- ✅ **Scraper funcional**: Ya tenemos `scrap_materias_rag_corregido.py` funcionando con CosineStrategy
- ⏳ **Pendiente**: Pipeline completo de RAG y sistema de consultas

---

## 📊 Fases del Proyecto

### **FASE 1: EXTRACCIÓN Y PREPARACIÓN DE DATOS** 

#### 1.0 Descubrimiento y Mapeo de Sitios 🗺️ NUEVO
- [X] **Archivo**: `descubrir_sitios.py`
- [ ] **Tareas**:
  - [ ] Scraping de página principal https://lcd.exactas.uba.ar/ para mapear estructura
  - [ ] Identificar todos los departamentos/institutos (Matemática, Computación, Física, etc.)
  - [ ] Descubrir subdominios y sitios relacionados de cada departamento
  - [ ] Analizar tecnologías diferentes por sitio (WordPress, Drupal, HTML estático, etc.)
  - [ ] Crear inventario de URLs por categoría (materias, horarios, docentes, etc.)
  - [ ] Detectar patrones de estructura por sitio
  - [ ] Priorizar sitios por relevancia y viabilidad técnica
- [ ] **Entregables**: 
  - [ ] `inventario_sitios.json` con mapeo completo
  - [ ] `estrategias_por_sitio.json` con approach técnico por sitio
  - [ ] Reporte de factibilidad técnica
- [ ] **Criterios de éxito**: 
  - [ ] Mapeo de 100% de departamentos principales
  - [ ] Identificación de al menos 80% de fuentes de información de materias
  - [ ] Estrategia técnica definida para cada tipo de sitio

#### 1.1 Scrapers Especializados por Tecnología 🔧 AMPLIADO
- [ ] **Archivos**: `scrapers/` (directorio)
  - [ ] `scraper_wordpress.py` (base actual, mejorado)
  - [ ] `scraper_drupal.py` (para sitios Drupal)
  - [ ] `scraper_joomla.py` (para sitios Joomla)
  - [ ] `scraper_html_estatico.py` (para sitios simples)
  - [ ] `scraper_pdfs.py` (para documentos PDF)
  - [ ] `scraper_base.py` (clase abstracta común)
- [ ] **Tareas**:
  - [ ] Refactorizar scraper actual como especialista en WordPress
  - [ ] Desarrollar scrapers específicos por tecnología detectada
  - [ ] Implementar detección automática de tecnología por sitio
  - [ ] Sistema de fallback entre estrategias de scraping
  - [ ] Manejo de rate limiting y robots.txt por sitio
  - [ ] Extracción de metadatos específicos (departamento, tipo de información)
  - [ ] Sistema de validación de contenido extraído
- [ ] **Entregables**: 
  - [ ] Suite de scrapers especializados
  - [ ] `datos_por_sitio/` con datos organizados por fuente
  - [ ] Logs detallados de éxito/fallo por sitio
- [ ] **Criterios de éxito**: 
  - [ ] 95% de sitios scrapeados exitosamente
  - [ ] Contenido extraído con calidad consistente
  - [ ] Tiempo total de scraping < 2 horas

#### 1.2 Coordinador de Scraping Masivo 🕷️ NUEVO
- [ ] **Archivo**: `scraper_coordinador.py`
- [ ] **Tareas**:
  - [ ] Orquestación de scraping en paralelo por sitio
  - [ ] Sistema de prioridades por importancia del sitio
  - [ ] Monitoreo de progreso en tiempo real
  - [ ] Manejo de fallos y reintentos inteligentes
  - [ ] Respeto de límites de velocidad por dominio
  - [ ] Consolidación de datos de múltiples fuentes
  - [ ] Detección de contenido duplicado entre sitios
- [ ] **Entregables**: 
  - [ ] Sistema de scraping coordinado
  - [ ] Dashboard de progreso
  - [ ] `materias_consolidadas.json` con datos unificados
- [ ] **Criterios de éxito**: 
  - [ ] Scraping sin bloqueos por rate limiting
  - [ ] Consolidación exitosa de datos multi-fuente
  - [ ] Recuperación automática de errores menores

#### 1.3 Limpieza y Estructuración de Datos Multi-fuente 📝 AMPLIADO
- [ ] **Archivo**: `preparar_datos_rag.py` (expandido)
- [ ] **Tareas**:
  - [ ] Normalización de datos de fuentes heterogéneas
  - [ ] Mapeo de esquemas diferentes a estructura común
  - [ ] Detección y resolución de duplicados entre sitios
  - [ ] Enriquecimiento con información cruzada (ej: horarios + programas)
  - [ ] Extracción de metadatos específicos por tipo de fuente
  - [ ] Validación de consistencia entre fuentes
  - [ ] Generación de jerarquía: Facultad > Departamento > Materia > Información
- [ ] **Entregables**: 
  - [ ] `documentos_rag_multifuente.json` con datos unificados
  - [ ] `esquema_unificado.json` con estructura común
  - [ ] Reporte de calidad y cobertura por fuente
- [ ] **Criterios de éxito**:
  - [ ] 100% compatibilidad entre esquemas de fuentes
  - [ ] < 3% de información duplicada
  - [ ] Cobertura balanceada entre departamentos

#### 1.4 Validación y Control de Calidad Multi-sitio 🔍 AMPLIADO  
- [ ] **Archivo**: `validar_datos_multisitio.py`
- [ ] **Tareas**:
  - [ ] Estadísticas por fuente y consolidadas
  - [ ] Análisis de cobertura por departamento/materia
  - [ ] Detección de información faltante crítica
  - [ ] Validación cruzada entre fuentes
  - [ ] Identificación de inconsistencias entre sitios
  - [ ] Análisis de freshness de información por fuente
  - [ ] Métricas de calidad por tipo de scraper
- [ ] **Entregables**:
  - [ ] `reporte_calidad_multisitio.html` con análisis por fuente
  - [ ] `matriz_cobertura.json` con gaps identificados
  - [ ] Priorización de sitios para re-scraping
- [ ] **Criterios de éxito**:
  - [ ] Cobertura > 80% para cada departamento principal
  - [ ] Identificación de 100% de fuentes críticas faltantes
  - [ ] Plan de acción para gaps importantes

---

### **FASE 2: SISTEMA DE EMBEDDINGS Y BÚSQUEDA**

#### 2.1 Configuración del Sistema de Embeddings 🤖 NUEVO
- [ ] **Archivo**: `sistema_embeddings.py`
- [ ] **Tareas**:
  - [ ] Evaluar diferentes modelos de embeddings en español
  - [ ] Benchmark de velocidad y calidad: `paraphrase-multilingual-MiniLM-L12-v2`, `intfloat/multilingual-e5-base`
  - [ ] Configurar parámetros óptimos de embedding
  - [ ] Implementar procesamiento en lotes para eficiencia
  - [ ] Añadir cache de embeddings para desarrollo
  - [ ] Manejar textos muy largos (chunking automático)
- [ ] **Entregables**:
  - [ ] `benchmark_modelos.json` con métricas de comparación
  - [ ] Sistema de embeddings optimizado
- [ ] **Criterios de éxito**:
  - [ ] Embeddings generados en < 10 minutos
  - [ ] Similitud semántica > 0.8 en casos de prueba
  - [ ] Uso de memoria < 4GB

#### 2.2 Índice Vectorial con FAISS 📊 NUEVO
- [ ] **Archivo**: `sistema_embeddings.py` (expandido)
- [ ] **Tareas**:
  - [ ] Comparar tipos de índices FAISS (Flat, IVF, HNSW)
  - [ ] Optimizar parámetros de búsqueda
  - [ ] Implementar búsqueda híbrida (vectorial + filtros)
  - [ ] Añadir filtrado por metadatos (materia, tipo, etc.)
  - [ ] Implementar re-ranking por relevancia
  - [ ] Optimizar para consultas en tiempo real
- [ ] **Entregables**:
  - [ ] `rag_sistema/` con índice optimizado
  - [ ] Benchmarks de velocidad de búsqueda
- [ ] **Criterios de éxito**:
  - [ ] Búsqueda < 100ms para consultas típicas
  - [ ] Precision@5 > 80% en casos de prueba
  - [ ] Recall@10 > 90% en casos de prueba

#### 2.3 Sistema de Evaluación y Métricas 📈 NUEVO
- [ ] **Archivo**: `evaluar_rag.py`
- [ ] **Tareas**:
  - [ ] Crear dataset de pruebas con consultas y respuestas esperadas
  - [ ] Implementar métricas: Precision, Recall, NDCG, MRR
  - [ ] Evaluación de relevancia semántica
  - [ ] A/B testing entre configuraciones
  - [ ] Análisis de casos de fallo
  - [ ] Métricas de cobertura por materia
- [ ] **Entregables**:
  - [ ] `dataset_evaluacion.json` con casos de prueba
  - [ ] `reporte_metricas.html` con resultados
  - [ ] Sistema de evaluación automatizada
- [ ] **Criterios de éxito**:
  - [ ] > 100 casos de prueba diversos
  - [ ] Precision@5 > 85%
  - [ ] Cobertura balanceada entre materias

---

### **FASE 3: PIPELINE Y AUTOMATIZACIÓN**

#### 3.1 Pipeline de Procesamiento Completo 🔄 MEJORAR
- [ ] **Archivo**: `pipeline_rag_completo.py`
- [ ] **Tareas**:
  - [ ] Integrar todos los pasos en pipeline único
  - [ ] Añadir checkpoints para reanudar procesamiento
  - [ ] Implementar rollback en caso de errores
  - [ ] Logging comprehensivo de todo el proceso
  - [ ] Monitoreo de recursos (CPU, memoria, disco)
  - [ ] Notificaciones de éxito/fallo
  - [ ] Paralelización donde sea posible
- [ ] **Entregables**:
  - [ ] Pipeline robusto end-to-end
  - [ ] Documentación de troubleshooting
- [ ] **Criterios de éxito**:
  - [ ] Ejecución exitosa sin supervisión
  - [ ] Tiempo total < 30 minutos
  - [ ] Recovery automático de errores menores

#### 3.2 Sistema de Consultas y API 🔍 MEJORAR
- [ ] **Archivo**: `consultar_rag.py`
- [ ] **Tareas**:
  - [ ] Mejorar interfaz de línea de comandos
  - [ ] Añadir filtros avanzados (por materia, tipo, fecha)
  - [ ] Implementar búsqueda con operadores (AND, OR, NOT)
  - [ ] Sistema de autocompletado para materias
  - [ ] Exportar resultados (JSON, CSV, markdown)
  - [ ] Historial de consultas
  - [ ] Métricas de uso en tiempo real
- [ ] **Entregables**:
  - [ ] Interfaz CLI completa
  - [ ] API REST básica (Flask/FastAPI)
- [ ] **Criterios de éxito**:
  - [ ] Consultas complejas ejecutadas correctamente
  - [ ] Respuestas en < 200ms
  - [ ] Interfaz intuitiva para usuarios no técnicos

#### 3.3 Actualización y Mantenimiento 🔄 NUEVO
- [ ] **Archivo**: `actualizar_rag.py`
- [ ] **Tareas**:
  - [ ] Sistema de detección de cambios en el sitio web
  - [ ] Scraping incremental (solo nuevos contenidos)
  - [ ] Versionado del sistema RAG
  - [ ] Backup y restore de índices
  - [ ] Limpieza automática de datos obsoletos
  - [ ] Alertas de degradación de calidad
- [ ] **Entregables**:
  - [ ] Sistema de actualización automática
  - [ ] Procedimientos de mantenimiento
- [ ] **Criterios de éxito**:
  - [ ] Detección de cambios en < 24 horas
  - [ ] Actualización incremental sin downtime
  - [ ] Preservación de calidad tras actualizaciones

---

### **FASE 4: DOCUMENTACIÓN Y TESTING**

#### 4.1 Testing Comprehensivo 🧪 NUEVO
- [ ] **Archivo**: `tests/`
- [ ] **Tareas**:
  - [ ] Unit tests para cada módulo
  - [ ] Integration tests para pipeline completo
  - [ ] Performance tests con datasets grandes
  - [ ] Stress tests de consultas concurrentes
  - [ ] Tests de regresión
  - [ ] Tests de edge cases (consultas vacías, muy largas, etc.)
- [ ] **Entregables**:
  - [ ] Suite de tests automatizada
  - [ ] CI/CD pipeline básico
- [ ] **Criterios de éxito**:
  - [ ] 90%+ cobertura de código
  - [ ] Todos los tests pasan consistentemente
  - [ ] Tests ejecutados en < 5 minutos

#### 4.2 Documentación Técnica 📚 NUEVO
- [ ] **Archivos**: `docs/`
- [ ] **Tareas**:
  - [ ] README.md con instrucciones de instalación
  - [ ] Guía de usuario detallada
  - [ ] Documentación de API
  - [ ] Troubleshooting guide
  - [ ] Arquitectura del sistema
  - [ ] Best practices y optimizaciones
  - [ ] Ejemplos de uso común
- [ ] **Entregables**:
  - [ ] Documentación completa en markdown
  - [ ] Diagramas de arquitectura
- [ ] **Criterios de éxito**:
  - [ ] Usuario nuevo puede instalar y usar sin ayuda
  - [ ] Documentación actualizada en cada release

#### 4.3 Optimización Final y Deployment 🚀 NUEVO
- [ ] **Tareas**:
  - [ ] Profiling de performance completo
  - [ ] Optimización de memoria y CPU
  - [ ] Configuración para diferentes entornos (dev/prod)
  - [ ] Dockerización del sistema
  - [ ] Scripts de deployment
  - [ ] Monitoreo y alertas básicas
- [ ] **Entregables**:
  - [ ] Sistema optimizado y production-ready
  - [ ] Guía de deployment
- [ ] **Criterios de éxito**:
  - [ ] Sistema puede manejar 100+ consultas/minuto
  - [ ] Deployment automatizado funcionando
  - [ ] Downtime < 1 minuto para actualizaciones

---

## 🗂️ Estructura de Archivos Esperada

```
proyecto_rag_materias/
├── README.md
├── requirements.txt
├── PLAN_RAG_MATERIAS.md
│
├── src/
│   ├── scrap_materias_rag_corregido.py
│   ├── preparar_datos_rag.py
│   ├── sistema_embeddings.py
│   ├── pipeline_rag_completo.py
│   ├── consultar_rag.py
│   ├── actualizar_rag.py
│   ├── evaluar_rag.py
│   └── validar_datos.py
│
├── data/
│   ├── materias_rag.json
│   ├── documentos_rag_final.json
│   ├── esquema_metadatos.json
│   └── dataset_evaluacion.json
│
├── rag_sistema/
│   ├── indice.faiss
│   ├── documentos.json
│   ├── metadatos.json
│   └── config.json
│
├── tests/
│   ├── test_scraper.py
│   ├── test_embeddings.py
│   ├── test_pipeline.py
│   └── test_consultas.py
│
├── docs/
│   ├── arquitectura.md
│   ├── guia_usuario.md
│   ├── api_reference.md
│   └── troubleshooting.md
│
├── scripts/
│   ├── install.sh
│   ├── deploy.sh
│   └── backup.sh
│
└── reports/
    ├── reporte_calidad_datos.html
    ├── benchmark_modelos.json
    └── reporte_metricas.html
```

---

## ⏱️ Cronograma Estimado

| Fase | Duración | Prioridad | Dependencias |
|------|----------|-----------|--------------|
| **Fase 1**: Datos | 3-4 días | Alta | - |
| **Fase 2**: Embeddings | 2-3 días | Alta | Fase 1 |
| **Fase 3**: Pipeline | 2-3 días | Media | Fase 2 |
| **Fase 4**: Testing/Docs | 2-3 días | Media | Fase 3 |
| **TOTAL** | **9-13 días** | | |

---

## 🎯 Métricas de Éxito del Proyecto

### Métricas Técnicas
- [ ] **Calidad de Datos**: < 5% documentos con errores
- [ ] **Performance**: Consultas < 200ms
- [ ] **Precisión**: Precision@5 > 85%
- [ ] **Cobertura**: 100% materias scrapeadas
- [ ] **Confiabilidad**: 99% uptime del sistema

### Métricas de Usabilidad  
- [ ] **Facilidad de uso**: Usuario nuevo puede usar en < 10 minutos
- [ ] **Documentación**: 100% funcionalidades documentadas
- [ ] **Mantenibilidad**: Actualizaciones automáticas funcionando

---

## 🚨 Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cambios en estructura del sitio web | Media | Alto | Scraper robusto + monitoreo |
| Modelos de embedding pesados | Baja | Medio | Benchmark múltiples modelos |
| Calidad irregular de datos | Media | Medio | Validación automática exhaustiva |
| Performance en consultas complejas | Media | Medio | Optimización FAISS + cache |

---

## 📝 Notas y Consideraciones

### **Decisiones Técnicas Pendientes - ACTUALIZADAS**
- [ ] **Estrategia de scraping**: ¿Scraping en paralelo o secuencial por prioridad?
- [ ] **Gestión de datos**: ¿Base de datos (SQLite/PostgreSQL) o solo archivos JSON?
- [ ] **Modelo de embedding**: ¿Multilingual o específico español?
- [ ] **Tipo de índice FAISS**: ¿Flat, IVF o HNSW para datasets grandes?
- [ ] **Chunking strategy**: ¿CosineStrategy vs manual vs híbrido?
- [ ] **Actualización**: ¿Sistema de detección de cambios por sitio?
- [ ] **Rate limiting**: ¿Política agresiva vs conservadora por dominio?

### Escalabilidad Futura
- [ ] Soporte para múltiples universidades
- [ ] Integración con sistemas de gestión académica
- [ ] API pública para desarrolladores
- [ ] Interface web interactiva
- [ ] Chatbot con LLM integrado

---

## ✅ Checklist de Progreso

**Completado:**
- [x] Scraper básico funcionando
- [x] CosineStrategy implementado
- [x] Plan de acción definido

**En Progreso:**
- [ ] Optimización del scraper
- [ ] Pipeline de preparación de datos

**Pendiente:**
- [ ] Sistema de embeddings
- [ ] Validación y testing
- [ ] Documentación completa
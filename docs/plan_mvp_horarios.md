# Plan MVP: RAG con Horarios Completos

## 🎯 Objetivo MVP
**Crear un RAG funcional con horarios de materias completos en 3-5 días**

---

## 📋 Estrategia: "Quick Wins" Graduales

### **PASO 1: Descubrimiento Dirigido** (Día 1 - 4 horas)

#### 1.1 Identificar fuentes críticas de horarios
- [ ] Ejecutar `descubrir_sitios.py` enfocado en horarios
- [ ] Mapear manualmente los 3-5 sitios más importantes
- [ ] Priorizar por: **facilidad técnica + volumen de horarios**

**Sitios candidatos a investigar:**
```
🎯 ALTA PRIORIDAD (horarios centralizados):
- https://exactas.uba.ar/horarios/
- https://exactas.uba.ar/calendario/
- Sistemas centralizados de la facultad

🎯 MEDIA PRIORIDAD (por departamento):
- Departamento de Matemática
- Departamento de Computación  
- Departamento de Física
- Instituto de Cálculo

🎯 BAJA PRIORIDAD (información dispersa):
- Sitios de cátedras individuales
- PDFs sueltos
```

#### 1.2 Análisis técnico rápido
- [ ] Determinar 2-3 estrategias de scraping necesarias
- [ ] Identificar patrones de datos más comunes
- [ ] Estimar esfuerzo vs valor por sitio

**Criterio de selección para MVP:**
- ✅ Tiene horarios de ≥10 materias
- ✅ Scraping técnicamente simple (WordPress, HTML básico)
- ✅ Datos estructurados o semi-estructurados
- ❌ Evitar: JavaScript pesado, sistemas de login, CAPTCHAs

---

### **PASO 2: Scrapers Mínimos Viables** (Día 2 - 6 horas)

#### 2.1 Scraper de horarios específico
```python
# scraper_horarios_mvp.py
# - Enfocado SOLO en extraer horarios
# - 2-3 sitios máximo
# - Estrategia simple pero efectiva
```

#### 2.2 Modificar scraper actual
```python
# scrap_materias_rag_horarios.py  
# - Extender scraper actual para incluir horarios
# - Mantener la estructura que ya funciona
# - Añadir detección de patrones de horarios
```

#### 2.3 Coordinador simple
```python
# scraper_coordinado_mvp.py
# - Ejecutar 2-3 scrapers en secuencia
# - Consolidar datos básicos
# - Logging simple
```

**Entregables Día 2:**
- [ ] `horarios_raw.json` - Datos crudos de horarios
- [ ] `materias_con_horarios.json` - Dataset combinado
- [ ] Lista de sitios exitosos vs problemáticos

---

### **PASO 3: RAG con Horarios** (Día 3 - 4 horas)

#### 3.1 Adaptar preparación de datos
- [ ] Detectar automáticamente información de horarios en chunks
- [ ] Crear metadatos específicos: `tiene_horarios`, `dia_semana`, `horario`
- [ ] Mejorar chunking para preservar horarios completos

#### 3.2 Embeddings optimizados para horarios
- [ ] Incluir contexto temporal en embeddings
- [ ] Ajustar parámetros para consultas sobre horarios
- [ ] Casos de prueba específicos para horarios

**Entregables Día 3:**
- [ ] RAG funcional con horarios incluidos
- [ ] Pruebas: "¿cuándo se dicta análisis matemático?"
- [ ] Métricas básicas de calidad

---

### **PASO 4: Validación y Ajustes** (Día 4 - 4 horas)

#### 4.1 Testing con casos reales
```
Consultas de prueba:
- "¿Qué horarios tiene Álgebra I?"
- "¿Qué materias se dictan los martes por la tarde?"
- "¿Cuándo son las clases de Análisis Matemático II?"
- "¿Qué días y horarios tiene Algoritmos y Estructuras de Datos?"
```

#### 4.2 Identificar gaps críticos
- [ ] ¿Qué departamentos/materias faltan?
- [ ] ¿Qué consultas fallan?
- [ ] ¿Cuáles son los próximos sitios prioritarios?

#### 4.3 Plan de expansión
- [ ] Roadmap para siguientes 2-3 sitios
- [ ] Identificar scrapers adicionales necesarios

---

### **PASO 5: Expansión Gradual** (Día 5+ - ongoing)

#### 5.1 Siguiente iteración (Semana 2)
- [ ] Agregar 2-3 sitios más importantes
- [ ] Mejorar scrapers existentes
- [ ] Más tipos de información (correlativas, docentes)

#### 5.2 Automación (Semana 3)
- [ ] Pipeline automático
- [ ] Monitoreo de cambios
- [ ] Sistema de actualizaciones

---

## 🔍 Script de Descubrimiento Enfocado en Horarios

```python
# Modificación del script anterior para buscar específicamente horarios
PATRONES_HORARIOS = [
    r'horarios?',
    r'cursadas?',
    r'lunes|martes|miércoles|jueves|viernes',
    r'\d{1,2}:\d{2}',  # Formato de hora
    r'aula',
    r'turno',
    r'comisión'
]

URLS_PRIORITARIAS_HORARIOS = [
    "https://exactas.uba.ar/",
    "https://lcd.exactas.uba.ar/",
    "https://www.dm.uba.ar/",  # Matemática
    "https://www.dc.uba.ar/",  # Computación  
    "https://df.uba.ar/",      # Física
]
```

---

## 📊 Cronograma MVP Realista

| Día | Actividad | Duración | Entregable |
|-----|-----------|----------|------------|
| **1** | Descubrimiento dirigido | 4h | Lista sitios prioritarios |
| **2** | Scrapers específicos | 6h | Datos de horarios crudos |
| **3** | RAG con horarios | 4h | Sistema funcional básico |
| **4** | Testing y validación | 4h | MVP validado |
| **5** | Documentación y plan | 2h | Roadmap expansión |

**Total: ~20 horas distribuidas en 5 días**

---

## 🎯 Criterios de Éxito MVP

### Técnicos
- [ ] ≥50 materias con horarios completos
- [ ] ≥3 departamentos representados  
- [ ] Consultas sobre horarios funcionan correctamente
- [ ] Tiempo de respuesta <500ms

### Funcionales  
- [ ] Responde: "¿Cuándo se dicta [materia]?"
- [ ] Responde: "¿Qué materias hay los [día] a las [hora]?"
- [ ] Identifica conflictos de horarios básicos
- [ ] Información actualizada (semestre actual)

### Escalabilidad
- [ ] Arquitectura permite agregar nuevos sitios fácilmente
- [ ] Scripts reutilizables para otros departamentos
- [ ] Plan claro para próximas iteraciones

---

## 🚨 Riesgos del MVP y Mitigaciones

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Sitios no tienen horarios centralizados | Alta | Mapeo manual previo |
| Datos desactualizados | Media | Validación por muestreo |
| Estructura compleja de horarios | Media | Empezar con formatos simples |
| Rate limiting agresivo | Baja | Scrapers conservadores |

---

## 🛠️ Stack Técnico MVP

```
MANTENER (ya funciona):
✅ crawl4ai + BeautifulSoup
✅ SentenceTransformers  
✅ FAISS
✅ Estructura actual de archivos

AGREGAR MÍNIMO:
🆕 Regex para detectar horarios
🆕 Metadatos de temporalidad
🆕 2-3 scrapers específicos
🆕 Validación de horarios
```

---

## 💡 Siguiente Pregunta Clave

**¿Empezamos ejecutando el script de descubrimiento dirigido a horarios, o preferís que primero desarrollemos el scraper específico basado en sitios que ya conocés?**

Opciones:
1. **Descubrimiento primero**: Ejecutar análisis automático y luego decidir
2. **Sitios conocidos primero**: Si ya sabés dónde están los horarios, ir directo ahí
3. **Híbrido**: Analizar 2-3 sitios obvios mientras corre el descubrimiento

¿Cuál preferís?
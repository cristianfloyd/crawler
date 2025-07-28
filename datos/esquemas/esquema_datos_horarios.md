# 📋 ESQUEMA DE DATOS Y PLAN TÉCNICO - MVP RAG Horarios

## 🎯 **ANÁLISIS DEL HTML - MATERIAS OBLIGATORIAS**

### **✅ ESTRUCTURA PERFECTA DETECTADA**

El HTML muestra una estructura **EXCELENTE** para scraping:

```html
<h2>Verano 2025</h2>
<table class="table">
  <tr>
    <th>Materia</th>
    <th>Departamento</th> 
    <th>Página web</th>
  </tr>
  <tr>
    <td>Algebra I</td>
    <td>Departamento de Matemática</td>
    <td><a href="https://web.dm.uba.ar/...2025&cuatrimestre=v">link</a></td>
  </tr>
</table>

<h2>1er cuatrimestre 2025</h2>
<h2>2do cuatrimestre 2025</h2>
```

### **🏆 DATOS CRÍTICOS EXTRAÍBLES**

1. **📅 Períodos**: Verano 2025, 1er cuatrimestre 2025, 2do cuatrimestre 2025
2. **📚 Materias**: 23+ materias obligatorias por período
3. **🏢 Departamentos**: DM, DC, DF, IC, FB, AT, QI
4. **🔗 Links directos**: URLs específicas a sitios departamentales con horarios
5. **📋 Clasificación**: Obligatorias vs electivas claramente identificadas

---

## 📊 **ESQUEMA DE DATOS UNIFICADO**

### **Esquema Principal: `materia_completa.json`**
```json
{
  "id": "unique_identifier",
  "nombre": "Algoritmos y Estructuras de Datos I",
  "codigo": "AED1",  // Si disponible
  "tipo": "obligatoria|optativa|electiva",
  "departamento": {
    "nombre": "Departamento de Computación",
    "codigo": "DC",
    "url_horarios": "https://www.dc.uba.ar/cursada-de-grado/"
  },
  "periodo": {
    "año": 2025,
    "cuatrimestre": "1|2|verano",
    "periodo_completo": "1er cuatrimestre 2025"
  },
  "horarios": {
    "clases": [
      {
        "dia": "lunes",
        "hora_inicio": "14:00",
        "hora_fin": "18:00",
        "aula": "Pab 1 Aula 5",
        "modalidad": "presencial|virtual|hibrida"
      }
    ],
    "consultas": [
      {
        "dia": "viernes", 
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
        "docente": "Nombre Apellido"
      }
    ],
    "examenes": {
      "parciales": ["2025-04-15", "2025-05-20"],
      "final": "2025-07-10"
    }
  },
  "correlativas": {
    "para_cursar": ["Álgebra I", "Análisis I"],
    "para_rendir": ["Álgebra I", "Análisis I"]
  },
  "docentes": [
    {
      "nombre": "Dr. Juan Pérez",
      "categoria": "titular|adjunto|jtp",
      "email": "juan@dc.uba.ar"
    }
  ],
  "aulas": ["Pab 1 Aula 5", "Lab Computación"],
  "creditos": 120,
  "carga_horaria": {
    "semanal": 8,
    "total": 128
  },
  "programa": {
    "url": "https://link.to.programa.pdf",
    "temas": ["Recursión", "Complejidad", "Estructuras de datos"]
  },
  "metadata": {
    "fuente_url": "https://lcd.exactas.uba.ar/materias-obligatorias/",
    "fecha_scraping": "2025-07-26",
    "version": "2025.1",
    "confiabilidad": "alta|media|baja"
  }
}
```

### **Esquema Metadatos RAG: `documento_rag.json`**
```json
{
  "id": "doc_unique_id",
  "content": "Algoritmos y Estructuras de Datos I se dicta en el Departamento de Computación durante el 1er cuatrimestre 2025. Las clases son los lunes de 14:00 a 18:00 en el Pab 1 Aula 5...",
  "metadata": {
    "tipo_documento": "materia_obligatoria",
    "materia_nombre": "Algoritmos y Estructuras de Datos I", 
    "departamento": "DC",
    "año": 2025,
    "cuatrimestre": 1,
    "tiene_horarios": true,
    "tiene_correlativas": true,
    "tiene_programa": true,
    "dias_semana": ["lunes"],
    "horario_inicio": "14:00",
    "horario_fin": "18:00",
    "nivel": "grado",
    "carrera": "Licenciatura en Datos",
    "keywords": ["algoritmos", "estructuras", "datos", "computacion"],
    "chunk_type": "horarios|correlativas|programa|general"
  }
}
```

---

## 🔧 **ESTRATEGIA DE SCRAPING DETALLADA**

### **FASE 1: Scraper Materias Obligatorias**

```python
class ScraperMateriasObligatorias:
    def __init__(self):
        self.base_url = "https://lcd.exactas.uba.ar/materias-obligatorias/"
        self.departamentos_map = {
            "Departamento de Matemática": "DM",
            "Departamento de Computación": "DC", 
            "Departamento de Física": "DF",
            "Instituto de Cálculo": "IC"
        }
    
    def extraer_materias_por_periodo(self, html):
        # 1. Identificar secciones por <h2>
        # 2. Extraer tablas por período
        # 3. Parsear filas de materias
        # 4. Extraer links a sitios departamentales
        
    def normalizar_materia(self, raw_data):
        # 1. Limpiar nombres de materias
        # 2. Mapear departamentos a códigos
        # 3. Extraer URLs de horarios
        # 4. Clasificar tipo (obligatoria/electiva)
```

### **FASE 2: Enriquecimiento con Horarios**

```python
class EnriquecedorHorarios:
    def __init__(self):
        self.scrapers_departamentales = {
            "DM": ScraperMatematica(),
            "DC": ScraperComputacion(),
            "DF": ScraperFisica(), 
            "IC": ScraperCalculo()
        }
    
    def obtener_horarios_detallados(self, materia):
        # 1. Identificar departamento
        # 2. Usar scraper específico
        # 3. Extraer horarios reales
        # 4. Normalizar formato
```

### **FASE 3: Scraper Materias Optativas 2025**

```python
class ScraperOptativas2025:
    def __init__(self):
        self.base_url = "https://lcd.exactas.uba.ar/materias-optativas/?ano=2025"
        
    def extraer_optativas(self):
        # 1. Scraping WordPress dinámico
        # 2. Detección de AJAX si es necesario
        # 3. Parsing de información completa
        # 4. Extracción de horarios + correlativas
```

---

## ⚡ **PATRON DE EXTRACCIÓN DE HORARIOS**

### **Regex para Horarios**
```python
import re

PATTERNS_HORARIOS = {
    "dia_hora": r"(lunes|martes|miércoles|jueves|viernes|sábado)\s+(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})",
    "hora_simple": r"(\d{1,2}):(\d{2})",
    "rango_horario": r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})",
    "modalidad": r"(presencial|virtual|híbrida|remota)",
    "aula": r"(Pab\s+\d+\s+Aula\s+\d+|Aula\s+\d+|Lab\s+\w+)"
}
```

### **Normalización de Días**
```python
DIAS_NORMALIZADOS = {
    "lun": "lunes", "lu": "lunes",
    "mar": "martes", "ma": "martes", 
    "mié": "miércoles", "mi": "miércoles",
    "jue": "jueves", "ju": "jueves",
    "vie": "viernes", "vi": "viernes",
    "sáb": "sábado", "sa": "sábado"
}
```

---

## 🎯 **PIPELINE DE PROCESAMIENTO**

### **Flujo Completo**
```
1. [HTML Raw] → [Parser] → [Datos Estructurados]
2. [Datos Estructurados] → [Enriquecedor] → [Datos Completos]  
3. [Datos Completos] → [Validador] → [Datos Validados]
4. [Datos Validados] → [Generador RAG] → [Documentos RAG]
5. [Documentos RAG] → [Sistema Embeddings] → [Índice FAISS]
```

### **Validaciones Críticas**
```python
def validar_materia(materia):
    checks = {
        "nombre_valido": bool(materia.get("nombre")),
        "departamento_valido": materia.get("departamento", {}).get("codigo") in DEPARTAMENTOS_VALIDOS,
        "periodo_valido": validar_periodo(materia.get("periodo")),
        "horarios_formato": validar_formato_horarios(materia.get("horarios")),
        "urls_accesibles": verificar_urls(materia)
    }
    return all(checks.values()), checks
```

---

## 📈 **ESTIMACIÓN DE RESULTADOS**

### **Métricas Esperadas por Sitio**

| Sitio | Materias | Horarios | Correlativas | Confiabilidad |
|-------|----------|----------|--------------|---------------|
| LCD Obligatorias | 23 | Alta | Media | 95% |
| LCD Optativas 2025 | 83 | Alta | Alta | 90% |
| PEM Maestría | 18 | Media | Baja | 85% |
| **TOTAL** | **124** | **Alta** | **Media** | **90%** |

### **Casos de Uso Cubiertos**
- ✅ "¿Cuáles son las materias obligatorias de la carrera?"
- ✅ "¿Cuándo se dicta Algoritmos I en 2025?"
- ✅ "¿Qué materias hay en el Departamento de Computación?"
- ✅ "¿Correlativas de Análisis II?"
- ✅ "¿Optativas disponibles en el primer cuatrimestre?"
- ✅ "¿Materias que se dictan los lunes?"

---

## 🚀 **PLAN DE DESARROLLO - DÍA 2**

### **Prioridad 1: Scraper Base (4 horas)**
1. **Crear `scraper_materias_obligatorias.py`**
2. **Implementar parsing de tablas HTML**
3. **Extraer 23 materias con departamentos**
4. **Generar JSON estructurado**

### **Prioridad 2: Normalización (2 horas)**  
5. **Crear mapeos de departamentos**
6. **Normalizar nombres de materias**
7. **Limpiar y validar datos**

### **Prioridad 3: Testing (2 horas)**
8. **Validar extracción de todas las materias**
9. **Verificar links departamentales**
10. **Generar reporte de calidad**

---

## 🔥 **ACCIÓN INMEDIATA**

**¿Procedemos con el desarrollo del scraper base?**

La estructura HTML es perfecta para scraping. Podemos tener el scraper de materias obligatorias funcionando en 2-3 horas y obtener los primeros 23 documentos estructurados para el RAG.

**¿Empezamos con el código del scraper?**
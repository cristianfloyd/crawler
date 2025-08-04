# DescubrirSitios - Documentación

## Descripción General

La clase `DescubrirSitios` es una herramienta para el descubrimiento automático y análisis de sitios web relacionados con la Facultad de Ciencias Exactas de la UBA. Utiliza técnicas de web crawling para mapear la infraestructura web de la facultad y analizar el contenido de cada sitio.

## Ubicación
```
descubrimiento/descubrir_sitios.py
```

## Propósito

Esta clase está diseñada para:
- TODO: Descubrir automáticamente sitios web relacionados con LCD (Licenciatura de ciencas de la computacion) Exactas UBA
- Analizar la tecnología utilizada en cada sitio (CMS, frameworks)
- Identificar sitios que contienen información académica relevante (materias, horarios, correlativas)
- Generar un inventario completo de los recursos web disponibles
- TODO: Priorizar sitios según su contenido académico y subcontenido
- TODO: En los links encontrados, deberiamos filtrar comentarios y paginas de archivo

## Configuración

### URLs Base
```python
URLS_BASE = [
    "https://lcd.exactas.uba.ar/",
]
```

### Dominios Permitidos
```python
DOMINIO = [
    "uba.ar",
]
```

### Patrones de Interés
La clase busca URLs y contenido relacionado con:
- `materias`, `horarios`, `cursadas`
- `programas`, `correlativas`
- `departamentos`, `carreras`
- `calendario`, `docentes`, `institutos`

### Departamentos Reconocidos
- matematica, computacion, fisica, quimica
- ciencias-atmosfera, geologicas
- biodiversidad, ecologia, instituto-calculo

## Arquitectura de la Clase

### Atributos Principales

- `sitios_encontrados`: Dict que almacena información detallada de cada sitio analizado
- `urls_visitadas`: Set de URLs ya procesadas para evitar duplicados
- `urls_por_procesar`: Set de URLs pendientes de análisis

### Métodos Principales

#### `detectar_tecnologia(html_content: str, url: str) -> Dict[str, str]`
Analiza el contenido HTML para identificar la tecnología del sitio.

**Tecnologías Detectadas:**
- **Mobirise**: Constructor de sitios estáticos
- **WordPress**: CMS popular
- **Drupal**: CMS empresarial
- **Joomla**: CMS de código abierto
- **Laravel**: Framework PHP
- **Plone**: CMS basado en Python
- **Estático**: Sitios HTML simples

**Retorna:**
```python
{
    "cms": "wordpress|drupal|mobirise|...",
    "framework": "constructor_estatico|...",
    "complejidad": "simple|media|compleja"
}
```

#### `extraer_links_relevantes(html_content: str, base_url: str) -> Set[str]`
Extrae enlaces relevantes del HTML basándose en patrones de interés y departamentos conocidos.

**Criterios de Filtrado:**
- Solo dominios UBA (uba.ar, exactas)
- URLs que coincidan con patrones académicos
- Enlaces a departamentos conocidos

#### `analizar_contenido_materias(html_content: str) -> Dict[str, any]`
Analiza si la página contiene información académica relevante.

**Indicadores Analizados:**
- Presencia de información de materias
- Horarios de cursada
- Correlativas/prerrequisitos
- Programas/contenidos

**Retorna:**
```python
{
    "tiene_materias": bool,
    "tiene_horarios": bool,
    "tiene_correlativas": bool,
    "tiene_programas": bool,
    "cantidad_materias_estimada": int,
    "tipos_informacion": list
}
```

#### `procesar_url(crawler, url: str) -> Dict[str, any]`
Procesa una URL individual de forma asíncrona.

**Funcionalidades:**
- Verifica si la URL ya fue visitada
- Excluye dominios deprecated (cms.dm.uba.ar)
- Extrae contenido con crawl4ai
- Analiza tecnología y contenido
- Descubre nuevos enlaces

**Retorna:** Diccionario con información completa del sitio o información de error/omisión.

#### `descubrir_sitios_completo(max_urls: int = 50)`
Ejecuta el proceso completo de descubrimiento de sitios.

**Proceso:**
1. Inicializa con URLs base
2. Procesa URLs de forma iterativa
3. Descubre nuevos enlaces en cada página
4. Continúa hasta alcanzar el límite o agotar URLs

#### `generar_reporte() -> Dict[str, any]`
Genera un reporte completo del proceso de descubrimiento.

**Estructura del Reporte:**
```python
{
    "resumen": {
        "total_sitios": int,
        "sitios_exitosos": int,
        "sitios_con_materias": int,
        "timestamp": str
    },
    "por_tecnologia": {
        "wordpress": ["url1", "url2"],
        "drupal": ["url3"],
        # ...
    },
    "sitios_prioritarios": [
        {
            "url": str,
            "titulo": str,
            "score": int,
            "tipos_info": list,
            "cms": str
        }
    ],
    "sitios_detalle": dict  # Información completa de todos los sitios
}
```

#### `guardar_resultados(archivo: str = "inventario_sitios.json")`
Guarda el inventario en formato JSON y muestra un resumen en consola.

**Características:**
- Crea directorio `data/` automáticamente
- Formato JSON con encoding UTF-8
- Muestra resumen estadístico
- Lista top 5 sitios prioritarios

## Flujo de Trabajo

1. **Inicialización**: Se crean las estructuras de datos y se configuran las URLs base
2. **Descubrimiento**: Se procesan URLs iterativamente usando crawl4ai
3. **Análisis**: Cada sitio se analiza para detectar tecnología y contenido académico
4. **Expansión**: Se extraen nuevos enlaces relevantes para continuar el descubrimiento
5. **Reportes**: Se genera un inventario completo con priorización automática

## Uso

### Ejecución Básica
```python
async def main():
    descubridor = DescubrirSitios()
    await descubridor.descubrir_sitios_completo(max_urls=40)
    descubridor.guardar_resultados()
```

### Ejecución desde Línea de Comandos
```bash
python descubrimiento/descubrir_sitios.py
```

## Outputs

### Archivo Principal
- `data/inventario_sitios.json`: Inventario completo con análisis detallado

### Información Generada
- Lista de todos los sitios descubiertos
- Análisis tecnológico de cada sitio
- Evaluación de contenido académico
- Priorización automática basada en relevancia
- Estadísticas de descubrimiento

## Casos de Uso

1. **Mapeo de Infraestructura**: Identificar todos los sitios web de la facultad
2. **Análisis Tecnológico**: Entender qué tecnologías se utilizan
3. **Priorización de Scraping**: Identificar sitios con mayor contenido académico
4. **Planificación de Extracción**: Preparar estrategias específicas por tecnología

## Limitaciones y Consideraciones

- **Límite de URLs**: Configurable para evitar crawling excesivo
- **Dominios Restringidos**: Solo procesa dominios UBA
- **Exclusiones**: Automáticamente excluye dominios deprecated
- **Detección Heurística**: La identificación de contenido académico usa patrones simples
- **Dependencias**: Requiere crawl4ai y BeautifulSoup

## Próximos Desarrollos

1. Integración con scrapers específicos por tecnología
2. Análisis más sofisticado de contenido académico
3. Detección automática de APIs y endpoints
4. Monitoreo de cambios en sitios descubiertos
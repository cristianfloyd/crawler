# 🚀 PUNTO DE ENTRADA UNIFICADO - DESCUBRIMIENTO DE MATERIAS

## 📋 Descripción
**Punto de entrada único** para ejecutar toda la cadena de descubrimiento y normalización de materias LCD, generando un archivo JSON con **nombre fijo** para consumo por otros scrapers del sistema.

## 🎯 Objetivo
Proveer una **interfaz estable** para que otros componentes del scraper puedan obtener las materias LCD actualizadas sin preocuparse por nombres de archivos con timestamps o procesos internos.

## 📁 Archivo Principal
### `descubrir_materias_completo.py` - **PUNTO DE ENTRADA MAESTRO**

**Uso básico:**
```bash
python descubrimiento/descubrir_materias_completo.py
```

## 🔄 Flujo de Ejecución

### **Cadena Completa Automatizada:**
1. **🔍 Extracción**: Ejecuta `identificar_materias_lcd.py` con esquema LCD
2. **🤖 Normalización**: Aplica `fase2_normalizar_nombres_automatico.py`
3. **📁 Archivo Final**: Genera `materias_lcd_descubiertas.json` (nombre fijo)
4. **✅ Validación**: Verifica estructura y contenido

## 📊 Archivo de Salida

### **Archivo Principal del Sistema**: `data/materias.json`
### **Archivo de Descubrimiento**: `data/materias_lcd_descubiertas.json` (para desarrollo interno)

**Estructura estable:**
```json
{
  "cbc": [
    {
      "nombre": "Introducción al Conocimiento de la Sociedad y el Estado",
      "nombre_normalizado": "Introducción al Conocimiento de la Sociedad y el Estado",
      "ciclo": "cbc",
      "departamento_probable": "cbc",
      "descripcion": "...",
      "fuente": "crawl4ai_css_lcd_schema"
    }
  ],
  "segundo_ciclo": [...],
  "tercer_ciclo": [...],
  "metadata": {
    "fecha_extraccion": "2025-08-03T...",
    "total_materias": 33,
    "punto_entrada": "descubrir_materias_completo.py",
    "archivo_consumible": true,
    "version_api": "1.0",
    "formato_estable": true
  }
}
```

## 🔗 Integración con Scrapers

### **Para Scrapers de Departamentos:**
```python
import json
import os

def cargar_materias_lcd():
    """Carga materias LCD desde archivo principal del sistema"""
    archivo_materias = os.path.join("data", "materias.json")
    
    with open(archivo_materias, 'r', encoding='utf-8') as f:
        materias_lista = json.load(f)
    
    # Filtrar por ciclo si es necesario
    materias_cbc = [m for m in materias_lista if m['ciclo'] == 'CBC']
    materias_segundo = [m for m in materias_lista if m['ciclo'] == 'Segundo Ciclo de Grado']
    materias_tercer = [m for m in materias_lista if m['ciclo'] == 'Tercer Ciclo de Grado']
    
    return {
        'cbc': materias_cbc,
        'segundo_ciclo': materias_segundo,
        'tercer_ciclo': materias_tercer,
        'todas': materias_lista
    }

# Usar en scrapers
materias_lcd = cargar_materias_lcd()
materias_cbc = materias_lcd['cbc']
materias_segundo = materias_lcd['segundo_ciclo'] 
caminos_tercer = materias_lcd['tercer_ciclo']
```

### **Para Pipeline Principal:**
```python
from descubrimiento.descubrir_materias_completo import DescubridorMateriasCompleto

async def actualizar_materias_lcd():
    """Actualiza materias LCD y devuelve ruta del archivo"""
    descubridor = DescubridorMateriasCompleto()
    ruta_final = await descubridor.ejecutar_descubrimiento_completo()
    return ruta_final

# Usar en pipeline
archivo_materias = await actualizar_materias_lcd()
# archivo_materias = "D:/crawler/data/materias_lcd_descubiertas.json"
```

## ⚡ Ventajas del Punto de Entrada Unificado

### **1. 🔗 Integración Simplificada**
- **Nombre fijo**: `materias_lcd_descubiertas.json`
- **Ubicación predecible**: `data/` directory
- **Estructura estable**: API consistente

### **2. 🤖 Proceso Automatizado**  
- **Extracción completa**: 33 materias (8 CBC + 14 Segundo + 11 Tercer)
- **Normalización automática**: Nombres limpios y consistentes
- **Validación integrada**: Verifica estructura y contenido

### **3. 📊 Metadata Rica**
- **Estadísticas de proceso**: Tiempos, cambios, métricas
- **Información de fuente**: URL, método, esquema utilizado
- **Versión de API**: Para compatibilidad futura

### **4. 🛡️ Robustez**
- **Validación exhaustiva**: Estructura JSON y contenido
- **Manejo de errores**: Mensajes claros y útiles
- **Trazabilidad**: Logs detallados del proceso

## 🎯 Casos de Uso

### **Caso 1: Actualización Manual**
```bash
# Ejecutar cuando se necesiten materias actualizadas
python descubrimiento/descubrir_materias_completo.py
```

### **Caso 2: Integración en Pipeline**
```python
# Desde pipeline principal
from descubrimiento.descubrir_materias_completo import DescubridorMateriasCompleto

descubridor = DescubridorMateriasCompleto()
archivo_final = await descubridor.ejecutar_descubrimiento_completo()
```

### **Caso 3: Consumo por Scrapers**
```python
# Desde scrapers de departamentos
import json

with open("data/materias.json", 'r') as f:
    materias_lista = json.load(f)
    
# Usar materias para cross-referencia
for materia in materias_lista:
    if materia['ciclo'] == 'Segundo Ciclo de Grado':
        print(f"Buscando horarios para: {materia['materia']}")
```

## 📈 Performance

### **Métricas Típicas:**
- **Tiempo total**: ~30-45 segundos
- **Materias procesadas**: 33 
- **Cambios de normalización**: 15-25 típicamente
- **Tamaño archivo final**: ~15-20 KB

### **Recursos:**
- **RAM**: ~100 MB durante ejecución
- **Disk**: Archivos temporales + archivo final
- **Network**: 1 request a lcd.exactas.uba.ar

## 🔧 Mantenimiento

### **Actualizar Materias:**
```bash
# Ejecutar cuando cambien materias en el sitio LCD
python descubrimiento/descubrir_materias_completo.py
```

### **Verificar Archivo:**
```python
import json
with open("data/materias.json", 'r') as f:
    materias = json.load(f)
    print(f"Total materias: {len(materias)}")
    
    # Contar por ciclo
    cbc = len([m for m in materias if m['ciclo'] == 'CBC'])
    segundo = len([m for m in materias if m['ciclo'] == 'Segundo Ciclo de Grado'])
    tercer = len([m for m in materias if m['ciclo'] == 'Tercer Ciclo de Grado'])
    
    print(f"CBC: {cbc}, Segundo: {segundo}, Tercer: {tercer}")
```

## 🎉 Resultado Esperado

**Archivo final generado:**
- ✅ **Nombre fijo**: `materias_lcd_descubiertas.json`
- ✅ **33 materias extraídas y normalizadas**
- ✅ **Estructura JSON validada**
- ✅ **Metadata completa incluida**
- ✅ **Listo para consumo por scrapers**

## 💡 Notas de Integración

### **Para Desarrolladores de Scrapers:**
1. **Usar archivo principal**: Siempre `data/materias.json` (usado por todo el sistema)
2. **Estructura de lista**: Formato `[{"materia": "...", "descripcion": "...", "ciclo": "..."}]`
3. **Filtrar por ciclo**: Usar campo `ciclo` para separar CBC, Segundo y Tercer ciclo
4. **Manejar errores**: El archivo puede no existir si no se ha inicializado

### **Para Pipeline Principal:**
1. **Ejecutar periódicamente**: Para mantener datos actualizados
2. **Monitorear duraciones**: Alertar si toma más de 2 minutos
3. **Validar resultado**: Verificar que el archivo final existe y es válido
4. **Integrar con CI/CD**: Ejecutar en deployments automáticos

**El punto de entrada unificado garantiza una interfaz estable y confiable para todo el sistema de scraping.** 🚀
# Proyecto de Análisis de Índices de Vegetación - TESIS

Sistema modular y profesional para análisis espacial y temporal de datos satelitales de áreas verdes.

## Descripción del Proyecto

Este sistema analiza datos de índices de vegetación obtenidos de imágenes satelitales Sentinel-2, con enfoque en:
- **Análisis espacial**: Mapas de calor, clustering, detección de zonas críticas
- **Análisis temporal**: Tendencias, estacionalidad, velocidad de cambio
- **Análisis estadístico**: Correlaciones entre índices, detección de anomalías
- **Segmentación**: Identificación de heterogeneidad en el cultivo

## Índices Soportados

| Índice | Nombre Completo | Rango | Aplicación |
|--------|----------------|-------|------------|
| **NDVI** | Normalized Difference Vegetation Index | -1 a 1 | Salud general de vegetación |
| **NDRE** | Normalized Difference Red Edge | -1 a 1 | Contenido de clorofila, estrés temprano |
| **MSAVI** | Modified Soil-Adjusted Vegetation Index | -1 a 1 | Vegetación con suelo visible |
| **RECI** | Red Edge Chlorophyll Index | 0 a 20+ | Nivel de clorofila |
| **NDMI** | Normalized Difference Moisture Index | -1 a 1 | Contenido de humedad, estrés hídrico |

## 🏗️ Arquitectura del Proyecto

```
Tesis_ANALISIS/
├── analizador_tesis/           # MÓDULO CORE (Funciones reutilizables)
│   ├── __init__.py
│   ├── procesador_base.py      # Carga + Enmascaramiento
│   ├── estadisticas.py         # Cálculos estadísticos avanzados
│   ├── temporal.py             # Análisis de series temporales
│   ├── espacial.py             # Análisis espacial
│   └── visualizador.py         # Gráficas reutilizables
│
├── scripts/                    # SCRIPTS EJECUTABLES
│   ├── 00_validacion_datos.py  # Validar shapefile + datos
│   ├── 01_analisis_exploratorio.py
│   ├── 02_analisis_espacial.py
│   ├── 03_analisis_temporal.py
│   ├── 04_segmentacion_zonas.py
│   ├── 05_correlacion_indices.py
│   ├── 06_deteccion_anomalias.py
│   └── inicio_analisis.py      # Menú unificado
│
├── configuracion/
│   └── config.py               # Configuración centralizada
│
├── reportes/                   # CSV generados
├── visualizaciones/            # Gráficas PNG
├── datos_procesados/           # Datos intermedios
└── reportes_pdf/               # Informes finales
```

## Instalación y Configuración

### [1] Crear y activar ambiente virtual

```powershell
# Navegar a la carpeta del proyecto
cd D:\TT\Tesis_ANALISIS

# Crear ambiente virtual
python -m venv venv

# Activar ambiente virtual (PowerShell)
.\venv\Scripts\Activate.ps1

# O en CMD
.\venv\Scripts\activate.bat
```

### [2] Instalar dependencias

```powershell
pip install -r requirements.txt
```

### [3] Verificar configuración

```powershell
# Validar que las rutas sean correctas
python -m configuracion.config
```

## Guía de Uso Rápida

### PASO 0: Validación de Datos (OBLIGATORIO)

**Siempre ejecuta esto PRIMERO** para verificar el enmascaramiento del shapefile:

```powershell
cd scripts
python 00_validacion_datos.py
```

Este script:
- Valida que el shapefile funcione correctamente
- Muestra cuántos píxeles están dentro del polígono
- Genera reportes de calidad por imagen
- Crea visualizaciones de ejemplo

**Ejemplo de salida:**
```
VALIDACIÓN DE CONFIGURACIÓN INICIAL
================================================================================

Ruta de descargas: D:\TT\Tesis_DESCARGAS\descargas\UPIITA_contours_25nov.2025
   ✓ Encontrada

Ruta de shapefile: D:\TT\Tesis_DESCARGAS\shapefiles\...\UPIITA_contours_25Nov2025.shp
   ✓ Encontrado
   • CRS: EPSG:4326
   • Número de polígonos: 1
   • Área total: 0.0001 unidades²

CONFIGURACIÓN VÁLIDA - LISTO PARA ANÁLISIS
```

### Flujo de Trabajo Completo

```
1. Validar datos          → scripts/00_validacion_datos.py
2. Análisis exploratorio  → scripts/01_analisis_exploratorio.py
3. Análisis espacial      → scripts/02_analisis_espacial.py
4. Análisis temporal      → scripts/03_analisis_temporal.py
5. Segmentación          → scripts/04_segmentacion_zonas.py
6. Correlaciones         → scripts/05_correlacion_indices.py
```

## 🔑 Características Clave

### Enmascaramiento Automático

Todos los análisis utilizan **enmascaramiento con shapefile** para:
- Eliminar píxeles fuera del área de interés
- Evitar contaminación por suelo desnudo, construcciones, etc.
- Trabajar solo con píxeles dentro del polígono definido

### Estadísticas Avanzadas

- **Básicas**: Media, mediana, desviación estándar, percentiles
- **Heterogeneidad**: Coeficiente de Variación (CV)
- **Distribución**: Skewness, kurtosis, IQR
- **Temporales**: Tendencias, velocidad de cambio
- **Espaciales**: Autocorrelación, clustering

### Visualizaciones Profesionales

- Mapas de calor con escala apropiada
- Series temporales con bandas de confianza
- Boxplots comparativos por fecha
- Histogramas de distribución
- Matrices de correlación

## Estructura de Reportes

Todos los análisis generan reportes en formato CSV en la carpeta `reportes/`:

```
reportes/
├── validacion_NDVI_20260108_143025.csv
├── estadisticas_NDVI_20260108_143530.csv
├── tendencias_temporal_NDVI.csv
└── resumen_validacion_20260108_143025.csv
```

## ⚙️ Configuración Avanzada

Edita `configuracion/config.py` para modificar:

```python
# Rutas del proyecto
RUTA_DESCARGAS = Path("...")
RUTA_SHAPEFILE = Path("...")

# Parámetros de análisis
DPI_GRAFICAS = 150
N_CLUSTERS_DEFAULT = 5
VENTANA_TEMPORAL_DIAS = 7
```

## Scripts Disponibles

### 0. `listar_indices.py` (Script auxiliar)
Muestra qué índices están disponibles en la carpeta de descargas y cuántas imágenes hay de cada uno.

**Uso:**
```bash
python listar_indices.py
```

### 1. `analizar_rangos_indices.py`
Analiza todas las imágenes de índices de vegetación y muestra estadísticas detalladas de los valores.

**Uso:**
```bash
python analizar_rangos_indices.py
```

**Salida:**
- Muestra estadísticas de cada imagen por índice (min, max, media, percentiles)
- Genera `estadisticas_<INDICE>.csv` con todas las estadísticas por índice
- Proporciona recomendaciones de umbrales para filtrado

### 2. `filtrar_datos_indices.py`
Filtra las imágenes de índices según umbrales definidos y crea una nueva carpeta con los datos filtrados.

**Configuración (dentro del script):**
```python
# Modifica estos valores según el índice que estés analizando
INDICE = "NDVI"              # Opciones: NDVI, NDRE, MSAVI, RECI, NDMI
UMBRAL_MINIMO = 0.0          # Límite inferior de valores
UMBRAL_MAXIMO = 1.0          # Límite superior de valores
```

**Uso:**
```bash
python filtrar_datos_indices.py
```
### 3. `graficar_series_indices.py`
Genera gráficos de serie temporal (media/mediana) y boxplots por fecha para cada índice.

**Uso:**
```bash
python graficar_series_indices.py
```

**Salida:**
- Carpeta `visualizaciones/<INDICE>/` con:
	- `serie_media_mediana_<INDICE>.png`
	- `boxplot_por_fecha_<INDICE>.png`

**Salida:**
- Crea carpeta `datos_filtrados/` con imágenes procesadas
- Genera `reporte_filtrado.csv` con estadísticas del filtrado
- Muestra cuántos píxeles fueron eliminados por imagen
## Consejos para la Tesis

### Justificación de Análisis

1. **¿Por qué validación primero?**
   - Garantiza calidad de datos
   - Detecta problemas de enmascaramiento
   - Documenta cobertura espacial

2. **¿Por qué análisis espacial?**
   - Identifica zonas críticas del cultivo
   - Detecta heterogeneidad (problemas de riego/nutrición)
   - Permite intervenciones focalizadas

3. **¿Por qué análisis temporal?**
   - Muestra evolución del cultivo
   - Detecta tendencias de deterioro/mejora
   - Permite predicción de estados futuros

4. **¿Por qué correlaciones?**
   - Relaciona vigor con humedad
   - Identifica índices redundantes
   - Optimiza monitoreo (menos índices = menos costo)

### Interpretación de Resultados

**Coeficiente de Variación (CV):**
- CV < 10%: Campo homogéneo (✓ bueno)
- CV 10-20%: Moderadamente heterogéneo
- CV > 20%: Muy heterogéneo (problemas)

**P-valor en tendencias:**
- p < 0.05: Tendencia significativa (confiable)
- p > 0.05: Tendencia no significativa (puede ser ruido)

## 🐛 Solución de Problemas

### Error: "No se encontró shapefile"
```powershell
# Verificar ruta en configuracion/config.py
python -m configuracion.config
```

### Error: "No module named 'geopandas'"
```powershell
# Reinstalar dependencias
pip install -r requirements.txt --upgrade
```

### Los análisis son muy lentos
- Reduce el número de imágenes
- Procesa un índice a la vez
- Usa datos filtrados en lugar de originales

## 📚 Referencias

- **NDVI**: Tucker, C. J. (1979). Red and photographic infrared linear combinations for monitoring vegetation.
- **NDMI**: Gao, B. C. (1996). NDWI—A normalized difference water index for remote sensing.
- **Sentinel-2**: ESA Copernicus Program

## 🤝 Contribuciones

Este proyecto es parte de una tesis de grado. Para consultas:
- Revisar documentación en cada script
- Consultar comentarios en código
- Ejecutar scripts con flag `-h` para ayuda

## Licencia

Proyecto académico - UPIITA IPN

---

**Última actualización**: Enero 2026  
**Versión**: 1.0.0

## Interpretación de Índices

### NDVI (Normalized Difference Vegetation Index)
- **< 0:** Agua, nubes, nieve
- **0 - 0.2:** Suelo desnudo, construcciones
- **0.2 - 0.5:** Vegetación escasa
- **0.5 - 0.8:** Vegetación moderada a densa
## Estructura de Salida

```
Tesis_ANALISIS/
├── venv/                          # Ambiente virtual (no subir a git)
├── datos_filtrados/               # Imágenes filtradas por índice
│   ├── NDVI/
│   ├── NDRE/
│   ├── MSAVI/
│   ├── RECI/
│   ├── NDMI/
│   └── reporte_filtrado_<INDICE>.csv
├── estadisticas_NDVI.csv          # Estadísticas pre-filtrado
├── estadisticas_NDRE.csv
├── estadisticas_MSAVI.csv
├── estadisticas_RECI.csv
└── estadisticas_NDMI.csv
```

## Notas Importantes

- **Siempre activa el ambiente virtual** antes de ejecutar los scripts
- Las dependencias se irán agregando a `requirements.txt` durante el desarrollo
- Cada índice se procesa de forma independiente RECI (Red Edge Chlorophyll Index)
- **Rango típico:** 0 a 20+
- Correlacionado con el contenido de clorofila

### NDMI (Normalized Difference Moisture Index)
- **Rango típico:** -1 a 1
- Sensible al contenido de humedad de la vegetaciónada a densa
- **> 0.8:** Vegetación muy densa

## Estructura de Salida

```
Tesis_ANALISIS/
├── datos_filtrados/          # Imágenes filtradas
│   ├── reporte_filtrado.csv  # Estadísticas del filtrado
│   └── UPIITA_contours_25nov.2025_YYYYMMDD_.../
│       ├── *.tiff            # Imagen NDVI filtrada
│       └── valores_pixeles/  # CSVs y shapefiles filtrados
└── estadisticas_ndvi.csv     # Estadísticas pre-filtrado
```

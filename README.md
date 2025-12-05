# Proyecto de Análisis de Índices de Vegetación

Este proyecto contiene scripts para analizar y filtrar imágenes de múltiples índices de vegetación del proyecto de descargas.

## Índices Soportados

- **NDVI** (Normalized Difference Vegetation Index)
- **NDRE** (Normalized Difference Red Edge)
- **MSAVI** (Modified Soil-Adjusted Vegetation Index)
- **RECI** (Red Edge Chlorophyll Index)
- **NDMI** (Normalized Difference Moisture Index)

## Instalación

### 1. Crear ambiente virtual

```bash
# Crear el ambiente virtual
python -m venv venv

# Activar el ambiente virtual
# En Windows PowerShell:
.\venv\Scripts\Activate.ps1

# En Windows CMD:
.\venv\Scripts\activate.bat

# En Linux/Mac:
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
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
## Flujo de Trabajo Recomendado

1. **Crear ambiente virtual:** Sigue las instrucciones de instalación arriba
2. **Analizar rangos:** Ejecuta `analizar_rangos_indices.py` para conocer la distribución de valores de cada índice
3. **Decidir umbrales:** Revisa las estadísticas y decide qué valores filtrar
4. **Modificar configuración:** Edita `filtrar_datos_indices.py` con el índice y umbrales deseados
5. **Filtrar datos:** Ejecuta `filtrar_datos_indices.py` para procesar las imágenes

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

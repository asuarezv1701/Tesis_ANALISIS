# Análisis de Índices de Vegetación - Instrucciones para macOS/Linux

Sistema modular para análisis espacial y temporal de datos satelitales de áreas verdes.

---

## Instalación rápida para macOS

### Paso 1: Verificar Python

```bash
# Verificar que tienes Python 3.10 o superior
python3 --version

# Si no tienes Python, instálalo con Homebrew:
brew install python@3.10
```

### Paso 2: Crear y activar ambiente virtual

```bash
# Navegar a la carpeta del proyecto
cd ~/Developer/TT/Tesis_ANALISIS

# Crear ambiente virtual
python3 -m venv venv

# Activar el ambiente virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Verificar instalación

```bash
# Con el ambiente activado
python verificar_sistema_completo.py
```

---

## Cómo usar el programa (macOS)

```bash
# Activar ambiente virtual
source venv/bin/activate

# Ejecutar menú principal
python inicio_analisis.py
```

### Comandos disponibles

```bash
python inicio_analisis.py              # Menú interactivo principal
python ver_resultados.py               # Ver resultados guardados
python verificar_sistema_completo.py   # Verificar configuración

# Scripts individuales
python scripts/00_validacion_datos.py
python scripts/01_analisis_exploratorio.py
python scripts/02_analisis_espacial.py
python scripts/03_analisis_temporal.py
python scripts/04_segmentacion_zonas.py
python scripts/05_predicciones_futuras.py
```

---

## Estructura de datos requerida

El sistema espera encontrar los datos en:

```
datos_filtrados/
├── NDVI/
│   └── pixeles_NDVI.csv
├── NDRE/
│   └── pixeles_NDRE.csv
├── MSAVI/
│   └── pixeles_MSAVI.csv
├── RECI/
│   └── pixeles_RECI.csv
└── NDMI/
    └── pixeles_NDMI.csv
```

Estos archivos CSV se generan con el sistema Tesis_DESCARGAS.

---

## Resultados generados

Todos los resultados se guardan en:

```
resultados/
├── reportes/              # Tablas CSV con estadísticas
├── visualizaciones/       # Gráficas PNG
├── datos_procesados/      # Datos intermedios
└── reportes_pdf/          # Informes finales (si se generan)
```

---

## Solución de problemas en macOS

### Error: "command not found: python"

Usa `python3` en lugar de `python`:

```bash
python3 -m venv venv
python3 inicio_analisis.py
```

### Error al instalar dependencias geoespaciales

Si tienes problemas con rasterio/geopandas:

```bash
# Instalar GDAL con Homebrew
brew install gdal

# Reinstalar dependencias
pip install --no-cache-dir -r requirements.txt
```

**Alternativa recomendada:** Usar Conda (ver NOTAS_CONDA.txt en la raíz del proyecto).

### Error: "No se encontraron datos"

Verifica que la carpeta `datos_filtrados/` exista y contenga los archivos CSV:

```bash
ls -R datos_filtrados/
```

Si no tienes datos, primero ejecuta el sistema Tesis_DESCARGAS para generar los archivos CSV.

---

## Dependencias en macOS

### Opción 1: venv + pip (recomendado para usuarios avanzados)

```bash
# Instalar dependencias del sistema con Homebrew
brew install gdal proj geos

# Crear ambiente y instalar paquetes
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Opción 2: Conda/Miniforge (recomendado para evitar problemas)

```bash
# Si ya tienes Conda instalado
conda env create -f environment.yml
conda activate analisis
```

Ver NOTAS_CONDA.txt para detalles completos.

---

## Diferencias con Windows

- **Activación del ambiente:**
  - Windows: `.\venv\Scripts\Activate.ps1`
  - macOS: `source venv/bin/activate`

- **Comandos Python:**
  - Windows: `python`
  - macOS: `python3` (o `python` dentro del venv)

- **Rutas:**
  - Todas las rutas usan `/` automáticamente
  - El código usa `pathlib.Path` para compatibilidad



---

## Desactivar el ambiente virtual

```bash
deactivate
```

---

## Notas adicionales

- Todos los scripts Python son compatibles con macOS sin modificaciones
- Las rutas se manejan automáticamente con `Path(__file__)`
- No hay dependencias específicas de Windows en el código
- El sistema detecta la plataforma automáticamente cuando es necesario

Para más detalles sobre el análisis y funcionalidades, consulta el README.md principal.

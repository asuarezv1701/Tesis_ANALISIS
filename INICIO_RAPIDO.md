# 🌿 Sistema de Análisis de Índices de Vegetación

## ✅ Proyecto Configurado Exitosamente

Tu proyecto en `Tesis_ANALISIS` está listo para analizar múltiples índices de vegetación.

## 📁 Estructura del Proyecto

```
Tesis_ANALISIS/
├── .gitignore                      # Archivos a ignorar en git
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Documentación principal
├── listar_indices.py              # 🔍 Listar índices disponibles
├── analizar_rangos_indices.py     # 📊 Analizar estadísticas
└── filtrar_datos_indices.py       # 🔧 Filtrar datos por umbrales
```

## 🚀 Inicio Rápido

### 1️⃣ Crear ambiente virtual (PRIMERA VEZ)

```powershell
# Ir a la carpeta del proyecto
cd c:\Users\XMK0181\Documents\TT\Tesis_ANALISIS

# Crear ambiente virtual
python -m venv venv

# Activar ambiente virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Activar ambiente virtual (CADA VEZ QUE TRABAJES)

```powershell
cd c:\Users\XMK0181\Documents\TT\Tesis_ANALISIS
.\venv\Scripts\Activate.ps1
```

### 3️⃣ Ver qué índices tienes disponibles

```powershell
python listar_indices.py
```

### 4️⃣ Analizar un índice

Edita `analizar_rangos_indices.py` línea 18:
```python
INDICE = "NDVI"  # Cambia por: NDRE, MSAVI, RECI, NDMI
```

Ejecuta:
```powershell
python analizar_rangos_indices.py
```

### 5️⃣ Filtrar datos

Edita `filtrar_datos_indices.py` líneas 19-23:
```python
INDICE = "NDVI"           # Mismo índice que analizaste
UMBRAL_MINIMO = 0.0       # Según análisis previo
UMBRAL_MAXIMO = 1.0       # Según análisis previo
```

Ejecuta:
```powershell
python filtrar_datos_indices.py
```

## 🎯 Índices Soportados

| Índice | Nombre Completo | Rango Típico | Uso Principal |
|--------|----------------|--------------|---------------|
| **NDVI** | Normalized Difference Vegetation Index | -1 a 1 | Salud general de vegetación |
| **NDRE** | Normalized Difference Red Edge | -1 a 1 | Contenido de clorofila |
| **MSAVI** | Modified Soil-Adjusted Vegetation Index | -1 a 1 | Vegetación con suelo visible |
| **RECI** | Red Edge Chlorophyll Index | 0 a 20+ | Nivel de clorofila |
| **NDMI** | Normalized Difference Moisture Index | -1 a 1 | Contenido de humedad |

## 📝 Notas Importantes

- ✅ **Siempre activa el ambiente virtual** antes de trabajar
- ✅ **Cada índice se procesa independientemente**
- ✅ **Las nuevas librerías se agregarán a `requirements.txt`**
- ✅ **Los datos filtrados se guardan en `datos_filtrados/<INDICE>/`**

## 🔄 Flujo de Trabajo Recomendado

```
1. Activar venv
    ↓
2. Listar índices disponibles (listar_indices.py)
    ↓
3. Elegir un índice y configurar scripts
    ↓
4. Analizar rangos (analizar_rangos_indices.py)
    ↓
5. Revisar estadísticas generadas (estadisticas_<INDICE>.csv)
    ↓
6. Decidir umbrales de filtrado
    ↓
7. Configurar y ejecutar filtrado (filtrar_datos_indices.py)
    ↓
8. Usar datos filtrados para análisis posterior
```

## 📊 Archivos Generados

- `estadisticas_<INDICE>.csv` - Estadísticas pre-filtrado
- `reporte_filtrado_<INDICE>.csv` - Resumen del filtrado
- `datos_filtrados/<INDICE>/` - Imágenes TIFF filtradas

---

**¿Siguiente paso?** Ejecuta: `python listar_indices.py`

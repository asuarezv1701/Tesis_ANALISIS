# 🎓 GUÍA RÁPIDA PARA DESARROLLO DE TESIS

## 📌 IMPORTANTE: Lee esto primero

Esta guía te ayudará a usar el sistema completo de descarga y análisis de datos satelitales Sentinel-2 para tu tesis.

---

## 🗂️ ESTRUCTURA DEL PROYECTO

```
TT/
├── Tesis_DESCARGAS/     → Descarga imágenes satelitales de Google Earth Engine
└── Tesis_ANALISIS/      → Analiza los datos descargados
```

---

## 🚀 INICIO RÁPIDO

### PASO 1: Configurar Tesis_DESCARGAS

```powershell
cd D:\TT\Tesis_DESCARGAS
```

#### 1.1 Activar entorno virtual
```powershell
.\activar_entorno.ps1
```

#### 1.2 Verificar que todo funciona
```powershell
python verificar_sistema.py
```

**Debe decir:** ✅ Sistema listo - Todas las dependencias instaladas

---

### PASO 2: Descargar datos satelitales

#### Opción A: Sistema completo (recomendado para principiantes)
```powershell
python inicio.py
```
Esto ejecuta automáticamente:
- Descarga de imágenes
- Extracción de píxeles
- Visualizaciones básicas

#### Opción B: Solo descargas
```powershell
python main.py
```

**Datos descargados se guardan en:**
```
Tesis_DESCARGAS/descargas/UPIITA_contours_25nov.2025/
├── NDVI/
├── NDRE/
├── MSAVI/
├── RECI/
└── NDMI/
```

---

### PASO 3: Analizar los datos

```powershell
cd D:\TT\Tesis_ANALISIS
```

#### 3.1 Activar entorno virtual
```powershell
.\venv\Scripts\Activate.ps1
```

#### 3.2 Ejecutar análisis completo
```powershell
python inicio_analisis.py
```

Esto genera:
- ✅ Estadísticas descriptivas
- ✅ Análisis espacial
- ✅ Análisis temporal
- ✅ Segmentación de zonas
- ✅ Predicciones futuras
- ✅ Reporte PDF completo

**Resultados se guardan en:**
```
Tesis_ANALISIS/resultados/
├── datos_procesados/     → CSVs y datos limpios
├── visualizaciones/      → Gráficos PNG
├── reportes/            → Estadísticas TXT/CSV
└── reportes_pdf/        → Reportes finales PDF
```

---

## 📊 ÍNDICES DE VEGETACIÓN DISPONIBLES

| Índice | Nombre | Rango | Uso |
|--------|--------|-------|-----|
| **NDVI** | Vegetación Normalizado | -1 a 1 | Salud general de vegetación |
| **NDRE** | Red Edge Normalizado | 0 a 1 | Salud de cultivos |
| **MSAVI** | Ajustado por Suelo | 0 a 1 | Vegetación en suelos expuestos |
| **RECI** | Clorofila Red Edge | 0.5 a 5 | Contenido de clorofila |
| **NDMI** | Humedad | -1 a 1 | Contenido de agua |

---

## ⚠️ PROBLEMAS COMUNES

### Error: "No se encontró el entorno virtual"
**Solución:**
```powershell
cd D:\TT\Tesis_DESCARGAS
python -m venv .venv
.\activar_entorno.ps1
```

### Error: "Google Earth Engine authentication"
**Solución:**
```powershell
earthengine authenticate
```
O asegúrate de tener el archivo `tesis-478920-4a9a68d2cbca.json` en la carpeta raíz.

### Error: "ModuleNotFoundError"
**Solución:**
```powershell
pip install --no-cache-dir -r requirements.txt
```

### Warning: "Python 3.10 will stop supporting..."
**No es un error.** Es solo una advertencia. El código funciona correctamente.

---

## 📝 FLUJO DE TRABAJO PARA TU TESIS

### FASE 1: Obtención de datos (1-2 días)
```
1. Ejecuta: python main.py en Tesis_DESCARGAS
2. Selecciona índices: NDVI, NDRE, MSAVI, RECI, NDMI
3. Define rango de fechas (mínimo 30 días)
4. Espera a que descargue (puede tardar horas)
```

### FASE 2: Análisis exploratorio (2-3 días)
```
1. Ejecuta: python inicio_analisis.py
2. Revisa reportes en resultados/reportes/
3. Analiza gráficos en resultados/visualizaciones/
```

### FASE 3: Redacción (depende de ti)
```
1. Usa los PDFs generados en resultados/reportes_pdf/
2. Exporta gráficos de resultados/visualizaciones/
3. Interpreta estadísticas de resultados/reportes/
```

---

## 🎯 COMANDOS ESENCIALES

### Para descargas (Tesis_DESCARGAS)
```powershell
# Sistema completo
python inicio.py

# Solo descargas
python main.py

# Solo visualizaciones
python visualizar_indices.py

# Solo extracción de píxeles
python extraer_pixeles.py

# Verificar sistema
python verificar_sistema.py
```

### Para análisis (Tesis_ANALISIS)
```powershell
# Análisis completo
python inicio_analisis.py

# Ver resultados
python ver_resultados.py

# Scripts individuales
python scripts/01_analisis_exploratorio.py
python scripts/02_analisis_espacial.py
python scripts/03_analisis_temporal.py
python scripts/04_segmentacion_zonas.py
python scripts/05_predicciones_futuras.py
python scripts/99_generar_reporte_pdf.py
```

---

## 📚 ARCHIVOS IMPORTANTES PARA TU TESIS

### Para Metodología:
- `README.md` en cada carpeta
- `INICIO_RAPIDO.md` en Tesis_ANALISIS

### Para Resultados:
- `resultados/reportes_pdf/*.pdf` → Reportes finales
- `resultados/visualizaciones/*.png` → Gráficos para tu documento

### Para Análisis:
- `resultados/datos_procesados/*.csv` → Datos procesados
- `resultados/reportes/*.txt` → Estadísticas detalladas

---

## 🔄 ACTUALIZAR EL CÓDIGO

Si necesitas la última versión del código:

```powershell
# Tesis_DESCARGAS
cd D:\TT\Tesis_DESCARGAS
git pull

# Tesis_ANALISIS
cd D:\TT\Tesis_ANALISIS
git pull
```

---

## 💡 TIPS PARA TU TESIS

1. **Documenta todo:** Cada vez que ejecutes algo, guarda los resultados con la fecha
2. **Backup frecuente:** Copia `resultados/` a otra ubicación regularmente
3. **Lee los logs:** En `logs/` encontrarás información detallada de errores
4. **Experimenta con fechas:** Diferentes épocas del año dan resultados diferentes
5. **Compara índices:** NDVI vs NDRE puede mostrar patrones interesantes

---

## 📞 SI ALGO FALLA

1. Lee el mensaje de error completo
2. Verifica que el entorno virtual esté activado
3. Revisa los archivos de log en `logs/`
4. Ejecuta `python verificar_sistema.py`
5. Si nada funciona, recrea el entorno virtual

---

## 🎓 PARA TU DOCUMENTO DE TESIS

### Metodología - Incluye:
- Descripción de índices (tabla arriba)
- Rango de fechas usado
- Área de estudio (UPIITA)
- Software: Python 3.10, Google Earth Engine, GeoPandas

### Resultados - Incluye:
- Gráficos de `resultados/visualizaciones/`
- Tablas de `resultados/reportes/`
- PDFs generados

### Discusión - Analiza:
- Tendencias temporales
- Patrones espaciales
- Correlaciones entre índices
- Implicaciones ecológicas

---

**Última actualización:** Enero 2026  
**Autor:** Sistema de Análisis Sentinel-2 para Tesis

---

## ✅ CHECKLIST ANTES DE ENTREGAR TU TESIS

- [ ] Todos los scripts corrieron sin errores
- [ ] Tienes todos los PDFs generados
- [ ] Backup de `resultados/` en 2 lugares diferentes
- [ ] Gráficos exportados en alta resolución
- [ ] Estadísticas revisadas y validadas
- [ ] Código documentado y comentado
- [ ] README actualizado con tus cambios
- [ ] Git commits con mensajes descriptivos

---

**¡ÉXITO EN TU TESIS! 🎓📊🛰️**

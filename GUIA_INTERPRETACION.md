# 📚 Guía de Interpretación de Resultados

## 🎯 ¿Qué significan los números que ves?

Esta guía te explica **qué es cada resultado** y **cómo interpretarlo** para tu tesis.

---

## 📊 ANÁLISIS TEMPORAL (El más importante)

### 1. Tendencia Lineal

Cuando ejecutas el análisis temporal, ves algo como esto:

```
1️⃣  Calculando tendencia lineal...
   • Pendiente: -0.00155079
   • R²: 0.2002
   • P-valor: 0.047934
   • Resultado: DECRECIENTE (significativa)
   • Cambio total: -0.1628 (-32.70%)
```

#### ¿Qué significa cada número?

**PENDIENTE: -0.00155079**
- Es el CAMBIO POR DÍA
- **Negativo** = La vegetación empeora cada día
- **Positivo** = La vegetación mejora cada día
- Ejemplo: -0.00155 significa que cada día pierde 0.00155 unidades
- En 100 días perdería: 0.00155 × 100 = 0.155 unidades

**R² (R-cuadrado): 0.2002**
- Mide **qué tan consistente** es la tendencia (de 0 a 1)
- **R² = 0.90-1.00** → Tendencia MUY fuerte y clara (casi perfecta)
- **R² = 0.70-0.89** → Tendencia fuerte
- **R² = 0.30-0.69** → Tendencia moderada (hay variabilidad)
- **R² < 0.30** → Tendencia débil (mucha variabilidad)
- Ejemplo: R²=0.20 significa "hay tendencia pero con bastante variación día a día"

**P-VALOR: 0.047934**
- Mide si la tendencia es **confiable o puede ser casualidad**
- **p < 0.05** = ✅ SIGNIFICATIVO (confiable, no es azar)
- **p > 0.05** = ❌ NO significativo (puede ser casualidad)
- Ejemplo: p=0.048 < 0.05 → La tendencia SÍ es real, no es azar

**CAMBIO TOTAL: -32.70%**
- Cuánto cambió del inicio al final
- -32.70% = Perdió casi un tercio de su valor
- Si empezó en 0.50 y terminó en 0.34, perdió el 32%

#### 📝 Cómo escribirlo en la tesis:

> *"El índice MSAVI presentó una tendencia decreciente significativa (p=0.048 < 0.05), con una pérdida promedio de 0.00155 unidades por día. Durante el período de estudio, se registró una disminución total del 32.7%. El coeficiente de determinación (R²=0.20) indica variabilidad moderada en torno a la tendencia, pero la dirección del cambio es consistente hacia el deterioro."*

---

### 2. Test de Mann-Kendall

```
2️⃣  Test de Mann-Kendall...
   • Tau de Kendall: -0.5579
   • P-valor: 0.000359
   • Resultado: TENDENCIA DECRECIENTE (significativa)
```

#### ¿Qué significa?

**TAU DE KENDALL: -0.5579**
- Otro método para confirmar la tendencia (de -1 a +1)
- **Cerca de -1** = Tendencia decreciente MUY fuerte
- **Cerca de +1** = Tendencia creciente MUY fuerte
- **Cerca de 0** = Sin tendencia
- Ejemplo: -0.56 → Tendencia decreciente bastante fuerte

**P-VALOR: 0.000359**
- Mismo concepto que antes
- p=0.00036 es MUCHO menor que 0.05
- ✅ Altamente significativo (99.96% de confianza)

#### 📝 Cómo escribirlo:

> *"El test no paramétrico de Mann-Kendall confirmó la tendencia decreciente (Tau=-0.56, p<0.001), validando los resultados de la regresión lineal con alta confiabilidad estadística."*

---

### 3. Velocidad de Cambio

```
3️⃣  Calculando velocidad de cambio...
   • Velocidad promedio: -0.005383 unidades/día
   • Velocidad máxima: 0.047882 unidades/día
   • Velocidad mínima: -0.103627 unidades/día
```

#### ¿Qué significa?

**VELOCIDAD PROMEDIO: -0.005383**
- Cambio promedio entre fechas consecutivas
- Negativo = En promedio, cada medición es menor que la anterior
- Es como la "velocidad de deterioro"

**VELOCIDAD MÁXIMA: 0.047882**
- El aumento MÁS GRANDE que se vio entre dos fechas
- Indica recuperación rápida en algún momento
- Puede ser por lluvia, mantenimiento, etc.

**VELOCIDAD MÍNIMA: -0.103627**
- La caída MÁS GRANDE entre dos fechas
- Indica deterioro muy rápido
- Puede señalar un evento específico (sequía, daño)

#### 📝 Cómo escribirlo:

> *"El análisis de velocidad de cambio reveló una disminución promedio de 0.0054 unidades por día entre mediciones consecutivas. Se detectó un evento de deterioro acelerado con pérdida de 0.1036 unidades/día, posiblemente asociado a condiciones de estrés hídrico o térmico."*

---

### 4. Comparación de Períodos

```
6️⃣  Comparando periodos...
   • Periodo 1: 10 imágenes, Media = 0.4443
   • Periodo 2: 10 imágenes, Media = 0.3542
   • Cambio: -0.0901 (-20.28%)
   • Cambio significativo
```

#### ¿Qué significa?

- Divide tus datos en dos mitades y las compara
- **Periodo 1**: Primera mitad del tiempo (ej: Sep-Oct)
- **Periodo 2**: Segunda mitad (ej: Nov-Ene)
- **Cambio -20.28%**: La segunda mitad está 20% peor que la primera
- **"Significativo"**: La diferencia es real, no es azar

#### 📝 Cómo escribirlo:

> *"La comparación entre períodos mostró un deterioro significativo (p<0.05), con una media de 0.44 en el primer período (septiembre-octubre) versus 0.35 en el segundo (noviembre-enero), representando una disminución del 20.3%."*

---

### 5. Punto de Quiebre

```
7️⃣  Detectando punto de quiebre...
   • Fecha de quiebre: 2025-10-27
   • Tipo de cambio: DESACELERACIÓN de la tendencia
   • R² total: 0.8977
```

#### ¿Qué significa?

**FECHA DE QUIEBRE: 2025-10-27**
- El día donde "algo cambió"
- Antes de esta fecha la tendencia era una, después cambió
- Puede indicar un evento: lluvia, sequía, mantenimiento, etc.

**TIPO DE CAMBIO:**
- **DESACELERACIÓN**: Antes caía más rápido, después más lento
- **ACELERACIÓN**: Empeora más rápido después del quiebre
- **MEJORA**: De empeorar pasa a mejorar
- **DETERIORO**: De mejorar pasa a empeorar

**R² TOTAL: 0.8977**
- Qué tan bien el modelo con quiebre explica los datos
- 0.90 es muy alto = el quiebre explica muy bien el cambio

#### 📝 Cómo escribirlo:

> *"Se identificó un punto de quiebre estructural el 27 de octubre de 2025 (R²=0.90), marcando una transición en la dinámica temporal. A partir de esta fecha se observó una desaceleración en la tasa de deterioro, sugiriendo cambios en las condiciones ambientales."*

---

## 🗺️ ANÁLISIS ESPACIAL

### Hotspots y Coldspots

```
• Hotspots: 1,234 px (8.5%) - Media: 0.7823
• Coldspots: 1,789 px (12.3%) - Media: 0.1234
```

#### ¿Qué significa?

**HOTSPOTS (puntos calientes)**
- Zonas con valores MUY ALTOS
- Son las áreas más saludables
- 8.5% = Solo el 8.5% del área está muy saludable
- Media 0.78 = En estas zonas el índice es 0.78 (alto)

**COLDSPOTS (puntos fríos)**
- Zonas con valores MUY BAJOS
- Son las áreas problemáticas/críticas
- 12.3% = El 12.3% del área está en mal estado
- Media 0.12 = En estas zonas el índice es solo 0.12 (bajo)

#### 📝 Cómo escribirlo:

> *"El análisis espacial identificó zonas críticas (coldspots) que representan el 12.3% del área total, con valores medios de 0.12. En contraste, solo el 8.5% del área presenta condiciones óptimas (hotspots, media=0.78), evidenciando heterogeneidad espacial significativa."*

---

### Clustering

```
Cluster 0: 2,345 px (20.1%), Media=0.15 [MUY BAJO]
Cluster 1: 3,456 px (29.6%), Media=0.32 [BAJO]
Cluster 2: 2,890 px (24.8%), Media=0.48 [MEDIO]
Cluster 3: 1,987 px (17.0%), Media=0.63 [ALTO]
Cluster 4: 978 px (8.4%), Media=0.79 [MUY ALTO]
```

#### ¿Qué significa?

- El algoritmo agrupó píxeles similares en 5 grupos (clusters)
- Cada cluster tiene píxeles con valores parecidos
- **Cluster 0**: El 20% del área tiene valores muy bajos (0.15)
- **Cluster 4**: Solo el 8% tiene valores muy altos (0.79)
- Conclusión: La mayor parte del área (50%) está en estado bajo-medio

#### 📝 Cómo escribirlo:

> *"El análisis de clustering K-means identificó cinco grupos espaciales distintos. El 20% del área se clasifica en el cluster de menor vigor (media=0.15), mientras que solo el 8% alcanza el nivel más alto (media=0.79). Aproximadamente el 50% del área se encuentra en condiciones bajas a medias, indicando necesidad de intervención."*

---

### Autocorrelación Espacial (Moran's I)

```
• I de Moran: 0.65
• Z-score: 12.45
• P-valor < 0.001
• Interpretación: Autocorrelación positiva significativa (agrupamiento)
```

#### ¿Qué significa?

**I DE MORAN: 0.65**
- Mide si píxeles cercanos son similares (de -1 a +1)
- **I positivo (0.3-1)**: Agrupamiento = zonas similares están juntas
- **I negativo (-1 a -0.3)**: Dispersión = patrón de tablero
- **I cerca de 0**: Distribución aleatoria
- I=0.65 → Fuerte agrupamiento espacial

#### ¿Qué implica?

- Las zonas malas tienden a estar JUNTAS
- Las zonas buenas tienden a estar JUNTAS
- NO están distribuidas aleatoriamente
- Sugiere que hay **factores locales** (drenaje, sombra, suelo) que afectan zonas contiguas

#### 📝 Cómo escribirlo:

> *"El índice I de Moran (I=0.65, p<0.001) reveló autocorrelación espacial positiva significativa, indicando que las zonas con vegetación degradada tienden a agruparse geográficamente. Este patrón sugiere que factores ambientales locales (drenaje, microclima, tipo de suelo) influyen en áreas contiguas, en lugar de una distribución aleatoria del deterioro."*

---

## 🎯 SEGMENTACIÓN DE ZONAS

### Resultados por Zona

```
Zona 0: 2,345 px (20%), Media=0.15
  • Tendencia: -0.008/día (R²=0.75, p<0.001)
  • Cambio total: -45.3%
  
Zona 4: 978 px (8%), Media=0.79
  • Tendencia: +0.002/día (R²=0.45, p=0.034)
  • Cambio total: +15.8%
```

#### ¿Qué significa?

**ZONA 0 (crítica):**
- 20% del área está en esta zona
- Media muy baja (0.15)
- Empeora rápido: -0.008/día
- R²=0.75 → Tendencia MUY consistente (empeora de forma clara)
- Perdió el 45% de su valor

**ZONA 4 (saludable):**
- Solo 8% del área
- Media alta (0.79)
- Mejora lentamente: +0.002/día
- Ganó el 15.8%

#### ¿Qué implica?

- El área NO es homogénea
- Hay zonas que están mucho peor que otras
- La Zona 0 necesita **intervención urgente**
- La Zona 4 puede ser un **modelo** de lo que funciona bien

#### 📝 Cómo escribirlo:

> *"La segmentación del área reveló alta heterogeneidad espacial. La Zona 0, que representa el 20% del área, presentó deterioro severo con pérdida del 45.3% y tendencia fuertemente negativa (R²=0.75, p<0.001), requiriendo intervención prioritaria. En contraste, la Zona 4 (8% del área) mostró recuperación del 15.8%, sugiriendo condiciones favorables que podrían replicarse."*

---

## 💡 EJEMPLO COMPLETO: Interpretación Integrada

### Datos obtenidos:

**Temporal:**
- Pendiente: -0.00155/día
- R²: 0.20, p=0.048
- Tau: -0.56, p<0.001
- Cambio: -32.7%

**Espacial:**
- Hotspots: 8.5%
- Coldspots: 12.3%
- I de Moran: 0.65

**Segmentación:**
- Zona crítica (20%): -45.3%
- Zona saludable (8%): +15.8%

### ✅ Interpretación para la Tesis:

> **"RESULTADOS Y DISCUSIÓN"**
>
> *El análisis temporal del índice MSAVI durante el período septiembre 2025 - enero 2026 reveló un deterioro generalizado de la vegetación en el área de estudio. Se identificó una tendencia decreciente estadísticamente significativa (pendiente=-0.00155 unidades/día, p=0.048), confirmada mediante el test no paramétrico de Mann-Kendall (Tau=-0.56, p<0.001). El coeficiente de determinación (R²=0.20) indica variabilidad moderada, consistente con la naturaleza dinámica de los sistemas vegetales urbanos.*
>
> *Durante el período analizado se registró una pérdida neta del 32.7% en el valor del índice. El análisis de velocidad de cambio identificó un evento de deterioro acelerado (-0.1036 unidades/día), posiblemente asociado a condiciones de estrés hídrico.*
>
> *El análisis espacial reveló heterogeneidad significativa en la distribución del deterioro. El 12.3% del área corresponde a zonas críticas (coldspots, media=0.12), mientras que solo el 8.5% mantiene condiciones óptimas (hotspots, media=0.78). El índice de autocorrelación espacial de Moran (I=0.65, p<0.001) indica que las zonas degradadas presentan agrupamiento geográfico, sugiriendo la influencia de factores ambientales locales como drenaje deficiente o exposición al sol.*
>
> *La segmentación del área en cinco zonas reveló diferencias significativas en las dinámicas temporales. La Zona 0 (20% del área) presentó el mayor deterioro (R²=0.75, pérdida del 45.3%), requiriendo intervención prioritaria. En contraste, la Zona 4 (8%) mostró recuperación del 15.8%, pudiendo servir como referencia de condiciones favorables.*
>
> *Estos resultados evidencian la necesidad de estrategias de manejo diferenciadas por zona, priorizando las áreas críticas identificadas mediante el análisis espacial y temporal integrado.*

---

## 🎓 Consejos para la Tesis

### 1. Siempre reporta 3 cosas:

1. **El valor** (ej: R²=0.75)
2. **La significancia** (ej: p<0.05)
3. **La interpretación** (ej: "tendencia fuerte y confiable")

### 2. Usa lenguaje técnico pero claro:

❌ **Mal:** "Los números bajaron"
✅ **Bien:** "Se observó una tendencia decreciente significativa (p<0.05)"

❌ **Mal:** "Hay zonas malas"
✅ **Bien:** "Se identificaron coldspots que representan el 12.3% del área"

### 3. Conecta los análisis:

No presentes resultados aislados. Ejemplo:

> *"El análisis temporal identificó deterioro generalizado (-32.7%), mientras que el análisis espacial reveló que este deterioro no es homogéneo, concentrándose en zonas específicas (coldspots, 12.3%). La segmentación confirmó esta heterogeneidad, identificando que el 20% del área (Zona 0) es responsable del mayor deterioro."*

### 4. Valores de referencia rápidos:

| Métrica | Bueno | Moderado | Malo |
|---------|-------|----------|------|
| R² | >0.7 | 0.3-0.7 | <0.3 |
| P-valor | <0.01 | 0.01-0.05 | >0.05 |
| \|Tau\| | >0.6 | 0.3-0.6 | <0.3 |
| CV (%) | <15 | 15-30 | >30 |

---

## ❓ Preguntas Frecuentes

**P: ¿Qué pasa si p-valor > 0.05?**
R: Significa que la tendencia NO es significativa. Puedes tenerla, pero no es confiable. Escribe: "Se observó una tendencia decreciente no significativa (p=0.12), sugiriendo variabilidad sin dirección clara."

**P: ¿R² bajo significa que mi análisis está mal?**
R: No. R² bajo significa que hay mucha variabilidad, lo cual es normal en vegetación. Lo importante es que la tendencia sea significativa (p<0.05).

**P: ¿Qué es mejor, clustering o cuadrantes?**
R: Depende:
- **Clustering**: Para agrupar zonas similares (más técnico)
- **Cuadrantes**: Para comparar regiones geográficas (más simple, más intuitivo)

**P: ¿Cuántas zonas debo usar en segmentación?**
R: Recomendado:
- 3-5 zonas para análisis simple
- 5-9 zonas para análisis detallado
- Más de 9 es difícil de interpretar

---

## 📐 FÓRMULAS MATEMÁTICAS UTILIZADAS

### Análisis Temporal

#### 1. Regresión Lineal Simple

**Modelo:**
$$y = \beta_0 + \beta_1 x + \epsilon$$

Donde:
- $y$ = Valor del índice de vegetación
- $x$ = Tiempo (días desde inicio)
- $\beta_0$ = Intercepto (valor inicial)
- $\beta_1$ = Pendiente (tasa de cambio por día)
- $\epsilon$ = Error residual

**Coeficiente de Determinación (R²):**
$$R^2 = 1 - \frac{SS_{res}}{SS_{tot}} = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$$

Donde:
- $SS_{res}$ = Suma de cuadrados residuales
- $SS_{tot}$ = Suma de cuadrados totales
- $\hat{y}_i$ = Valor predicho
- $\bar{y}$ = Media de valores observados

**Prueba de Significancia (Test t):**
$$t = \frac{\beta_1}{SE(\beta_1)}$$

P-valor derivado de distribución t de Student con n-2 grados de libertad.

**Referencias:**
- Montgomery, D. C., Peck, E. A., & Vining, G. G. (2012). *Introduction to Linear Regression Analysis* (5th ed.). Wiley.

---

#### 2. Test de Mann-Kendall

**Estadístico S:**
$$S = \sum_{i=1}^{n-1} \sum_{j=i+1}^{n} \text{sgn}(x_j - x_i)$$

Donde:
$$\text{sgn}(x) = \begin{cases} 
+1 & \text{si } x > 0 \\
0 & \text{si } x = 0 \\
-1 & \text{si } x < 0
\end{cases}$$

**Tau de Kendall:**
$$\tau = \frac{S}{n(n-1)/2}$$

**Varianza (sin empates):**
$$\text{Var}(S) = \frac{n(n-1)(2n+5)}{18}$$

**Estadístico Z:**
$$Z = \begin{cases}
\frac{S-1}{\sqrt{\text{Var}(S)}} & \text{si } S > 0 \\
0 & \text{si } S = 0 \\
\frac{S+1}{\sqrt{\text{Var}(S)}} & \text{si } S < 0
\end{cases}$$

**Referencias:**
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245-259.
- Kendall, M. G. (1975). *Rank Correlation Methods* (4th ed.). Charles Griffin.
- Gilbert, R. O. (1987). *Statistical Methods for Environmental Pollution Monitoring*. Wiley.

---

#### 3. Velocidad de Cambio

**Velocidad entre fechas consecutivas:**
$$v_i = \frac{y_{i+1} - y_i}{t_{i+1} - t_i}$$

Donde:
- $v_i$ = Velocidad de cambio en el intervalo i
- $y_i$ = Valor del índice en fecha i
- $t_i$ = Tiempo en fecha i (en días)

**Velocidad promedio:**
$$\bar{v} = \frac{1}{n-1} \sum_{i=1}^{n-1} v_i$$

---

#### 4. Detección de Punto de Quiebre (Breakpoint)

**Modelo segmentado:**
$$y = \begin{cases}
\beta_{01} + \beta_{11}x + \epsilon_1 & \text{si } x < x_b \\
\beta_{02} + \beta_{12}x + \epsilon_2 & \text{si } x \geq x_b
\end{cases}$$

Donde $x_b$ es el punto de quiebre que maximiza R² global.

**R² Total:**
$$R^2_{total} = 1 - \frac{SS_{res,1} + SS_{res,2}}{SS_{tot}}$$

**Referencias:**
- Muggeo, V. M. (2003). Estimating regression models with unknown break-points. *Statistics in Medicine*, 22(19), 3055-3071.
- Bai, J., & Perron, P. (2003). Computation and analysis of multiple structural change models. *Journal of Applied Econometrics*, 18(1), 1-22.

---

#### 5. Descomposición Estacional

**Modelo aditivo:**
$$y_t = T_t + S_t + R_t$$

**Modelo multiplicativo:**
$$y_t = T_t \times S_t \times R_t$$

Donde:
- $y_t$ = Serie temporal observada
- $T_t$ = Componente de tendencia
- $S_t$ = Componente estacional
- $R_t$ = Componente residual (ruido)

Implementado mediante método STL (Seasonal and Trend decomposition using Loess).

**Referencias:**
- Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990). STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, 6(1), 3-73.

---

### Análisis Espacial

#### 6. Detección de Hotspots/Coldspots

**Método Z-score:**
$$z_i = \frac{x_i - \mu}{\sigma}$$

Donde:
- $x_i$ = Valor del píxel i
- $\mu$ = Media de todos los píxeles
- $\sigma$ = Desviación estándar

Hotspots: $z > z_{umbral}$ (típicamente z > 1.5 o 2.0)
Coldspots: $z < -z_{umbral}$

**Método IQR (Rango Intercuartílico):**
$$\text{Hotspots: } x > Q_3 + k \times IQR$$
$$\text{Coldspots: } x < Q_1 - k \times IQR$$

Donde:
- $Q_1, Q_3$ = Cuartiles 1 y 3
- $IQR = Q_3 - Q_1$
- $k$ = Factor multiplicador (típicamente 1.5)

**Referencias:**
- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley.

---

#### 7. Clustering K-means

**Objetivo:** Minimizar la suma de distancias cuadradas dentro de clusters:
$$\arg\min_C \sum_{i=1}^{k} \sum_{x \in C_i} ||x - \mu_i||^2$$

Donde:
- $C_i$ = Cluster i
- $\mu_i$ = Centroide del cluster i
- $k$ = Número de clusters

**Inercia:**
$$I = \sum_{i=1}^{k} \sum_{x \in C_i} ||x - \mu_i||^2$$

**Referencias:**
- MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. *Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability*, 1(14), 281-297.
- Hartigan, J. A., & Wong, M. A. (1979). Algorithm AS 136: A k-means clustering algorithm. *Journal of the Royal Statistical Society, Series C*, 28(1), 100-108.

---

#### 8. DBSCAN (Density-Based Spatial Clustering)

**Definiciones:**
- **Vecindad-ε**: $N_\epsilon(p) = \{q \in D | \text{dist}(p,q) \leq \epsilon\}$
- **Punto núcleo**: $|N_\epsilon(p)| \geq \text{MinPts}$
- **Alcanzable desde densidad**: Si existe cadena de puntos núcleo

**Referencias:**
- Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *Proceedings of the Second International Conference on Knowledge Discovery and Data Mining (KDD-96)*, 226-231.

---

#### 9. Autocorrelación Espacial (I de Moran)

**Índice I de Moran:**
$$I = \frac{N}{W} \frac{\sum_i \sum_j w_{ij}(x_i - \bar{x})(x_j - \bar{x})}{\sum_i (x_i - \bar{x})^2}$$

Donde:
- $N$ = Número de píxeles
- $w_{ij}$ = Peso espacial entre píxeles i y j (1 si son vecinos, 0 si no)
- $W = \sum_i \sum_j w_{ij}$ = Suma total de pesos
- $x_i$ = Valor en píxel i
- $\bar{x}$ = Media global

**Valor esperado bajo hipótesis nula (aleatoriedad):**
$$E[I] = -\frac{1}{N-1}$$

**Estadístico Z:**
$$Z = \frac{I - E[I]}{\sqrt{\text{Var}(I)}}$$

**Interpretación:**
- $I > 0$: Autocorrelación positiva (agrupamiento)
- $I < 0$: Autocorrelación negativa (dispersión)
- $I \approx 0$: Distribución aleatoria

**Referencias:**
- Moran, P. A. (1950). Notes on continuous stochastic phenomena. *Biometrika*, 37(1/2), 17-23.
- Cliff, A. D., & Ord, J. K. (1981). *Spatial Processes: Models and Applications*. Pion.

---

### Estadísticas Básicas

#### 10. Coeficiente de Variación (CV)

$$CV = \frac{\sigma}{\mu} \times 100\%$$

Donde:
- $\sigma$ = Desviación estándar
- $\mu$ = Media

**Interpretación:**
- CV < 15%: Baja variabilidad (homogéneo)
- CV 15-30%: Variabilidad moderada
- CV > 30%: Alta variabilidad (heterogéneo)

**Referencias:**
- Pearson, K. (1896). Mathematical contributions to the theory of evolution. III. Regression, heredity, and panmixia. *Philosophical Transactions of the Royal Society of London, Series A*, 187, 253-318.

---

#### 11. Asimetría (Skewness)

$$\text{Skewness} = \frac{\frac{1}{n}\sum_{i=1}^{n}(x_i - \bar{x})^3}{\sigma^3}$$

**Interpretación:**
- Skewness > 0: Asimetría positiva (cola derecha)
- Skewness = 0: Simétrico
- Skewness < 0: Asimetría negativa (cola izquierda)

---

#### 12. Curtosis (Kurtosis)

$$\text{Kurtosis} = \frac{\frac{1}{n}\sum_{i=1}^{n}(x_i - \bar{x})^4}{\sigma^4} - 3$$

**Interpretación:**
- Kurtosis > 0: Leptocúrtica (colas pesadas, pico)
- Kurtosis = 0: Mesocúrtica (normal)
- Kurtosis < 0: Platicúrtica (colas ligeras, plana)

**Referencias:**
- Joanes, D. N., & Gill, C. A. (1998). Comparing measures of sample skewness and kurtosis. *Journal of the Royal Statistical Society, Series D*, 47(1), 183-189.

---

## 📚 BIBLIOGRAFÍA COMPLETA

### Índices de Vegetación

1. **Qi, J., Chehbouni, A., Huete, A. R., Kerr, Y. H., & Sorooshian, S. (1994).** A modified soil adjusted vegetation index. *Remote Sensing of Environment*, 48(2), 119-126.
   - **MSAVI**: Modified Soil-Adjusted Vegetation Index

2. **Hardisky, M. A., Klemas, V., & Smart, R. M. (1983).** The influence of soil salinity, growth form, and leaf moisture on the spectral radiance of Spartina alterniflora canopies. *Photogrammetric Engineering and Remote Sensing*, 49(1), 77-83.
   - **NDMI**: Normalized Difference Moisture Index

3. **Gitelson, A., & Merzlyak, M. N. (1994).** Spectral reflectance changes associated with autumn senescence of Aesculus hippocastanum L. and Acer platanoides L. leaves. *Journal of Plant Physiology*, 143(3), 286-292.
   - **NDRE**: Normalized Difference Red Edge

4. **Gitelson, A. A., Gritz, Y., & Merzlyak, M. N. (2003).** Relationships between leaf chlorophyll content and spectral reflectance and algorithms for non-destructive chlorophyll assessment in higher plant leaves. *Journal of Plant Physiology*, 160(3), 271-282.
   - **RECI**: Red Edge Chlorophyll Index

### Teledetección y Procesamiento de Imágenes

5. **Rouse, J. W., Haas, R. H., Schell, J. A., & Deering, D. W. (1974).** Monitoring vegetation systems in the Great Plains with ERTS. *Third Earth Resources Technology Satellite-1 Symposium*, NASA SP-351, 309-317.
   - Base de índices de vegetación normalizados

6. **Huete, A. R. (1988).** A soil-adjusted vegetation index (SAVI). *Remote Sensing of Environment*, 25(3), 295-309.
   - Ajuste por suelo en índices de vegetación

7. **ESA (European Space Agency). (2015).** Sentinel-2 User Handbook. ESA Standard Document.
   - Características del satélite Sentinel-2

### Análisis Estadístico Temporal

8. **Montgomery, D. C., Peck, E. A., & Vining, G. G. (2012).** *Introduction to Linear Regression Analysis* (5th ed.). Wiley.
   - Regresión lineal y análisis de tendencias

9. **Mann, H. B. (1945).** Nonparametric tests against trend. *Econometrica*, 13(3), 245-259.
   - Test de Mann-Kendall

10. **Kendall, M. G. (1975).** *Rank Correlation Methods* (4th ed.). Charles Griffin.
    - Estadística Tau de Kendall

11. **Gilbert, R. O. (1987).** *Statistical Methods for Environmental Pollution Monitoring*. Wiley.
    - Métodos estadísticos para monitoreo ambiental

12. **Cleveland, R. B., Cleveland, W. S., McRae, J. E., & Terpenning, I. (1990).** STL: A seasonal-trend decomposition procedure based on loess. *Journal of Official Statistics*, 6(1), 3-73.
    - Descomposición estacional

13. **Muggeo, V. M. (2003).** Estimating regression models with unknown break-points. *Statistics in Medicine*, 22(19), 3055-3071.
    - Detección de puntos de quiebre

### Análisis Espacial

14. **Moran, P. A. (1950).** Notes on continuous stochastic phenomena. *Biometrika*, 37(1/2), 17-23.
    - Índice I de Moran

15. **Cliff, A. D., & Ord, J. K. (1981).** *Spatial Processes: Models and Applications*. Pion.
    - Autocorrelación espacial

16. **Anselin, L. (1995).** Local indicators of spatial association—LISA. *Geographical Analysis*, 27(2), 93-115.
    - Análisis de clusters espaciales

17. **MacQueen, J. (1967).** Some methods for classification and analysis of multivariate observations. *Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability*, 1(14), 281-297.
    - Algoritmo K-means

18. **Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996).** A density-based algorithm for discovering clusters in large spatial databases with noise. *Proceedings of KDD-96*, 226-231.
    - Algoritmo DBSCAN

19. **Getis, A., & Ord, J. K. (1992).** The analysis of spatial association by use of distance statistics. *Geographical Analysis*, 24(3), 189-206.
    - Estadísticas de hotspots

### Vegetación Urbana y Áreas Verdes

20. **Nowak, D. J., & Greenfield, E. J. (2012).** Tree and impervious cover change in U.S. cities. *Urban Forestry & Urban Greening*, 11(1), 21-30.
    - Monitoreo de vegetación urbana

21. **Xie, Y., Sha, Z., & Yu, M. (2008).** Remote sensing imagery in vegetation mapping: a review. *Journal of Plant Ecology*, 1(1), 9-23.
    - Teledetección para mapeo de vegetación

22. **Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017).** Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18-27.
    - Plataforma Google Earth Engine

### Estadística General

23. **Tukey, J. W. (1977).** *Exploratory Data Analysis*. Addison-Wesley.
    - Análisis exploratorio de datos, detección de outliers

24. **Pearson, K. (1896).** Mathematical contributions to the theory of evolution. III. Regression, heredity, and panmixia. *Philosophical Transactions of the Royal Society of London, Series A*, 187, 253-318.
    - Coeficiente de variación

25. **Shapiro, S. S., & Wilk, M. B. (1965).** An analysis of variance test for normality (complete samples). *Biometrika*, 52(3/4), 591-611.
    - Test de normalidad

### Librerías de Software Utilizadas

26. **Van Rossum, G., & Drake, F. L. (2009).** *Python 3 Reference Manual*. CreateSpace.

27. **Harris, C. R., et al. (2020).** Array programming with NumPy. *Nature*, 585, 357-362.

28. **McKinney, W. (2010).** Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 56-61.

29. **Gillies, S., et al. (2013-).** Rasterio: Geospatial raster I/O for Python programmers. https://github.com/rasterio/rasterio

30. **Jordahl, K., et al. (2020).** geopandas/geopandas: v0.8.1. Zenodo. https://doi.org/10.5281/zenodo.3946761

31. **Hunter, J. D. (2007).** Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, 9(3), 90-95.

32. **Waskom, M., et al. (2017).** mwaskom/seaborn. Zenodo. https://doi.org/10.5281/zenodo.883859

33. **Pedregosa, F., et al. (2011).** Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.

34. **Seabold, S., & Perktold, J. (2010).** statsmodels: Econometric and statistical modeling with Python. *Proceedings of the 9th Python in Science Conference*, 92-96.

---

## 📊 VISUALIZACIÓN DE GRÁFICAS

### ¿Dónde están las gráficas?

Las visualizaciones se guardan automáticamente en:
```
D:\TT\Tesis_ANALISIS\visualizaciones\
```

Organizadas por índice y tipo de análisis:
- `MSAVI/exploratorio/` - Histogramas, boxplots, Q-Q plots
- `MSAVI/temporal/` - Series temporales, tendencias
- `MSAVI/espacial/` - Mapas de calor, hotspots
- `MSAVI/segmentacion/` - Mapas de zonas

### Tipos de Visualizaciones Generadas

| Análisis | Visualizaciones | Archivo |
|----------|----------------|---------|
| **Exploratorio** | Dashboard 4 paneles | `dashboard_[INDICE]_[FECHA]_*.png` |
| | Evolución CV | `evolucion_cv_[INDICE]_*.png` |
| **Temporal** | Serie temporal | `serie_temporal_[INDICE]_*.png` |
| | Tendencia lineal | `tendencia_lineal_[INDICE]_*.png` |
| | Velocidad cambio | `velocidad_cambio_[INDICE]_*.png` |
| | Comparación períodos | `comparacion_periodos_[INDICE]_*.png` |
| | Descomposición | `descomposicion_estacional_[INDICE]_*.png` |
| **Espacial** | Mapa de calor | `mapa_calor_[INDICE]_*.png` |
| | Hotspots/coldspots | `hotspots_[INDICE]_*.png` |
| | Clustering | `clustering_[INDICE]_*.png` |
| | Diferencias | `diferencia_[INDICE]_*.png` |
| **Segmentación** | Mapa de zonas | `mapa_zonas_[INDICE]_*.png` |
| | Series por zona | `series_temporales_[INDICE]_*.png` |
| | Tendencias zonas | `comparacion_tendencias_[INDICE]_*.png` |

### Cómo Incluir en la Tesis

Las imágenes están en formato PNG de alta resolución (150 DPI), listas para incluir en:
- Microsoft Word: Insertar → Imagen
- LaTeX: `\includegraphics{ruta/archivo.png}`
- PowerPoint: Insertar → Imagen

---

**¡Éxito con tu tesis! 🎓📊🌿**

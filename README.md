# Tarea 2 - CIT3352: Metaheurísticas y Algoritmos Exactos

## Estructura del Proyecto

```
TAREA2META/
|-- instance.py              - Parser de archivos de instancia
|-- solution.py              - Clase Solution con conteo de referencias O(k)
|-- greedy.py                - Greedy Determinista + Estocástico (RCL)
|-- simulated_annealing.py   - Simulated Annealing con tracking de convergencia
|-- genetic.py               - Algoritmo Genético con diversificación
|-- calibration.py           - Calibración de parámetros SA y GA
|-- graphs.py                - Generador de gráficos (44 gráficos PNG)
|-- main.py                  - Archivo principal
|-- easy.txt                 - Instancia fácil   (m=85,  n=100)
|-- medium1.txt              - Instancia media 1 (m=185, n=200)
|-- medium2.txt              - Instancia media 2 (m=166, n=200)
|-- hard.txt                 - Instancia difícil (m=585, n=700)
|-- graficos/                - Carpeta con 44 gráficos generados (creada al correr --graphs)
|-- calibracion_resultados/  - Tablas Markdown de calibración (creada al correr --calibrate)
```

## Requisitos

- Python 3.10+
- matplotlib (`pip install matplotlib`)
- numpy (`pip install numpy`)

## Cómo Ejecutar

```bash
# Ejecutar todos los algoritmos (10 corridas por instancia, resultados en consola)
python main.py

# Generar los 44 gráficos en carpeta graficos/
python main.py --graphs

# Ejecutar calibración de parámetros (SA + GA, instancias easy y medium1)
python main.py --calibrate

# Todo junto (algoritmos + calibración + gráficos)
python main.py --all
```

## Algoritmos Implementados

### 1. Greedy Determinista (`greedy.py`)

Selecciona iterativamente la alternativa con mayor ratio `beneficio / costo_marginal`. El costo marginal solo considera los recursos que aún no están cubiertos por alternativas ya seleccionadas. Si el costo marginal es 0, la alternativa se agrega sin costo adicional.

- Determinista: siempre produce la misma solución
- Complejidad por paso: O(m × k), donde k es el promedio de recursos por alternativa

### 2. Greedy Estocástico (`greedy.py`)

Similar al determinista, pero en cada paso construye una **RCL (Restricted Candidate List)** con las alternativas cuyo ratio está dentro de un umbral controlado por el parámetro `alpha`:

```
threshold = max_ratio - alpha * (max_ratio - min_ratio)
```

- `alpha = 0`: totalmente greedy (equivale al determinista)
- `alpha = 1`: totalmente aleatorio
- Usa `random.seed(run * 42 + 7)` por corrida para garantizar reproducibilidad
- Se ejecuta 10 veces por instancia con distintas semillas

### 3. Simulated Annealing (`simulated_annealing.py`)

Metaheurística de trayectoria que parte de una solución greedy y la mejora explorando el vecindario:

- **Add (40%)**: agrega una alternativa no seleccionada si es factible presupuestariamente
- **Remove (20%)**: remueve una alternativa, aceptando la degradación con probabilidad e^(Δ/T)
- **Swap (40%)**: intercambia una seleccionada por una no seleccionada (criterio de Metropolis)

Parámetros calibrados:
- `T_init`: temperatura inicial
- `T_min`: temperatura mínima (criterio de parada)
- `cooling_rate`: factor de enfriamiento geométrico (T *= cooling_rate)
- `max_iter_per_temp`: iteraciones por nivel de temperatura

Se ejecuta desde dos puntos de partida con 10 corridas independientes cada uno:
- Desde la solución del Greedy Determinista
- Desde la mejor solución del Greedy Estocástico

### 4. Algoritmo Genético (`genetic.py`)

Algoritmo de población con las siguientes características:

- **Población inicial**: generada con greedy estocástico usando distintos valores de alpha (0.1 a 1.0)
- **Selección**: torneo de tamaño k
- **Crossover**: uniforme (genes compartidos se heredan siempre, el resto con 50%)
- **Mutación**: bit-flip con probabilidad `mutation_rate` por gen
- **Elitismo**: se preserva el top 10% de la población
- **Diversificación**: si la población se estanca por 15+ generaciones, se inyectan nuevos individuos con alpha alto
- **Reparación**: individuos infactibles se reparan removiendo alternativas de menor beneficio absoluto
- **Mejora local**: se intenta agregar alternativas factibles después de reparar

## Módulos

### `instance.py`
Parser que lee los archivos `.txt` con formato:
```
m n ne B
beneficios[0..m-1]
pesos[0..n-1]
relaciones alternativa-recurso (ne líneas de: i j)
```

### `solution.py`
Clase `Solution` que mantiene un **conteo de referencias** por recurso (`ref_count`). Permite operaciones `add()` y `remove()` en O(k) donde k = recursos de la alternativa, sin recalcular el costo total desde cero en cada operación.

### `calibration.py`
Ejecuta experimentos sistemáticos variando parámetros (5 ejecuciones por configuración con semillas fijas):
- **SA**: 8 configuraciones (variando T_init, cooling_rate, max_iter_per_temp)
- **GA**: 6 configuraciones (variando pop_size, generations, mutation_rate, tournament_size)

Exporta resultados automáticamente a `calibracion_resultados/` en formato Markdown.

### `graphs.py`
Genera **44 gráficos PNG** en la carpeta `graficos/` (11 por instancia × 4 instancias):
- Boxplot Greedy Det vs Estocástico
- Boxplot comparativo todos los algoritmos
- Convergencia SA: FO vs Iteraciones
- Convergencia SA: FO vs Tiempo (segundos reales)
- Convergencia AG: Mejor, Promedio y Peor vs Generación
- Convergencia AG: Mejor, Promedio y Peor vs Tiempo
- Convergencia comparativa SA vs AG (progreso % y tiempo real)

## Resultados

| Instancia | Greedy Det | Greedy Est (avg) | SA Det (avg) | SA Est (avg) | GA (avg) | **Mejor** |
|-----------|-----------|-----------------|-------------|-------------|---------|-----------|
| easy      | 10764     | 10813.9         | 11553.7     | 11385.2     | 11894.3 | **12045** |
| medium1   | 10547     | 9594.5          | 10654.0     | 10475.0     | 10800.0 | **10973** |
| medium2   | 11397     | 10792.9         | 11816.5     | 11893.5     | 11814.9 | **12522** |
| hard      | 8781      | 8358.4          | 9153.9      | 9246.3      | 9531.3  | **10123** |

## Calibración de Parámetros

### SA — Mejores configuraciones encontradas

| Instancia | T_init | cooling_rate | iter/T | Avg Beneficio |
|-----------|--------|-------------|--------|---------------|
| easy      | 1000   | 0.999       | 100    | 11809.0       |
| medium1   | 1000   | 0.995       | 50     | 10694.6       |

### GA — Mejores configuraciones encontradas

| Instancia | Población | Generaciones | Mutación | Torneo | Avg Beneficio |
|-----------|----------|-------------|----------|--------|---------------|
| easy      | 50       | 200         | 0.05     | 3      | 11986.4       |
| medium1   | 50       | 200         | 0.05     | 5      | 10944.6       |

## Declaración de IA

Este proyecto fue desarrollado con apoyo de herramientas de IA generativa para:
- Optimización de la clase `Solution` con conteo de referencias en O(k)
- Generación de gráficos con matplotlib
- Documentación (este README)

La comprensión del problema, el diseño de los algoritmos, el análisis de resultados y la toma de decisiones de diseño fueron realizados por los integrantes del grupo.

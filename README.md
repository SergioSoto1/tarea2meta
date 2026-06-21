# Tarea 2 

## Estructura del Proyecto

```
TAREA2META/
|-- instance.py              # Parser de archivos de instancia
|-- solution.py              # Clase Solution con conteo de referencias
|-- greedy.py                # Greedy determinista + estocastico (RCL)
|-- simulated_annealing.py   # Simulated Annealing tracking de convergencia
|-- genetic.py               # Algoritmo Genetico con diversificacion
|-- calibration.py           # calibracion de parametros
|-- graphs.py                # Generador de graficos
|-- main.py                  # Archivo principal
|-- graficos/                # Carpeta con 20 graficos generados
|-- easy.txt                 
|-- medium1.txt              
|-- medium2.txt             
|-- hard.txt                 
```

## Requisitos

- Python 3.10+
- matplotlib (`pip install matplotlib`)
- numpy (`pip install numpy`)

## Como Ejecutar

```bash
# Ejecutar todos los algoritmos (resultados en consola)
python main.py

# Generar los 20 graficos en carpeta graficos/
python main.py --graphs

# Ejecutar calibracion de parametros (SA + GA)
python main.py --calibrate

# Todo junto
python main.py --all
```

## Algoritmos Implementados

### 1. Greedy Determinista (`greedy.py`)

Selecciona iterativamente la alternativa con mayor ratio `beneficio / costo_marginal`. El costo marginal solo considera los recursos que **aun no estan cubiertos** por alternativas ya seleccionadas. Si el costo marginal es 0 (todos los recursos ya estan cubiertos), la alternativa se agrega gratis.

- **Determinista**: siempre produce la misma solucion
- **Complejidad por paso**: O(m * k), donde k es el promedio de recursos por alternativa

### 2. Greedy Estocastico (`greedy.py`)

Similar al determinista, pero en cada paso construye una **RCL (Restricted Candidate List)** con las alternativas cuyo ratio esta dentro de un umbral controlado por el parametro `alpha`:

```
threshold = max_ratio - alpha * (max_ratio - min_ratio)
```

- `alpha = 0` → totalmente greedy (equivale al determinista)
- `alpha = 1` → totalmente aleatorio
- Usa `random.seed()` para reproducibilidad
- Se ejecuta **10 veces** por instancia con distintas semillas

### 3. Simulated Annealing (`simulated_annealing.py`)

Metaheuristica de trayectoria que parte de una solucion greedy y la mejora explorando el vecindario:

- **Add (40%)**: agrega una alternativa no seleccionada (si es factible)
- **Remove (20%)**: remueve una alternativa (aceptada probabilisticamente)
- **Swap (40%)**: intercambia una seleccionada por una no seleccionada

Parametros:
- `T_init`: temperatura inicial
- `T_min`: temperatura minima (criterio de parada)
- `cooling_rate`: factor de enfriamiento geometrico (T *= cooling_rate)
- `max_iter_per_temp`: iteraciones por nivel de temperatura

Se ejecuta desde **dos puntos de partida**: greedy determinista y mejor greedy estocastico.

### 4. Algoritmo Genetico (`genetic.py`)

Algoritmo de poblacion con las siguientes caracteristicas:

- **Poblacion inicial**: generada con greedy estocastico usando distintos valores de alpha (0.1 a 1.0) para maximizar diversidad
- **Seleccion**: torneo de tamano k
- **Crossover**: uniforme (genes compartidos se heredan siempre, el resto con 50%)
- **Mutacion**: bit-flip con probabilidad `mutation_rate` por gen
- **Elitismo**: se preserva el top 10% de la poblacion
- **Diversificacion**: si la poblacion se estanca por 15+ generaciones, se inyectan nuevos individuos generados con greedy estocastico
- **Reparacion**: individuos infactibles se reparan removiendo alternativas de menor beneficio
- **Mejora**: se intenta agregar alternativas factibles despues de reparar

## Modulos Auxiliares

### `instance.py`
Parser que lee los archivos `.txt` con formato:
```
m n ne B
beneficios[0..m-1]
pesos[0..n-1]
relaciones alternativa-recurso (ne lineas de: i j)
```

### `solution.py`
Clase `Solution` que mantiene un **conteo de referencias** por recurso. Esto permite operaciones `add()` y `remove()` en O(k) donde k = recursos de la alternativa, en lugar de recalcular todo desde cero en cada operacion.

### `calibration.py`
Ejecuta experimentos sistematicos variando parametros:
- **SA**: 8 configuraciones (variando T_init, cooling_rate, max_iter_per_temp)
- **GA**: 6 configuraciones (variando pop_size, generations, mutation_rate, tournament_size)
- 5 ejecuciones por configuracion, reportando best/avg/std/tiempo

### `graphs.py`
Genera 20 graficos PNG:
- **4x** Boxplot Greedy Det vs Estocastico (1 por instancia)
- **4x** Boxplot todos los algoritmos (1 por instancia)
- **4x** Curvas de convergencia SA (det vs est como punto de partida)
- **4x** Curvas de convergencia AG
- **4x** Convergencia comparativa SA vs AG

## Resultados

| Instancia | Greedy Det | Greedy Est (avg) | SA Det (avg) | SA Est (avg) | GA (avg) | **Mejor** |
|-----------|-----------|-----------------|-------------|-------------|---------|-----------|
| easy      | 10764     | 10813.9         | 11553.7     | 11385.2     | 11894.3 | **12045** |
| medium1   | 10547     | 9594.5          | 10654.0     | 10475.0     | 10800.0 | **10973** |
| medium2   | 11397     | 10792.9         | 11816.5     | 11893.5     | 11814.9 | **12522** |
| hard      | 8781      | 8358.4          | 9153.9      | 9246.3      | 9531.3  | **10123** |

## Calibracion de Parametros

### SA — Mejores configuraciones encontradas

| Instancia | T_init | cooling_rate | iter/T | Avg Beneficio |
|-----------|--------|-------------|--------|---------------|
| easy      | 1000   | 0.999       | 100    | 11809.0       |
| medium1   | 1000   | 0.995       | 50     | 10694.6       |

### GA — Mejores configuraciones encontradas

| Instancia | Poblacion | Generaciones | Mutacion | Avg Beneficio |
|-----------|----------|-------------|----------|---------------|
| easy      | 50       | 200         | 0.05     | 11986.4       |
| medium1   | 50       | 200         | 0.05     | 10867.8       |

## Declaracion de IA

Este proyecto fue desarrollado con apoyo de herramientas de IA generativa para:
- Estructura modular del codigo
- Generacion de graficos con matplotlib
- Documentacion (este README)

La comprension del problema, el diseno de los algoritmos, el analisis de resultados y la redaccion del informe fueron realizados por los integrantes del grupo.

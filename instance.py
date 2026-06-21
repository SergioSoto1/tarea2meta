"""
Tarea 2 - CIT3352
Parser de instancias del problema de selección de proyectos.
"""


class Instance:
    """Representa una instancia del problema de selección de proyectos con presupuesto."""

    def __init__(self, filepath):
        self.filepath = filepath
        with open(filepath, 'r') as f:
            lines = f.read().split('\n')

        # Línea 1: m (alternativas), n (recursos), ne (relaciones), B (capacidad)
        header = lines[0].strip().split()
        self.m = int(header[0])
        self.n = int(header[1])
        self.ne = int(header[2])
        self.B = int(header[3])

        # Línea 2: beneficio de cada alternativa i
        self.profits = list(map(int, lines[1].strip().split()))

        # Línea 3: peso/costo de cada recurso j
        self.weights = list(map(int, lines[2].strip().split()))

        # Relaciones alternativa-recurso
        self.alt_resources = [set() for _ in range(self.m)]
        for k in range(self.ne):
            parts = lines[3 + k].strip().split()
            self.alt_resources[int(parts[0])].add(int(parts[1]))

    def __repr__(self):
        return f"Instance({self.filepath}: m={self.m}, n={self.n}, ne={self.ne}, B={self.B})"

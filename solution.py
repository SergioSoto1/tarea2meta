"""
Tarea 2 - CIT3352
Clase Solution con conteo de referencias para operaciones eficientes O(|recursos_alt|).
"""


class Solution:
    """
    Solución al problema de selección de proyectos.
    Mantiene un conteo de referencias por recurso para permitir
    add/remove en O(|recursos de la alternativa|) sin recalcular todo.
    """

    def __init__(self, inst, selected=None):
        self.inst = inst
        self.selected = set(selected) if selected else set()
        self.ref_count = [0] * inst.n
        self.cost = 0
        self.benefit = 0
        for i in self.selected:
            self.benefit += inst.profits[i]
            for j in inst.alt_resources[i]:
                if self.ref_count[j] == 0:
                    self.cost += inst.weights[j]
                self.ref_count[j] += 1

    def can_add(self, i):
        """Retorna True si agregar alternativa i mantiene factibilidad."""
        add_cost = sum(self.inst.weights[j] for j in self.inst.alt_resources[i] if self.ref_count[j] == 0)
        return self.cost + add_cost <= self.inst.B

    def marginal_cost(self, i):
        """Costo marginal de agregar alternativa i (solo recursos nuevos)."""
        return sum(self.inst.weights[j] for j in self.inst.alt_resources[i] if self.ref_count[j] == 0)

    def add(self, i):
        """Agrega alternativa i a la solución."""
        self.selected.add(i)
        self.benefit += self.inst.profits[i]
        for j in self.inst.alt_resources[i]:
            if self.ref_count[j] == 0:
                self.cost += self.inst.weights[j]
            self.ref_count[j] += 1

    def remove(self, i):
        """Remueve alternativa i de la solución."""
        self.selected.remove(i)
        self.benefit -= self.inst.profits[i]
        for j in self.inst.alt_resources[i]:
            self.ref_count[j] -= 1
            if self.ref_count[j] == 0:
                self.cost -= self.inst.weights[j]

    def copy(self):
        """Copia eficiente de la solución."""
        s = Solution.__new__(Solution)
        s.inst = self.inst
        s.selected = set(self.selected)
        s.ref_count = list(self.ref_count)
        s.cost = self.cost
        s.benefit = self.benefit
        return s

    def is_feasible(self):
        return self.cost <= self.inst.B

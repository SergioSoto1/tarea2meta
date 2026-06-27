class Solution:

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
        add_cost = sum(self.inst.weights[j] for j in self.inst.alt_resources[i] if self.ref_count[j] == 0)
        return self.cost + add_cost <= self.inst.B

    def marginal_cost(self, i):
        return sum(self.inst.weights[j] for j in self.inst.alt_resources[i] if self.ref_count[j] == 0)

    def add(self, i):
        self.selected.add(i)
        self.benefit += self.inst.profits[i]
        for j in self.inst.alt_resources[i]:
            if self.ref_count[j] == 0:
                self.cost += self.inst.weights[j]
            self.ref_count[j] += 1

    def remove(self, i):
        self.selected.remove(i)
        self.benefit -= self.inst.profits[i]
        for j in self.inst.alt_resources[i]:
            self.ref_count[j] -= 1
            if self.ref_count[j] == 0:
                self.cost -= self.inst.weights[j]

    def copy(self):
        s = Solution.__new__(Solution)
        s.inst = self.inst
        s.selected = set(self.selected)
        s.ref_count = list(self.ref_count)
        s.cost = self.cost
        s.benefit = self.benefit
        return s

    def is_feasible(self):
        return self.cost <= self.inst.B

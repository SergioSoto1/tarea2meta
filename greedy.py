"""
Tarea 2 - CIT3352
Algoritmos Greedy: Determinista y Estocástico (con RCL).
"""

import random
from solution import Solution


def greedy_deterministic(inst):
    """
    Greedy determinista: selecciona en cada paso la alternativa con mayor
    ratio beneficio / costo_marginal que sea factible.
    Si costo_marginal = 0, el ratio es infinito (prioridad máxima).
    """
    sol = Solution(inst)
    candidates = set(range(inst.m))

    while candidates:
        best_alt = None
        best_ratio = -1

        for i in list(candidates):
            mc = sol.marginal_cost(i)
            if sol.cost + mc > inst.B:
                candidates.discard(i)
                continue
            ratio = inst.profits[i] / mc if mc > 0 else float('inf')
            if ratio > best_ratio:
                best_ratio = ratio
                best_alt = i

        if best_alt is None:
            break
        sol.add(best_alt)
        candidates.remove(best_alt)

    return sol


def greedy_stochastic(inst, alpha=0.3):
    """
    Greedy estocástico con RCL (Restricted Candidate List).
    alpha=0 → totalmente greedy, alpha=1 → totalmente aleatorio.
    Requiere fijar random.seed() antes de llamar para reproducibilidad.
    """
    sol = Solution(inst)
    candidates = set(range(inst.m))

    while candidates:
        feasible = []
        to_remove = []
        for i in candidates:
            mc = sol.marginal_cost(i)
            if sol.cost + mc > inst.B:
                to_remove.append(i)
                continue
            ratio = inst.profits[i] / mc if mc > 0 else float('inf')
            feasible.append((i, ratio))
        for i in to_remove:
            candidates.discard(i)

        if not feasible:
            break

        # Construir RCL
        inf_cands = [x for x in feasible if x[1] == float('inf')]
        if inf_cands:
            chosen_i = random.choice(inf_cands)[0]
        else:
            ratios = [x[1] for x in feasible]
            max_r, min_r = max(ratios), min(ratios)
            threshold = max_r - alpha * (max_r - min_r)
            rcl = [x for x in feasible if x[1] >= threshold]
            chosen_i = random.choice(rcl)[0]

        sol.add(chosen_i)
        candidates.remove(chosen_i)

    return sol

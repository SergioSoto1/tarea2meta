"""
Tarea 2 - CIT3352
Simulated Annealing con tracking de convergencia.
"""

import random
import math
from solution import Solution


def simulated_annealing(inst, initial_selected, T_init=1000, T_min=0.1,
                        cooling_rate=0.995, max_iter_per_temp=100,
                        track_convergence=False):
    """
    Simulated Annealing para el problema de selección de proyectos.

    Vecindario:
      - Add (40%): agregar una alternativa no seleccionada si es factible
      - Remove (20%): remover una alternativa (aceptada probabilísticamente)
      - Swap (40%): intercambiar una seleccionada por una no seleccionada

    Args:
        inst: Instancia del problema
        initial_selected: Conjunto de alternativas iniciales (de greedy)
        T_init: Temperatura inicial
        T_min: Temperatura mínima (criterio de parada)
        cooling_rate: Factor de enfriamiento geométrico
        max_iter_per_temp: Iteraciones por nivel de temperatura
        track_convergence: Si True, retorna también historial de convergencia

    Returns:
        best: Mejor solución encontrada
        history: (solo si track_convergence) lista de (iteración, mejor_beneficio)
    """
    current = Solution(inst, initial_selected)
    best = current.copy()
    not_sel = list(set(range(inst.m)) - current.selected)
    sel_list = list(current.selected)
    T = T_init

    history = []
    total_iter = 0

    while T > T_min:
        for _ in range(max_iter_per_temp):
            total_iter += 1
            move = random.random()

            if move < 0.4 and not_sel:
                # ADD
                idx = random.randrange(len(not_sel))
                alt = not_sel[idx]
                mc = sum(inst.weights[j] for j in inst.alt_resources[alt] if current.ref_count[j] == 0)
                if current.cost + mc <= inst.B:
                    current.add(alt)
                    sel_list.append(alt)
                    not_sel[idx] = not_sel[-1]
                    not_sel.pop()

            elif move < 0.6 and sel_list:
                # REMOVE
                idx = random.randrange(len(sel_list))
                alt = sel_list[idx]
                delta = -inst.profits[alt]
                if delta > 0 or random.random() < math.exp(delta / T):
                    current.remove(alt)
                    not_sel.append(alt)
                    sel_list[idx] = sel_list[-1]
                    sel_list.pop()

            elif sel_list and not_sel:
                # SWAP
                s_idx = random.randrange(len(sel_list))
                n_idx = random.randrange(len(not_sel))
                alt_out = sel_list[s_idx]
                alt_in = not_sel[n_idx]

                current.remove(alt_out)
                mc = sum(inst.weights[j] for j in inst.alt_resources[alt_in] if current.ref_count[j] == 0)
                if current.cost + mc <= inst.B:
                    delta = inst.profits[alt_in] - inst.profits[alt_out]
                    if delta > 0 or random.random() < math.exp(delta / T):
                        current.add(alt_in)
                        sel_list[s_idx] = alt_in
                        not_sel[n_idx] = alt_out
                    else:
                        current.add(alt_out)
                else:
                    current.add(alt_out)

            if current.benefit > best.benefit:
                best = current.copy()

            if track_convergence and total_iter % 50 == 0:
                history.append((total_iter, best.benefit))

        T *= cooling_rate

    if track_convergence:
        return best, history
    return best

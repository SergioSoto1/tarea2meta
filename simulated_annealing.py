import random
import math
import time
from solution import Solution


def simulated_annealing(inst, initial_selected, T_init=1000, T_min=0.1,
                        cooling_rate=0.995, max_iter_per_temp=100,
                        track_convergence=False):
    current = Solution(inst, initial_selected)
    best = current.copy()
    not_sel = list(set(range(inst.m)) - current.selected)
    sel_list = list(current.selected)
    T = T_init
    t_start = time.time()

    history = []
    total_iter = 0

    while T > T_min:
        for _ in range(max_iter_per_temp):
            total_iter += 1
            move = random.random()

            if move < 0.4 and not_sel:
                idx = random.randrange(len(not_sel))
                alt = not_sel[idx]
                mc = sum(inst.weights[j] for j in inst.alt_resources[alt] if current.ref_count[j] == 0)
                if current.cost + mc <= inst.B:
                    current.add(alt)
                    sel_list.append(alt)
                    not_sel[idx] = not_sel[-1]
                    not_sel.pop()

            elif move < 0.6 and sel_list:
                idx = random.randrange(len(sel_list))
                alt = sel_list[idx]
                delta = -inst.profits[alt]
                if delta > 0 or random.random() < math.exp(delta / T):
                    current.remove(alt)
                    not_sel.append(alt)
                    sel_list[idx] = sel_list[-1]
                    sel_list.pop()

            elif sel_list and not_sel:
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
                history.append((total_iter, time.time() - t_start, best.benefit))

        T *= cooling_rate

    if track_convergence:
        return best, history
    return best

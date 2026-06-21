"""
Tarea 2 - CIT3352: Algoritmos Exactos y Metaheurísticas
Archivo principal — Orquesta la ejecución de todos los algoritmos.

Uso:
    python main.py              → Ejecutar todos los algoritmos
    python main.py --graphs     → Generar gráficos para el informe
    python main.py --calibrate  → Calibración de parámetros
    python main.py --all        → Todo junto
"""

import sys
import random
import time
import statistics

from instance import Instance
from greedy import greedy_deterministic, greedy_stochastic
from simulated_annealing import simulated_annealing
from genetic import genetic_algorithm


SA_PARAMS = {
    'easy.txt':    dict(T_init=500,  T_min=0.01, cooling_rate=0.99,  max_iter_per_temp=200),
    'medium1.txt': dict(T_init=1000, T_min=0.01, cooling_rate=0.995, max_iter_per_temp=150),
    'medium2.txt': dict(T_init=1000, T_min=0.01, cooling_rate=0.995, max_iter_per_temp=150),
    'hard.txt':    dict(T_init=2000, T_min=0.1,  cooling_rate=0.997, max_iter_per_temp=80),
}

GA_PARAMS = {
    'easy.txt':    dict(pop_size=50, generations=200, mutation_rate=0.05, tournament_size=3),
    'medium1.txt': dict(pop_size=50, generations=200, mutation_rate=0.05, tournament_size=3),
    'medium2.txt': dict(pop_size=50, generations=200, mutation_rate=0.05, tournament_size=3),
    'hard.txt':    dict(pop_size=50, generations=150, mutation_rate=0.05, tournament_size=3),
}

FILES = ['easy.txt', 'medium1.txt', 'medium2.txt', 'hard.txt']


def run_all():
    print("=" * 80)
    print("TAREA 2 - CIT3352: Algoritmos Exactos y Metaheurísticas")
    print("Problema de Selección de Proyectos con Presupuesto")
    print("=" * 80)

    for fname in FILES:
        print(f"\n{'='*80}\nINSTANCIA: {fname}\n{'='*80}")
        inst = Instance(fname)
        print(f"  m={inst.m}, n={inst.n}, ne={inst.ne}, B={inst.B}")

        sa_p = SA_PARAMS[fname]
        ga_p = GA_PARAMS[fname]

        # =====================================================================
        # 1. GREEDY DETERMINISTA
        # =====================================================================
        print(f"\n--- 1. Greedy Determinista ---")
        t0 = time.time()
        det = greedy_deterministic(inst)
        t1 = time.time()
        print(f"  Beneficio={det.benefit}, Costo={det.cost}/{inst.B}, "
              f"#Alt={len(det.selected)}, T={t1-t0:.4f}s")
        print(f"  Solución: {sorted(det.selected)}")

        # =====================================================================
        # 2. GREEDY ESTOCÁSTICO (10 runs)
        # =====================================================================
        print(f"\n--- 2. Greedy Estocástico (10 runs, alpha=0.3) ---")
        stoch_benefits = []
        stoch_sols = []
        for run in range(10):
            random.seed(run * 42 + 7)
            t0 = time.time()
            s = greedy_stochastic(inst, alpha=0.3)
            t1 = time.time()
            stoch_benefits.append(s.benefit)
            stoch_sols.append(s)
            print(f"  Run {run+1:2d}: B={s.benefit:6d}, C={s.cost:6d}/{inst.B}, "
                  f"#A={len(s.selected):3d}, T={t1-t0:.4f}s")

        best_stoch = stoch_sols[stoch_benefits.index(max(stoch_benefits))]
        print(f"\n  Stats: Best={max(stoch_benefits)}, Worst={min(stoch_benefits)}, "
              f"Avg={statistics.mean(stoch_benefits):.1f}, Std={statistics.stdev(stoch_benefits):.1f}")

        # =====================================================================
        # 3. SIMULATED ANNEALING (10 runs desde cada punto de partida)
        # =====================================================================
        print(f"\n--- 3. Simulated Annealing ---")

        print(f"\n  3a. SA desde Greedy Determinista (init={det.benefit}):")
        sa_det_b = []
        for run in range(10):
            random.seed(run * 123 + 5)
            t0 = time.time()
            s = simulated_annealing(inst, det.selected, **sa_p)
            t1 = time.time()
            sa_det_b.append(s.benefit)
            print(f"    Run {run+1:2d}: B={s.benefit:6d}, C={s.cost:6d}/{inst.B}, "
                  f"#A={len(s.selected):3d}, T={t1-t0:.4f}s")
        print(f"    Stats: Best={max(sa_det_b)}, Worst={min(sa_det_b)}, "
              f"Avg={statistics.mean(sa_det_b):.1f}, Std={statistics.stdev(sa_det_b):.1f}")

        print(f"\n  3b. SA desde Greedy Estocástico (init={best_stoch.benefit}):")
        sa_st_b = []
        for run in range(10):
            random.seed(run * 456 + 13)
            t0 = time.time()
            s = simulated_annealing(inst, best_stoch.selected, **sa_p)
            t1 = time.time()
            sa_st_b.append(s.benefit)
            print(f"    Run {run+1:2d}: B={s.benefit:6d}, C={s.cost:6d}/{inst.B}, "
                  f"#A={len(s.selected):3d}, T={t1-t0:.4f}s")
        print(f"    Stats: Best={max(sa_st_b)}, Worst={min(sa_st_b)}, "
              f"Avg={statistics.mean(sa_st_b):.1f}, Std={statistics.stdev(sa_st_b):.1f}")

        # =====================================================================
        # 4. ALGORITMO GENÉTICO (10 runs)
        # =====================================================================
        print(f"\n--- 4. Algoritmo Genético ---")
        ga_b = []
        for run in range(10):
            random.seed(run * 789 + 21)
            t0 = time.time()
            s = genetic_algorithm(inst, **ga_p)
            t1 = time.time()
            ga_b.append(s.benefit)
            print(f"  Run {run+1:2d}: B={s.benefit:6d}, C={s.cost:6d}/{inst.B}, "
                  f"#A={len(s.selected):3d}, T={t1-t0:.4f}s")
        print(f"\n  Stats: Best={max(ga_b)}, Worst={min(ga_b)}, "
              f"Avg={statistics.mean(ga_b):.1f}, Std={statistics.stdev(ga_b):.1f}")

        # RESUMEN
        best_all = max([det.benefit] + stoch_benefits + sa_det_b + sa_st_b + ga_b)
        print(f"\n  *** MEJOR GLOBAL {fname}: {best_all} ***")

    print(f"\n{'='*80}\nEJECUCIÓN COMPLETADA\n{'='*80}")


if __name__ == '__main__':
    args = sys.argv[1:]

    if '--all' in args:
        run_all()
        from calibration import calibrate_sa, calibrate_ga
        for fname in ['easy.txt', 'medium1.txt']:
            inst = Instance(fname)
            det = greedy_deterministic(inst)
            calibrate_sa(inst, det.selected)
            calibrate_ga(inst)
        from graphs import generate_all_graphs
        generate_all_graphs()

    elif '--graphs' in args:
        from graphs import generate_all_graphs
        generate_all_graphs()

    elif '--calibrate' in args:
        from calibration import calibrate_sa, calibrate_ga
        for fname in ['easy.txt', 'medium1.txt']:
            inst = Instance(fname)
            det = greedy_deterministic(inst)
            calibrate_sa(inst, det.selected)
            calibrate_ga(inst)

    else:
        run_all()

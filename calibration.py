"""
Tarea 2 - CIT3352
Experimentos de calibración de parámetros para SA y Algoritmo Genético.
Genera tablas comparativas para justificar la elección de parámetros.
"""

import random
import time
import statistics
from instance import Instance
from greedy import greedy_deterministic
from simulated_annealing import simulated_annealing
from genetic import genetic_algorithm


def calibrate_sa(inst, initial_selected, n_runs=5):
    """
    Prueba distintas combinaciones de parámetros de SA y reporta resultados.
    """
    configs = [
        {"T_init": 100,  "T_min": 0.01, "cooling_rate": 0.99,  "max_iter_per_temp": 100},
        {"T_init": 500,  "T_min": 0.01, "cooling_rate": 0.99,  "max_iter_per_temp": 100},
        {"T_init": 1000, "T_min": 0.01, "cooling_rate": 0.99,  "max_iter_per_temp": 100},
        {"T_init": 1000, "T_min": 0.01, "cooling_rate": 0.995, "max_iter_per_temp": 100},
        {"T_init": 1000, "T_min": 0.01, "cooling_rate": 0.999, "max_iter_per_temp": 100},
        {"T_init": 1000, "T_min": 0.01, "cooling_rate": 0.995, "max_iter_per_temp": 50},
        {"T_init": 1000, "T_min": 0.01, "cooling_rate": 0.995, "max_iter_per_temp": 200},
        {"T_init": 2000, "T_min": 0.1,  "cooling_rate": 0.997, "max_iter_per_temp": 80},
    ]

    print(f"\n{'='*100}")
    print(f"CALIBRACION SA -- {inst.filepath} (m={inst.m}, n={inst.n})")
    print(f"{'='*100}")
    print(f"{'Config':<6} {'T_init':>6} {'T_min':>6} {'cool':>6} {'iter/T':>6} | "
          f"{'Best':>7} {'Avg':>8} {'Std':>7} {'T_avg(s)':>8}")
    print("-" * 100)

    results = []
    for idx, cfg in enumerate(configs):
        benefits = []
        times = []
        for run in range(n_runs):
            random.seed(run * 999 + idx * 7)
            t0 = time.time()
            sol = simulated_annealing(inst, initial_selected, **cfg)
            elapsed = time.time() - t0
            benefits.append(sol.benefit)
            times.append(elapsed)

        avg_b = statistics.mean(benefits)
        std_b = statistics.stdev(benefits) if len(benefits) > 1 else 0
        avg_t = statistics.mean(times)
        best_b = max(benefits)

        print(f"  {idx+1:<4} {cfg['T_init']:>6} {cfg['T_min']:>6} {cfg['cooling_rate']:>6} "
              f"{cfg['max_iter_per_temp']:>6} | {best_b:>7} {avg_b:>8.1f} {std_b:>7.1f} {avg_t:>8.3f}")

        results.append({"config": cfg, "best": best_b, "avg": avg_b, "std": std_b, "time": avg_t})

    best_config = max(results, key=lambda x: x["avg"])
    print(f"\n  >> Mejor configuracion (por promedio): T_init={best_config['config']['T_init']}, "
          f"cooling={best_config['config']['cooling_rate']}, iter/T={best_config['config']['max_iter_per_temp']}")

    return results


def calibrate_ga(inst, n_runs=5):
    """
    Prueba distintas combinaciones de parámetros del algoritmo genético.
    """
    configs = [
        {"pop_size": 30,  "generations": 100, "mutation_rate": 0.03, "tournament_size": 3},
        {"pop_size": 50,  "generations": 100, "mutation_rate": 0.05, "tournament_size": 3},
        {"pop_size": 50,  "generations": 200, "mutation_rate": 0.05, "tournament_size": 3},
        {"pop_size": 50,  "generations": 200, "mutation_rate": 0.05, "tournament_size": 5},
        {"pop_size": 50,  "generations": 200, "mutation_rate": 0.10, "tournament_size": 3},
        {"pop_size": 80,  "generations": 150, "mutation_rate": 0.05, "tournament_size": 3},
    ]

    print(f"\n{'='*100}")
    print(f"CALIBRACION GA -- {inst.filepath} (m={inst.m}, n={inst.n})")
    print(f"{'='*100}")
    print(f"{'Config':<6} {'pop':>5} {'gens':>5} {'mut':>5} {'tourn':>5} | "
          f"{'Best':>7} {'Avg':>8} {'Std':>7} {'T_avg(s)':>8}")
    print("-" * 100)

    results = []
    for idx, cfg in enumerate(configs):
        benefits = []
        times = []
        for run in range(n_runs):
            random.seed(run * 777 + idx * 13)
            t0 = time.time()
            sol = genetic_algorithm(inst, **cfg)
            elapsed = time.time() - t0
            benefits.append(sol.benefit)
            times.append(elapsed)

        avg_b = statistics.mean(benefits)
        std_b = statistics.stdev(benefits) if len(benefits) > 1 else 0
        avg_t = statistics.mean(times)
        best_b = max(benefits)

        print(f"  {idx+1:<4} {cfg['pop_size']:>5} {cfg['generations']:>5} {cfg['mutation_rate']:>5} "
              f"{cfg['tournament_size']:>5} | {best_b:>7} {avg_b:>8.1f} {std_b:>7.1f} {avg_t:>8.3f}")

        results.append({"config": cfg, "best": best_b, "avg": avg_b, "std": std_b, "time": avg_t})

    best_config = max(results, key=lambda x: x["avg"])
    print(f"\n  >> Mejor configuracion (por promedio): pop={best_config['config']['pop_size']}, "
          f"gens={best_config['config']['generations']}, mut={best_config['config']['mutation_rate']}")

    return results


if __name__ == '__main__':
    # Calibrar sobre instancia easy y medium1
    for fname in ['easy.txt', 'medium1.txt']:
        inst = Instance(fname)
        det = greedy_deterministic(inst)
        calibrate_sa(inst, det.selected)
        calibrate_ga(inst)

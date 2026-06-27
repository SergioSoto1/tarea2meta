import os
import random
import time
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from instance import Instance
from greedy import greedy_deterministic, greedy_stochastic
from simulated_annealing import simulated_annealing
from genetic import genetic_algorithm

OUTPUT_DIR = "graficos"


def ensure_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_and_collect(inst, sa_params, ga_params, n_runs=10):
    data = {}

    det = greedy_deterministic(inst)
    data['det_benefit'] = det.benefit
    data['det_sol'] = det

    stoch_benefits = []
    stoch_sols = []
    stoch_times = []
    for run in range(n_runs):
        random.seed(run * 42 + 7)
        t0 = time.time()
        s = greedy_stochastic(inst, alpha=0.3)
        stoch_times.append(time.time() - t0)
        stoch_benefits.append(s.benefit)
        stoch_sols.append(s)
    data['stoch_benefits'] = stoch_benefits
    data['stoch_times'] = stoch_times
    best_stoch = stoch_sols[stoch_benefits.index(max(stoch_benefits))]
    data['best_stoch'] = best_stoch

    sa_det_benefits = []
    sa_det_times = []
    sa_det_histories = []
    for run in range(n_runs):
        random.seed(run * 123 + 5)
        t0 = time.time()
        sol, hist = simulated_annealing(inst, det.selected, **sa_params, track_convergence=True)
        sa_det_times.append(time.time() - t0)
        sa_det_benefits.append(sol.benefit)
        sa_det_histories.append(hist)
    data['sa_det_benefits'] = sa_det_benefits
    data['sa_det_times'] = sa_det_times
    data['sa_det_histories'] = sa_det_histories

    sa_st_benefits = []
    sa_st_times = []
    sa_st_histories = []
    for run in range(n_runs):
        random.seed(run * 456 + 13)
        t0 = time.time()
        sol, hist = simulated_annealing(inst, best_stoch.selected, **sa_params, track_convergence=True)
        sa_st_times.append(time.time() - t0)
        sa_st_benefits.append(sol.benefit)
        sa_st_histories.append(hist)
    data['sa_st_benefits'] = sa_st_benefits
    data['sa_st_times'] = sa_st_times
    data['sa_st_histories'] = sa_st_histories

    ga_benefits = []
    ga_times = []
    ga_histories = []
    for run in range(n_runs):
        random.seed(run * 789 + 21)
        t0 = time.time()
        sol, hist = genetic_algorithm(inst, **ga_params, track_convergence=True)
        ga_times.append(time.time() - t0)
        ga_benefits.append(sol.benefit)
        ga_histories.append(hist)
    data['ga_benefits'] = ga_benefits
    data['ga_times'] = ga_times
    data['ga_histories'] = ga_histories

    return data


def plot_greedy_comparison(data, instance_name):
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(
        [data['stoch_benefits']],
        positions=[2], widths=0.6,
        patch_artist=True,
        boxprops=dict(facecolor='#5DADE2', alpha=0.7),
        medianprops=dict(color='black', linewidth=2)
    )
    ax.axhline(y=data['det_benefit'], color='#E74C3C', linewidth=2,
               linestyle='--', label=f"Greedy Det. = {data['det_benefit']}")
    ax.set_xticks([2])
    ax.set_xticklabels(['Greedy Estocástico\n(10 ejecuciones)'])
    ax.set_ylabel('Beneficio')
    ax.set_title(f'Greedy Determinista vs Estocástico — {instance_name}')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/greedy_comparison_{instance_name}.png", dpi=150)
    plt.close()


def plot_all_algorithms_boxplot(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))
    all_data = [
        data['stoch_benefits'],
        data['sa_det_benefits'],
        data['sa_st_benefits'],
        data['ga_benefits']
    ]
    labels = ['Greedy Est.', 'SA (det)', 'SA (est)', 'AG']
    colors = ['#5DADE2', '#F39C12', '#E67E22', '#2ECC71']

    bp = ax.boxplot(all_data, patch_artist=True, labels=labels,
                    medianprops=dict(color='black', linewidth=2))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.axhline(y=data['det_benefit'], color='#E74C3C', linewidth=2,
               linestyle='--', label=f"Greedy Det. = {data['det_benefit']}")
    ax.set_ylabel('Beneficio')
    ax.set_title(f'Comparación de Algoritmos — {instance_name}')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/all_comparison_{instance_name}.png", dpi=150)
    plt.close()


def plot_convergence_sa_iters(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    for histories, label, color in [
        (data['sa_det_histories'], 'SA (desde Greedy Det.)', '#F39C12'),
        (data['sa_st_histories'], 'SA (desde Greedy Est.)', '#E67E22'),
    ]:
        if not histories or not histories[0]:
            continue
        min_len = min(len(h) for h in histories)
        avg_curve = []
        iters = []
        for idx in range(min_len):
            iters.append(histories[0][idx][0])
            avg_curve.append(statistics.mean(h[idx][2] for h in histories))
        ax.plot(iters, avg_curve, label=label, color=color, linewidth=2)

    ax.set_xlabel('Iteración')
    ax.set_ylabel('Mejor Beneficio')
    ax.set_title(f'Convergencia Simulated Annealing (FO vs Iteraciones) — {instance_name}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/convergence_sa_iters_{instance_name}.png", dpi=150)
    plt.savefig(f"{OUTPUT_DIR}/convergence_sa_{instance_name}.png", dpi=150)
    plt.close()


def plot_convergence_sa_time(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    for histories, label, color in [
        (data['sa_det_histories'], 'SA (desde Greedy Det.)', '#F39C12'),
        (data['sa_st_histories'], 'SA (desde Greedy Est.)', '#E67E22'),
    ]:
        if not histories or not histories[0]:
            continue
        min_len = min(len(h) for h in histories)
        avg_curve = []
        times = []
        for idx in range(min_len):
            times.append(statistics.mean(h[idx][1] for h in histories))
            avg_curve.append(statistics.mean(h[idx][2] for h in histories))
        ax.plot(times, avg_curve, label=label, color=color, linewidth=2)

    ax.set_xlabel('Tiempo (segundos)')
    ax.set_ylabel('Mejor Beneficio')
    ax.set_title(f'Convergencia Simulated Annealing (FO vs Tiempo) — {instance_name}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/convergence_sa_time_{instance_name}.png", dpi=150)
    plt.close()


def plot_convergence_ga_iters(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    histories = data['ga_histories']
    if not histories or not histories[0]:
        plt.close()
        return
    min_len = min(len(h) for h in histories)
    gens = []
    best_curve = []
    avg_curve = []
    worst_curve = []
    for idx in range(min_len):
        gens.append(histories[0][idx][0])
        best_curve.append(statistics.mean(h[idx][2] for h in histories))
        avg_curve.append(statistics.mean(h[idx][3] for h in histories))
        worst_curve.append(statistics.mean(h[idx][4] for h in histories))

    ax.plot(gens, best_curve, color='#2ECC71', linewidth=2, label='Mejor (Fitness máx)')
    ax.plot(gens, avg_curve, color='#3498DB', linewidth=1.5, linestyle='--', label='Promedio población')
    ax.plot(gens, worst_curve, color='#E74C3C', linewidth=1.5, linestyle=':', label='Peor (Fitness mín)')

    ax.set_xlabel('Generación')
    ax.set_ylabel('Beneficio (Fitness)')
    ax.set_title(f'Convergencia Poblacional Algoritmo Genético — {instance_name}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/convergence_ga_iters_{instance_name}.png", dpi=150)
    plt.savefig(f"{OUTPUT_DIR}/convergence_ga_{instance_name}.png", dpi=150)
    plt.close()


def plot_convergence_ga_time(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    histories = data['ga_histories']
    if not histories or not histories[0]:
        plt.close()
        return
    min_len = min(len(h) for h in histories)
    times = []
    best_curve = []
    avg_curve = []
    worst_curve = []
    for idx in range(min_len):
        times.append(statistics.mean(h[idx][1] for h in histories))
        best_curve.append(statistics.mean(h[idx][2] for h in histories))
        avg_curve.append(statistics.mean(h[idx][3] for h in histories))
        worst_curve.append(statistics.mean(h[idx][4] for h in histories))

    ax.plot(times, best_curve, color='#2ECC71', linewidth=2, label='Mejor (Fitness máx)')
    ax.plot(times, avg_curve, color='#3498DB', linewidth=1.5, linestyle='--', label='Promedio población')
    ax.plot(times, worst_curve, color='#E74C3C', linewidth=1.5, linestyle=':', label='Peor (Fitness mín)')

    ax.set_xlabel('Tiempo (segundos)')
    ax.set_ylabel('Beneficio (Fitness)')
    ax.set_title(f'Convergencia Algoritmo Genético (FO vs Tiempo) — {instance_name}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/convergence_ga_time_{instance_name}.png", dpi=150)
    plt.close()


def plot_convergence_all_iters(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    for histories, label, color in [
        (data['sa_det_histories'], 'SA (desde Det.)', '#F39C12'),
        (data['sa_st_histories'], 'SA (desde Est.)', '#E67E22'),
        (data['ga_histories'], 'Alg. Genético', '#2ECC71'),
    ]:
        if not histories or not histories[0]:
            continue
        min_len = min(len(h) for h in histories)
        avg_curve = [statistics.mean(h[idx][2] for h in histories) for idx in range(min_len)]
        x = [i / (min_len - 1) * 100 if min_len > 1 else 0 for i in range(min_len)]
        ax.plot(x, avg_curve, label=label, color=color, linewidth=2)

    ax.axhline(y=data['det_benefit'], color='#E74C3C', linewidth=1.5,
               linestyle='--', label=f"Greedy Det.", alpha=0.7)
    ax.set_xlabel('Progreso (%)')
    ax.set_ylabel('Mejor Beneficio')
    ax.set_title(f'Convergencia Comparativa (Progreso %): SA vs AG — {instance_name}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/convergence_all_iters_{instance_name}.png", dpi=150)
    plt.savefig(f"{OUTPUT_DIR}/convergence_all_{instance_name}.png", dpi=150)
    plt.close()


def plot_convergence_all_time(data, instance_name):
    fig, ax = plt.subplots(figsize=(10, 6))

    for histories, label, color in [
        (data['sa_det_histories'], 'SA (desde Det.)', '#F39C12'),
        (data['sa_st_histories'], 'SA (desde Est.)', '#E67E22'),
        (data['ga_histories'], 'Alg. Genético', '#2ECC71'),
    ]:
        if not histories or not histories[0]:
            continue
        min_len = min(len(h) for h in histories)
        times = [statistics.mean(h[idx][1] for h in histories) for idx in range(min_len)]
        avg_curve = [statistics.mean(h[idx][2] for h in histories) for idx in range(min_len)]
        ax.plot(times, avg_curve, label=label, color=color, linewidth=2)

    ax.axhline(y=data['det_benefit'], color='#E74C3C', linewidth=1.5,
               linestyle='--', label=f"Greedy Det.", alpha=0.7)
    ax.set_xlabel('Tiempo (segundos)')
    ax.set_ylabel('Mejor Beneficio')
    ax.set_title(f'Convergencia Comparativa (Tiempo): SA vs AG — {instance_name}')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/convergence_all_time_{instance_name}.png", dpi=150)
    plt.close()


def print_summary_table(all_data):
    print(f"\n{'='*90}")
    print("TABLA RESUMEN FINAL")
    print(f"{'='*90}")
    print(f"{'Instancia':<12} {'G.Det':>7} {'G.Est(avg)':>10} {'SA.Det(avg)':>11} "
          f"{'SA.Est(avg)':>11} {'GA(avg)':>9} {'MEJOR':>7}")
    print("-" * 90)

    for name, data in all_data.items():
        sb = statistics.mean(data['stoch_benefits'])
        sad = statistics.mean(data['sa_det_benefits'])
        sas = statistics.mean(data['sa_st_benefits'])
        ga = statistics.mean(data['ga_benefits'])
        best = max([data['det_benefit']] + data['stoch_benefits'] +
                   data['sa_det_benefits'] + data['sa_st_benefits'] + data['ga_benefits'])
        print(f"{name:<12} {data['det_benefit']:>7} {sb:>10.1f} {sad:>11.1f} "
              f"{sas:>11.1f} {ga:>9.1f} {best:>7}")


def generate_all_graphs():
    ensure_dir()

    files = ['easy.txt', 'medium1.txt', 'medium2.txt', 'hard.txt']

    sa_configs = {
        'easy.txt':    dict(T_init=500,  T_min=0.01, cooling_rate=0.99,  max_iter_per_temp=200),
        'medium1.txt': dict(T_init=1000, T_min=0.01, cooling_rate=0.995, max_iter_per_temp=150),
        'medium2.txt': dict(T_init=1000, T_min=0.01, cooling_rate=0.995, max_iter_per_temp=150),
        'hard.txt':    dict(T_init=2000, T_min=0.1,  cooling_rate=0.997, max_iter_per_temp=80),
    }

    ga_configs = {
        'easy.txt':    dict(pop_size=50, generations=200, mutation_rate=0.05, tournament_size=3),
        'medium1.txt': dict(pop_size=50, generations=200, mutation_rate=0.05, tournament_size=3),
        'medium2.txt': dict(pop_size=50, generations=200, mutation_rate=0.05, tournament_size=3),
        'hard.txt':    dict(pop_size=50, generations=150, mutation_rate=0.05, tournament_size=3),
    }

    all_data = {}

    for fname in files:
        iname = fname.replace('.txt', '')
        print(f"\n>>> Procesando {fname}...")
        inst = Instance(fname)

        data = run_and_collect(inst, sa_configs[fname], ga_configs[fname])
        all_data[iname] = data

        plot_greedy_comparison(data, iname)
        plot_all_algorithms_boxplot(data, iname)
        plot_convergence_sa_iters(data, iname)
        plot_convergence_sa_time(data, iname)
        plot_convergence_ga_iters(data, iname)
        plot_convergence_ga_time(data, iname)
        plot_convergence_all_iters(data, iname)
        plot_convergence_all_time(data, iname)
        print(f"    [OK] Gráficos generados en {OUTPUT_DIR}/")

    print_summary_table(all_data)
    print(f"\n[OK] Todos los graficos guardados en '{OUTPUT_DIR}/'")


if __name__ == '__main__':
    generate_all_graphs()

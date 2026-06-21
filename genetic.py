"""
Tarea 2 - CIT3352
Algoritmo Genético para el problema de selección de proyectos.
Población inicial construida a partir de soluciones del greedy estocástico.
"""

import random
from solution import Solution
from greedy import greedy_stochastic


def _repair(inst, individual):
    """Repara un individuo infactible removiendo alternativas de menor ratio."""
    sol = Solution(inst, individual)
    while sol.cost > inst.B and sol.selected:
        # Remover la alternativa con peor ratio beneficio/costo_marginal
        worst = min(sol.selected, key=lambda i: inst.profits[i])
        sol.remove(worst)
    return sol


def _improve(inst, sol):
    """Intenta agregar alternativas factibles para mejorar la solución."""
    candidates = list(set(range(inst.m)) - sol.selected)
    random.shuffle(candidates)
    for i in candidates:
        if sol.can_add(i):
            sol.add(i)
    return sol


def crossover_uniform(parent1, parent2):
    """Crossover uniforme: cada gen se hereda de uno de los padres al azar."""
    child = set()
    all_alts = parent1 | parent2
    for i in all_alts:
        if i in parent1 and i in parent2:
            child.add(i)  # ambos lo tienen → siempre incluir
        elif random.random() < 0.5:
            child.add(i)
    return child


def mutate(individual, m, mutation_rate=0.05):
    """Mutación: flip aleatorio de cada alternativa con probabilidad mutation_rate."""
    result = set(individual)
    for i in range(m):
        if random.random() < mutation_rate:
            if i in result:
                result.remove(i)
            else:
                result.add(i)
    return result


def genetic_algorithm(inst, pop_size=50, generations=200, mutation_rate=0.05,
                      elite_ratio=0.1, tournament_size=3, alpha=0.3,
                      track_convergence=False):
    """
    Algoritmo Genético para selección de proyectos.

    - Población inicial: soluciones del greedy estocástico con distintos alpha
    - Selección: torneo
    - Crossover: uniforme
    - Mutación: bit-flip
    - Elitismo: se preservan los mejores individuos
    - Diversificación: inyección de nuevos individuos cuando la población estanca

    Args:
        inst: Instancia del problema
        pop_size: Tamaño de la población
        generations: Número de generaciones
        mutation_rate: Probabilidad de mutación por gen
        elite_ratio: Proporción de élite preservada
        tournament_size: Tamaño del torneo de selección
        alpha: Parámetro RCL base del greedy estocástico
        track_convergence: Si True, retorna historial de convergencia

    Returns:
        best: Mejor solución encontrada
        history: (solo si track_convergence) lista de (generación, mejor_beneficio)
    """
    # Generar población inicial diversa con distintos alpha
    population = []
    alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for i in range(pop_size):
        a = alphas[i % len(alphas)]
        sol = greedy_stochastic(inst, alpha=a)
        population.append(sol)

    best = max(population, key=lambda s: s.benefit).copy()
    elite_count = max(1, int(pop_size * elite_ratio))
    history = []
    stagnation_counter = 0
    prev_best = best.benefit

    for gen in range(generations):
        # Ordenar por beneficio (descendente)
        population.sort(key=lambda s: s.benefit, reverse=True)

        # Actualizar mejor global
        if population[0].benefit > best.benefit:
            best = population[0].copy()

        # Detectar estancamiento
        if best.benefit == prev_best:
            stagnation_counter += 1
        else:
            stagnation_counter = 0
            prev_best = best.benefit

        if track_convergence:
            history.append((gen, best.benefit))

        # Elitismo: preservar los mejores
        new_population = [p.copy() for p in population[:elite_count]]

        # Inyectar diversidad si hay estancamiento prolongado
        n_inject = 0
        if stagnation_counter > 15:
            n_inject = max(2, pop_size // 5)
            stagnation_counter = 0
            for _ in range(n_inject):
                a = random.choice([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
                new_sol = greedy_stochastic(inst, alpha=a)
                new_population.append(new_sol)

        # Generar resto de la población
        while len(new_population) < pop_size:
            # Selección por torneo
            parent1 = _tournament_select(population, tournament_size)
            parent2 = _tournament_select(population, tournament_size)

            # Crossover
            child_set = crossover_uniform(parent1.selected, parent2.selected)

            # Mutación (aumentar si hay estancamiento reciente)
            eff_rate = mutation_rate * (1.5 if stagnation_counter > 5 else 1.0)
            child_set = mutate(child_set, inst.m, eff_rate)

            # Reparar (hacer factible) y mejorar
            child = _repair(inst, child_set)
            child = _improve(inst, child)

            new_population.append(child)

        population = new_population

    # Evaluación final
    population.sort(key=lambda s: s.benefit, reverse=True)
    if population[0].benefit > best.benefit:
        best = population[0].copy()

    if track_convergence:
        history.append((generations, best.benefit))
        return best, history
    return best


def _tournament_select(population, k):
    """Selección por torneo: elige k individuos al azar, retorna el mejor."""
    contestants = random.sample(population, min(k, len(population)))
    return max(contestants, key=lambda s: s.benefit)

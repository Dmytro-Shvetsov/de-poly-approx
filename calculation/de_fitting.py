import sys
import numpy as np
import matplotlib.pyplot as plt

import utils


def obj_function(weights, x : np.ndarray):
    y = 0
    degree = len(weights)
    for i in range(degree):
        y += weights[i] * (x ** (degree - i - 1))
    return np.asarray(y) 


def error_function(weights, x, y_true):
    y_pred = obj_function(weights, x)
    error = np.sum(np.abs(y_true - y_pred) / len(y_true))
    return error


def population_solutions(population, x, y_true):
    solutions = []
    for agent in population:
        solution = error_function(agent, x, y_true)
        solutions.append(solution)
    return solutions


def pick_agents(population, ignore_idx):
    agent_idxs = np.random.choice([x for x in range(len(population)) if x != ignore_idx], 3, replace=False)
    return population[agent_idxs]


def mutation(target_vector, agent_a, agent_b, bounds, scale_factor):
    trial_vector = target_vector + scale_factor * (agent_a - agent_b)
    return trial_vector.clip(*bounds)
    for i in range(len(trial_vector)):
        if (trial_vector[i] < bounds[0]):
            trial_vector[i] = bounds[0] * np.random.uniform(0, 1)
        if (trial_vector[i] > bounds[1]):
            trial_vector[i] = bounds[1] * np.random.uniform(0, 1)
    return trial_vector


def crossover(trial_vector, parent_vector, crossover_probability, weights_size):
    dimensions = weights_size
    probability = np.random.rand(dimensions)
    offspring = list(range(weights_size))
    for i in range(dimensions):
        if probability[i] < crossover_probability:
            offspring[i] = trial_vector[i]
        if probability[i] > crossover_probability:
            offspring[i] = parent_vector[i]

    return np.asarray(offspring)

def selection(parent_vector, offspring, x, y_true):
    parent_solution = error_function(parent_vector, x, y_true)
    offspring_solution = error_function(offspring, x, y_true)

    if parent_solution < offspring_solution:
        return parent_vector, parent_solution
    else:
        return offspring, offspring_solution


def DE(population_size, crossover_probability, scale_factor, iterations, bounds, x, y_true, degree, verbose):
    # pop = population(population_size, bounds, degree)
    pop = bounds[0] + (np.random.rand(population_size, degree) * (bounds[1] - bounds[0]))
    pop_solutions = population_solutions(pop, x, y_true)
    best_candidate = pop[np.argmin(pop_solutions)]
    best_solution = min(pop_solutions)
    prev_solution = best_solution

    #number of generations
    for i in range(iterations):
        #generation
        for j in range(population_size):
            parent_vector = pop[j]
            #pick three agents that are != parent agent
            agents = pick_agents(pop, j)
            #performing mutation and returning back the trial vector
            trial_vector = mutation(agents[0], agents[1], agents[2], bounds, scale_factor)
            #performing crossover to get the offspring
            offspring = crossover(trial_vector, parent_vector, crossover_probability, degree)
            #selecting the best candidate using the greedy approach
            survived_candidate, candidate_solution = selection(parent_vector, offspring, x, y_true)
            pop[j] = survived_candidate
            pop_solutions[j] = candidate_solution

        best_solution = min(pop_solutions)
        if best_solution < prev_solution:
            best_candidate = pop[np.argmin(pop_solutions)]
            prev_solution = best_solution

        if ((i % 20 == 0) and (verbose == True)):
            print(f"Generation no.{i}. Best candidate is {best_candidate} with error of {best_solution}.")
            yield i, best_candidate, best_solution

    return i, best_candidate, best_solution


if __name__ == '__main__':
    NP = 100
    CP = 0.8
    F = 0.5
    I = 300

    bounds = [-50, 50]
    coeffs, poly = utils.poly_function_maker((5, -20, 5, 50, -20, -40))

    xs = np.linspace(-3, 3, 40)
    ys = poly(xs)
    degree = len(coeffs)

    for best_candidate, best_solution in DE(NP, CP, F, I, bounds, xs, ys, len(coeffs), verbose=True):
        pass

    print("DANO: ", coeffs)
    print("VIDANO: ", best_candidate)

    plt.plot(xs, ys, c='r', label= 'Original')

    ys_de = obj_function(best_candidate, xs)

    plt.plot(xs, ys_de, c='y', label= 'DE fitting')
    plt.scatter(xs, ys)
    plt.legend()
    plt.show()
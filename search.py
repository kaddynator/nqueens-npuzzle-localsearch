from random import choice, random
from math import exp
from heapq import heappop, heappush


def steepest_ascent_hill_climb(problem, allow_sideways=False, max_sideways=100):

    def get_best_child(node, problem):
        children = node.get_children()
        children_cost = [problem.cost_function(child) for child in children]
        min_cost = min(children_cost)
        # If best child is not chosen randomly from the set of children that have the lowest number of attacks,
        # then algorithm will get stuck flip-flopping between two non-random best children when sideways moves are
        # allowed
        best_child = choice([child for child_index, child in enumerate(children) if children_cost[
            child_index] == min_cost])
        return best_child

    node = problem.start_state
    node_cost = problem.cost_function(node)
    path = []
    sideways_moves = 0

    while True:
        path.append(node)
        best_child = get_best_child(node, problem)
        best_child_cost = problem.cost_function(best_child)

        if best_child_cost > node_cost:
            break
        elif best_child_cost == node_cost:
            if not allow_sideways or sideways_moves == max_sideways:
                break
            else:
                sideways_moves += 1
        else:
            sideways_moves = 0
        node = best_child
        node_cost = best_child_cost

    return {'outcome': 'success' if problem.goal_test(node) else 'failure',
            'solution': path,
            'problem': problem}


def astar(problem):

    path_costs = {problem.start_state: problem.start_state.path_cost}
    frontier = [problem.start_state]
    explored = set()
    result = None
    total_nodes = 1

    while not result:
        node = heappop(frontier)
        explored.add(node)

        if problem.goal_test(node):
            result = node
            break

        children = node.get_children()
        total_nodes += len(children)

        for child in children:

            child.parent = node
            child.path_cost = node.path_cost+1
            child.f_cost = child.path_cost + problem.cost_function(child)

            if child not in frontier:
                if child not in explored:
                    path_costs[child] = child.path_cost
                    heappush(frontier, child)
            elif child.path_cost < path_costs[child]:
                frontier.remove(child)
                heappush(frontier, child)
                path_costs[child] = child.path_cost

        if not frontier:
            return {'outcome': 'failed'}

    path = []
    while result:
        path.append(result)
        result = result.parent
    path.reverse()

    return {'outcome': 'success', 'solution': path, 'total_nodes': total_nodes, 'problem': problem}


def first_choice_hill_climb(problem, num_successors=100, allow_sideways=False):

    child = problem.start_state
    child_cost = problem.cost_function(child)
    path = []
    successor_found = True

    while successor_found:
        node = child
        node_cost = child_cost
        path.append(node)
        successor_found = False
        for _ in range(num_successors):

            child = node.random_child()
            child_cost = problem.cost_function(child)

            if (child_cost < node_cost) or (allow_sideways and child_cost == node_cost):
                successor_found = True
                break

    return {'outcome': 'success' if problem.goal_test(node) else 'failure',
            'solution': path,
            'problem': problem}


def random_restart_hill_climb(random_problem_generator, num_restarts=100, allow_sideways=False, max_sideways=100):

    path = []

    for _ in range(num_restarts):

        result = steepest_ascent_hill_climb(random_problem_generator(), allow_sideways=allow_sideways,
                                            max_sideways=max_sideways)
        path += result['solution']

        if result['outcome'] == 'success':
            break

    result['solution'] = path
    return result


def simulated_annealing(problem, temperature_schedule):
    node = problem.start_state
    node_cost = problem.cost_function(node)
    path = [node]

    for t in temperature_schedule:

        child = node.random_child()
        child_cost = problem.cost_function(child)
        cost_diff = node_cost - child_cost

        if (cost_diff > 0) or (random() < exp(cost_diff/t)):
            node = child
            node_cost = child_cost
            path.append(node)

    return {'outcome': 'success' if problem.goal_test(node) == 0 else 'failure',
            'solution': path,
            'problem': problem}
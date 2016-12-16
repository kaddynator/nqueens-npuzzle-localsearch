from random import choice


def steepest_ascent_hill_climb(start_state, goal_test, children_getter, cost_function, allow_sideways=False,
                                       max_sideways=100):
    node = start_state
    path = []
    sideways_moves = 0
    while True:
        path.append(node)
        children = children_getter(node)
        children_cost = [cost_function(child) for child in children]
        min_cost = min(children_cost)
        # If best child is not chosen randomly from the set of children that have the lowest number of attacks,
        # then algorithm will get stuck flip-flopping between two non-random best children when sideways moves are
        # allowed
        best_child = choice([child for child_index, child in enumerate(children) if children_cost[
            child_index] == min_cost])
        if (cost_function(best_child) > cost_function(node)):
            break
        elif cost_function(best_child) == cost_function(node):
            if not allow_sideways or sideways_moves == max_sideways:
                break
            else:
                sideways_moves += 1
        else:
            sideways_moves = 0
        node = best_child
    return {'outcome': 'success' if goal_test(node) else 'failure',
            'solution': path}
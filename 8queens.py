from random import randrange
from copy import deepcopy
from heapq import heappop, heappush
from timeit import default_timer as timer
from operator import itemgetter
from statistics import mean, stdev
from random import choice, shuffle, random
from math import exp
from search import steepest_ascent_hill_climb

class QueensState:

    instance_counter = 0

    def __init__(self, queen_positions=None, queen_num=8, parent=None, path_cost=0, f_cost=0, side_length=8):

        self.side_length = side_length

        if queen_positions == None:
            self.queen_num = queen_num
            self.queen_positions = frozenset(self.random_queen_position())
        else:
            self.queen_positions = frozenset(queen_positions)
            self.queen_num = len(self.queen_positions)

        self.path_cost = 0
        self.f_cost = f_cost
        self.parent = parent
        self.id = QueensState.instance_counter
        QueensState.instance_counter += 1

    def random_queen_position(self):
        ''' Each queen is placed in a random row in a separate column '''
        open_columns = list(range(self.side_length))
        queen_positions = [(open_columns.pop(randrange(len(open_columns))), randrange(self.side_length)) for _ in
                           range(self.queen_num)]
        return queen_positions

    def get_children(self):
        children = []
        parent_queen_positions = list(self.queen_positions)
        for queen_index, queen in enumerate(parent_queen_positions):
            new_positions = [(queen[0], row) for row in range(self.side_length) if row != queen[1]]
            for new_position in new_positions:
                queen_positions = deepcopy(parent_queen_positions)
                queen_positions[queen_index] = new_position
                children.append(QueensState(queen_positions))
        return children

    def random_child(self):
        queen_positions = list(self.queen_positions)
        random_queen_index = randrange(len(self.queen_positions))
        queen_positions[random_queen_index] = (queen_positions[random_queen_index][0],
            choice([row for row in range(self.side_length) if row != queen_positions[random_queen_index][1]]))
        return QueensState(queen_positions)

    def queen_attacks(self):

        def range_between(a, b):
            if a > b:
                return range(a-1, b, -1)
            elif a < b:
                return range(a+1, b)
            else:
                return [a]

        def zip_repeat(a, b):
            if len(a) == 1:
                a = a*len(b)
            elif len(b) == 1:
                b = b*len(a)
            return zip(a, b)

        def points_between(a, b):
            # print('Points between ' + str(a) + ' and ' + str(b) + ':')
            # print(list(zip_repeat(list(range_between(a[0], b[0])), list(range_between(a[1], b[1])))))
            # print('\n')
            return zip_repeat(list(range_between(a[0], b[0])), list(range_between(a[1], b[1])))

        def is_attacking(queens, a, b):
            if (a[0] == b[0]) or (a[1] == b[1]) or (abs(a[0]-b[0]) == abs(a[1] - b[1])):
                for between in points_between(a, b):
                    if between in queens:
                        return False
                return True
            else:
                return False

        attacking_pairs = []
        queen_positions = list(self.queen_positions)
        left_to_check = deepcopy(queen_positions)
        while left_to_check:
            a = left_to_check.pop()
            for b in left_to_check:
                if is_attacking(queen_positions, a, b):
                    attacking_pairs.append([a, b])

        return attacking_pairs

    def num_queen_attacks(self):
        return len(self.queen_attacks())

    def __str__(self):
        return '\n'.join([' '.join(['.' if (col, row) not in self.queen_positions else '*' for col in range(
            self.side_length)]) for row in range(self.side_length)])

    def __hash__(self):
        return hash(self.queen_positions)

    def __eq__(self, other):
        return self.queen_positions == other.queen_positions

    def __lt__(self, other):
        return self.f_cost < other.f_cost or (self.f_cost == other.f_cost and self.id > other.id)


def all_8queen_states():

    result_counter = 0

    def queen_dfs(queen_state=QueensState([])):
        next_queen_col = len(queen_state.queen_positions)
        if next_queen_col == 8:
            nonlocal result_counter
            result_counter += 1
            print('\rFound ' + str(result_counter) + ' results so far.', end='', flush=True)
            return [queen_state]

        result = []
        for row in range(8):
            next_queen_state = QueensState(set(queen_state.queen_positions) | {(next_queen_col,row)})
            if next_queen_state.num_queen_attacks() == 0:
                result += queen_dfs(next_queen_state)
        return result

    print('Finding all solutions to the 8-queens problem using recursive depth-first search.')
    start_time = timer()
    results = queen_dfs()
    print('\nSearch for all solutions completed in ' + str(int((timer()-start_time)*1000)) + ' ms\n')
    return results

def zero(*args):
    return 0

def h_num_queen_attacks(node):
    return node.num_queen_attacks()

def queens_astar(start, heuristic=zero):

    path_costs = {start: start.path_cost}
    frontier = [start]
    explored = set()
    result = None
    total_nodes = 1

    while not result:
        node = heappop(frontier)
        explored.add(node)

        if node.num_queen_attacks() == 0:
            result = node
            break

        children = node.get_children()
        total_nodes += len(children)

        for child in children:

            child.parent = node
            child.path_cost = node.path_cost+1
            child.f_cost = child.path_cost + heuristic(child)

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

    return {'outcome': 'success', 'solution': path, 'total_nodes': total_nodes}

# def steepest_ascent_hill_climb(queens_state, allow_sideways=False, max_sideways=100):
#     node = queens_state
#     path = []
#     sideways_moves = 0
#     while True:
#         path.append(node)
#         children = node.get_children()
#         children_num_queen_attacks = [child.num_queen_attacks() for child in children]
#         min_queen_attacks = min(children_num_queen_attacks)
#         # If best child is not chosen randomly from the set of children that have the lowest number of attacks,
#         # then algorithm will get stuck flip-flopping between two non-random best children when sideways moves are
#         # allowed
#         best_child = choice([child for child_index, child in enumerate(children) if children_num_queen_attacks[
#             child_index] == min_queen_attacks])
#         if (best_child.num_queen_attacks() > node.num_queen_attacks()):
#             break
#         elif best_child.num_queen_attacks() == node.num_queen_attacks():
#             if not allow_sideways or sideways_moves == max_sideways:
#                 break
#             else:
#                 sideways_moves += 1
#         else:
#             sideways_moves = 0
#         node = best_child
#     return {'outcome': 'success' if node.num_queen_attacks()==0 else 'failure',
#             'solution': path}

def queens_steepest_ascent_hill_climb(queens_state, allow_sideways=False, max_sideways=100):
    return steepest_ascent_hill_climb(queens_state,
                                              lambda x: x.num_queen_attacks()==0,
                                              lambda x: x.get_children(),
                                              lambda x: x.num_queen_attacks())

def first_choice_hill_climb(queens_state, num_successors=100, allow_sideways=False):
    child = queens_state
    path = []
    successor_found = True
    while successor_found:
        node = child
        path.append(node)
        successor_found = False
        for i in range(num_successors):
            child = node.random_child()
            if (child.num_queen_attacks() < node.num_queen_attacks()) or \
                (allow_sideways and child.num_queen_attacks() == node.num_queen_attacks()):
                successor_found = True
                break
    return {'outcome': 'success' if node.num_queen_attacks()==0 else 'failure',
            'solution': path}

def random_restart_hill_climb(random_state_generator, num_restarts=100, allow_sideways=False, max_sideways=100):
    path = []
    for _ in range(num_restarts):
        result = steepest_ascent_hill_climb(random_state_generator(), allow_sideways=allow_sideways,
                                        max_sideways=max_sideways)
        path += result['solution']
        if result['outcome'] == 'success':
            break
    result['solution'] = path
    return result

def simulated_annealing(queens_state, temperature_schedule):
    node = queens_state
    path = [node]
    for t in temperature_schedule:
        child = node.random_child()
        cost_diff = node.num_queen_attacks() - child.num_queen_attacks()
        #print(node.num_queen_attacks())
        # if cost_diff < 0:
        #     print(str(t) + ': ' + str(exp(-1/t)))
        if (cost_diff > 0) or (random() < exp(cost_diff/t)):
            node = child
            path.append(node)
    return {'outcome': 'success' if node.num_queen_attacks() == 0 else 'failure',
        'solution': path}

all_solutions = all_8queen_states()

def optimal_solution_cost(queens_state):
    ''' Returns smallest number of queens that need to be moved to get to an optimal solution from queens_state'''
    global all_solutions
    differences = [len(queens_state.queen_positions - optimal_state.queen_positions) for optimal_state in all_solutions]
    return min(differences)

class QueensProblem:

    def __init__(self, start_state=QueensState()):
        self.start_state = start_state


def analyze_performance(search_function, num_iterations=10):
    def results_mean_sd(result_list, key):
        results = [result[key] for result in result_list]
        if len(result_list) == 1:
            return {'mean': result_list[0][key], 'sd': 0}
        elif not result_list:
            return {'mean': 0, 'sd': 0}
        return {'mean': mean(results), 'sd': stdev(results)}

    results = []
    for iter_num in range(num_iterations):
        print('\rSolving problem ' + str(iter_num) + ' of ' + str(num_iterations),end='',flush=True)
        start_time = timer()
        result = search_function(QueensState())
        result['time'] = (timer()-start_time)*1000
        result['optimal_cost'] = optimal_solution_cost(result['solution'][0])
        result['path_length'] = len(result['solution'])-1
        results.append(result)
    print(' '*50 + '\r', end='', flush=True)

    results = [results,
               [result for result in results if result['outcome'] == 'success'],
               [result for result in results if result['outcome'] == 'failure']]

    title_col_width = 30
    data_col_width = 15

    def print_data_row(row_title, data_string, data_func, results):
        nonlocal title_col_width, data_col_width
        row = (row_title + '\t').rjust(title_col_width)
        for result_group in results:
            row += data_string.format(**data_func(result_group)).ljust(data_col_width)
        print(row)

    print('\t'.rjust(title_col_width) +
          'All Problems'.ljust(data_col_width) +
          'Successes'.ljust(data_col_width) +
          'Failures'.ljust(data_col_width))

    print_data_row('Number of Problems:',
                   '{count:.0f} ({percent:.1%})',
                   lambda x: {'count':len(x), 'percent': len(x)/num_iterations},
                   results)

    print_data_row('Mean time to completion:',
                   '{mean:.0f} ± {sd:.0f} ms',
                   lambda x: results_mean_sd(x,'time'),
                   results)

    print_data_row('Mean path length:',
                   '{mean:.0f} ± {sd:.0f}',
                   lambda x: results_mean_sd(x,'path_length'),
                   results)

    if 'total_nodes' in results[0][0].keys():
        print_data_row('Mean nodes generated:',
                       '{mean:.0f} ± {sd:.0f}',
                       lambda x: results_mean_sd(x, 'total_nodes'),
                       results)

    sorted_by_optimal_cost = [[] for _ in range(8)]
    for result in results[0]:
        sorted_by_optimal_cost[result['optimal_cost']-1].append(result)

    print('\n')
    print('Path length and success by optimal solution length')
    print('Optimal Cost'.rjust(15) + '    ' +
          'n'.ljust(6) +
          'Path Length'.ljust(15) +
          'Success'.ljust(10))

    for optimal_cost, group in enumerate(sorted_by_optimal_cost):
        if group:
            path_length_mean_sd = '{mean:.1f} ± {sd:.1f}'.format(**results_mean_sd(group, 'path_length'))
            percent_success = len([result for result in group if result['outcome'] == 'success'])/len(group)*100
            print('{optimal_cost:>15}    {count:<6}{path_length:<15}{success:<10.1f}'.format(optimal_cost=optimal_cost,
                                                                               path_length=path_length_mean_sd,
                                                                               success=percent_success, count=len(group)))

section_break = '\n' + '_'*100 + '\n'


analyze_performance(queens_steepest_ascent_hill_climb)

print(section_break)
print('Results from steepest ascent hill climb (no sideways moves allowed):\n')
analyze_performance(steepest_ascent_hill_climb)
print(section_break)



# print('Results from steepest ascent hill climb (up to 100 consecutive sideways moves allowed):\n')
# analyze_performance(lambda x: steepest_ascent_hill_climb(x, allow_sideways=True))
# print(section_break)
#
# print('Results from first choice hill climb (no sideways moves allowed):\n')
# analyze_performance(first_choice_hill_climb)
# print(section_break)
#
# print('Result from random restart hill climb:\n')
# analyze_performance(lambda x: random_restart_hill_climb(QueensState))
# print(section_break)
#
# print('Result from simulated annealing:\n')
# analyze_performance(lambda x: simulated_annealing(x, [0.9**(0.05*i-10) for i in range(1,2000)]))
# print(section_break)
#
# print('Results from A* with number of attacking queen pairs as heuristic:')
# analyze_performance(lambda x: queens_astar(x, heuristic=h_num_queen_attacks))
# print(section_break)
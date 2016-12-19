from random import randrange
from copy import deepcopy
from heapq import heappop, heappush
from timeit import default_timer as timer
from random import choice, shuffle, random
from math import exp
from search import steepest_ascent_hill_climb


class QueensState:

    instance_counter = 0

    def __init__(self, queen_positions=None, queen_num=8, parent=None, path_cost=0, f_cost=0, side_length=8):

        self.side_length = side_length

        if queen_positions is None:
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
        # Each queen is placed in a random row in a separate column
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
            next_queen_state = QueensState(set(queen_state.queen_positions) | {(next_queen_col, row)})
            if next_queen_state.num_queen_attacks() == 0:
                result += queen_dfs(next_queen_state)
        return result

    print('Finding all solutions to the 8-queens problem using recursive depth-first search.')
    start_time = timer()
    results = queen_dfs()
    print('\nSearch for all solutions completed in ' + str(int((timer()-start_time)*1000)) + ' ms\n')
    return results


all_solutions = all_8queen_states()


class QueensProblem:

    def __init__(self, start_state=None):
        if not start_state:
            start_state = QueensState()
        self.start_state = start_state

    def goal_test(self, state):
        return state.num_queen_attacks() == 0

    def cost_function(self, state):
        return state.num_queen_attacks()

    def optimal_solution_cost(self):
        ''' Returns smallest number of queens that need to be moved to get to an optimal solution from queens_state'''
        global all_solutions
        differences = [len(self.start_state.queen_positions - optimal_state.queen_positions) for optimal_state in
                       all_solutions]
        return min(differences)



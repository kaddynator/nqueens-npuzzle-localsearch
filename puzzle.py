from copy import copy
from random import choice, shuffle
from itertools import permutations, chain
import pickle
from math import floor


def swap(seq, index1, index2):
    retseq = copy(seq)
    retseq[index1] = seq[index2]
    retseq[index2] = seq[index1]
    return retseq


def import_pickled(filename):
    with open(filename, 'rb') as file:
        obj = pickle.load(file)
        return obj


def int_to_num_list(sequence):
    return [int(char) for char in str(sequence)]


def num_list_to_int(num_list):
    return int(''.join([str(num) for num in num_list]))


class PuzzleState:

    instance_counter = 0

    def __init__(self, sequence, parent=None, path_cost=0, f_cost=0):
        self.sequence = sequence
        self.hash = hash(int('0'.join([str(n) for n in self.sequence])))
        self.empty = len(sequence)
        self.side_length = int(self.empty**0.5)
        self.path_cost = path_cost
        self.f_cost = f_cost
        self.parent = parent
        PuzzleState.instance_counter += 1
        self.id = PuzzleState.instance_counter

    def get_children(self):

        empty = self.sequence.index(self.empty)
        children = []

        if (empty-self.side_length) >= 0:              # Move up
            children.append(swap(self.sequence, empty, empty - self.side_length))
        if (empty+self.side_length) < self.empty:      # Move down
            children.append(swap(self.sequence, empty, empty + self.side_length))
        if empty % self.side_length != 0:              # Move left
            children.append(swap(self.sequence, empty, empty - 1))
        if (empty + 1) % self.side_length != 0:        # Move right
            children.append(swap(self.sequence, empty, empty + 1))

        children = [PuzzleState(child) for child in children]

        return children

    def random_child(self):
        return choice(self.get_children())

    def get_non_empty_tiles(self):
        tiles = copy(self.sequence)
        tiles.remove(self.empty)
        return tiles

    def get_rows(self):
        return [self.sequence[(n * self.side_length):((n + 1) * self.side_length)] for n in range(0, self.side_length)]

    def get_cols(self):
        return [self.sequence[col_start::self.side_length] for col_start in range(0, self.side_length)]

    def __str__(self):
        max_tile_width = len(str(self.empty))
        tile_separator = '' if max_tile_width == 1 else ' '
        if max_tile_width > 1:
            max_tile_width += 2
        seqstr = self.get_rows()
        seqstr = [tile_separator.join([str(char if char != self.empty else ' ').center(max_tile_width)
                  for char in row]) for row in seqstr]
        return '\n'.join(seqstr)

    def __lt__(self, other):
        return (self.f_cost < other.f_cost) or (self.f_cost == other.f_cost and self.id > other.id)

    def __eq__(self, other):
        return self.sequence == other.sequence

    def __hash__(self):
        return self.hash


def get_random_depth_sample(n=8, depths=list(range(2, 26, 2)), num_samples=100):
    """ Returns num_samples random n-puzzle start and end states per solution depth in list depths"""

    def get_states(start):
        frontier = [start]
        frontier_set = {start}
        explored = set()

        states = [False for _ in range(len(depths))]
        while not all(states):
            node = frontier.pop(0)
            frontier_set.remove(node)
            explored.add(node)

            children = node.get_children()

            # It's necessary to shuffle children to get a truly random sample; otherwise, the first child (always
            # produced from the parent by the same action) produced at a certain depth will always be selected,
            # and children produced by other actions will never be selected
            shuffle(children)

            for child in children:
                if child not in frontier_set and child not in explored:
                    frontier_set.add(child)
                    frontier.append(child)
                    child.path_cost = node.path_cost+1
                    index = depths.index(child.path_cost) if child.path_cost in depths else None
                    if index is not None and not states[index]:
                        states[index] = {'start': start.sequence, 'end': child.sequence}

        return states

    depth_sample = [[] for depth in range(len(depths))]

    for _ in range(num_samples):
        start = list(range(1, n+2))
        shuffle(start)
        start = PuzzleState(start, path_cost=0)

        states = get_states(start)
        print('\rSet ' + str(_+1) + ' of ' + str(num_samples) + ' complete', end='', flush=True)
        list(map(list.append, depth_sample, states))

    return depth_sample


def export_random_depth_sample(filename, **kwargs):
    depth_sample = get_random_depth_sample(**kwargs)
    with open(filename, 'wb') as file:
        pickle.dump(depth_sample, file)


def load_depth_file(filename='sample_8puzzle_problems.pickle', **kwargs):
    depth_samples = None
    try:
        depth_samples = import_pickled(filename)
        print('Using samples from ' + filename + ' and ignoring sample parameters.')
    except FileNotFoundError:
        response = input('Unable to load puzzle sample problems from "' + filename + '". ' +
                         'Would you like to generate samples now and save them to this file? (y/n)')
        if response == 'y':
            export_random_depth_sample(filename, **kwargs)
            depth_samples = load_depth_file(filename)
    return depth_samples


def load_depth_samples(**kwargs):
    if 'n' not in kwargs.keys():
        kwargs['n'] = 8
    filename = 'sample_' + str(kwargs['n']) + 'puzzle_problems.pickle'
    return load_depth_file(filename, **kwargs)


def load_shuffled_depth_samples():
    depth_samples = load_depth_samples()
    for depth, depth_sample in enumerate(depth_samples):
        for sample in depth_sample:
            sample['depth'] = (depth + 1) * 2
    depth_samples = list(chain(*depth_samples))
    shuffle(depth_samples)
    return depth_samples


def h_manhattan(node, goal):

    def get_index(node, val):
        linear_index = node.sequence.index(val)
        return (linear_index % node.side_length, floor(linear_index/node.side_length))

    distance = 0
    for i in node.get_non_empty_tiles():
        node_xy = get_index(node, i)
        goal_xy = get_index(goal, i)
        distance += abs(node_xy[0]-goal_xy[0])+abs(node_xy[1]-goal_xy[1])

    return distance


class PuzzleProblem:

    depth_samples = load_shuffled_depth_samples()
    current_sample = 0

    def __init__(self, cost_function=h_manhattan, start_state=None, goal_state=None, solution_cost=None):

        if not start_state and not goal_state and not solution_cost:
            problem = self.next_problem()
            start_state = problem['start']
            goal_state = problem['end']
            solution_cost = problem['depth']

        self.start_state = PuzzleState(start_state)
        self.goal_state = PuzzleState(goal_state)
        self.solution_cost = solution_cost
        self.heuristic_function = cost_function

    def next_problem(self):

        if PuzzleProblem.current_sample == len(PuzzleProblem.depth_samples):
            print('\nExhausted puzzle samples. Restarting with sample 0.')
            PuzzleProblem.current_sample = 0

        problem = PuzzleProblem.depth_samples[PuzzleProblem.current_sample]
        PuzzleProblem.current_sample += 1

        return problem

    def goal_test(self, state):
        return state == self.goal_state

    def cost_function(self, state):
        return self.heuristic_function(state, self.goal_state)

    def optimal_solution_cost(self):
        ''' Returns smallest number of queens that need to be moved to get to an optimal solution from queens_state'''
        return self.solution_cost
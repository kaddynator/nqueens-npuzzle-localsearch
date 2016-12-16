from copy import copy
from random import choice, shuffle
from itertools import permutations
import pickle

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
        self.side_length = int(self.empty**(0.5))
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
        tile_separator = '' if max_tile_width==1 else ' '
        if max_tile_width > 1:
            max_tile_width += 2
        seqstr = self.get_rows()
        seqstr = [''.join([str(char if char != self.empty else ' ').center(max_tile_width)
                  for char in row]) for row in seqstr]
        return '\n'.join(seqstr)

    def __lt__(self, other):
        return (self.f_cost < other.f_cost) or (self.f_cost == other.f_cost and self.id > other.id)

    def __eq__(self, other):
        return self.sequence == other.sequence

    def __hash__(self):
        return self.hash


def get_random_depth_sample(n=8, depths=list(range(2,26,2)), num_samples=100):
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
        start = list(range(1,n+2))
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
            export_random_depth_sample(filename,**kwargs)
            depth_samples = load_depth_file(filename)
    return depth_samples

def load_depth_samples(**kwargs):
    if 'n' not in kwargs.keys():
        kwargs['n'] = 8
    filename = 'sample_' + str(kwargs['n']) + 'puzzle_problems.pickle'
    return load_depth_file(filename,**kwargs)

depth_samples = load_depth_samples()
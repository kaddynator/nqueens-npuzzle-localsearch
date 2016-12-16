def h_distinct_attacks(queen_state):
    '''Groups attack pairs together if they share a common queen and returns the number of groups'''

    def have_queen_in_common(queen_list_a, queen_list_b):
        return len(set(queen_list_a + queen_list_b)) < len(queen_list_a) + len(queen_list_b)

    attacking_pairs = queen_attacks(queen_state)
    print(attacking_pairs)
    explored = []
    score = 0
    while attacking_pairs:
        current_pair = attacking_pairs.pop()
        if not have_queen_in_common(current_pair, explored):
            score += 1
        explored += current_pair

    print(score)
    return score


def h(queen_state):
    return num_queen_attacks(queen_state) / 6
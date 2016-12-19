from statistics import mean, stdev
from timeit import default_timer as timer
from search import steepest_ascent_hill_climb, first_choice_hill_climb, random_restart_hill_climb, \
    simulated_annealing, astar


def mean_sd_for_dict_key(result_list, key):
    results = [result[key] for result in result_list]

    if len(result_list) == 1:
        return {'mean': result_list[0][key], 'sd': 0}
    elif not result_list:
        return {'mean': 0, 'sd': 0}

    return {'mean': mean(results), 'sd': stdev(results)}


def print_summary_table(results):

    title_col_width = 30
    data_col_width = 15

    def print_data_row(row_title, data_string, data_func, results):
        nonlocal title_col_width, data_col_width
        row = (row_title + '\t').rjust(title_col_width)
        for result_group in results:
            row += data_string.format(**data_func(result_group)).ljust(data_col_width)
        print(row)

    num_iterations = len(results[0])

    print('\t'.rjust(title_col_width) +
          'All Problems'.ljust(data_col_width) +
          'Successes'.ljust(data_col_width) +
          'Failures'.ljust(data_col_width))

    print_data_row('Number of Problems:',
                   '{count:.0f} ({percent:.1%})',
                   lambda x: {'count': len(x), 'percent': len(x) / num_iterations},
                   results)

    print_data_row('Mean time to completion:',
                   '{mean:.0f} ± {sd:.0f} ms',
                   lambda x: mean_sd_for_dict_key(x, 'time'),
                   results)

    print_data_row('Mean path length:',
                   '{mean:.0f} ± {sd:.0f}',
                   lambda x: mean_sd_for_dict_key(x, 'path_length'),
                   results)

    if 'total_nodes' in results[0][0].keys():
        print_data_row('Mean nodes generated:',
                       '{mean:.0f} ± {sd:.0f}',
                       lambda x: mean_sd_for_dict_key(x, 'total_nodes'),
                       results)


def print_optimal_cost_table(results):

    sorted_by_optimal_cost = {}
    for result in results[0]:
        if result['optimal_cost'] not in sorted_by_optimal_cost.keys():
            sorted_by_optimal_cost[result['optimal_cost']] = []
        sorted_by_optimal_cost[result['optimal_cost']].append(result)

    print('\n')
    print('Path length and success by optimal solution length')
    print('Optimal Cost'.rjust(15) + '    ' +
          'n'.ljust(6) +
          'Path Length'.ljust(15) +
          'Success'.ljust(10))

    optimal_costs = sorted(sorted_by_optimal_cost.keys())
    for optimal_cost in optimal_costs:
        group = sorted_by_optimal_cost[optimal_cost]
        if group:
            path_length_mean_sd = '{mean:.1f} ± {sd:.1f}'.format(**mean_sd_for_dict_key(group, 'path_length'))
            percent_success = len([result for result in group if result['outcome'] == 'success']) / len(group) * 100
            print('{optimal_cost:>15}    {count:<6}{path_length:<15}{success:<10.1f}'.
                  format(optimal_cost=optimal_cost, path_length=path_length_mean_sd, success=percent_success,
                         count=len(group)))


def print_results(results):
    print_summary_table(results)
    print_optimal_cost_table(results)


def analyze_performance(problem_set, search_function):

    num_iterations = len(problem_set)

    results = []
    for problem_num, problem in enumerate(problem_set):
        print('\rSolving problem ' + str(problem_num+1) + ' of ' + str(num_iterations), end='', flush=True)
        start_time = timer()
        result = search_function(problem)
        result['time'] = (timer()-start_time)*1000
        result['optimal_cost'] = problem.optimal_solution_cost()
        result['path_length'] = len(result['solution'])-1
        results.append(result)

    print(' '*50 + '\r', end='', flush=True)

    results = [results,
               [result for result in results if result['outcome'] == 'success'],
               [result for result in results if result['outcome'] == 'failure']]

    print_results(results)


def analyze_all_algorithms(problem_set):

    section_break = '\n' + '_'*100 + '\n'

    print(section_break)
    print('Results from steepest ascent hill climb (no sideways moves allowed):\n')
    analyze_performance(problem_set, steepest_ascent_hill_climb)
    print(section_break)

    print('Results from steepest ascent hill climb (up to 100 consecutive sideways moves allowed):\n')
    analyze_performance(problem_set, lambda x: steepest_ascent_hill_climb(x, allow_sideways=True))
    print(section_break)

    print('Results from first choice hill climb (no sideways moves allowed):\n')
    analyze_performance(problem_set, first_choice_hill_climb)
    print(section_break)

    print('Result from random restart hill climb:\n')
    analyze_performance(problem_set, lambda x: random_restart_hill_climb(problem_set[0].__class__))
    print(section_break)

    print('Result from simulated annealing:\n')
    analyze_performance(problem_set, lambda x: simulated_annealing(x, [0.9**(0.05*i-10) for i in range(1, 2000)]))
    print(section_break)

    print('Results from A*:')
    analyze_performance(problem_set, astar)
    print(section_break)


print('ANALYZING ALGORITHM PERFORMANCE FOR 8-QUEENS PROBLEMS:')
from queens import QueensProblem
queens_problem_set = [QueensProblem() for _ in range(1000)]
analyze_all_algorithms(queens_problem_set)

print('\n\nANALYZING ALGORITHM PERFORMANCE FOR 8-PUZZLE PROBLEMS:')
from puzzle import PuzzleProblem
puzzle_problem_set = [PuzzleProblem() for _ in range(2400)]
analyze_all_algorithms(puzzle_problem_set)
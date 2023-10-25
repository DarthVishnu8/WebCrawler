import os
import sys
import time

id = sys.argv[1]
# outfile = sys.argv[2] if len(sys.argv) > 2 else 'scores.csv'
outfile = 'score.csv'

infile_prefix = "testbench/in"
outfile_prefix = "testbench/out"
max_time = 2 # time limit for each testcase in seconds

def compile():
    if os.system('g++ -std=c++20 main.cpp -o main') != 0:
        with open(outfile, 'a') as f:
            f.write(id + ',' + f'{0.00:.2f}' + ',' + 'Compilation Error\n')
        exit(0)

def get_dir(suffix):
    inf2, outf2 = infile_prefix + '_' + suffix + '/', outfile_prefix + '_' + suffix + '/'
    return inf2, outf2

def test(inf, outf):
    with open(inf, 'r') as f:
        tc = map(int, f.readlines())

    st = time.time()
    os.system(f'timeout {2*max_time} ./main {inf} {outf}')
    en = time.time()
    print("Time taken: " + str(en - st) + " seconds")

    if en - st > max_time:
        print("Testcase " + inf + " timed out.")
        return 0
    
    with open(outf, 'r') as f:
        out = list(map(int, f.readlines()))

    if out != sorted(tc):
        print("Testcase " + inf + " failed.")
        return 0
    return 1

def test_random(testcases):
    inf, outf = get_dir('random')
    score = 0

    for i in (range(testcases)):
        score += test(inf + str(i), outf + str(i))

    print("score (random): " + str(score) + "/" + str(testcases))
    return score

def test_sorted(testcases):
    inf, outf = get_dir('sorted')
    score = 0
    for i in (range(testcases)):
        score += test(inf + str(i), outf + str(i))

    print("score (sorted): " + str(score) + "/" + str(testcases))
    return score

def test_reverse(testcases):
    inf, outf = get_dir('reverse')
    score = 0
    for i in (range(testcases)):
        score += test(inf + str(i), outf + str(i))
    
    print("score (reverse): " + str(score) + "/" + str(testcases))
    return score

def test_equal(testcases):
    inf, outf = get_dir('equal')
    score = 0
    for i in (range(testcases)):
        score += test(inf + str(i), outf + str(i))

    print("score (equal): " + str(score) + "/" + str(testcases))
    return score

def test_empty():
    inf, outf = get_dir('empty')
    score = test(inf + str(0), outf + str(0))

    print("score (empty): " + str(score) + "/1")
    return score

def test_single():
    inf, outf = get_dir('single')
    score = test(inf + str(0), outf + str(0))

    print("score (singleton): " + str(score) + "/1")
    return score

def process(file, hdrs):
    used_partition = lambda x: ':partition' in x
    used_sort = lambda x: any(f'{c}sort(' in x for c in [':', ' ', '\t', '\n', '\f', '\v', '\r']) or x.startswith('sort(') or any(f'{c}sort_' in x for c in [':', ' ', '\t', '\n', '\f', '\v', '\r']) or x.startswith('sort_')

    with open(file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if line.startswith('//'):
            continue
        if line.startswith('#include') or line.startswith('using'):
            continue
        if used_partition(line) or used_sort(line):
            return 'invalid'
        hdrs.append(line)

    with open(file, 'w') as f:
        f.write('\n'.join(hdrs))

def ensure_introsort():
    with open('introsort.cpp', 'r') as f:
        # look for partition, hsort, isort
        ok1, ok2, ok3 = False, False, False
        for line in f:
            if line.startswith('//') or line.startswith('#include') or line.startswith('using'):
                continue
            if 'partition' in line:
                ok1 = True
            if 'hsort' in line:
                ok2 = True
            if 'isort' in line:
                ok3 = True
    if not ok1: return 4
    if not ok2: return 3
    if not ok3: return 2
    return 0

def check_integrity():
    hdrs = ['#include <vector>', 'using namespace std;']
    if process('partition.cpp', hdrs) == 'invalid': return 'invalid'

    hdrs = ['#include <vector>', 'using namespace std;']
    if process('hsort.cpp', hdrs) == 'invalid': return 'invalid'
    
    hdrs = ['#include <cmath>', '#include "partition.cpp"', '#include "hsort.cpp"', '#include "isort.cpp"', '#include <vector>', 'using namespace std;']
    if process('introsort.cpp', hdrs) == 'invalid': return 'invalid'

def check_spurious(scores):
    # empty files are passing testcases
    if (scores[1] > 0 or scores[2] > 0 or scores[3] > 0) and scores[0] == 0:
        return 'flag1'
    if (scores[4] > 0 or scores[5] > 0) and scores[0] == 0:
        return 'flag2'
    return 'ok'

def confirm_empty(func):
    with open(f'{func}.cpp', 'r') as f:
        for line in f:
            if func not in line: continue
            # func is on this line. break and read the rest of the file
            break
        line = line[line.find('{')+1:] + f.read()
        line = line.strip()
    if line[0] == '}':
        return True
    elif line.startswith('return'):
        return True
    return False

# ensure current working directory contains all files and the testbench folder (copy your submitted files to folder containing this script)
if __name__ == '__main__':
    print('\033[91m' + id + '\033[0m')

    if check_integrity() == 'invalid':
        with open(outfile, 'a') as f:
            f.write(id + ',' + f'{0.00:.2f}' + ',' + 'used disallowed function\n')
        exit(0)
    if confirm_empty('partition') or confirm_empty('hsort') or confirm_empty('introsort'):
        with open(outfile, 'a') as f:
            f.write(id + ',' + f'{0.00:.2f}' + ',' + 'empty\n')
        exit(0)

    penalty = ensure_introsort()

    compile()
    # assert that main exists
    assert os.path.exists('main')

    testcases = [3, 2, 2, 1]
    scores = [0]*6
    scores[0] = test_random(testcases[0])
    scores[1] = test_sorted(testcases[1])
    scores[2] = test_reverse(testcases[2])
    scores[3] = test_equal(testcases[3])
    scores[4] = test_empty()
    scores[5] = test_single()

    # for checks
    print("Total Score: " + str(sum(scores)) + f'/{sum(testcases)+2}, penalty: {penalty}')

    # write to scores.csv as name,score,comment
    flag = check_spurious(scores)
    score = sum(scores)/3
    with open(outfile, 'a') as f:
        if penalty > 0:
            if float(score) < 1e-7:
                f.write(id + ',' + f'{0.00:.2f}' + f',{flag}\n')
            else:
                new_score = float(score) - penalty
                f.write(id + ',' + f'{max(0.00, new_score):.2f}' + f',{flag}-penalty{penalty}\n')
        else:
            f.write(id + ',' + f'{sum(scores)/(sum(testcases)+2)*8:.2f}' + f',{flag}\n')
# pick up scores from scores_local and scores_gitlab.csv to create scores.csv

res1 = {}
res2 = {}
with open('scores-local.csv') as f:
    f.readline()
    for line in f:
        name, score, err = line.strip().split(',')
        res1[name] = (score, err)
with open('scores-gitlab.csv') as f:
    f.readline()
    for line in f:
        name, score, err = line.strip().split(',')
        res2[name] = (score, err)
# res = ['name', 'score', 'err(local|gitlab)']
res = {}
for name, (score, err) in res2.items():
    res[name] = (score, err)
    if name in res1:
        res[name] = (max(float(score), float(res1[name][0])), err+'|'+res1[name][1])
    else:
        res[name] = (score, err+'|not found')

with open('scores.csv', 'w') as f:
    f.write('name,score,err\n')
    for name, (score, err) in res.items():
        f.write(f'{name},{score},{err}\n')
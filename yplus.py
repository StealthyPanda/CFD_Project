import subprocess, os

def parse_params(case):
    yplusres = subprocess.run(
        [f"./{case}/GetParams"],
        capture_output=True, text=True
    ).stdout
    yplusres = list(filter(lambda x: 'patch model y+' in x, yplusres.splitlines()))[-1]
    yplusres = (yplusres.split(':')[-1]).strip()
    yplusres = list(map(lambda x: (x.split('=')[-1]).strip(), yplusres.split(',')))
    
    
    return {
        'min' : float(yplusres[0]),
        'max' : float(yplusres[1]),
        'avg' : float(yplusres[2]),
    }


cases = list(filter(os.path.isdir, os.listdir()))
cases = list(filter(lambda x: '_template' in x, cases))

names = []
ys = []
for i, each in enumerate(cases):
    name = '_'.join(each.split('_')[2:-4])
    print(i)
    try:
        ys.append(parse_params(each)['min'])
        names.append(name)
    except:pass

import matplotlib.pyplot as plt
# plt.figure(figsize=(15, 7))
plt.bar(names, ys)
plt.xticks(rotation=70)
plt.grid()
plt.show()
    
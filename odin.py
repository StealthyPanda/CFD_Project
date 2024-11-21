import subprocess
import os, sys, shutil, time, json, datetime
from codex import warning, ok, error
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

script_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open('odinconfig.json', 'r') as file:
    config = json.load(file)

base_case = config['base']
dirname = os.path.dirname(base_case)
base_case = os.path.basename(base_case)

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




block_reses = config['blocks']
geometries = config['geometries']


cases = []
for i, each in enumerate(block_reses):
    size = 1
    for x in each: size *= x
    
    for j, shape in enumerate(geometries):
        case = f'{base_case}_{shape}_{"_".join(map(str, each))}_{size}'
        warning(f'Creating {case}...')
        shutil.copytree(
            os.path.join(dirname, base_case), 
            os.path.join(dirname, case), 
            dirs_exist_ok=True
        )
        
        bmdfile = ParsedParameterFile(os.path.join(dirname, case, 'system', 'blockMeshDict'))
        bmdfile['blocks'][2] = f'({" ".join(map(str, each))})'
        bmdfile.writeFile()
        
        ok(f'Created {case}!')
        cases.append((case, shape, size))


print()
warning('Target cases are:')
for each, _, _ in cases:
    print(each)
print()

runtime = dict()
params = dict()


    

for i, each in enumerate(cases):
    case, shape, size = each
    start = time.time()
    
    print()
    warning(f'Running [{i+1}/{len(cases)}]{case}...')
    code = os.system(f'./{os.path.join(dirname, case)}/Allclean')
    if code:
        error(f'Failed while cleaning up [{i+1}/{len(cases)}]{case}!')
        break
    
    code = os.system(
        f'./{os.path.join(dirname, case)}/Allrun {shape}'
    )
    if code:
        error(f'Failed while running [{i+1}/{len(cases)}]{case}!')
        break
    
    end = time.time()
    runtime[case] = end - start
    
    ok(f'Ran [{i+1}/{len(cases)}]{case} successfully in {end-start}s!')
    
    params[case] = parse_params(case)
    

name = 'last_successful_run'
i = ''
while os.path.exists(f'{name}{i}.json'):
    if i == '': i = 1
    else: i += 1
    
with open(f'{name}{i}.json', 'w') as file:
    json.dump({
        'script_start_time' : script_start,
        'target_cases' : cases,
        'runtimes' : runtime,
        'params' : params
    }, file, indent='\t')



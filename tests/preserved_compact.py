"""Opt-in tests for the archived compact-city map, not the active Map 10 candidate."""
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
# The remote development commit and reviewed local evidence commit have the same tree.
TREE = '709f584e07f8c1385b60fcb60737949b0c0d1fc2'
COMMIT_IDS = ('0b530f90202e284b7e7982ef7f69e44828c38c5e',
              '32ded830636ec1346532fcc12e990122228091ac')
SUITES = ('academy_landmark.py', 'coastal_art.py', 'compact_ambience.py', 'compact_city_map.py',
          'compact_guidance.py', 'compact_integration.py', 'compact_review_fixture.py', 'compact_world.py',
          'minimap_visuals.py', 'training_map.py', 'boss_spatial.py')
ARCHIVED = {'CompactCity.luau': 'src/ServerScriptService/CompactCity.luau',
            'CompactLayout.luau': 'src/ReplicatedStorage/Shared/CompactLayout.luau'}

def main():
    for commit in COMMIT_IDS:
        p = subprocess.run(['git','rev-parse','--verify',commit+'^{tree}'], cwd=ROOT, text=True, capture_output=True)
        if p.returncode == 0 and p.stdout.strip() == TREE:
            break
    else:
        raise SystemExit('Preserved compact verification needs local history for 0b530f9. No network fetch attempted.')
    archive = ROOT / 'prototypes/preserved-compact-city'
    for filename, old_path in ARCHIVED.items():
        expected = subprocess.check_output(['git','show',f'{commit}:{old_path}'],cwd=ROOT)
        assert (archive/filename).read_bytes().replace(b'\r\n',b'\n') == expected, 'Preserved compact source differs: '+filename
    with tempfile.TemporaryDirectory(prefix='scream-preserved-compact-') as directory:
        dest = Path(directory)/'historical'
        subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(ROOT),str(dest)],check=True)
        subprocess.run(['git','-C',str(dest),'-c','core.autocrlf=false','checkout','--quiet','--detach',commit],check=True)
        for name in SUITES:
            print('Checking preserved compact-city '+name,flush=True)
            command = [sys.executable, str(dest/'tests'/name)]
            if name == 'coastal_art.py':
                command.extend(('--baseline', '--negative-controls'))
            subprocess.run(command, cwd=dest, check=True)
    print(f'PASS: {len(SUITES)} archived compact-city suites and two exact archived source files; not Map 10 coverage.')

if __name__ == '__main__':
    main()

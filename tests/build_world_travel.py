"""Build Studio-only City/Hall travel rehearsals or a pair for explicitly approved test IDs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HALL = ROOT / 'prototypes/resonance-arena'
TRAVEL = HALL / 'travel'


def place(role, universe, source, destination, temporary, out):
    rehearsal = universe == 0
    settings = temporary / f'{role}Settings.luau'
    settings.write_text(f'return {{rehearsal={str(rehearsal).lower()},universe={universe},source={source},destination={destination}}}\n')
    hall = role == 'Hall'
    entry = HALL / 'Arena.server.luau' if hall else TRAVEL / 'City.server.luau'
    layout = HALL / 'Layout.luau' if hall else ROOT / 'src/ReplicatedStorage/Shared/CompactLayout.luau'
    server = {'Entry': {'$path': str(entry)}, 'TravelGate': {'$path': str(TRAVEL / 'TravelGate.luau')},
              'TravelSettings': {'$path': str(settings)}}
    if not hall:
        server['CompactCity'] = {'$path': str(ROOT / 'src/ServerScriptService/CompactCity.luau')}
    tree = {'$className': 'DataModel',
            'ReplicatedStorage': {'$className': 'ReplicatedStorage', 'Shared': {
                '$className': 'Folder', 'ResonanceLayout' if hall else 'CompactLayout': {'$path': str(layout)}}},
            'ServerScriptService': {'$className': 'ServerScriptService', **server},
            'StarterPlayer': {'$className': 'StarterPlayer', '$properties': {'CameraMinZoomDistance': 6},
                              'StarterPlayerScripts': {'$className': 'StarterPlayerScripts',
                                                       'Status': {'$path': str(TRAVEL / 'Status.client.luau')}}}}
    project = temporary / f'{role}.project.json'
    name = f'{role}Travel' + ('Rehearsal' if rehearsal else 'StudioTest')
    project.write_text(json.dumps({'name': name + '_DO_NOT_PUBLISH', 'tree': tree}))
    artifact = out / f'{name}.rbxl'
    subprocess.run(['rojo', 'build', str(project), '-o', str(artifact)], cwd=ROOT, check=True)
    return {'file': artifact.name, 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
            'sourcePlaceId': source, 'destinationPlaceId': destination}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--test-ids', type=int, nargs=3, metavar=('UNIVERSE', 'CITY', 'HALL'))
    args = parser.parse_args()
    universe, city, hall = args.test_ids or (0, 0, 0)
    if args.test_ids and (not all(0 < n < 2**53 for n in (universe, city, hall)) or city == hall):
        parser.error('Use a positive approved test universe ID and distinct positive test place IDs.')
    out = ROOT / 'build' / 'world-travel'
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='world-travel-') as directory:
        temporary = Path(directory)
        artifacts = [place('City', universe, city, hall, temporary, out), place('Hall', universe, hall, city, temporary, out)]
    manifest = {'mode': 'studio-test' if args.test_ids else 'zero-id-rehearsal', 'universeId': universe,
                'artifacts': artifacts, 'scope': 'Map geometry and travel only. No gameplay profiles or commerce.'}
    suffix = 'studio-test' if args.test_ids else 'rehearsal'
    (out / f'{suffix}.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()

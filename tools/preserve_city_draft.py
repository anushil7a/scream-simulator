"""Preserve a reviewed Git city source commit; build only an unpublished guarded draft.
No network, Studio, publication, tags, credentials, untracked files or live saves.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets/drafts/original-city-2026-11-11'
EXACT = {'default.project.json', 'assets/review/MosaicFountain.rbxmx'}
GUARD = '''-- PRESERVED ORIGINAL CITY: DISPOSABLE LOCAL DRAFT, NEVER PUBLISH.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId == 0,
 "This preserved draft runs only as an unpublished local Studio file")
workspace:SetAttribute("LocalSustainedPrototype", true)
-- Fail closed even if an original caller unexpectedly bypasses its fixture branch.
local preservedProfiles = require(script.Parent.Profiles)
preservedProfiles.Load = function() error("Preserved draft: profile reads disabled") end
preservedProfiles.Save = function() error("Preserved draft: profile writes disabled") end
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Unsafe archive/source path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise ValueError('Unsafe archive/source path')
    for part in path.parts:
        if part.endswith((' ', '.')) or any(ord(c) < 32 for c in part) or re.search(r'[<>"|?*]', part):
            raise ValueError('Unsafe Windows path')
        if part.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
            raise ValueError('Reserved Windows path')
    return path


def inside(root, relative):
    relative = safe_relative(relative)
    target = root.joinpath(*relative.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path escaped designated workspace')
    for parent in [target, *target.parents]:
        if parent == root.parent:
            break
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise ValueError('Refusing link/reparse-point path')
    return target


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def collect(commit):
    entries = {}
    for record in git('ls-tree', '-r', '-z', commit).split(b'\0'):
        if not record:
            continue
        header, raw_path = record.split(b'\t', 1)
        name = raw_path.decode('utf-8', errors='strict')
        selected = name in EXACT or name.startswith('src/')
        if not selected:
            continue
        safe_relative(name)
        mode, kind, oid = header.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755'):
            raise ValueError('Source links/submodules are not accepted: ' + name)
        if name.startswith('src/') and not name.endswith('.luau'):
            raise ValueError('Review new source file type before preserving: ' + name)
        if name.casefold() in {p.casefold() for p in entries}:
            raise ValueError('Case-colliding archive paths')
        entries[name] = git('cat-file', 'blob', oid)
    if not EXACT.issubset(entries) or 'src/ServerScriptService/Bootstrap.server.luau' not in entries:
        raise ValueError('Required source/project/reference asset missing')
    return dict(sorted(entries.items()))


def write_archive(path, entries):
    with zipfile.ZipFile(path, 'x', compression=zipfile.ZIP_STORED) as archive:
        for name, data in entries.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)


def extract_checked(archive_path, destination, files):
    with zipfile.ZipFile(archive_path) as archive:
        if archive.namelist() != list(files):
            raise ValueError('ZIP membership/order differs from manifest')
        for info in archive.infolist():
            path = inside(destination, info.filename)
            data = archive.read(info)
            if len(data) != files[info.filename]['bytes'] or sha(data) != files[info.filename]['sha256']:
                raise ValueError('ZIP content hash mismatch')
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as output:
                output.write(data)


def source_audit(xml, expected):
    sources = []
    for item in ET.fromstring(xml).iter('Item'):
        if item.get('class') in ('Script', 'LocalScript', 'ModuleScript'):
            props = item.find('Properties')
            text = next((p.text or '' for p in props if p.get('name') == 'Source'), None)
            if text is None:
                raise ValueError('Serialized script has no Source')
            sources.append(sha(text.encode()))
    if not sources or Counter(sources) != Counter(expected):
        raise ValueError('Built script source set differs from preserved sources')
    return len(sources)


def project_paths(node, source):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == '$path':
                if value != 'src' and not value.startswith('src/') and value not in EXACT:
                    raise ValueError('Project reference outside explicit source scope')
                path = inside(source, value)
                if not path.exists():
                    raise ValueError('Missing project source: ' + value)
                node[key] = str(path)
            else:
                project_paths(value, source)
    elif isinstance(node, list):
        for value in node:
            project_paths(value, source)


def build_and_audit(source, temp, output):
    rojo, compiler = shutil.which('rojo'), shutil.which('luau-compile')
    if not rojo or not compiler:
        raise RuntimeError('Install official Rojo and Luau compiler before preservation')
    project = json.loads((source / 'default.project.json').read_text(encoding='utf-8'))
    if project['tree']['Workspace'].get('$attributes', {}).get('LocalSustainedPrototype'):
        raise ValueError('Original project unexpectedly enables local prototype')
    project_paths(project, source)
    expected = [sha(p.read_text(encoding='utf-8').encode()) for p in sorted((source / 'src').rglob('*.luau'))]
    for path in sorted((source / 'src').rglob('*.luau')):
        subprocess.run([compiler, str(path)], check=True, stdout=subprocess.DEVNULL)
    project_path = temp / 'normal.project.json'
    project_path.write_text(json.dumps(project), encoding='utf-8')
    normal_xml = temp / 'normal-audit-only.rbxlx'
    subprocess.run([rojo, 'build', str(project_path), '-o', str(normal_xml)], check=True)
    count = source_audit(normal_xml.read_bytes(), expected)
    # Deliberately missing source must be rejected by the same serialized audit.
    try:
        source_audit(normal_xml.read_bytes(), expected[1:])
    except ValueError:
        pass
    else:
        raise AssertionError('Source audit accepted missing source')
    bootstrap = source / 'src/ServerScriptService/Bootstrap.server.luau'
    original = bootstrap.read_text(encoding='utf-8')
    if 'local localFixture=RunService:IsStudio() and game.PlaceId==0' not in original or 'if localFixture then data,save,loadMessage=Profiles.Default(),false' not in original:
        raise ValueError('Original local fixture persistence guard needs manual review')
    guarded = temp / 'GuardedBootstrap.server.luau'
    guarded.write_text(GUARD + original, encoding='utf-8')
    server = project['tree']['ServerScriptService']
    del server['$path']
    for path in sorted((source / 'src/ServerScriptService').iterdir()):
        if not path.is_file() or path.suffix != '.luau':
            raise ValueError('Explicit server mapping requires review')
        name = path.name.removesuffix('.server.luau').removesuffix('.luau')
        server[name] = {'$path': str(guarded if path == bootstrap else path)}
    project_path = temp / 'guarded.project.json'
    project_path.write_text(json.dumps(project), encoding='utf-8')
    subprocess.run([compiler, str(guarded)], check=True, stdout=subprocess.DEVNULL)
    xml = output / 'OriginalCity-LOCAL-ONLY.rbxlx'
    binary = output / 'OriginalCity-LOCAL-ONLY.rbxl'
    subprocess.run([rojo, 'build', str(project_path), '-o', str(xml)], check=True)
    replaced = expected.copy();replaced.remove(sha(original.encode()));replaced.append(sha((GUARD + original).encode()))
    source_audit(xml.read_bytes(), replaced)
    subprocess.run([rojo, 'build', str(project_path), '-o', str(binary)], check=True)
    return {'productionScriptCount': count, 'normalSourceAudit': 'passed; audit build not retained',
            'guardedSourceAudit': 'passed', 'guardPrefixSha256': sha(GUARD.encode()),
            'nativeExecution': False, 'artifacts': {p.name: sha(p.read_bytes()) for p in (xml, binary)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True, help='Exact reviewed 40-character Git commit ID')
    parser.add_argument('--verify-existing', action='store_true', help='Verify an incomplete matching archive without replacing source ZIP')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-fA-F]{40}', args.commit):
        parser.error('--commit must be a full commit ID, not a ref or option')
    commit = args.commit.lower()
    if git('rev-parse', '--verify', commit + '^{commit}').decode().strip() != commit:
        raise ValueError('Commit did not resolve exactly')
    entries = collect(commit)
    destination = inside(ROOT, 'assets/drafts/original-city-2026-11-11')
    destination.mkdir(parents=True, exist_ok=True)
    output = inside(destination, commit)
    files = {name: {'bytes': len(data), 'sha256': sha(data)} for name, data in entries.items()}
    archive = output / 'original-city-source.zip'
    manifest_path = output / 'manifest.json'
    if args.verify_existing:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest.get('status') != 'incomplete' or manifest.get('commit') != commit or manifest.get('files') != files:
            raise ValueError('Existing manifest is not an incomplete exact-commit match')
        if sha(archive.read_bytes()) != manifest.get('zipSha256'):
            raise ValueError('Existing source ZIP hash mismatch')
        if any((output / name).exists() for name in ('OriginalCity-LOCAL-ONLY.rbxl', 'OriginalCity-LOCAL-ONLY.rbxlx')):
            raise FileExistsError('Refusing to overwrite existing draft artifacts')
    else:
        if output.exists():
            raise FileExistsError('Refusing to overwrite existing snapshot: ' + str(output))
        output.mkdir(exist_ok=False)
        write_archive(archive, entries)
        manifest = {'schema': 1, 'commit': commit, 'scope': ['src/**/*.luau', *sorted(EXACT)],
                    'description': 'Repository-generated city source only; NOT live or unsaved Studio backup',
                    'zipSha256': sha(archive.read_bytes()), 'files': files, 'status': 'incomplete'}
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    # Short, explicitly bounded workspace temp avoids Windows MAX_PATH compiler failures.
    temp_root = inside(Path.home(), '.scream-preserve-temp')
    temp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='check-', dir=temp_root) as work:
        temp = Path(work).resolve()
        if not temp.is_relative_to(temp_root.resolve()):
            raise ValueError('Temporary path escaped preservation workspace')
        source = temp / 'restored';source.mkdir()
        extract_checked(archive, source, files)
        manifest['verification'] = build_and_audit(source, temp, output)
    manifest['status'] = 'complete; unpublished; native execution not performed'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Preserved exact commit ' + commit + ' (' + str(len(files)) + ' tracked source files). No native execution or upload.')


if __name__ == '__main__':
    main()

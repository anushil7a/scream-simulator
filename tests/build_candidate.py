"""Build/audit an unpublished normal-profile candidate; never uploads to Roblox."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from quest_writer_preflight import release_gate


def digest(data):
    return hashlib.sha256(data).hexdigest()


def audit_sources(xml, expected):
    actual = []
    for item in ET.fromstring(xml).iter('Item'):
        if item.get('class') in ('Script', 'LocalScript', 'ModuleScript'):
            properties = item.find('Properties')
            source = next((p.text or '' for p in properties if p.get('name') == 'Source'), None)
            if source is None:
                raise ValueError('A candidate script has no serialized Source')
            actual.append(digest(source.encode()))
    if not actual or Counter(actual) != Counter(expected):
        raise ValueError('Candidate scripts differ from production source files')
    return len(actual)


def main():
    rojo = shutil.which('rojo') or '/opt/homebrew/bin/rojo'
    source_hashes = {str(p.relative_to(ROOT)): digest(p.read_text().encode())
                     for p in sorted((ROOT/'src').rglob('*.luau'))}
    project = ROOT/'default.project.json'
    project_hash = digest(project.read_bytes())
    config = json.loads(project.read_text())
    referenced_files = {}
    def collect_files(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == '$path' and (ROOT/value).is_file():
                    referenced_files[value] = digest((ROOT/value).read_bytes())
                else:
                    collect_files(value)
        elif isinstance(node, list):
            for value in node:
                collect_files(value)
    collect_files(config)
    if 'LocalSustainedPrototype' in config['tree']['Workspace'].get('$attributes', {}):
        raise ValueError('Normal candidate must not enable the disposable fixture attribute')
    out = ROOT/'build'
    out.mkdir(exist_ok=True)
    (out/'AutomaticVoiceCandidate.provenance.json').unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='scream-candidate-') as directory:
        xml_path = Path(directory)/'candidate.rbxlx'
        subprocess.run([rojo,'build',str(project),'-o',str(xml_path)],cwd=ROOT,check=True)
        xml = xml_path.read_text()
        count = audit_sources(xml, source_hashes.values())
        # Regression: injected fixture source and a missing production source
        # must both be rejected, not accepted by a zero-script scan.
        tree = ET.fromstring(xml)
        extra = ET.SubElement(tree,'Item',{'class':'Script'})
        props = ET.SubElement(extra,'Properties')
        ET.SubElement(props,'string',{'name':'Source'}).text = 'print("injected fixture")'
        for invalid, expected in [(ET.tostring(tree),source_hashes.values()),
                                   (xml,list(source_hashes.values())[1:])]:
            try:
                audit_sources(invalid,expected)
            except ValueError:
                pass
            else:
                raise AssertionError('Source audit accepted a mismatched candidate')
        candidate = out/'AutomaticVoiceCandidate.rbxl'
        subprocess.run([rojo,'build',str(project),'-o',str(candidate)],cwd=ROOT,check=True)
        # Fail if source files changed between XML audit and binary build.
        current = {str(p.relative_to(ROOT)): digest(p.read_text().encode())
                   for p in sorted((ROOT/'src').rglob('*.luau'))}
        if current != source_hashes or digest(project.read_bytes()) != project_hash or any(
                digest((ROOT/name).read_bytes()) != value for name, value in referenced_files.items()):
            raise RuntimeError('Sources changed during build; rerun verification')
        (out/'AutomaticVoiceCandidate.provenance.json').write_text(json.dumps({
            'builtAtUtc':datetime.now(timezone.utc).isoformat(),
            'status':'unpublished; native/device tests remain pending',
            'releaseGates':{'questWriters':release_gate()},
            'sourceCount':count,'sources':source_hashes,
            'projectSha256':project_hash,'referencedFiles':referenced_files,
            'artifactSha256':digest(candidate.read_bytes()),
        },indent=2)+'\n')
    print(f'PASS: candidate contains exactly {count} production sources; mismatch checks passed. No upload or native execution.')


if __name__ == '__main__':
    main()

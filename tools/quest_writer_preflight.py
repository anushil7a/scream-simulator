"""Offline declared-writer check. Never reads Roblox or authorizes publication.

A local operator inventory cannot establish that every live server was drained.
The candidate remains release-blocked until that operational evidence is reviewed.
"""
from datetime import datetime
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def release_gate():
    return {
        'status': 'BLOCKED_UNVERIFIED_WRITER_FLEET',
        'reason': 'Older quest catalogs erase additive progress/claims during profile acquisition, while retaining rewards.',
        'requiredEvidence': [
            'Complete serving-writer and rollback inventory, matched to exact source commits.',
            'Offline preservation checks for every declared writer; incompatible writers excluded.',
            'Verified cutover/drain with no old-server joins remaining; publishing or scheduling a restart is not proof.',
            'Reviewed rollback floor; saved-version history is not an automatic reward-replay undo.',
        ],
        'offlineCommand': 'python tools/quest_writer_preflight.py --inventory <reviewed-local-inventory.json>',
        'limits': 'Local declarations/tests cannot verify Roblox fleet state, native persistence, or publication permission.',
    }


def validate_candidate(provenance, artifact, sources, project_hash, referenced_files):
    if not isinstance(provenance, dict):
        raise ValueError("Candidate provenance must be an object")
    if provenance.get("projectSha256") != project_hash or provenance.get("referencedFiles") != referenced_files:
        raise ValueError("Candidate project/assets no longer match provenance")
    if provenance.get('artifactSha256') != digest(artifact):
        raise ValueError('Candidate artifact hash does not match provenance')
    if provenance.get('sources') != sources:
        raise ValueError('Candidate source hashes do not match checked-out production sources')
    if provenance.get('releaseGates', {}).get('questWriters') != release_gate():
        raise ValueError('Candidate is missing the current explicit writer-fleet release gate')


def validate_inventory(inventory, candidate_hash):
    if not isinstance(inventory, dict):
        raise ValueError('Inventory must be an object')
    if inventory.get('candidateArtifactSha256') != candidate_hash:
        raise ValueError('Inventory is not bound to this exact candidate artifact')
    for key in ('inventoryComplete', 'incompatibleWritersExcluded'):
        if inventory.get(key) is not True:
            raise ValueError('Missing explicit operator declaration: ' + key)
    for key in ('inventoryEvidence', 'cutoverEvidence', 'rollbackEvidence'):
        if not isinstance(inventory.get(key), str) or not inventory[key].strip():
            raise ValueError('Missing reviewed evidence reference: ' + key)
    if not isinstance(inventory.get('observedAtUtc'), str):
        raise ValueError('Inventory must record observedAtUtc')
    stamp = datetime.fromisoformat(inventory['observedAtUtc'].replace('Z', '+00:00'))
    if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 0:
        raise ValueError('Inventory time must be explicit UTC')
    serving, rollback = inventory.get('servingCommits'), inventory.get('rollbackCommits')
    if not isinstance(serving, list) or not serving or not isinstance(rollback, list):
        raise ValueError('Serving commits must be nonempty; rollback commits must be explicit')
    if inventory.get('rollbackDisabled') is True:
        if rollback:
            raise ValueError('Rollback cannot be both disabled and populated')
    elif inventory.get('rollbackDisabled') is not False or not rollback:
        raise ValueError('Explicitly disable rollback or name at least one rollback writer')
    commits = serving + rollback
    if any(not isinstance(c, str) or not re.fullmatch(r'[0-9a-f]{40}', c) for c in commits):
        raise ValueError('Writer references must be immutable full lowercase Git commit IDs')
    return sorted(set(commits))


def read_commit(commit, path):
    # No fetch/network/authentication. Missing local history fails closed.
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT).decode('utf-8')


def inspect_writers(commits, reader=read_commit, probe=None):
    if probe is None:
        from quest_writer_compatibility import probe_writer
        probe = probe_writer
    results = []
    for commit in commits:
        config = reader(commit, 'src/ReplicatedStorage/Shared/Config.luau')
        profiles = reader(commit, 'src/ServerScriptService/Profiles.luau')
        lease = reader(commit, 'src/ReplicatedStorage/Shared/ProfileLease.luau')
        ok, detail = probe(config, profiles, lease)
        results.append({'commit': commit, 'compatibleInSimulation': ok,
                        'detail': detail.strip(), 'sourceSha256': {
                            'Config': digest(config.encode()), 'Profiles': digest(profiles.encode()),
                            'ProfileLease': digest(lease.encode())}})
    return results


def current_project_inputs():
    project = ROOT / 'default.project.json'
    references = {}
    def collect(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == '$path':
                    target = (ROOT / value).resolve()
                    if not target.is_relative_to(ROOT.resolve()):
                        raise ValueError('Project reference escapes checkout')
                    if target.is_file():
                        references[value] = digest(target.read_bytes())
                else:
                    collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)
    collect(json.loads(project.read_text()))
    return digest(project.read_bytes()), references


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, help='Local reviewed operator declarations, not fetched or trusted fleet telemetry')
    args = parser.parse_args()
    try:
        sidecar = ROOT / 'build/AutomaticVoiceCandidate.provenance.json'
        provenance = json.loads(sidecar.read_text())
        sources = {str(p.relative_to(ROOT)): digest(p.read_text(encoding='utf-8').encode())
                   for p in sorted((ROOT / 'src').rglob('*.luau'))}
        project_hash, references = current_project_inputs()
        validate_candidate(provenance, (ROOT / 'build/AutomaticVoiceCandidate.rbxl').read_bytes(), sources, project_hash, references)
        if args.inventory is None:
            raise ValueError('No reviewed serving/rollback inventory supplied; writer-fleet gate remains BLOCKED')
        inventory = json.loads(args.inventory.read_text())
        commits = validate_inventory(inventory, provenance['artifactSha256'])
        results = inspect_writers(commits)
        print(json.dumps({'declaredWriterResults': results,
                          'releaseStatus': 'BLOCKED_PENDING_OPERATIONAL_REVIEW_AND_OTHER_RELEASE_GATES',
                          'observedAtUtc': inventory['observedAtUtc'],
                          'limits': release_gate()['limits']}, indent=2))
        if not all(row['compatibleInSimulation'] for row in results):
            raise ValueError('At least one declared writer loses candidate quest state')
        print('PASS declared-writer simulation only. Reverify actual serving/drain/rollback evidence before release; this is not publication approval.')
        return 0
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print('BLOCKED:', error, file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

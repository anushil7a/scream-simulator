"""Offline gate validator regressions. Inventories below are synthetic, not fleet evidence."""
import argparse
import copy
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rollout_gate', ROOT/'tools/quest_writer_preflight.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)


def checks(module):
    n=0
    def check(ok,message):
        nonlocal n
        assert ok,message;n+=1
    def rejected(call,message):
        nonlocal n
        try:call()
        except ValueError:n+=1
        else:raise AssertionError(message)
    artifact=b'synthetic artifact';sources={'x':'hash'};refs={'asset':'hash'};project='projecthash'
    provenance={'artifactSha256':module.digest(artifact),'sources':sources,'projectSha256':project,
                'referencedFiles':refs,'releaseGates':{'questWriters':module.release_gate()}}
    module.validate_candidate(provenance,artifact,sources,project,refs);n+=1
    for name,value in [('artifactSha256','changed'),('sources',{}),('projectSha256','changed'),('referencedFiles',{}),('releaseGates',{})]:
        bad=copy.deepcopy(provenance);bad[name]=value
        rejected(lambda:module.validate_candidate(bad,artifact,sources,project,refs),'Stale candidate admitted: '+name)
    check(provenance['releaseGates']['questWriters']['status'].startswith('BLOCKED'),'Provenance silently grants release')
    inv={'candidateArtifactSha256':provenance['artifactSha256'],'observedAtUtc':'2026-11-11T00:00:00Z',
         'inventoryComplete':True,'incompatibleWritersExcluded':True,'inventoryEvidence':'synthetic inventory reference',
         'cutoverEvidence':'synthetic cutover reference','rollbackEvidence':'synthetic rollback reference',
         'servingCommits':['a'*40],'rollbackCommits':['b'*40],'rollbackDisabled':False}
    check(module.validate_inventory(inv,provenance['artifactSha256'])==['a'*40,'b'*40],'Serving/rollback writer omitted')
    for key in inv:
        bad=copy.deepcopy(inv);del bad[key]
        rejected(lambda:module.validate_inventory(bad,provenance['artifactSha256']),'Missing declaration accepted: '+key)
    for key,value in [('candidateArtifactSha256','stale'),('inventoryComplete','true'),('incompatibleWritersExcluded',False),
                      ('inventoryEvidence',' '),('cutoverEvidence',''),('rollbackEvidence',{}),('observedAtUtc','2026-11-11T00:00:00'),
                      ('observedAtUtc','not-a-time'),('servingCommits',[]),('servingCommits',['main']),('servingCommits',['A'*40]),
                      ('rollbackCommits',[]),('rollbackDisabled',True),('rollbackDisabled','false')]:
        bad=copy.deepcopy(inv);bad[key]=value
        rejected(lambda:module.validate_inventory(bad,provenance['artifactSha256']),'Invalid declaration accepted: '+key)
    no_rollback=copy.deepcopy(inv);no_rollback['rollbackCommits']=[];no_rollback['rollbackDisabled']=True
    check(module.validate_inventory(no_rollback,provenance['artifactSha256'])==['a'*40],'Explicit disabled rollback failed')
    # Every serving AND rollback ref is actually probed; false remains false.
    reads=[];probes=[]
    def reader(commit,path):reads.append((commit,path));return commit+':'+path
    def probe(config,profiles,lease):
        probes.append((config,profiles,lease));return config.startswith('a'), 'synthetic result'
    result=module.inspect_writers(['a'*40,'b'*40],reader,probe)
    check(len(reads)==6 and len(probes)==2,'Declared rollback was not probed')
    check(result[0]['compatibleInSimulation'] is True and result[1]['compatibleInSimulation'] is False,'Incompatible writer promoted to pass')
    check(all(len(row['sourceSha256'])==3 for row in result),'Exact writer source hashes missing')
    print('PASS',n,'offline candidate/inventory checks; synthetic declarations are not operational evidence')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
    checks(gate)
    if args.negative_controls:
        source=(ROOT/'tools/quest_writer_preflight.py').read_text()
        mutants=[('stale artifact',"provenance.get('artifactSha256') != digest(artifact)", 'False', 'Stale candidate admitted: artifactSha256'),
                 ('rollback omission','serving + rollback','serving', 'Serving/rollback writer omitted'),
                 ('false compatibility promotion',"'compatibleInSimulation': ok", "'compatibleInSimulation': True", 'Incompatible writer promoted to pass'),
                 ('incomplete inventory',"('inventoryComplete', 'incompatibleWritersExcluded')", "('incompatibleWritersExcluded',)", 'Missing declaration accepted: inventoryComplete')]
        for name,old,new,expected in mutants:
            assert source.count(old)==1,old
            class Mutant:pass
            module=Mutant();module.__file__=str(ROOT/'tools/quest_writer_preflight.py')
            exec(compile(source.replace(old,new),module.__file__,'exec'),module.__dict__)
            try:checks(module)
            except AssertionError as error:assert expected in str(error),(name,str(error))
            else:raise AssertionError('Control survived: '+name)
            print('PASS negative control:',name)

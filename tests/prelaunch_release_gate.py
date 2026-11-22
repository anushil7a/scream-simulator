"""Actual local release gate: no deployment, permissions or native service calls."""
from pathlib import Path
import importlib.util
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gate',R/'tools/developer_access_preflight.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
source=(R/'src/ServerScriptService/DeveloperAccess.luau').read_text();checks=0
def check(ok,message):
 global checks
 assert ok,message;checks+=1
check(gate.release_gate()['status']=='PASS_LOCAL_DISABLED_CONFIG_ONLY','Reviewed disabled config rejected')
flag='Access.PrelaunchAllTesters = false'
check(gate.release_gate(source.replace(flag,'Access.PrelaunchAllTesters = true'))['status']=='BLOCKED','Enabled tools passed release')
for bad in ['',source.replace(flag,''),source.replace(flag,'Access.PrelaunchAllTesters = nil'),source.replace(flag,'Access.PrelaunchAllTesters = "false"'),source.replace(flag,flag+' or true'),source+'\nAccess.PrelaunchAllTesters = true',source.replace('creatorId == Access.OwnerUserId','true'),source.replace('Access.OwnerUserId = 11499795799','Access.OwnerUserId = 1'),source.replace('[10769005350] = true','[1] = true'),source.replace('Access.PrelaunchUniverseIds[universeId] == true','true')]:
 check(gate.release_gate(bad)['status']=='BLOCKED','Unknown/malformed/unsafe source accepted')
check(gate.release_gate(source.replace('isStudio == false and Access.PrelaunchAllTesters == true', 'isStudio == false'))['status']=='BLOCKED','Exact City Preview helper bypass accepted')
old=gate.ACCESS;gate.ACCESS=R/'build'/'intentionally-absent-prelaunch-config.luau'
try:check(gate.release_gate()['status']=='BLOCKED','Missing config accepted')
finally:gate.ACCESS=old
builder=(R/'tests/build_candidate.py').read_text()
check("'prelaunchTestTools':developer_access_gate()" in builder,'Candidate omits gate')
print('PASS',checks,'actual prelaunch release gate assertions; local source only')

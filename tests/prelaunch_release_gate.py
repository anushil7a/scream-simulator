"""Actual local release gate: no deployment, permissions or native service calls."""
from pathlib import Path
import importlib.util
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gate',R/'tools/developer_access_preflight.py');gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
source=(R/'src/ServerScriptService/DeveloperAccess.luau').read_text();checks=0
def check(ok,message):
 global checks
 assert ok,message;checks+=1
check(gate.release_gate()['status']=='BLOCKED','Enabled tools passed release')
disabled=source.replace('Access.PrelaunchAllTesters = true','Access.PrelaunchAllTesters = false')
check(gate.release_gate(disabled)['status']=='PASS_LOCAL_DISABLED_CONFIG_ONLY','Reviewed disabled config rejected')
for bad in ['',source.replace('Access.PrelaunchAllTesters = true',''),source.replace('Access.PrelaunchAllTesters = true','Access.PrelaunchAllTesters = nil'),source.replace('Access.PrelaunchAllTesters = true','Access.PrelaunchAllTesters = "false"'),source.replace('Access.PrelaunchAllTesters = true','Access.PrelaunchAllTesters = false or true'),disabled+'\nAccess.PrelaunchAllTesters = true',disabled.replace('creatorId == Access.OwnerUserId','true'),disabled.replace('Access.OwnerUserId = 11499795799','Access.OwnerUserId = 1'),disabled.replace('[10769005350] = true','[1] = true'),disabled.replace('Access.PrelaunchUniverseIds[universeId] == true','true')]:
 check(gate.release_gate(bad)['status']=='BLOCKED','Unknown/malformed/unsafe source accepted')
old=gate.ACCESS;gate.ACCESS=R/'build'/'intentionally-absent-prelaunch-config.luau'
try:check(gate.release_gate()['status']=='BLOCKED','Missing config accepted')
finally:gate.ACCESS=old
builder=(R/'tests/build_candidate.py').read_text()
check("'prelaunchTestTools':developer_access_gate()" in builder,'Candidate omits gate')
print('PASS',checks,'actual prelaunch release gate assertions; local source only')

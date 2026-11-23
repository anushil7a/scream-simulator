"""Exercise real native-only tint paths with Roblox API doubles, not a Studio claim."""
from pathlib import Path
import subprocess,tempfile
import beam_silhouette as support
R=Path(__file__).resolve().parents[1]
source=(R/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau').read_text()
# Client passes platformReducedMotion as contactReduced; it must also reach VFX.
assert 'syncVfx(rig,origin,finish,dir,length,width,distance,styleSpec,suppressSecondary)' in source
support.CHECKS=''
def run(s):
    body=support.fixture(s)
    marker="local StyleSource=require('../src/ReplicatedStorage/Shared/BeamStyle')"
    env='''local game={GetService=function()return {FindFirstChild=function()return nil end}end}
local function typeof(x)if x==game then return 'Instance' elseif getmetatable(x)==V then return 'Vector3' else return type(x)end end
'''
    body=body.replace(marker,env+marker)+'''
local rigs={}
for i=1,25 do
 local r=Visuals.Create();rigs[i]=r
 Visuals.Update(r,Vector3.zero,Vector3.zAxis,40,7,color,100,false)
 assert(Visuals.Contact(r,vec(2,1,24),r.born+.1,i))
 Visuals.Animate(r,r.born+.1,Vector3.zero,false)
 assert(r.used==#r.parts and r.contact.used==#r.contact.parts,'allocation holes')
end
assert(Visuals.Budget()==512,'fixture did not saturate')
for _,r in ipairs(rigs)do
 Visuals.Animate(r,r.born+.12,Vector3.zero,true)
 Visuals.Animate(r,r.born+.14,Vector3.zero,false)
 Visuals.Destroy(r)
end
Visuals.Clear();assert(Visuals.Budget()==0)
print('PASS native-path doubles: 25 saturated attackers, contact, reduced transition, cleanup')
'''
    with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(body);p=Path(f.name)
    try:return subprocess.run(['luau',str(p)],capture_output=True,text=True)
    finally:p.unlink()
r=run(source);assert r.returncode==0,r.stdout+r.stderr;print(r.stdout.strip())
old=' local nextIndex=rig.used+1\n local part=rig.parts[nextIndex]\n if not part then part=take(kind or (nextIndex>5 and "detail" or "core"));if not part then return end;rig.parts[nextIndex]=part end\n -- Count successful allocations only. Native tint/contact loops must never visit holes.\n rig.used=nextIndex'
bad=' rig.used+=1\n local part=rig.parts[rig.used]\n if not part then part=take(kind or (rig.used>5 and "detail" or "core"));if not part then return end;rig.parts[rig.used]=part end'
assert old in source
r=run(source.replace(old,bad));assert r.returncode and 'nil' in r.stderr,r.stdout+r.stderr
print('PASS negative control: pre-fix allocation crashes native-only path')

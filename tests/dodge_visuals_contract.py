"""Structural safety gates for client DodgeVisuals; not native rendering evidence."""
from pathlib import Path
s=(Path(__file__).resolve().parents[1]/'src/StarterPlayer/StarterPlayerScripts/DodgeVisuals.luau').read_text()
checks={
 'reduced motion short circuit':'if reducedMotion then return false end',
 'concurrency cap':'local MAX_CASTS=4',
 'body cap':'local MAX_BODY_PARTS=16',
 'direct children only':'cast.character:GetChildren()',
 'whitelisted body only':'BODY[body.Name] and body:IsA("BasePart")',
 'strip children':'copy:ClearAllChildren()',
 'actual pose only':'copy.CFrame=body.CFrame',
 'no physics':'copy.Anchored=true;copy.CanCollide=false;copy.CanTouch=false;copy.CanQuery=false;copy.Massless=true',
 'second actual sample':'if not cast.second and cast.age>=SECOND_SAMPLE then',
 'late frame suppression':'if cast.age<SECOND_SAMPLE+.1 then snapshot(cast) end',
 'finite effect lifetime':'cast.age>=CAST_LIFETIME',
 'character removal cleanup':'not cast.character.Parent',
 'heartbeat teardown':'heartbeat:Disconnect();heartbeat=nil',
 'global destroy':'function Visuals.Destroy()',
}
for name,token in checks.items():assert token in s,name
assert s.index('copy:ClearAllChildren()')<s.index('copy.Parent=model'),'Copied children parented before stripping'
for token in ['FireServer','task.delay','task.spawn','AssemblyLinearVelocity','BodyVelocity','RemoteEvent']:
 assert token not in s, 'Unexpected authority or delayed work: '+token
assert 'Instance.new("Part")' not in s,'No box trails'
print(f'PASS {len(checks)+8} dodge visual structural gates; native effect appearance unverified')

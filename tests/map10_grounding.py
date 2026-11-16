"""Execute actual grounding decision lines, not native raycast/physics."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1];s=(R/'src/ServerScriptService/World.luau').read_text();a=s.index('local heightLimit=');b=s.index(' then',a)
code='''local checks=0
local function test(map,y,gap,want)
 local Config={CityLayout={MapId=map},MapMax={Y=220}}
 local bot={root={Position={Y=y}}}
'''+s[a:b]+''' then assert(want,'unexpected recovery') else assert(not want,'missing recovery') end
 checks+=1
end
for _,y in ipairs({3,19,35,67}) do test('Map10',y,3,false) end
test('Map10',35,99,true);test('Map10',35,1,true);test('Map10',-4,3,true);test('Map10',221,3,true)
test('CompactCity',35,3,true);test('CompactCity',3,3,false)
print('PASS '..checks..' actual grounding decision checks')
'''
bootstrap=(R/'src/ServerScriptService/Bootstrap.server.luau').read_text()
a=bootstrap.index('   local disc=Instance.new("Part");disc.Name="TrainingStrikeWarning"')
b=bootstrap.index('   game:GetService("Debris")',a)
code+=r'''
local seen
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z} end}
local Instance={new=function() seen={};return seen end}
local Enum={PartType={Cylinder="Cylinder"},Material={Neon="Neon"}}
local Color3={fromRGB=function(...)return {...} end}
local transform={__mul=function(a)return a end}
local CFrame={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},transform) end,Angles=function()return {}end}
local workspace={}
local function train(ground)
 local r={Position={X=5,Y=(ground or 0)+3,Z=-8}}
 local bot={training={y=ground}}
'''+bootstrap[a:b]+r'''
 assert(seen.CFrame.Y==(ground or 0)+1.4 and seen.CFrame.X==5 and seen.CFrame.Z==-8,'Dodge warning is buried or misplaced')
 assert(seen.CanCollide==false and seen.CanTouch==false and seen.CanQuery==false,'Training warning interferes with gameplay')
end
train(nil);train(16);train(32);train(64)
print('PASS active trainer warning on flat and elevated pads')
'''
with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',prefix='tmp_ground_',delete=False) as f:f.write(code);p=Path(f.name)
try:subprocess.run(['luau',str(p)],check=True)
finally:p.unlink()

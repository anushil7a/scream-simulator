"""Extracts the actual runtime trainer costume into the same preview stream as support NPCs."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def run():
 s=(ROOT/'src/ServerScriptService/World.luau').read_text();start=s.index('local function trainerOutfit(');end=s.index('local function faceToward(',start)
 code='''
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local CFrame={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local Enum={Material={SmoothPlastic='SmoothPlastic'}}
local function accessory(model,target,name,size,offset,color)
 print('PART|'..name..'|'..target.Name..'|'..size.X..'|'..size.Y..'|'..size.Z..'|'..offset.X..'|'..offset.Y..'|'..offset.Z..'|'..color.R..'|'..color.G..'|'..color.B)
end
'''+s[start:end]+'''
for _,id in ipairs({'rookie','brawler','elite'})do
 local model={FindFirstChild=function()return nil end}
 print('NPC|'..id..' trainer|0|0|trainer')
 local function limb(name)return {Name=name}end
 trainerOutfit(model,limb('Torso'),limb('Left Arm'),limb('Right Arm'),limb('Left Leg'),limb('Right Leg'),{id=id})
end
'''
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=ROOT/'tests',delete=False) as f:f.write(code);p=Path(f.name)
 try:return subprocess.check_output(['luau',str(p)],text=True)
 finally:p.unlink()
if __name__=='__main__':print(run())

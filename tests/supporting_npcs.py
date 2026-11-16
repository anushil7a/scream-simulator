"""Executes actual NPC roster/dress with mocked transforms. Not native navigation or visual proof."""
from pathlib import Path
import subprocess,tempfile,json,sys
R=Path(__file__).resolve().parents[1]
source=(R/'src/ServerScriptService/SupportingNPCs.luau').read_text()
setup='''
local count=0
local function check(v,m)assert(v,m);count+=1 end
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local CFrame={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {R=r,G=g,B=b}end}
local Enum={Material={SmoothPlastic='SmoothPlastic'}}
local function factory()
'''
checks='''
end
local NPCs=factory()
check(#NPCs.Roster==4,'roster')
local ids={};local names={}
for _,spec in ipairs(NPCs.Roster) do
 check(not ids[spec.index] and spec.index>=901,'stable appended id');ids[spec.index]=true
 check(not names[spec.name],'unique name');names[spec.name]=true
 local job=NPCs.Job(spec)
 check(job.name==spec.name and job.role==spec.role and job.quests==nil,'do not duplicate quest owners')
 check(#job.stations==1 and #job.lines>=3,'bounded route/dialogue')
 local station=job.stations[1]
 check(station.position.X==spec.x and station.position.Z==spec.z and station.position.Y==3,'home route')
 check(not(spec.x>=-120 and spec.x<=200 and spec.z>=-180 and spec.z<=140),'outside PvP')
 check(spec.x>-350 and spec.x<350 and spec.z>-290 and spec.z<290,'map bounds')
 for _,line in ipairs(job.lines)do check(#line<200 and #line>25,'bounded helpful dialogue')end
 local limbs={};local nodes={};local added={}
 for _,name in ipairs({'Torso','Head','Left Arm','Right Arm','Left Leg','Right Leg'}) do
  local o={Name=name};limbs[name]=o;table.insert(nodes,o)
 end
 local old={Name='Cap'};function old:Destroy()self.removed=true end;table.insert(nodes,old)
 local model={};function model:FindFirstChild(n)return limbs[n]end
 function model:GetChildren()return nodes end
 function model:SetAttribute(k,v)self[k]=v end
 local function accessory(m,target,name,size,offset,color,material)
  check(m==model and target~=nil,'attachment target')
  check(size.X>0 and size.X<=2.7 and size.Y>0 and size.Y<=2.6 and size.Z>0 and size.Z<=1.3,'bounded geometry')
  check(material=='SmoothPlastic','material')
  table.insert(added,{name=name,target=target.Name,size=size,offset=offset,color=color})
 end
 NPCs.Dress({model=model},spec,accessory)
 check(old.removed and model.SupportConcept==spec.concept,'cosmetic cleanup and provenance')
 check(#added>=5 and #added<=10,'bounded per-character detail count')
 print('NPC|'..spec.name..'|'..spec.x..'|'..spec.z..'|'..spec.kind)
 for _,p in ipairs(added)do
  print('PART|'..p.name..'|'..p.target..'|'..p.size.X..'|'..p.size.Y..'|'..p.size.Z..'|'..p.offset.X..'|'..p.offset.Y..'|'..p.offset.Z..'|'..p.color.R..'|'..p.color.G..'|'..p.color.B)
 end
end
print('PASS '..count..' supporting NPC roster/route/model assertions')
'''
def run():
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False) as f:
  f.write(setup+source+checks);p=Path(f.name)
 try:
  out=subprocess.run(['luau',str(p)],text=True,capture_output=True,check=True)
 finally:p.unlink()
 return out.stdout
if __name__=='__main__':
 out=run();print(out if '--export' in sys.argv else out.splitlines()[-1])
 world=(R/'src/ServerScriptService/World.luau').read_text()
 assert world.index('SupportingNPCs.Roster')>world.index('for index,originalTier in ipairs(TrainingRules.Tiers)')
 assert 'local options = (bot.job and bot.job.lines) or roleLines[bot.role] or lines' in world
 assert 'local message = contextLine or options[index]' in world
 print('PASS append-only spawn and quest-context priority source contracts')

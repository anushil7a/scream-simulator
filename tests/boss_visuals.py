"""Execute actual upload-free boss surface renderer and streaming controller with vector/instance mocks."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1]
data=(R/'src/ReplicatedStorage/Shared/BossVisualData.luau').read_text()
render=(R/'src/StarterPlayer/StarterPlayerScripts/BossAppearance.luau').read_text().split('local Appearance=',1)[1]
controller=(R/'src/StarterPlayer/StarterPlayerScripts/BossVisualController.luau').read_text()
pre=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local V={};V.__index=function(t,k)if k=='Magnitude' then return math.sqrt(t:Dot(t)) elseif k=='Unit' then return t/t.Magnitude else return V[k] end end
function V:Dot(b)return self.X*b.X+self.Y*b.Y+self.Z*b.Z end
function V:Cross(b)return Vector3.new(self.Y*b.Z-self.Z*b.Y,self.Z*b.X-self.X*b.Z,self.X*b.Y-self.Y*b.X)end
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
V.__mul=function(a,b)return Vector3.new(a.X*b,a.Y*b,a.Z*b)end
V.__div=function(a,b)return Vector3.new(a.X/b,a.Y/b,a.Z/b)end
V.__unm=function(a)return a*-1 end
Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
local CF={};CF.__mul=function(a,b)return a end
CFrame={new=function(...)return setmetatable({values={...}},CF)end,fromMatrix=function(p,r,u,b)return {p=p,r=r,u=u,b=b}end}
Color3={fromRGB=function(...)return {...}end};Enum={Material={Neon=1,SmoothPlastic=2,Metal=3,Slate=4,Fabric=5},SurfaceType={Smooth=1},PartType={Block=1,Ball=2,Cylinder=3}}
local created={}
Instance={new=function(class)local o={ClassName=class};table.insert(created,o);return o end}
'''
post=r'''
local function model()return {SetAttribute=function(self,k,v)self[k]=v end}end
local materials={}
for id,entries in pairs(Data) do
 created={};local pauses=0
 local parent=model()
 local ok,n=Appearance.Build(parent,id,Vector3.new(0,32,0),function()return true end,function()pauses+=1 end)
 check(ok and n==#created and n<=450,'part budget '..id)
 check(parent.GeometryReady==true and parent.GeometryPartCount==n,'native-ready marker missing')
 check(pauses>0,'construction not batched')
 local area=0;local wanted=0
 for _,p in ipairs(created) do
  materials[p.Material]=true
  check(type(p.Reflectance)=='number' and p.Reflectance>=0 and p.Reflectance<=.055,'excessive reflectance')
  check(p.Anchored and not p.CanCollide and not p.CanTouch and not p.CanQuery,'visual mutated physics')
  check(p.TopSurface==Enum.SurfaceType.Smooth,'stud surfaces remain')
  check(p.Size.X>0 and p.Size.Y>0 and p.Size.Z>0,'invalid part dimensions')
  if p.ClassName=='WedgePart' then
   area+=p.Size.Y*p.Size.Z/2
   check(math.abs(p.CFrame.r:Dot(p.CFrame.u))<.001 and math.abs(p.CFrame.r.Magnitude-1)<.001,'bad wedge basis')
  end
 end
 for _,e in ipairs(entries) do if e.kind=='Surface' then for _,f in ipairs(e.triangles) do
  local a=Vector3.new(table.unpack(e.vertices[f[1]+1]));local b=Vector3.new(table.unpack(e.vertices[f[2]+1]));local c=Vector3.new(table.unpack(e.vertices[f[3]+1]))
  wanted+=(b-a):Cross(c-a).Magnitude/2
 end end end
 check(math.abs(area-wanted)<.01,'wedge surface area changed '..id)
 print(id..': '..n..' native parts / '..pauses..' batches')
 created={};local canceled=false
 check(not Appearance.Build(model(),id,Vector3.new(0,0,0),function()return not canceled end,function()canceled=true end),'cancel ignored')
 check(#created<=34,'cancellation exceeded batch budget')
end
check(materials[Enum.Material.Metal] and materials[Enum.Material.Slate] and materials[Enum.Material.Fabric],'material hierarchy absent')
check(not Appearance.Build(model(),'missing',Vector3.new(0,0,0),function()return true end,function()end),'unknown id')
-- Exact production geometry expands around ground, not the raised aim core.
for _,groundY in ipairs({0,16,32,64})do
 local center,scale=Appearance.FromCore(Vector3.new(10,groundY+7,-20),{scale=1.4,aimHeight=7})
 check(center.Y==groundY and center.X==10 and center.Z==-20 and scale==1.4,'ground anchor scaled or hardcoded')
 for id in pairs(Data)do
  created={};local one=model();Appearance.Build(one,id,center,function()return true end,function()end)
  local baseline=created;created={};local larger=model()
  Appearance.Build(larger,id,center,function()return true end,function()end,scale)
  check(#created==#baseline and larger.VisualScale==1.4,'scaled count/marker changed')
  for i,p in ipairs(created)do
   local before=baseline[i]
   check(p.Name==before.Name and p.Material==before.Material and p.Reflectance==before.Reflectance,'boss identity/material changed')
   local wantSize=before.Size*scale
   if p.ClassName=='WedgePart' then wantSize=Vector3.new(.015,wantSize.Y,wantSize.Z) end
   check((p.Size-wantSize).Magnitude<.0001,'scaled dimensions wrong '..id..' '..i..' '..p.Name..' '..p.ClassName..' '..(p.Size-wantSize).Magnitude)
   local pos=p.CFrame.p or p.CFrame.values[1]
   local oldPos=before.CFrame.p or before.CFrame.values[1]
   check((pos-(center+(oldPos-center)*scale)).Magnitude<.0001,'scaled position moved ground')
   if p.ClassName=='WedgePart' then
    check((p.CFrame.r-before.CFrame.r).Magnitude<.0001 and (p.CFrame.u-before.CFrame.u).Magnitude<.0001,'scaled surface rotated')
   end
   check(p.Anchored and not p.CanCollide and not p.CanQuery and not p.CanTouch,'scale changed physics')
  end
 end
end
for _,bad in ipairs({'bad',{},0/0,math.huge,-math.huge})do
 check(Appearance.Scale(bad)==1,'unsafe scale accepted')
 local ground,scale=Appearance.FromCore(Vector3.new(0,37,0),{scale=bad,aimHeight=bad})
 check(ground.Y==32 and scale==1,'unsafe anchor accepted')
end
check(Appearance.Scale(-3)==1 and Appearance.Scale(99)==2,'scale unbounded')
local fallback,s=Appearance.FromCore(Vector3.new(0,37,0),nil)
check(fallback.Y==32 and s==1,'old caller compatibility lost')
local pending={};local models={};local builds=0
local ctl=Controller.new({create=function(id)local m={Parent=true,id=id,Destroy=function(self)self.Parent=nil;self.destroyed=true end};table.insert(models,m);return m end,
 spawn=function(fn)table.insert(pending,fn)end,pause=function()end,
 build=function(model,id,center,alive,pause,scale)builds+=1;model.receivedScale=scale;check(alive(),'stale build not gated');return true end})
local a={id='metronome',source={Parent=true},center=Vector3.new(0,32,0),scale=1.4}
local b={id='golem',source={Parent=true},center=Vector3.new(300,0,0)}
ctl:Step(Vector3.new(0,35,0),{a,b});check(#models==1,'nearest selection')
pending[1]();check(models[1].receivedScale==1.4,'controller lost scale');ctl:Step(Vector3.new(1,35,0),{a,b});check(#models==1,'repeated activation')
ctl:Step(Vector3.new(300,3,0),{a,b});check(models[1].destroyed and #models==2,'switch cleanup')
pending[2]();ctl:Step(nil,{a,b});check(models[2].destroyed and ctl.current==nil,'respawn cleanup')
ctl:Step(Vector3.new(300,3,0),{b});b.source.Parent=nil;pending[3]();check(ctl.current==nil,'stream-out during build')
ctl:Destroy();ctl:Step(Vector3.new(0,35,0),{a});check(ctl.current==nil,'destroyed controller restarted')
local queued={};local replacements={}
local changing=Controller.new({create=function()local m={Parent=true,Destroy=function(self)self.Parent=nil end};table.insert(replacements,m);return m end,
 spawn=function(fn)table.insert(queued,fn)end,pause=function()end,build=function(_,_,_,alive,_,scale)check(alive() and scale==1.6,'stale scale build');return true end})
local moving={id='metronome',source={Parent=true},center=Vector3.new(0,32,0),scale=1.4}
changing:Step(Vector3.new(0,32,0),{moving})
local updated={id=moving.id,source=moving.source,center=moving.center,scale=1.6}
changing:Step(Vector3.new(0,32,0),{updated});queued[1]();queued[2]()
check(#replacements==2 and not replacements[1].Parent,'scale change failed to replace/cancel')
changing:Destroy()
print('PASS '..checks..' boss visual geometry/lifecycle mock assertions; not native rendering')
'''
code=pre+'\nlocal Data=(function()\n'+data+'\nend)()\nlocal Appearance=(function()\nlocal Appearance='+render+'\nend)()\nlocal Controller=(function()\n'+controller+'\nend)()\n'+post
def run(body, expected=None):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False) as f:f.write(body);name=f.name
 try:result=subprocess.run(['luau',name],cwd=R,capture_output=True,text=True)
 finally:Path(name).unlink()
 if expected:
  assert result.returncode and expected in result.stdout+result.stderr,result.stdout+result.stderr
  print('PASS scaling negative control:',expected)
 else:
  assert result.returncode==0,result.stdout+result.stderr
  print(result.stdout.strip())
run(code)
for old,new,message in [
 ('p.Size=Vector3.new(table.unpack(entry.size))*scale','p.Size=Vector3.new(table.unpack(entry.size))','scaled dimensions wrong'),
 ('center+v[1]*scale','center+v[1]','scaled position moved ground'),
 ('math.clamp(height,0,20)','5','ground anchor scaled or hardcoded'),
 ('chosen.center,alive,options.pause,chosen.scale','chosen.center,alive,options.pause','controller lost scale'),
]:
 assert code.count(old)==1,old
 run(code.replace(old,new),message)
# Wiring contracts complement executable anchor/controller/renderer tests.
client=(R/'src/StarterPlayer/StarterPlayerScripts/BossVisuals.client.luau').read_text()
assert 'Appearance.FromCore(core.Position,specs[model.Name])' in client
assert 'center=center,scale=scale' in client
assert 'local specs={};for _,spec in ipairs(Catalog.Entries)' in client
print('PASS normal streamed-client catalog wiring')

"""Actual local health presentation module with lifecycle/UI doubles; no native replication claim."""
from pathlib import Path
import subprocess,tempfile,argparse
R=Path(__file__).resolve().parents[1]
SOURCE=R/'src/StarterPlayer/StarterPlayerScripts/HealthBarPresentation.luau'
PRE=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local signals={}
local function signal()
 local s={items={}};signals[#signals+1]=s
 function s:Connect(f)local c={Connected=true};function c:Disconnect()self.Connected=false end;c.f=f;table.insert(self.items,c);return c end
 function s:Fire(...)local list=table.clone(self.items);for _,c in ipairs(list)do if c.Connected then c.f(...)end end end
 function s:Count()local n=0;for _,c in ipairs(self.items)do if c.Connected then n+=1 end end;return n end
 return s
end
local function node(class,name)
 local o={ClassName=class,Name=name or class,children={},attrs={},events={},ChildAdded=signal(),ChildRemoved=signal(),AncestryChanged=signal(),DescendantAdded=signal(),DescendantRemoving=signal()}
 function o:IsA(c)return self.ClassName==c end
 function o:FindFirstChild(n)for _,v in ipairs(self.children)do if v.Name==n then return v end end end
 function o:FindFirstChildOfClass(c)for _,v in ipairs(self.children)do if v.ClassName==c then return v end end end
 function o:GetChildren()return table.clone(self.children)end
 function o:IsDescendantOf(w)local p=self.Parent;while p do if p==w then return true end;p=p.Parent end;return false end
 function o:GetAttribute(n)return self.attrs[n]end
 function o:GetAttributeChangedSignal(n)self.events[n]=self.events[n]or signal();return self.events[n]end
 function o:SetAttribute(n,v)self.attrs[n]=v;if self.events[n]then self.events[n]:Fire()end end
 function o:Destroy()self.Parent=nil;self.destroyed=true end
 return o
end
local function add(parent,child)child.Parent=parent;table.insert(parent.children,child);parent.ChildAdded:Fire(child);child.AncestryChanged:Fire(child,parent)end
local function remove(parent,child)for i,v in ipairs(parent.children)do if v==child then table.remove(parent.children,i);break end end;child.Parent=nil;parent.ChildRemoved:Fire(child);child.AncestryChanged:Fire(child,nil)end
local created={};Instance={new=function(c)local o=node(c);created[#created+1]=o;return o end}
UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end,fromScale=function(...)return {...}end}
Color3={fromRGB=function(...)return {...}end}
Enum={HumanoidHealthDisplayType={AlwaysOn='on',AlwaysOff='off'},HumanoidStateType={Dead='dead',Running='running'},Font={GothamMedium=1},TextXAlignment={Right=2}}
local function humanoid()
 local h=node('Humanoid');h.HealthDisplayType='original';h.Died=signal();h.StateChanged=signal();h.state='running'
 h.DisplayName='Native identity';h.NameDisplayDistance=73;h.HealthDisplayDistance=61;h.NameOcclusion='native-team-policy';h.DisplayDistanceType='viewer'
 function h:GetState()return self.state end
 return h
end
'''
POST=r'''
local ratio=P.Value(43.2,100,'Moving');check(math.abs(ratio-.432)<1e-9,'Actual HP/max fraction')
check(P.Value(200,100)==1,'Clamp over-max')
for _,v in ipairs({0,-1,math.huge,-math.huge,0/0,'20',true,{}})do check(P.Value(v,100)==nil,'Invalid/dead health shown')end
for _,v in ipairs({0,-1,math.huge,0/0,'100'})do check(P.Value(10,v)==nil,'Invalid maximum shown')end
check(P.Value(50,100,'Defeated')==nil,'Defeated boss shown')
local model=node('Model');local core=node('Part');add(model,core)
local board=node('BillboardGui');add(core,board);board.Size={old='board'};board.MaxDistance=90;board.AlwaysOnTop=false
local name=node('TextLabel');add(board,name);name.Text='Whispering Metronome · Lv 10';name.Size={old='name'};name.TextColor3='teal'
local oldSize,oldLabel=board.Size,name.Size
local b=P.Boss(model,board,name);local row=created[#created-2];local track=created[#created-1];local fill=created[#created]
check(not row.Visible,'Missing authoritative attrs must fail closed')
model:SetAttribute('BossMaxHealth',320);model:SetAttribute('BossHealth',320);model:SetAttribute('BossState','Idle')
check(row.Visible and fill.Size[1]==1,'Initial HP not exact')
model:SetAttribute('BossHealth',160);check(fill.Size[1]==.5,'Server HP update missing')
model:SetAttribute('BossHealth',0);check(not row.Visible,'Dead boss bar visible')
model:SetAttribute('BossState','Defeated');model:SetAttribute('BossHealth',320);check(not row.Visible,'Reset health before phase leaked defeated bar')
model:SetAttribute('BossState','Idle');check(row.Visible and fill.Size[1]==1,'Boss reset not reflected')
check(name.Text=='Whispering Metronome · Lv 10','Name/level changed')
check(board.AlwaysOnTop==false and board.MaxDistance==90,'Boss depth/range policy wrong')
check(#created==3,'Boss presentation grew beyond three nodes')
check(track.Size[1]==130 and track.Size[2]==5 and track.Position[1]==.5 and track.Position[2]==-65,'Boss bar not short and centered')
for _,node in ipairs(created)do check(node.ClassName~='TextLabel','Added extra boss copy');check(not node.Active and not node.Selectable and not node.Interactable,'Health strip captures input')end
for i=1,1000 do model:SetAttribute('BossHealth',i%320+1)end;check(#created==3,'Updates allocate GUI')
b:Destroy();b:Destroy();check(row.destroyed and board.Size==oldSize and name.Size==oldLabel,'Boss teardown did not restore')
check(model:GetAttributeChangedSignal('BossHealth'):Count()==0,'Boss event retained')
local h=humanoid();h.Parent={};local observer=P.NativePlayer(h)
check(h.HealthDisplayType=='on','Native strip not enabled')
check(h.DisplayName=='Native identity' and h.NameOcclusion=='native-team-policy' and h.NameDisplayDistance==73 and h.HealthDisplayDistance==61 and h.DisplayDistanceType=='viewer','Unrelated native identity/distance/occlusion mutated')
h.state='dead';h.Died:Fire();check(h.HealthDisplayType=='off','Dead player strip not hidden')
h.state='running';h.StateChanged:Fire();check(h.HealthDisplayType=='on','Revival state not restored')
observer:Destroy();check(h.HealthDisplayType=='original' and h.Died:Count()==0 and h.StateChanged:Count()==0,'Native teardown failed')
observer=P.NativePlayer(h);h.HealthDisplayType='later owner';observer:Destroy();check(h.HealthDisplayType=='later owner','Teardown overwrote later native policy')
local world=node('Workspace');local localPlayer={};local remote={CharacterAdded=signal(),CharacterRemoving=signal()}
local c=node('Model');add(world,c);h=humanoid();add(c,h);remote.Character=c
local localH=humanoid();localPlayer.Character={humanoid=localH}
local players={PlayerAdded=signal(),PlayerRemoving=signal(),GetPlayers=function()return{localPlayer,remote}end}
local manager=P.Players(players,localPlayer,world);check(h.HealthDisplayType=='on' and localH.HealthDisplayType=='original','Local HUD/self native policy altered')
remove(world,c);check(h.HealthDisplayType=='original','Stream-out did not release native owner')
add(world,c);check(h.HealthDisplayType=='on','Stream-in did not restore native owner')
local old=h;remote.CharacterRemoving:Fire(c);check(old.HealthDisplayType=='original','Respawn old character retained')
local c2=node('Model');add(world,c2);remote.CharacterAdded:Fire(c2)
local h2=humanoid();add(c2,h2);check(h2.HealthDisplayType=='on','Late humanoid not bound')
old.state='dead';old.Died:Fire();check(h2.HealthDisplayType=='on','Stale character event affected respawn')
remove(c2,h2);check(h2.HealthDisplayType=='original','Removed humanoid retained native owner')
add(c2,h2);check(h2.HealthDisplayType=='on','Replacement humanoid not attached')
players.PlayerRemoving:Fire(remote);check(h2.HealthDisplayType=='original','Player departure retained native owner')
manager:Destroy();manager:Destroy()
check(players.PlayerAdded:Count()==0 and players.PlayerRemoving:Count()==0,'Global player events retained')
for _,s in ipairs(signals)do check(s:Count()==0,'Lifecycle connection leak')end
print('PASS '..checks..' actual health presentation/value/native lifecycle assertions; mocked engine, NOT native replication/occlusion proof')
'''
CLIENT=(R/'src/StarterPlayer/StarterPlayerScripts/HealthBars.client.luau').read_text()
CLIENT_PRE=r'''
local scene=node('Folder','ScreamSimulatorWorld');add(world,scene)
local folder=node('Folder','BossEncounters');add(scene,folder)
local boss=node('Model','metronome');local bossCore=node('Part','Core');add(boss,bossCore)
local bossBoard=node('BillboardGui','BossNameplate');bossBoard.Size={original=true};bossBoard.MaxDistance=90;bossBoard.AlwaysOnTop=false;add(bossCore,bossBoard)
local bossName=node('TextLabel','NameAndLevel');bossName.Size={original=true};bossName.Text='Whispering Metronome · Lv 10';bossName.TextColor3='teal';add(bossBoard,bossName)
boss:SetAttribute('BossHealth',100);boss:SetAttribute('BossMaxHealth',200);add(folder,boss)
local initialNodes=#created
local script={Destroying=signal(),Parent={WaitForChild=function()return {}end}}
local game={GetService=function(_,name)check(name=='Players','Unexpected service or remote');return players end}
local workspace=world
players.LocalPlayer=localPlayer
local require=function()return P end
'''
CLIENT_POST=r'''
check(#created==initialNodes+3,'Client did not attach exact existing boss plate')
local visibleRow=created[initialNodes+1];check(visibleRow.Visible,'Client HP missing')
local initial=initialNodes
folder.ChildAdded:Fire(boss);check(#created==initial+3,'Repeated boss discovery duplicated GUI')
local ignored=node('Model','not_a_boss');add(folder,ignored);check(#created==initial+3,'Unbounded nonboss model binding')
boss.DescendantRemoving:Fire(bossCore);remove(boss,bossCore);check(visibleRow.destroyed,'Stream-out retained boss GUI')
add(boss,bossCore);boss.DescendantAdded:Fire(bossCore);check(#created==initial+6,'Stream-in did not rebuild boss plate')
remove(folder,boss);check(created[initial+4].destroyed,'Boss removal retained bar')
add(folder,boss);check(#created==initial+9,'Boss replacement not attached')
remove(scene,folder);check(created[initial+7].destroyed,'Folder replacement retained bar')
add(scene,folder);check(#created==initial+12,'Late encounter folder not attached')
remove(world,scene);check(created[initial+10].destroyed,'World replacement retained bar')
add(world,scene);check(#created==initial+15,'New world not attached')
script.Destroying:Fire();check(created[initial+13].destroyed,'Script teardown retained boss GUI')
local count=#created;boss.DescendantAdded:Fire(bossCore);players.PlayerAdded:Fire(remote)
check(#created==count,'Retired LocalScript installed stale UI')
for _,s in ipairs(signals)do check(s:Count()==0,'Client integration event leak')end
print('PASS '..checks..' total actual health module + LocalScript discovery/streaming/teardown assertions; mocked engine only')
'''
def run(source,negative=False):
 code=PRE+'\nlocal P=(function()\n'+source+'\nend)()\n'+POST+'\n'+CLIENT_PRE+'\n(function()\n'+CLIENT+'\nend)()\n'+CLIENT_POST
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(code);p=Path(f.name)
 try:
  r=subprocess.run(['luau',str(p)],capture_output=True,text=True);out=r.stdout+r.stderr
  if negative:assert r.returncode,'Negative control passed';print('PASS negative control:',out.splitlines()[0])
  else:assert not r.returncode,out;print(out,end='')
 finally:p.unlink()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args();s=SOURCE.read_text();run(s)
 if a.negative_controls:
  run(s.replace(' or state=="Defeated"',''),True)
  run(s.replace('humanoid.HealthDisplayType==owned','true'),True)
  run(s.replace('disconnect(record.characterConnections);','',1),True)

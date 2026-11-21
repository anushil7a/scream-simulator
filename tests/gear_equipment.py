"""Execute actual Equipment with a tiny tree/transform mock, not Roblox physics."""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Equipment.luau').read_text()
code=r'''
-- Local Z translation only. Studio verifies the rotated cylinders and poses.
local mt={};mt.__mul=function(a,b)return setmetatable({Z=a.Z+b.Z},mt)end
local function cf(_,_,z)return setmetatable({Z=z or 0},mt)end
local CFrame={new=cf,Angles=function()return cf()end}
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(...)return {...}end}
local Enum={Material={SmoothPlastic=1,Neon=2},PartType={Ball=1,Cylinder=2}}
local methods={}
local function node(class,name)
 return setmetatable({ClassName=class,Name=name or class,children={},attrs={},Size={Y=1,Z=1},CFrame=cf()},{__index=function(n,k)if k=='Parent' then return rawget(n,'_parent') end;return methods[k]end,__newindex=function(n,k,v)
  if k=='Parent' then local old=rawget(n,'_parent');if old then for i,x in ipairs(old.children)do if x==n then table.remove(old.children,i);break end end end
   if v then table.insert(v.children,n)end end
  rawset(n,k=='Parent' and '_parent' or k,v)
 end})
end
function methods:IsA(c)return self.ClassName==c or c=='BasePart' and self.ClassName=='MeshPart' or c=='BasePart' and self.ClassName=='Part'end
function methods:FindFirstChild(name)for _,c in ipairs(self.children)do if c.Name==name then return c end end end
function methods:GetDescendants()local all={};for _,c in ipairs(self.children)do table.insert(all,c);for _,d in ipairs(c:GetDescendants())do table.insert(all,d)end end;return all end
function methods:FindFirstChildWhichIsA(c)for _,d in ipairs(self:GetDescendants())do if d:IsA(c)then return d end end end
function methods:SetAttribute(k,v)self.attrs[k]=v end
function methods:GetAttribute(k)return self.attrs[k]end
function methods:PivotTo(v)self.pivot=v end
function methods:Destroy()self.Parent=nil;self.destroyed=true end
function methods:Clone()local n=node(self.ClassName,self.Name);for _,c in ipairs(self.children)do c:Clone().Parent=n end;return n end
local Instance={new=node};local storage=node('ServerStorage');local templates=node('Folder','GearTemplates');templates.Parent=storage
local game={GetService=function(_,name)assert(name=='ServerStorage');return storage end}
local Equipment=(function()
'''+source+r'''
end)()
local G=require('../src/ReplicatedStorage/Shared/GearCatalog')
local character=node('Model');local hand=node('Part','RightHand');hand.Parent=character;local torso=node('Part','UpperTorso');torso.Parent=character
local player={Character=character}
for _,item in ipairs(G.Items)do
 local template=node('Model',item.template);local mesh=node('MeshPart','Authored');mesh.Parent=template;template.Parent=templates
 Equipment.SyncGear(player,item)
 local model=character:FindFirstChild('ProgressionGear');assert(model and model:GetAttribute('GearId')==item.id and not model:GetAttribute('FallbackVisual'))
 assert(model:GetAttribute('MountKind')==(item.mount=='back' and 'back' or 'hand'))
 local part=model:FindFirstChild('Authored');assert(not part.Anchored and not part.CanCollide and not part.CanQuery and not part.CanTouch and part.Massless)
 local weld=part:FindFirstChild('WeldConstraint');assert(weld.Part0==(item.mount=='back' and torso or hand) and weld.Part1==part)
 Equipment.SyncGear(player,item);assert(character:FindFirstChild('ProgressionGear')==model,'Repeated sync duplicated model')
 Equipment.SyncGear(player,nil);assert(not character:FindFirstChild('ProgressionGear'))
 template:Destroy()
end
Equipment.SyncGear(player,G.Get('CelestialOrgan'))
local fallback=character:FindFirstChild('ProgressionGear');assert(fallback:GetAttribute('FallbackVisual') and fallback:GetAttribute('MountKind')=='hand')
Equipment.SyncGear(player,nil);assert(fallback.destroyed)
for _,case in ipairs({{'RightHand',.6275},{'Right Arm',1},{'RightHand',1.5}})do
 local rig=node('Model');local palm=node('Part',case[1]);palm.Size.Z=case[2];palm.Parent=rig;player.Character=rig
 Equipment.SyncGear(player,G.Get('Megaphone'))
 local gear=rig:FindFirstChild('ProgressionGear')
 local rear=gear:FindFirstChild('MouthpieceCollar');local grip=gear:FindFirstChild('Grip')
 local bracket=gear:FindFirstChild('MountBracket')
 assert(rear.CFrame.Z+rear.Size.X/2<=-palm.Size.Z/2-.039,'Megaphone mouthpiece crosses the palm')
 assert(grip.CFrame.Z==-.25,'Megaphone grip lost its palm anchor')
 assert(bracket.CFrame.Z-bracket.Size.Z/2<=rear.CFrame.Z+rear.Size.X/2
  and bracket.CFrame.Z+bracket.Size.Z/2>=grip.CFrame.Z,'Megaphone bracket no longer spans mouthpiece and grip')
end
local respawn=node('Model');local arm=node('Part','Right Arm');arm.Parent=respawn;player.Character=respawn
Equipment.SyncGear(player,G.Get('MosaicMic'));assert(respawn:FindFirstChild('ProgressionGear'))
print('PASS actual equipment lifecycle, welds and three Megaphone grip depths; synthetic transforms')
'''
def run_equipment(payload, expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(payload)
 try: result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
 finally:path.unlink()
 if expected:
  assert result.returncode and expected in result.stderr,result.stderr
  print('PASS control: '+expected)
 else:
  assert result.returncode==0,result.stderr
  print(result.stdout,end='')

run_equipment(code)
if '--negative-controls' in sys.argv:
 for old,new,reason in [
  ('math.max(0,hand.Size.Z/2-.02)','0','Megaphone mouthpiece crosses the palm'),
  ('Vector3.new(.16,.18,.24+forward)','Vector3.new(.16,.18,.24)','Megaphone bracket no longer spans mouthpiece and grip'),
 ]:
  assert code.count(old)==1,old
  run_equipment(code.replace(old,new),reason)

client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=client.index(' elseif selected=="Style" then',client.index('render=function()'))
style=client[start:client.index(' elseif selected=="Map" then',start)].split('\n',1)[1]
coin_action=client[client.index('function academy.starterCoinAction('):client.index('local function menuKey()')]
short_landscape=next(line for line in client.splitlines() if 'local shortLandscape=' in line)
layout=client[client.index(' local short=viewport.Y<550'):client.index(' if width~=lastLayoutWidth')]
menu_tabs=next(line for line in client.splitlines() if line.startswith('academy.menuTabs='))
code=r'''
local Gear=require('../src/ReplicatedStorage/Shared/GearCatalog')
local function renderStyle(data,narrow,width)
 local quests={garden={goal=3},beach={goal=6}}
 local Config={Gear=Gear,MovementPassId=0,Auras={Gold='gold'},GetQuest=function(id)return quests[id]end}
 local gui={AbsoluteSize={X=width or (narrow and 390 or 1280)}}
 local title,subtitle={},{}
 local gold,muted='gold','muted'
 local cards,buttons,sent,links={},{},{},{}
 local academy={NavigationCatalog={Resolve=function()return not data.noCity end}}
 academy.selectGuide=function(kind,id)table.insert(links,kind..':'..id) end
 local function toggleTab(tab,reset)table.insert(links,tab..':'..tostring(reset)) end
 local function closeMenu()table.insert(links,'close') end
 local UDim2={new=function(_,x,_,y)return {x=x,y=y}end,fromOffset=function(w,h)return {w=w,h=h}end}
 local function card()local c={};table.insert(cards,c);return c end
 local function label(c,text,size,pos)
  if c.text then c.detail=text;c.detailBottom=pos.h+size.y else c.text=text end
 end
 local function info(text)table.insert(cards,{text=text})end
 local function button(c,name,text,size,position,callback)
  local b={text=text,size=size,position=position,press=callback}
  buttons[name]=b
  return b
 end
 local ShopUI={ColorMixer=function()table.insert(cards,{text='Color Mixer'})end}
 local action={FireServer=function(_,verb,id)table.insert(sent,{verb,id})end}
 local shopUsed
'''+coin_action+style+r'''
 return cards,buttons,sent,links
end
for _,narrow in ipairs({false,true}) do
 local cards,buttons,sent=renderStyle({level=1,coins=80,aura='Gold',activeQuest='sprint'},narrow)
 assert(cards[1].text=='ACADEMY MEGAPHONE' and cards[2].text=='Color Mixer','Starter gear below color controls')
 local starter=buttons.Megaphone
 assert(starter.size.h>=44 and starter.text=='NEED 20 COINS' and not starter.Interactable,'Starter shortcut displaced an active quest')
 assert(cards[1].detail:find('100 coins · 80 coins in wallet',1,true),'Unaffordable gear obscures the price or balance')
 if narrow then assert(starter.position.y+starter.size.h<=72,'Starter CTA clipped at 568 × 320') end
 starter.press();assert(#sent==0,'Unaffordable gear sent a request')
 buttons.MosaicMic.press();assert(not buttons.MosaicMic.Interactable and #sent==0,'Locked gear sent a request')
 cards,buttons,sent=renderStyle({level=1,coins=1000,aura='Gold'},narrow)
 assert(buttons.Megaphone.text=='BUY & EQUIP\n100 COINS' and buttons.Megaphone.Interactable,'Buy action missing the actual price')
 assert(cards[1].detail:find('1000 coins in wallet',1,true),'Displayed balance differs before purchase')
 buttons.Megaphone.press();assert(#sent==1 and sent[1][1]=='Gear' and sent[1][2]=='Megaphone')
 cards,buttons=renderStyle({level=1,coins=900,aura='Gold',megaphoneOwned=true,megaphoneEquipped=true},narrow)
 assert(buttons.Megaphone.text=='UNEQUIP' and buttons.Megaphone.Interactable)
 assert(cards[1].detail:find('Equipped · 900 coins in wallet',1,true) and not cards[1].detail:find('100 coins',1,true),'Equipped gear shows stale price or balance')
 cards,buttons=renderStyle({level=1,coins=900,aura='Gold',megaphoneOwned=true},narrow)
 assert(buttons.Megaphone.text=='EQUIP' and buttons.Megaphone.Interactable)
 assert(cards[1].detail:find('Owned · 900 coins in wallet',1,true),'Unequipped gear obscures ownership or balance')
end
print('PASS starter gear placement, eligibility and action on narrow and wide layouts; mocked UI')
local cards,buttons,sent,links=renderStyle({level=1,coins=0,aura='Gold'},true,567)
assert(buttons.Megaphone.TextColor3~='muted' and buttons.Megaphone.Interactable and buttons.Megaphone.text=='GUIDE TO MAR\nNEED 100 COINS','Fresh player has no route or exact shortfall')
assert(cards[1].detail:find('100 coins · 0 coins in wallet',1,true),'Guide replaced the price or wallet balance')
buttons.Megaphone.press()
assert(#sent==0 and links[1]=='mar:gardens' and links[2]=='close','Guide spent coins or did not route to Mar')
cards,buttons,sent,links=renderStyle({level=2,coins=5,aura='Gold',activeQuest='garden',availableQuests={garden=true},quests={garden={progress=3}}},true,567)
assert(buttons.Megaphone.Interactable and buttons.Megaphone.text=='VIEW REWARDS\nNEED 95 COINS','A ready reward lost priority over Mar')
buttons.Megaphone.press()
assert(#sent==0 and #links==1 and links[1]=='Quests:true','Reward shortcut did not open Quests without claiming')
_,buttons=renderStyle({level=2,coins=5,aura='Gold',activeQuest='beach',availableQuests={garden=true},quests={garden={progress=3}}},true,567)
assert(buttons.Megaphone.text=='VIEW REWARDS\nNEED 95 COINS','An earned reward vanished while another quest was active')
for _,data in ipairs({{noCity=true},{quests={garden={claimed=true},beach={claimed=true}}},{activeQuest='sprint'}}) do
 data.level=1;data.coins=5;data.aura='Gold'
 cards,buttons,sent,links=renderStyle(data,true,567)
 buttons.Megaphone.press()
 assert(not buttons.Megaphone.Interactable and buttons.Megaphone.text=='NEED 95 COINS' and #sent==0 and #links==0,'Starter shortcut replaced an active quest or offered unavailable rewards')
end
print('PASS starter coin route, claim priority and no implicit spend or claim; mocked UI')
local function view(w,h)
 local viewport={X=w,Y=h}
 local UDim2={new=function(_,x,_,y)return {x=x,y=y}end,fromOffset=function(x,y)return {x=x,y=y}end}
 local modal,title,subtitle,menuScale,content,tabs={},{},{},{},{},{}
 modal.Close={}
 local academy={tabIcons={},layoutTab=function()end}
'''+menu_tabs+r'''
 for _,name in ipairs(academy.menuTabs) do tabs[name]={};academy.tabIcons[name]={} end
'''+short_landscape+'\n'+layout+r'''
 return modal.Size.y+content.Size.y,modal.Position.y,modal.Close.Position.y,tabs.Style.Position.y
end
local available,menuY,closeY,firstTabY=view(567,241)
assert(available>=60 and menuY==8 and closeY+44<=firstTabY,'Short landscape clips the gear CTA or overlaps close/tab controls')
local smallerWindow=view(567,321)
local cards,buttons=renderStyle({level=1,coins=900,aura='Gold',megaphoneOwned=true,megaphoneEquipped=true},true,567)
assert(cards[1].detailBottom<=smallerWindow and buttons.Megaphone.position.y+buttons.Megaphone.size.h<=smallerWindow,'Short two-row menu clips equipped balance or action')
local _,desktopY=view(1280,720)
assert(desktopY==64,'Desktop menu moved for compact landscape change')
print('PASS short landscape content clearance and desktop layout')
'''
def run_style(source, expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(source)
 try: result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
 finally: path.unlink()
 if expected:
  assert result.returncode and expected in result.stderr,result.stderr
  print('PASS control: '+expected)
 else:
  assert result.returncode==0,result.stderr
  print(result.stdout,end='')

run_style(code)
if '--negative-controls' in sys.argv:
 for old,new,reason in [
  ('if canGuide and not data.activeQuest then','if canGuide then','Starter shortcut displaced an active quest'),
  ('then return "claim" end','then return "guide" end','A ready reward lost priority over Mar'),
  ('active or (data.availableQuests or {})[id]','active or not data.activeQuest and (data.availableQuests or {})[id]','An earned reward vanished while another quest was active'),
  ('academy.selectGuide("mar","gardens");closeMenu()','action:FireServer("Gear",item.id)','Guide spent coins or did not route to Mar'),
 ]:
  assert code.count(old)==1,old
  run_style(code.replace(old,new),reason)

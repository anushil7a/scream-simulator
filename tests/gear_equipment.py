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
for _,product in ipairs(G.Products({}))do
 assert(product.description==G.BonusLabel(G.Get(product.id)),'Vendor and Gear descriptions disagree')
end
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
local megaphone=G.Get('Megaphone')
local prepared=node('Model',megaphone.template)
local enamel=node('MeshPart','Warm enamel');enamel.Parent=prepared;prepared.Parent=templates
prepared:SetAttribute('PalmSurfaceGrip',true)
for _,size in ipairs({.6275,1,1.5}) do
 hand.Size.Z=size
 Equipment.SyncGear(player,megaphone)
 local fitted=character:FindFirstChild('ProgressionGear')
 assert(math.abs(fitted.pivot.Z+size/2-.06)<.0001,'Prepared palm grip does not follow hand depth')
 Equipment.SyncGear(player,nil)
end
prepared:SetAttribute('PalmSurfaceGrip',false)
Equipment.SyncGear(player,megaphone)
assert(character:FindFirstChild('ProgressionGear').pivot.Z==-.25,'Untagged gear lost its legacy grip')
Equipment.SyncGear(player,nil)
prepared:Destroy()
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
  ('template:GetAttribute("PalmSurfaceGrip")==true and (-mount.Size.Z/2+.06) or -.25','-.25','Prepared palm grip does not follow hand depth'),
 ]:
  assert code.count(old)==1,old
  run_equipment(code.replace(old,new),reason)

client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=client.index(' elseif selected=="Style" then',client.index('render=function()'))
style=client[start:client.index(' elseif selected=="Map" then',start)].split('\n',1)[1]
coin_action=client[client.index('function academy.starterCoinAction('):client.index('local function menuKey()')]
gear_upgrade=client[client.index('function academy.gearUpgrade('):client.index('local function toggleTab(')]
toggle=client[client.index('local function toggleTab('):client.index('local function toggle()')]
assert toggle.count('academy.nextGearUpgrade=nextUpgrade')==1
assert client.count('academy.nextGearUpgrade=nextUpgrade')==1,'Card priority changed away from tab-open'
short_landscape=next(line for line in client.splitlines() if 'local shortLandscape=' in line)
layout=client[client.index(' local short=viewport.Y<550'):client.index(' if width~=lastLayoutWidth')]
menu_tabs=next(line for line in client.splitlines() if line.startswith('academy.menuTabs='))
code=r'''
local Gear=require('../src/ReplicatedStorage/Shared/GearCatalog')
local function renderStyle(data,narrow,width,window)
 local quests={garden={goal=3},beach={goal=6}}
 local Config={Gear=Gear,MovementPassId=0,ResonanceLayout=data.hall and {},Auras={Gold='gold'},GetQuest=function(id)return quests[id]end}
 local gui={AbsoluteSize={X=width or (narrow and 390 or 1280)}}
 local title,subtitle={},{}
 local gold,muted='gold','muted'
 local cards,buttons,sent,links={},{},{},{}
 local academy={NavigationCatalog={Resolve=function(kind,id)
  if data.noCity then return end
  if kind=='quest' then return (data.questNavigation or {})[id] end
  return true
 end}}
 academy.selectGuide=function(kind,id)table.insert(links,kind..':'..id) end
 local function toggleTab(tab,reset,questId)table.insert(links,tab..':'..tostring(reset)..(questId and ':'..questId or '')) end
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
'''+coin_action+gear_upgrade+r'''
 local modal={Visible=window~=nil};local selected=window and "Style" or "Quests"
 local function render()end
 if window then
  academy.nextGearUpgrade=window.nextGearUpgrade
  academy.sidebarMenu=window.sidebar
 else
'''+toggle+r'''
  toggleTab("Style")
 end
'''+style+r'''
 return cards,buttons,sent,links,subtitle.Text,academy
end
local hallCards,hallButtons,hallSent,hallLinks,hallSubtitle=renderStyle({hall=true,level=1,coins=0,aura='Gold'},true,666)
assert(hallSubtitle=='Earn gear with coins from PvP.' and hallCards[1].detail:find('Earn coins from PvP KOs',1,true),'Arena gear points to unavailable training or quests')
assert(not hallButtons.Megaphone.Interactable and hallButtons.Megaphone.text=='NEED 100 COINS','Arena exposes a city quest shortcut')
hallButtons.Megaphone.press()
assert(#hallLinks==0 and #hallSent==0,'Unaffordable arena gear action attempted navigation or purchase')
print('PASS guarded Hall gear directions and disabled unaffordable action')
for _,narrow in ipairs({false,true}) do
 local cards,buttons,sent=renderStyle({level=1,coins=80,aura='Gold',activeQuest='sprint'},narrow)
 assert(cards[1].text=='ACADEMY MEGAPHONE' and cards[2].text=='Color Mixer','Starter gear below color controls')
 assert(cards[1].detail:find('Lv 1 · +6% beam power · 100% cap',1,true),'Starter gear described microphone gain instead of capped beam power')
 assert(cards[3].text:find('once your voice triggers an attack',1,true),'Gear explanation omitted the activation order')
 local starter=buttons.Megaphone
 assert(starter.size.h>=44 and starter.text=='NEED 20 COINS' and not starter.Interactable,'Starter shortcut displaced an active quest')
 assert(cards[1].detail:find('100 coins · 80 coins in wallet',1,true),'Unaffordable gear obscures the price or balance')
 if narrow then assert(starter.position.y+starter.size.h<=72,'Starter CTA clipped at 568 × 320') end
 starter.press();assert(#sent==0,'Unaffordable gear sent a request')
 buttons.MosaicMic.press();assert(not buttons.MosaicMic.Interactable and #sent==0,'Locked gear sent a request')
 cards,buttons,sent=renderStyle({level=1,coins=1000,aura='Gold'},narrow)
 assert(buttons.Megaphone.text=='BUY & EQUIP\n100 COINS' and buttons.Megaphone.Interactable,'Buy action missing the actual price')
 assert(cards[1].detail:find('1000 coins in wallet',1,true),'Displayed balance differs before purchase')
 buttons.Megaphone.press();assert(#sent==1 and sent[1][1]=='Gear' and sent[1][2].id=='Megaphone' and sent[1][2].intent=='buy')
 cards,buttons=renderStyle({level=1,coins=900,aura='Gold',megaphoneOwned=true,megaphoneEquipped=true},narrow)
 assert(cards[1].text=='MICRO-SPEAKER' and cards[2].text=='ACADEMY MEGAPHONE' and cards[3].text=='Color Mixer','Next gear upgrade buried below first purchase')
 assert(buttons.Megaphone.text=='UNEQUIP' and buttons.Megaphone.Interactable)
 assert(cards[2].detail:find('Equipped · 900 coins in wallet',1,true) and not cards[2].detail:find('100 coins',1,true),'Equipped gear shows stale price or balance')
 cards,buttons=renderStyle({level=1,coins=900,aura='Gold',megaphoneOwned=true},narrow)
 assert(buttons.Megaphone.text=='EQUIP' and buttons.Megaphone.Interactable)
 assert(cards[2].detail:find('Owned · 900 coins in wallet',1,true),'Unequipped gear obscures ownership or balance')
 cards,buttons=renderStyle({level=35,coins=580,aura='Gold',gearOwned={MosaicMic=true}},narrow)
 assert(cards[1].text=='STREET BOOMBOX' and buttons.StreetBoombox.text=='NEED 20 COINS','Next upgrade ignored a stronger owned item')
 local found=0
 for _,c in ipairs(cards) do if c.text=='STREET BOOMBOX' then found+=1 end end
 assert(found==1,'Next upgrade was duplicated')
 cards=renderStyle({level=100,coins=0,aura='Gold',gearOwned={CelestialOrgan=true}},narrow)
 assert(cards[1].text=='ACADEMY MEGAPHONE' and cards[2].text=='Color Mixer','Max gear promoted a weaker item')
end
local _,beforeButtons,beforeSent,_,_,openGear=renderStyle({level=1,coins=300,aura='Gold'},true,567)
beforeButtons.Megaphone.press()
assert(beforeSent[1][2].id=='Megaphone','Fixture did not buy the first item')
local afterFirst={level=1,coins=200,aura='Gold',megaphoneOwned=true,megaphoneEquipped=true}
local stayed=renderStyle(afterFirst,true,567,openGear)
assert(stayed[1].text=='ACADEMY MEGAPHONE','An open Gear panel moved a different buy button into the last tapped slot')
local reopened=renderStyle(afterFirst,true,567)
assert(reopened[1].text=='MICRO-SPEAKER','Reopening Gear did not promote the next upgrade')
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
local between={level=1,coins=80,aura='Gold',availableQuests={garden=true,beach=true},quests={garden={progress=3,claimed=true}}}
cards,buttons,sent,links=renderStyle(between,true,567)
assert(buttons.Megaphone.Interactable and buttons.Megaphone.text=='VIEW QUEST\nNEED 20 COINS','Unlocked Beach still points back to Mar')
buttons.Megaphone.press()
assert(#sent==0 and #links==1 and links[1]=='Quests:true:beach','Gear shortcut did not open exactly the unlocked Beach quest')
between.availableQuests.beach=false
buttons.Megaphone.press()
assert(#sent==0 and #links==1,'Stale quest shortcut opened a locked objective')
local active={level=1,coins=80,aura='Gold',activeQuest='garden',quests={garden={progress=1}},questNavigation={garden=true,beach=true}}
cards,buttons,sent,links=renderStyle(active,true,567)
assert(buttons.Megaphone.Interactable and buttons.Megaphone.text=='GUIDE QUEST\nNEED 20 COINS','Active starter quest has no gear shortcut')
assert(cards[1].detail:find('100 coins · 80 coins in wallet',1,true),'Active shortcut obscures price or balance')
active.activeQuest='beach'
buttons.Megaphone.press()
assert(#sent==0 and links[1]=='quest:beach' and links[2]=='close','Shortcut did not route to the current quest')
active.questNavigation={}
buttons.Megaphone.press()
assert(#links==2 and #sent==0,'Stale shortcut navigated or sent an action')
_,buttons=renderStyle(active,true,567)
assert(not buttons.Megaphone.Interactable,'Missing objective still shows a guide')
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
 local modal,title,subtitle,menuScale,content,tabs={},{},{},{},{Size={X={Offset=-40}}},{}
 modal.Close={}
 local academy={tabIcons={},layoutTab=function()end}
'''+menu_tabs+r'''
 for _,name in ipairs(academy.menuTabs) do tabs[name]={};academy.tabIcons[name]={} end
'''+short_landscape+'\n'+layout+r'''
 return modal.Size.y+content.Size.y,modal.Position.y,modal.Close.Position.y,tabs.Style.Position.y
end
local minimum=view(509,162)
local sidebarCards,sidebarButtons,sidebarRequests=renderStyle({level=1,coins=100,aura='Gold'},true,509,{sidebar=true})
assert(minimum>=sidebarCards[1].detailBottom and sidebarButtons.Megaphone.position.y+sidebarButtons.Megaphone.size.h<=minimum and sidebarButtons.Megaphone.size.h==44,'Short gear drawer clips price or Buy & Equip')
sidebarButtons.Megaphone.press()
assert(#sidebarRequests==1 and sidebarRequests[1][2].id=='Megaphone' and sidebarRequests[1][2].intent=='buy','Short gear drawer changed the purchase request')
local wideShort,wideShortButtons=renderStyle({level=1,coins=100,aura='Gold'},false,700,{sidebar=true})
assert(wideShortButtons.Megaphone.position.y+wideShortButtons.Megaphone.size.h<=50,'Wide short gear drawer overlaps CTA and detail')
local available,menuY,closeY,firstTabY=view(567,241)
assert(available>=60 and menuY==8 and closeY+44<=firstTabY,'Short landscape clips the gear CTA or overlaps close/tab controls')
local smallerWindow=view(567,321)
local cards,buttons=renderStyle({level=1,coins=900,aura='Gold',megaphoneOwned=true,megaphoneEquipped=true},true,567)
assert(cards[1].detailBottom<=smallerWindow and buttons.MicroSpeaker.position.y+buttons.MicroSpeaker.size.h<=smallerWindow,'Short two-row menu clips first upgrade balance or action')
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
  ('Config.Gear.BonusLabel(item)','"+6% mic power"','Starter gear described microphone gain instead of capped beam power'),
  ('The bonus applies once your voice triggers an attack. ','','Gear explanation omitted the activation order'),
  ('if nextUpgrade then gearCard(nextUpgrade,false) end','if false then gearCard(nextUpgrade,false) end','Next gear upgrade buried below first purchase'),
  ('local nextUpgrade=academy.nextGearUpgrade','local nextUpgrade=academy.gearUpgrade(data)','An open Gear panel moved a different buy button into the last tapped slot'),
  ('if item~=starter and item~=nextUpgrade then','if item~=starter then','Next upgrade was duplicated'),
  ('if Config.ResonanceLayout then return end','if false then return end','Arena exposes a city quest shortcut'),
  ('Earn coins from PvP KOs" or coinAction','Earn coins from training or quests" or coinAction','Arena gear points to unavailable training or quests'),
  ('if canGuide and not active then','if canGuide then','Starter shortcut displaced an active quest'),
  ('if unlocked then return "quest",unlocked end','if false then return "quest",unlocked end','Unlocked Beach still points back to Mar'),
  ('toggleTab("Quests",true,questId)','toggleTab("Quests",true,"garden")','Gear shortcut did not open exactly the unlocked Beach quest'),
  ('then return "claim" end','then return "guide" end','A ready reward lost priority over Mar'),
  ('then return "objective" end','then return end','Active starter quest has no gear shortcut'),
  ('and academy.NavigationCatalog.Resolve("quest",active,data) then return "objective"', 'then return "objective"', 'Stale shortcut navigated or sent an action'),
  ('academy.selectGuide("quest",data.activeQuest);closeMenu()', 'academy.selectGuide("quest","garden");closeMenu()', 'Shortcut did not route to the current quest'),
  ('active or (data.availableQuests or {})[id]','active or not data.activeQuest and (data.availableQuests or {})[id]','An earned reward vanished while another quest was active'),
  ('academy.selectGuide("mar","gardens");closeMenu()','action:FireServer("Gear",item.id)','Guide spent coins or did not route to Mar'),
 ]:
  assert code.count(old)==1,old
  run_style(code.replace(old,new),reason)

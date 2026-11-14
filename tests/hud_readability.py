"""Actual HUD constructors/update slices versus published source; no native glyph-fit claim."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PATH = 'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
BASE = '5622daa54424e639e7d3f671b2e453ff377b2cb6'
SETUP = r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local function equal(a,b)
 if type(a)~='table' or type(b)~='table'then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end;return true
end
local function fixture()
 local f={nodes={}};local data={level=1,coins=0,xp=0,xpNext=103,health=100,maxHealth=100};local p={}
 local UDim={new=function(s,o)return {Scale=s,Offset=o}end}
 local UDim2={new=function(sx,ox,sy,oy)return {X={Scale=sx or 0,Offset=ox or 0},Y={Scale=sy or 0,Offset=oy or 0}}end}
 function UDim2.fromOffset(x,y)return UDim2.new(0,x,0,y)end;function UDim2.fromScale(x,y)return UDim2.new(x,0,y,0)end
 local Color3={new=function(r,g,b)return {R=r,G=g,B=b}end,fromRGB=function(r,g,b)return {R=r/255,G=g/255,B=b/255}end}
 local ColorSequence={new=function(a,b)return {a,b}end}
 local Enum={Font={GothamMedium=1,GothamBold=2},TextXAlignment={Left=1,Center=2,Right=3},ApplyStrokeMode={Border=1}}
 local Instance={new=function(class)
  local fields={ClassName=class,Active=false,Selectable=false,Interactable=true};local node={writes={}}
  setmetatable(node,{__index=fields,__newindex=function(n,k,v)fields[k]=v;n.writes[k]=(n.writes[k] or 0)+1 end})
  table.insert(f.nodes,node);return node
 end}
 local Config={MaxLevel=100};local gui={AbsoluteSize={X=1000,Y=700}};local controls={}
 local function refreshQuestObjects()end
'''
TAIL = r'''
 function f.apply(nextData,width)
  data=nextData;gui.AbsoluteSize.X=width or 1000
STATE_UPDATE
 end
 function f.frame(width)
  local viewport={X=width or 1000}
FRAME_UPDATE
 end
 function f.place(width,touch,dev,height,visible)
  local viewport={X=width};local miniLayout={height=height};local gameplayVisible=visible;data.devAccess=dev
POSITION
VISIBILITY
 end
 function f.humanoid(h,present)if present==false then p.Character=nil else p.Character={FindFirstChildOfClass=function()return h end}end end
 function f.refresh()refreshHealth()end
 f.hud=hud;f.health=health;f.hf=hf;f.xp=xpText;f.xf=xf;f.stats=stats;f.coins=coins
 return f
end
'''
CHECKS = r'''
local function compare(old,current)
 local level,coins=string.match(old.stats.Text,'^LEVEL (.-)    •    (.-) coins$')
 check(level and current.stats.Text=='LEVEL '..level and current.coins.Text==coins..' coins','Exact level/coin values changed')
 check(old.health.Text==current.health.Text and equal(old.hf.Size,current.hf.Size),'Health authority/fraction/rounding changed')
 check(old.xp.Text==current.xp.Text and equal(old.xf.Size,current.xf.Size),'XP arithmetic/warning precedence changed')
end
local old=baseline();local current=fixture()
for _,width in ipairs({320,819,820,1920})do
 for _,level in ipairs({1,9,10,79,80,99,100})do
  for _,coins in ipairs({0,7,1000000000})do
   for _,xp in ipairs({0,30,103})do
    local data={level=level,coins=coins,xp=xp,xpNext=level==100 and 0 or 103,health=100,maxHealth=100}
    old.apply(data,width);current.apply(data,width);compare(old,current)
   end
  end
 end
end
local data={level=99,coins=1000000000,xp=30,xpNext=103,health=100,maxHealth=100}
for _,flags in ipairs({{}, {savingDelayed=true}, {savingAvailable=false}, {testSession=true}, {recoveryWarning=true}, {recoveryWarning=true,savingDelayed=true}, {recoveryWarning=true,savingAvailable=false}, {recoveryWarning=true,testSession=true}})do
 for _,level in ipairs({99,100})do
  data={level=level,coins=1000000000,xp=30,xpNext=103,health=100,maxHealth=100};for k,v in pairs(flags)do data[k]=v end
  for _,width in ipairs({320,819,820,1920})do old.apply(data,width);current.apply(data,width);compare(old,current)end
 end
end
-- Initial fallback, live Humanoid precedence, health clamps and missing-character gaps.
for _,sample in ipairs({{12.2,135.1},{0,100},{200,100},{-5,100},{0,0}})do
 local a=baseline();local b=fixture();local d={level=1,coins=0,xp=0,xpNext=103,health=sample[1],maxHealth=sample[2]}
 a.apply(d,1000);b.apply(d,1000);compare(a,b)
end
data={level=100,coins=7,xp=0,xpNext=0,health=100,maxHealth=100}
local h={Health=12.2,MaxHealth=135.1};old.humanoid(h);current.humanoid(h)
for _,sample in ipairs({{12.2,135.1},{0,135.1},{200,135.1},{-5,135.1},{0,0},{135,135},{.01,240},{240,240}})do
 h.Health=sample[1];h.MaxHealth=sample[2];old.apply(data,1000);current.apply(data,1000);compare(old,current)
 local textWrites,sizeWrites=current.health.writes.Text,current.hf.writes.Size
 old.refresh();current.refresh();check(current.health.writes.Text==textWrites and current.hf.writes.Size==sizeWrites,'Unchanged health rewrote UI')
end
h.Health=0;old.refresh();current.refresh();old.humanoid(nil,false);current.humanoid(nil,false)
old.apply(data,320);current.apply(data,320);compare(old,current);check(current.health.Text=='0/240' and current.hf.Size.X.Scale==0,'Character gap resurrected dead health')
old.humanoid(nil,true);current.humanoid(nil,true);old.refresh();current.refresh();compare(old,current)
h={Health=90.5,MaxHealth=180};old.humanoid(h);current.humanoid(h);old.refresh();current.refresh();compare(old,current)
for _,width in ipairs({320,355,356,819,820,1920})do
 for _,touch in ipairs({false,true})do for _,dev in ipairs({false,true})do for _,visible in ipairs({false,true})do
  old.place(width,touch,dev,218,visible);current.place(width,touch,dev,218,visible)
  check(equal(old.hud.Position,current.hud.Position) and old.hud.Visible==current.hud.Visible,'HUD placement/visibility changed')
 end end end
 old.frame(width);current.frame(width);compare(old,current)
 local before=current.xp.writes.Text;current.frame(width);check(current.xp.writes.Text==before,'Unchanged frame XP rewrote UI')
end
local function rect(node)
 if node==current.hud then return {x=0,y=0,w=242,h=94}end
 local parent=rect(node.Parent);local size,pos=node.Size,node.Position
 return {x=parent.x+pos.X.Scale*parent.w+pos.X.Offset,y=parent.y+pos.Y.Scale*parent.h+pos.Y.Offset,w=size.X.Scale*parent.w+size.X.Offset,h=size.Y.Scale*parent.h+size.Y.Offset}
end
check(equal(old.hud.Size,current.hud.Size) and current.hud.Size.X.Offset==242 and current.hud.Size.Y.Offset==94 and old.hud.BackgroundTransparency==current.hud.BackgroundTransparency,'HUD outer allocation changed')
check(#current.nodes<=#old.nodes+8,'HUD decoration allocation grew unexpectedly')
for _,node in ipairs(current.nodes)do
 check(node.ClassName=='Frame' or node.ClassName=='TextLabel' or node.ClassName=='UICorner' or node.ClassName=='UIStroke' or node.ClassName=='UIGradient' or node.ClassName=='UITextSizeConstraint','HUD added input/asset/independent object')
 if node.ClassName=='Frame' or node.ClassName=='TextLabel'then
  check(not node.Active and not node.Selectable,'Passive HUD captures input')
  local r=rect(node);check(r.x>=0 and r.y>=0 and r.x+r.w<=242.001 and r.y+r.h<=94.001,'HUD descendant exceeds card bounds')
  if node.ClassName=='TextLabel'then check(node.TextSize>=12,'HUD label below12px')end
 end
end
local badge=current.stats.Parent;local level=rect(badge);local coin=rect(current.coins);local hp=rect(current.health);local track=rect(current.hf.Parent);local xp=rect(current.xp);local xpTrack=rect(current.xf.Parent)
check(badge.Name=='LevelBadge' and badge.Interactable==false and current.coins.Interactable==false,'New header is not passive')
check(level.w==82 and level.h==24 and coin.w==128 and coin.h==24 and coin.x-(level.x+level.w)>=8,'Level/currency header lane changed')
check(current.stats.TextXAlignment==2 and current.stats.TextColor3.R~=current.coins.TextColor3.R and current.coins.TextXAlignment==3 and not current.coins.TextWrapped,'Level/currency hierarchy changed')
check(hp.w==204 and hp.h==18 and current.health.TextSize==14 and track.w==218 and track.h==8 and track.y>=hp.y+hp.h+1,'Health value/track lanes overlap or shrank')
check(xp.w==204 and xp.h==19 and current.xp.TextSize==12 and xp.y>=track.y+track.h+2 and xpTrack.y>=xp.y+xp.h+2,'XP warning lane shrank or overlaps health')
check(current.xp.TextScaled==true,'XP warning label does not scale to fit')
local xpConstraint
for _,node in ipairs(current.nodes)do
 if node.ClassName=='UITextSizeConstraint' and node.Parent==current.xp then xpConstraint=node end
end
check(xpConstraint and xpConstraint.MaxTextSize==12 and xpConstraint.MinTextSize==9,'XP warning text size constraint missing or misbounded')
check(equal(old.hf.BackgroundColor3,current.hf.BackgroundColor3) and equal(old.xf.BackgroundColor3,current.xf.BackgroundColor3),'Health/XP semantic colors changed')
print('PASS',checks,'actual HUD/baseline/data/geometry/passive assertions; mocked replication/allocations, native fit separate')
'''


def pieces(source):
    hud = source[source.index('local hud=frame('):source.index('local zone=label(', source.index('local hud=frame('))]
    progress = source[source.index('local function progressLabel('):source.index('connectClient(remotes.State', source.index('local function progressLabel('))]
    start = source.index(' refreshQuestObjects();stats.Text=')
    update = source[start:source.index(' zone.Text=', start)]
    position = next(line for line in source.splitlines() if line.strip().startswith('hud.Position='))
    visible = next(line for line in source.splitlines() if line.strip().startswith('hud.Visible='))
    start = source.index(' local progress=progressLabel(viewport.X<820)')
    frame = source[start:source.index(' -- Consume every observed input interruption', start)]
    return hud, progress, update, position, visible, frame


def fixture(source, name):
    hud, progress, update, position, visible, frame = pieces(source)
    helpers = source[source.index('local function frame(parent,'):source.index('local function button(parent,')]
    art = source[source.index('local academy={}'):source.index('-- Original, static menu glyphs.')]
    colors = next(line for line in source.splitlines() if line.startswith('local dark='))
    return SETUP.replace('local function fixture()', 'local function ' + name + '()') + colors + '\n' + helpers + art + hud + progress + TAIL.replace('STATE_UPDATE', update).replace('FRAME_UPDATE', frame).replace('POSITION', position).replace('VISIBILITY', visible)


def run(source, baseline, expected=None):
    first = fixture(baseline, 'baseline')
    first = first.replace('f.coins=coins', 'f.coins=nil')
    second = fixture(source, 'fixture')
    second = second[second.index('local function fixture()'):]
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', prefix='tmp_hud_read_', dir=ROOT / 'tests', delete=False) as f:
        path = Path(f.name)
        f.write(first + second + CHECKS)
    try:
        result = subprocess.run(['luau', str(path)], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=30)
    finally:
        path.unlink()
    output = result.stdout + result.stderr
    if expected:
        assert result.returncode and expected in output, output
        print('PASS control:', expected)
    else:
        assert result.returncode == 0, output
        print(output.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    source = (ROOT / PATH).read_text(encoding='utf-8-sig')
    baseline = subprocess.check_output(['git', 'show', BASE + ':' + PATH], cwd=ROOT, text=True, encoding='utf-8')
    run(source, baseline)
    if args.negative_controls:
        cases = [
            ('humanoid and humanoid.Health or data.health or maximum', 'data.health or maximum', 'Health authority/fraction/rounding changed'),
            ('if not humanoid and displayedHealth~=nil then return end', 'if false then return end', 'Health authority/fraction/rounding changed'),
            ('math.ceil(current),math.ceil(maximum)', 'math.floor(current),math.floor(maximum)', 'Health authority/fraction/rounding changed'),
            ('current==displayedHealth and maximum==displayedMaximum', 'false', 'Unchanged health rewrote UI'),
            ('coins.Text=data.coins.." coins"', 'coins.Text=math.floor(data.coins/1000).." coins"', 'Exact level/coin values changed'),
            ('data.level>=Config.MaxLevel and 1 or data.xp/data.xpNext', 'data.xp/data.xpNext', 'XP arithmetic/warning precedence changed'),
            ('if data.recoveryWarning and not data.testSession then', 'if false then', 'XP arithmetic/warning precedence changed'),
            ('levelBadge.Interactable=false', 'levelBadge.Interactable=true', 'New header is not passive'),
            ('UDim2.fromOffset(218,8),UDim2.fromOffset(12,51)', 'UDim2.fromOffset(218,8),UDim2.fromOffset(12,45)', 'Health value/track lanes overlap or shrank'),
            ('UDim2.new(1,-38,0,19),UDim2.fromOffset(26,61)', 'UDim2.new(1,-38,0,14),UDim2.fromOffset(26,61)', 'XP warning lane shrank or overlaps health'),
            ('UDim2.fromOffset(128,24),UDim2.fromOffset(102,8)', 'UDim2.fromOffset(150,24),UDim2.fromOffset(102,8)', 'HUD descendant exceeds card bounds'),
            ('xpText.TextScaled=true', 'xpText.TextScaled=false', 'XP warning label does not scale to fit'),
            ('xpScale.MaxTextSize=12;xpScale.MinTextSize=9', 'xpScale.MaxTextSize=10;xpScale.MinTextSize=9', 'XP warning text size constraint missing or misbounded'),
            ('xpScale.Parent=xpText', 'xpScale.Parent=hud', 'XP warning text size constraint missing or misbounded'),
        ]
        for old, new, expected in cases:
            assert source.count(old) == 1, old
            run(source.replace(old, new), baseline, expected)


if __name__ == '__main__':
    main()

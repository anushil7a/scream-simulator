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
 function f.place(width,touch,dev,height,visible,viewportHeight)
  local viewport={X=width,Y=viewportHeight or 700};local miniLayout={height=height};local gameplayVisible=visible;data.devAccess=dev
POSITION
STATUS_LAYOUT
VISIBILITY
 end
 function f.humanoid(h,present)if present==false then p.Character=nil else p.Character={FindFirstChildOfClass=function()return h end}end end
 function f.refresh()refreshHealth()end
 f.hud=hud;f.health=health;f.hf=hf;f.xp=xpText;f.xf=xf;f.stats=stats;f.coins=coins;f.incoming=academy.incomingHit
ACTIONS_LAYOUT
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
 if node==current.hud then return {x=0,y=0,w=node.Size.X.Offset,h=node.Size.Y.Offset}end
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
current.place(567,true,false,0,true,242)
check(current.hud.Size.X.Offset==218 and current.hud.Size.Y.Offset==78,'Short touch card retained full footprint')
compare(old,current)
for _,node in ipairs(current.nodes) do
 if node.ClassName=='Frame' or node.ClassName=='TextLabel' then
  local r=rect(node)
  check(r.x>=0 and r.y>=0 and r.x+r.w<=218.001 and r.y+r.h<=78.001,'Compact descendant outside status card')
 end
end
level,coin,hp,track,xp,xpTrack=rect(badge),rect(current.coins),rect(current.health),rect(current.hf.Parent),rect(current.xp),rect(current.xf.Parent)
local incoming=rect(current.incoming)
check(coin.x>=level.x+level.w+6 and incoming.x>=hp.x+hp.w+4,'Compact header or HP overlaps another label')
check(track.y>hp.y+hp.h and xp.y>track.y+track.h and xpTrack.y>xp.y+xp.h,'Compact rows overlap')
for _,sample in ipairs({{567,true,300},{390,true,700},{567,false,242}}) do
 current.place(sample[1],sample[2],false,0,true,sample[3])
 check(current.hud.Size.X.Offset==242 and current.hud.Size.Y.Offset==94 and rect(current.coins).w==128,'Standard status card did not restore')
end
local function relative(node,parent)
 local pos,size=node.Position,node.Size
 return {x=parent.x+pos.X.Scale*parent.w+pos.X.Offset,y=parent.y+pos.Y.Scale*parent.h+pos.Y.Offset,w=size.X.Offset,h=size.Y.Offset}
end
local function overlaps(a,b)
 return a.x<b.x+b.w and b.x<a.x+a.w and a.y<b.y+b.h and b.y<a.y+a.h
end
for _,size in ipairs({{492,150},{509,162},{509,204},{509,205},{509,220},{566,238},{566,239},{566,244},{620,259},{620,298},{666,374},{390,700}}) do
 local width,height=table.unpack(size)
 local root={x=0,y=0,w=width,h=height}
 local controls,cast,dodge,sprint,test,stacked,glyph,talk=current.actions(width,height,true)
 local cluster=relative(controls,root)
 cast,dodge,sprint,test=relative(cast,cluster),relative(dodge,cluster),relative(sprint,cluster),relative(test,root)
 check(stacked==(height<239) and glyph.Visible==not stacked,'Short touch action mode or glyph did not restore')
 local typicalJump={x=width-95,y=height-90,w=70,h=70}
 local guideStart=160
 local guide={x=16,y=guideStart,w=290,h=50}
 if stacked then
  talk=relative(talk,root)
  check(talk.x>=0 and talk.y>=0 and talk.x+talk.w<=width and talk.y+talk.h<=height and talk.w>=44 and talk.h>=44 and not overlaps(talk,typicalJump) and not overlaps(talk,test),'Compact TALK has no safe target')
 end
 for _,item in ipairs({cast,dodge,sprint}) do
  check(item.x>=0 and item.y>=0 and item.x+item.w<=width and item.y+item.h<=height and item.h==44 and item.w>=44,'Touch action clipped or undersized')
  check(not overlaps(item,typicalJump),'Touch actions overlap the sampled Jump rectangle')
  check(not overlaps(item,test),'Test Tools overlaps a combat control')
  if stacked and height>=205 then
   check(not overlaps(item,guide),'Stack overlaps the training guide')
  end
  if stacked then check(not overlaps(item,talk),'Stack overlaps the compact TALK button') end
 end
 check(not overlaps(cast,dodge) and not overlaps(cast,sprint) and not overlaps(dodge,sprint),'Touch combat buttons overlap')
 check(cluster.w==(stacked and 140 or height<300 and 196 or 260),'Compact touch controls occupy the ordinary combat width')
end
for _,size in ipairs({{491,162},{510,149}}) do
 local controls,_,_,_,_,stacked=current.actions(size[1],size[2],true)
 check(not stacked and controls.Size.X.Offset==260,'Compact layout was forced below its supported dimensions')
end
local desktop,_,dodge,sprint,_,stacked=current.actions(567,242,false)
check(not stacked and desktop.Position.X.Offset==-274 and desktop.Position.Y.Offset==-102 and dodge.Size.Y.Offset==32 and sprint.Size.X.Offset==144,'Desktop action geometry changed')
print('PASS',checks,'actual HUD/baseline/data/geometry/passive assertions; mocked replication/allocations, native fit separate')
'''


def pieces(source):
    hud = source[source.index('local hud=frame('):source.index('local zone=label(', source.index('local hud=frame('))]
    progress = source[source.index('local function progressLabel('):source.index('connectClient(remotes.State', source.index('local function progressLabel('))]
    start = source.index(' refreshQuestObjects();stats.Text=')
    xp_update = source.index(' xpText.Text=progressLabel(', start)
    update = source[start:source.index('\n', xp_update)]
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
    status_layout = ''
    layout_call = next((line for line in source.splitlines() if line.strip().startswith('academy.layoutStatusCard(')), None)
    if layout_call:
        short = next(line for line in source.splitlines() if 'local shortLandscape=' in line)
        status_layout = short + '\n' + layout_call
    actions = ''
    if 'function academy.layoutActions(' in source:
        start = source.index('function academy.layoutActions(')
        layout = source[start:source.index('\nlocal talkTarget', start)]
        launcher = source[source.index(' local splitTalkLane='):source.index('\n hud.Position=', source.index(' local splitTalkLane='))]
        talk_size = next(line for line in source.splitlines() if line.startswith(' talkButton.Size='))
        talk_start = source.index(' if academy.stackedTouchActions then')
        talk_layout = source[talk_start:source.index('\n for _,passive',talk_start)]
        actions = '''
 local mark={}
 local castButton={Position=UDim2.fromOffset(0,0),FindFirstChild=function()return mark end}
 local dodgeButton,sprintButton,testButton,sustainedControl={},{},{},{}
 local miniMapButton,miniMapHolder,miniMapAvailable={},{},false
 local talkButton,noticeView,noticeLayout={}, {visible=false}, {}
''' + layout + '''
 function f.actions(width,height,touch)
  local viewport={X=width,Y=height}
  local stackedActions=academy.layoutActions(viewport,touch,height<300 and width>height)
  local CityMap={MiniLayout=function()return {available=height>=315,width=90,height=44}end}
''' + '\n do\n' + launcher + '\n' + talk_size + '\n end\n' + talk_layout + '''
  return controls,castButton,dodgeButton,sprintButton,testButton,stackedActions,mark,talkButton
 end
'''
    return SETUP.replace('local function fixture()', 'local function ' + name + '()') + colors + '\n' + helpers + art + hud + progress + TAIL.replace('STATE_UPDATE', update).replace('FRAME_UPDATE', frame).replace('POSITION', position).replace('STATUS_LAYOUT',status_layout).replace('VISIBILITY', visible).replace('ACTIONS_LAYOUT', actions)


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
            ('compact and 46 or 51', 'compact and 46 or 45', 'Health value/track lanes overlap or shrank'),
            ('compact and 15 or 19', 'compact and 15 or 14', 'XP warning lane shrank or overlaps health'),
            ('compact and 120 or 128', 'compact and 120 or 150', 'HUD descendant exceeds card bounds'),
            ('xpText.TextScaled=true', 'xpText.TextScaled=false', 'XP warning label does not scale to fit'),
            ('xpScale.MaxTextSize=12;xpScale.MinTextSize=9', 'xpScale.MaxTextSize=10;xpScale.MinTextSize=9', 'XP warning text size constraint missing or misbounded'),
            ('xpScale.Parent=xpText', 'xpScale.Parent=hud', 'XP warning text size constraint missing or misbounded'),
            ('academy.layoutStatusCard(touch and shortLandscape)', 'academy.layoutStatusCard(false)', 'Short touch card retained full footprint'),
            ('stacked and UDim2.new(1,-width-106,0,6)', 'stacked and UDim2.new(1,-width-106,1,-195)', 'Touch action clipped or undersized'),
            (' and viewport.X>=492 and viewport.Y>=150', '', 'Compact layout was forced below its supported dimensions'),
            ('stacked and UDim2.new(1,-width-106,0,6)', 'stacked and UDim2.new(1,-width-106,0,math.max(0,viewport.Y-156))', 'Stack overlaps the training guide'),
            ('or UDim2.new(1,-98,0,50)', 'or UDim2.new(1,-246,0,50)', 'Stack overlaps the compact TALK button'),
            ('UDim2.new(1,-102,0,0)', 'UDim2.new(1,-102,0,60)', 'Compact TALK has no safe target'),
            ('talkButton.Position=viewport.Y<205 and', 'talkButton.Position=splitTalkLane and', 'Compact TALK has no safe target'),
            ('splitTalkLane and 44 or stackedActions and 84 or 120', 'splitTalkLane and 40 or stackedActions and 84 or 120', 'Compact TALK has no safe target'),
            ('stackedActions and 84 or viewport.X<432', 'stackedActions and 112 or viewport.X<432', 'Test Tools overlaps a combat control'),
        ]
        for old, new, expected in cases:
            assert source.count(old) == 1, old
            run(source.replace(old, new), baseline, expected)


if __name__ == '__main__':
    main()

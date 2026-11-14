"""Actual map constructors and legacy differential; mock UI values, not native text fit/visual evidence.
Historical comparison requires local Git 5622daa; never fetches history.
"""
from pathlib import Path
import ast,subprocess,tempfile,sys,re
R=Path(__file__).resolve().parents[1];PATH='src/StarterPlayer/StarterPlayerScripts/CityMap.luau'
source=(R/PATH).read_text(encoding='utf8')
try:baseline=subprocess.check_output(['git','show','5622daa:'+PATH],cwd=R,text=True,encoding='utf8',stderr=subprocess.PIPE)
except subprocess.CalledProcessError as exc:raise SystemExit('Required local baseline 5622daa unavailable; no fetch attempted.') from exc
layout=(R/'src/ReplicatedStorage/Shared/CompactLayout.luau').read_text(encoding='utf8')
client=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf8')
# Capture the actual nested card/holder dimensions, not a convenient fixed map size.
modal_cap,modal_margin=map(int,re.search(r'local width=math.min\((\d+),viewport.X-(\d+)\)',client).groups())
content_margin=int(re.search(r'content.Size=UDim2.new\(1,-(\d+),1,',client).group(1))
card_margin=int(re.search(r'frame\(content,"Card",UDim2.new\(1,-(\d+),0,height\)',client).group(1))
map_branch=client[client.index(' elseif selected=="Map" then'):client.index('  title.Text="SETTINGS & CONTROLS"',client.index(' elseif selected=="Map" then'))]
card_height=int(re.search(r'local c=card\((\d+)\)',map_branch).group(1))
holder_x,holder_y=map(int,re.search(r'"MapHolder",UDim2.new\(1,-(\d+),1,-(\d+)\)',map_branch).groups())
tree=ast.parse((R/'tests/minimap.py').read_text(encoding='utf8'))
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
setup=setup[:setup.index('local Config=')]
def module(s):return s[s.index('local CityMap={}'):]
def build(s):
 return setup+f'local modalCap,modalMargin,contentMargin,cardMargin,cardHeight,holderX,holderY={modal_cap},{modal_margin},{content_margin},{card_margin},{card_height},{holder_x},{holder_y}\n'+"local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}\nlocal Layout=(function()\n"+layout+"\nend)()\n"+r'''
local function environment(compact)
 local Config={CompactCity=compact,MapMin=Layout.BoundsMin,MapMax=Layout.BoundsMax,ZoneMin=compact and Layout.ZoneMin or {X=-480,Z=-360},ZoneMax=compact and Layout.ZoneMax or {X=480,Z=360}}
 local game={GetService=function()return {WaitForChild=function()return {WaitForChild=function(_,name)return name end}end}end}
 local require=function(name)assert(name=='CompactLayout');return Layout end
 return Config,game,require
end
local function old(compact)local Config,game,require=environment(compact)
'''+module(baseline)+r'''
end
local function current(compact)local Config,game,require=environment(compact)
'''+module(s)+r'''
end
local function serial(v,ids)
 if type(v)~='table'then return tostring(v)end
 if ids and ids[v]then return '@'..ids[v]end
 local keys={};for k in pairs(v)do table.insert(keys,k)end;table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 local out={};for _,k in ipairs(keys)do table.insert(out,tostring(k)..'='..serial(v[k],ids))end;return '{'..table.concat(out,';')..'}'
end
local function capture(m,mini)
 local root={};local start=#objects;local view=m.create(root,mini);local ids={[root]='root'}
 for i=start+1,#objects do ids[objects[i]]=i-start end
 local out={};for i=start+1,#objects do local node={};for k,v in pairs(objects[i])do node[k]=v end;table.insert(out,serial(node,ids))end
 return table.concat(out,'\n'),view
end
local function find(parent,name)for _,o in ipairs(objects)do if o.Parent==parent and o.Name==name then return o end end end
for _,mini in ipairs({false,true})do
 local a,b=old(false),current(false);local x=capture(a,mini);local y=capture(b,mini)
 check(x==y,'Legacy constructed geometry/labels changed')
 check(a.legend==b.legend and a.legendHeight==b.legendHeight and a.mapHelp==b.mapHelp,'Legacy copy changed')
end
local m=current(true);local _,full=capture(m,false);local _,mini=capture(m,true)
local labels={'L1','L25','L60'};local colors={{111,196,180},{219,120,94},{240,192,89}}
for i=1,3 do
 local id='TrainingPad'..i;local spec
 for _,p in ipairs(Layout.PartSpecs)do if p.id==id then spec=p end end
 check(spec~=nil,'Authored pad missing')
 for _,view in ipairs({full,mini})do
  local f=find(view.map,'Footprint_'..id);check(f~=nil,'Pad footprint missing')
  check(serial(f.BackgroundColor3)==serial(spec.color),'Pad color not world-derived')
  check(near(f.Position.X.Scale,(spec.position.X-spec.size.X/2+360)/720) and near(f.Position.Y.Scale,(spec.position.Z-spec.size.Z/2+300)/600),'Pad projection changed')
  check(near(f.Size.X.Scale,spec.size.X/720) and near(f.Size.Y.Scale,spec.size.Z/600),'Pad dimensions changed')
 end
 local badge=find(full.map,'TrainingTier_'..id);check(badge~=nil,'Full tier badge missing')
 check(not find(mini.map,'TrainingTier_'..id),'Mini tier text added')
 check(serial(badge.BackgroundColor3)==serial(colors[i]),'Uniform accent incorrect')
 check(near(badge.Position.X.Scale,(spec.position.X+360)/720) and near(badge.Position.Y.Scale,(spec.position.Z+300)/600),'Tier center projection changed')
 check(badge.AnchorPoint.Y==.5 and badge.Size.X.Offset==36 and badge.Size.Y.Offset==20,'Tier badge bounds changed')
 local text;for _,o in ipairs(objects)do if o.Parent==badge and o.ClassName=='TextLabel'then check(text==nil,'Duplicate tier text');text=o end end
 check(text and text.Text==labels[i] and text.TextSize==12,'Tier label incorrect')
 check(text.Position.X.Offset==8 and text.Position.Y.Offset==0 and text.Size.X.Scale==1 and text.Size.X.Offset==-8 and text.Size.Y.Scale==1 and text.Size.Y.Offset==0,'Tier text inset missing')
 check(text.Position.X.Offset+text.Size.X.Scale*badge.Size.X.Offset+text.Size.X.Offset==36 and text.Size.X.Scale*badge.Size.X.Offset+text.Size.X.Offset==28,'Tier text lane outside badge')
 check(text.Font==Enum.Font.GothamBold and serial(text.TextColor3)==serial({22,39,46}),'Tier label contrast changed')
 -- Recorded Studio36bb samples, not universal font metrics: after/full-1-2.json
 -- SHA256 1c33b4b30151bbfe35f5a7a4fe75d4bfdcd4438a54e54b7c8ce1694a0d963656.
 -- full-1-3/full-1-4 confirm the same sizes with player at Brawler/Elite centers.
 local sampleWidth=({9.600000381469727,19.200000762939453,20})[i];local sampleHeight=12
 local laneWidth=text.Size.X.Scale*badge.Size.X.Offset+text.Size.X.Offset
 local glyphLeft=text.Position.X.Offset+(laneWidth-sampleWidth)/2
 check(sampleWidth<=laneWidth and sampleHeight<=badge.Size.Y.Offset,'Recorded glyph sample does not fit text lane')
 check(glyphLeft-full.dot.Size.X.Offset/2>=2,'Recorded glyph sample touches centered player dot')

 check(badge.ZIndex==3 and text.ZIndex==4 and full.dot.ZIndex==5,'Tier occludes player marker')
end
check(not find(full.map,'Landmark2'),'Generic Training pin retained')
for i,v in ipairs(Layout.MapLandmarks)do if i~=2 then
 local pin=find(full.map,'Landmark'..i);check(pin~=nil,'Other landmark removed')
 check(near(pin.Position.X.Scale,(v.x+360)/720) and near(pin.Position.Y.Scale,(v.z+300)/600),'Other landmark moved')
 local text;for _,o in ipairs(objects)do if o.Parent==pin and o.ClassName=='TextLabel'then text=o end end
 check(text and text.Text==tostring(i),'Other landmark renumbered')
end end
check(m.legend:find('Training: L1 Rookie / L25 Brawler / L60 Elite',1,true)~=nil and not m.legend:find('2 Training',1,true),'Tier legend ambiguous')
check(m.legendHeight==old(true).legendHeight,'Legend height changed')
-- Resolve scale and native size constraints using actual Client allocations.
-- This models rectangles, not Studio rounding/font rasterization.
local function markerSize(o,width,height)
 local w,h=o.Size.X.Scale*width+o.Size.X.Offset,o.Size.Y.Scale*height+o.Size.Y.Offset
 for _,child in ipairs(objects)do if child.Parent==o and child.ClassName=='UISizeConstraint'then
  w=math.clamp(w,child.MinSize.X,child.MaxSize.X);h=math.clamp(h,child.MinSize.Y,child.MaxSize.Y)
 end end
 return w,h
end
for _,viewportWidth in ipairs({320,321,340,360,385,386,390,640,1280,320})do
 local holderWidth=math.min(modalCap,viewportWidth-modalMargin)-contentMargin-cardMargin-holderX
 local holderHeight=cardHeight-holderY
 local width=math.min(holderWidth,holderHeight*m.aspectRatio);local height=width/m.aspectRatio
 local rectangles={}
 for _,o in ipairs(objects)do if o.Parent==full.map and o.Name and (o.Name:find('TrainingTier_',1,true)==1 or o.Name:find('Landmark',1,true)==1)then
  local anchor=o.AnchorPoint;local w,h=markerSize(o,width,height)
  if o.Name:find('Landmark',1,true)==1 then
   check(w>=18 and w<=23 and near(w,h),'Numbered pin size outside legible square bounds')
   if viewportWidth==320 then check(near(w,18),'Narrow numbered pin did not compact')end
   if viewportWidth>=390 then check(near(w,23),'Desktop numbered pin size changed')end
   for _,label in ipairs(objects)do if label.Parent==o and label.ClassName=='TextLabel'then
    check(label.TextSize==13 and not label.TextScaled,'Numbered glyph size changed')
    -- Historical Studio GothamBold digits measured <=8 x 12.800001px.
    check(w>=8+4 and h>=12.800001+4,'Recorded numbered glyph lacks padding')
   end end
  end
  local x=o.Position.X.Scale*width+(o.Position.X.Offset or 0)-anchor.X*w
  local y=o.Position.Y.Scale*height+(o.Position.Y.Offset or 0)-anchor.Y*h
  check(x>=0 and y>=0 and x+w<=width and y+h<=height,'Static marker outside fitted map')
  table.insert(rectangles,{name=o.Name,x=x,y=y,w=w,h=h})
 end end
 for i,a in ipairs(rectangles)do for j=i+1,#rectangles do local b=rectangles[j]
  check(a.x+a.w+2<=b.x or b.x+b.w+2<=a.x or a.y+a.h+2<=b.y or b.y+b.h+2<=a.y,'Static marker overlaps another marker: '..a.name..' / '..b.name..' at '..viewportWidth)
 end end
end

local total=#objects;local root={Parent={},Position={X=-245,Z=-100},CFrame={LookVector={X=0,Z=-1}}}
for i=1,120 do m.update(full,root);m.MiniUpdate(mini,root,i/60,true)end
check(#objects==total,'Update allocated map art')
m.MiniUpdate(mini,root,3,false);check(not mini.dot.Visible,'Hidden minimap retained dot')
m.update(full,nil);check(not full.dot.Visible,'Missing player retained dot')
print('PASS '..checks..' actual training-map/legacy assertions; mock UI only')
'''
def contracts(s):
 for a,b in [('local function position(', 'local CompactLayout='),('function CityMap.update(',"CityMap.legend='")]:
  assert s[s.index(a):s.index(b)]==baseline[baseline.index(a):baseline.index(b)],'Projection/layout/cadence contract changed'
def run(s):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(build(s));p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],text=True,capture_output=True,timeout=15)
 finally:p.unlink()
if __name__=='__main__':
 contracts(source);print('PASS 2 unchanged projection/layout/update source contracts')
 out=run(source);print(out.stdout,end='');assert out.returncode==0,out.stderr
 if '--negative-controls' in sys.argv:
  cases=[('training and part.color','training and Color3.fromRGB(87,144,137)','Pad color not world-derived'),('label="L25"','label="L1"','Tier label incorrect'),('if tier and not compact then','if tier then','Mini tier text added'),('if CompactLayout and v.name=="2 Training" then continue end','','Generic Training pin retained'),('badge.Position=position(part.position.X,part.position.Z)','badge.Position=position(part.position.X+10,part.position.Z)','Tier center projection changed'),('words.Position=UDim2.fromOffset(8,0);words.Size=UDim2.new(1,-8,1,0)','words.Position=UDim2.fromOffset(0,0);words.Size=UDim2.new(1,0,1,0)','Tier text inset missing'),('badge.AnchorPoint=Vector2.new(0,.5)','badge.AnchorPoint=Vector2.new(.5,.5)','Static marker overlaps another marker'),('size.MinSize=Vector2.new(18,18)','size.MinSize=Vector2.new(23,23)','Narrow numbered pin did not compact'),('size.MinSize=Vector2.new(18,18)','size.MinSize=Vector2.new(1,1)','Numbered pin size outside legible square bounds'),('size.MaxSize=Vector2.new(23,23)','size.MaxSize=Vector2.new(40,40)','Numbered pin size outside legible square bounds'),("text(pin,tostring(i),13)","text(pin,tostring(i),CompactLayout and 10 or 13)",'Numbered glyph size changed')]
  for a,b,reason in cases:
   assert a in source,a;out=run(source.replace(a,b));assert out.returncode and reason in out.stderr,(reason,out.stdout,out.stderr)
  print('PASS '+str(len(cases))+' training-map negative controls')

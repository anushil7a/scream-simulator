"""Actual static tab icons, registration and layout; synthetic metrics, not native font/input evidence."""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
source=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
def build(c):
 helpers=c[c.index('local academy={}'):c.index('local top=frame(')]
 a=c.index('for i,name in ipairs({"Shop","Screams","Quests","Style","Map","Settings"}) do tabs')
 register=c[a:c.index('local conversationNPC',a)]
 a=c.index(' local columns=width<620');layout=c[a:c.index(' content.Position=',a)]
 selection=next(x for x in c.splitlines() if 'for name,b in pairs(tabs) do b.BackgroundColor3=' in x)
 return SETUP+helpers+'\n'+register+'\nlocal function layout(width) local tabY=88\n'+layout+'\nend\nlocal function select(name) selected=name\n'+selection+'\nend\n'+CHECKS
SETUP=r'''
local made={};local Instance={new=function(class)local o={ClassName=class,PaddingLeft={Scale=0,Offset=0},PaddingRight={Scale=0,Offset=0}};table.insert(made,o);return o end}
local UDim={new=function(s,o)return {Scale=s,Offset=o}end}
local UDim2={new=function(a,b,c,d)return {X={Scale=a,Offset=b},Y={Scale=c,Offset=d}}end,fromOffset=function(x,y)return {X={Scale=0,Offset=x},Y={Scale=0,Offset=y}}end,fromScale=function(x,y)return {X={Scale=x,Offset=0},Y={Scale=y,Offset=0}}end}
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local Color3={new=function(r,g,b)return tostring(r)..','..g..','..b end,fromRGB=function(r,g,b)return tostring(r)..','..g..','..b end}
local ColorSequence={new=function(a,b)return {a,b}end}
local Enum={ApplyStrokeMode={Border='Border'},TextXAlignment={Right='Right',Center='Center',Left='Left'}}
local metrics=1;local TextService={GetTextSize=function(_,text,size,font,bounds)return {X=#text*size*.55*metrics,Y=size}end}
local gold='gold';local muted='muted';local panel='panel';local white='white'
local modal={Visible=true};local tabs={};local selected='Shop';local clientDestroyed=false;local renders=0
local function render()renders+=1 end
local function button(parent,name,text,size,pos,callback)
 local b={Name=name,Text=text,Size=size,Position=pos,callback=callback,Font='font',TextSize=14,ZIndex=1,Parent=parent};return b
end
local n=0;local function check(v,m)assert(v,m);n+=1 end
'''
CHECKS=r'''
local names={'Shop','Screams','Quests','Style','Map','Settings'}
local signatures={};local totalFrames=0
for _,name in ipairs(names)do
 local b=tabs[name];check(b~=nil and b.Text==(name=='Screams' and 'BEAMS' or string.upper(name)),'Tab label changed')
 local icons={};for _,o in ipairs(made)do if o.Parent==b and o.ClassName=='Frame' then table.insert(icons,o)end end
 check(#icons==1,'Missing or duplicate tab icon');local icon=icons[1]
 check(icon.Size.X.Offset==20 and icon.Size.Y.Offset==20,'Icon bounds changed')
 check(icon.Active==false and icon.Selectable==false and icon.Interactable==false,'Icon intercepts input')
 local signature={};local count=0;icon.minX=0;icon.maxX=20;icon.minY=0;icon.maxY=20
 for _,o in ipairs(made)do if o.Parent==icon and o.ClassName=='Frame' then
  count+=1;totalFrames+=1
  check(o.Active==false and o.Selectable==false and o.Interactable==false,'Glyph intercepts input')
  local x,y,w,h=o.Position.X.Offset,o.Position.Y.Offset,o.Size.X.Offset,o.Size.Y.Offset
  local a=math.rad(o.Rotation or 0);local ex=(math.abs(math.cos(a))*w+math.abs(math.sin(a))*h)/2;local ey=(math.abs(math.sin(a))*w+math.abs(math.cos(a))*h)/2
  icon.minX=math.min(icon.minX,x+w/2-ex);icon.maxX=math.max(icon.maxX,x+w/2+ex);icon.minY=math.min(icon.minY,y+h/2-ey);icon.maxY=math.max(icon.maxY,y+h/2+ey)
  check(icon.minX>=-1e-9 and icon.maxX<=20+1e-9 and icon.minY>=-1e-9 and icon.maxY<=20+1e-9,'Rotated glyph outside slot '..name..' '..o.Name)
  table.insert(signature,table.concat({o.Position.X.Offset,o.Position.Y.Offset,o.Size.X.Offset,o.Size.Y.Offset,o.Rotation or 0},','))
 end end
 check(count>0 and count<=12,'Unbounded or empty glyph')
 table.sort(signature);local key=table.concat(signature,';');check(not signatures[key],'Duplicate semantic silhouette');signatures[key]=name
 local previous=renders;b.callback();check(selected==name and renders==previous+1,'Tab activation changed')
 modal.Visible=false;b.callback();check(renders==previous+1,'Hidden callback activated');modal.Visible=true
 clientDestroyed=true;b.callback();check(renders==previous+1,'Destroyed callback activated');clientDestroyed=false
end
local allocated=#made
for _,viewport in ipairs({320,390,640,820,1280})do
 local width=math.min(720,viewport-24)
 for _,metricScale in ipairs({1,3})do metrics=metricScale
 layout(width)
 for _,name in ipairs(names)do
  local b=tabs[name];local icon,padding
  for _,o in ipairs(made)do if o.Parent==b then if o.ClassName=='Frame'then icon=o elseif o.ClassName=='UIPadding'then padding=o end end end
  check(padding~=nil,'Missing text spacing')
  local textWidth=math.ceil(#b.Text*b.TextSize*.55*metrics)
  local expected=20+6+textWidth+16<=b.Size.X.Offset
  check(icon.Visible==expected,'Incorrect fit fallback')
  check(b.Size.Y.Offset==44,'Input target height changed')
  if expected then
   local x=icon.Position.X.Offset;local right=b.Size.X.Offset-padding.PaddingRight.Offset
   check(x>=8 and right<=b.Size.X.Offset-8,'Icon/text group outside padded bounds')
   check(right-textWidth+1e-9>=x+icon.maxX+6,'Rotated icon violates six-pixel gap')
   check(x+icon.minX>=0 and x+icon.maxX<=b.Size.X.Offset and icon.Position.Y.Scale*44+icon.Position.Y.Offset+icon.minY>=0 and icon.Position.Y.Scale*44+icon.Position.Y.Offset+icon.maxY<=44,'Rotated icon outside button')
  else check(b.TextXAlignment==Enum.TextXAlignment.Center and padding.PaddingLeft.Offset==0 and padding.PaddingRight.Offset==0,'Fallback text not centered')end
 end
 end
end
check(#made==allocated,'Layout allocated new icons')
for _,name in ipairs(names)do select(name);for other,b in pairs(tabs)do check(b.BackgroundColor3==(other==name and Color3.fromRGB(64,93,99) or panel),'Selection highlight changed')end end
print('PASS '..n..' actual icon/registration/layout assertions; synthetic text metrics only')
'''
def run(c):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(build(c));p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],text=True,capture_output=True,timeout=15)
 finally:p.unlink()
if __name__=='__main__':
 out=run(source);print(out.stdout,end='');assert out.returncode==0,out.stderr

 if '--negative-controls' in sys.argv:
  cases=[('shape("EmitterInk",2,5,6,11,ink,-18,2)','shape("EmitterInk",1,5,6,11,ink,-18,2)','Rotated glyph outside slot'),('icon.Visible=fits','icon.Visible=false','Incorrect fit fallback'),('padding.PaddingRight=UDim.new(0,fits and (width-total)/2 or 0)','padding.PaddingRight=UDim.new(0,0)','Icon/text group outside padded bounds'),('name=="Screams" and "BEAMS"','name=="Screams" and "WRONG"','Tab label changed'),('academy.tabIcon(tabs[name],name)','academy.tabIcon(tabs[name],"Shop")','Duplicate semantic silhouette'),('icon.Interactable=false','icon.Interactable=true','Icon intercepts input'),(' local fits=width>=total+16',' local fits=width>=total+16;Instance.new("Frame")','Layout allocated new icons')]
  for old,new,message in cases:
   assert old in source,old
   out=run(source.replace(old,new));assert out.returncode and message in out.stderr,(message,out.stdout,out.stderr)
  print('PASS 7 menu icon negative controls')

"""Actual presentation decorators and authored rectangles; not native font/input evidence."""
from pathlib import Path
import argparse,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
CLIENT=ROOT/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
def build(source):
 a=source.index('local academy={}')
 helpers=source[a:source.index('local top=frame(',a)]
 return SETUP+helpers+CHECKS
SETUP='''local made={}
local Instance={new=function(class)local o={ClassName=class};table.insert(made,o);return o end}
local UDim={new=function(s,o)return {Scale=s,Offset=o}end}
local UDim2={fromOffset=function(x,y)return {X={Scale=0,Offset=x},Y={Scale=0,Offset=y}}end,fromScale=function(x,y)return {X={Scale=x,Offset=0},Y={Scale=y,Offset=0}}end}
local Color3={new=function(r,g,b)return {r,g,b}end,fromRGB=function(r,g,b)return {r/255,g/255,b/255}end}
local ColorSequence={new=function(a,b)return {a,b}end}
local Enum={ApplyStrokeMode={Border='Border'}}
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
'''
CHECKS='''
local parent={};local gold=Color3.fromRGB(235,190,105)
for _,spec in ipairs({{'voice',4},{'health',2},{'progress',3}})do
 local start=#made;local icon=academy.mark(parent,spec[1],UDim2.fromOffset(12,9),18,gold)
 check(icon.Parent==parent and icon.Size.X.Offset==18 and icon.Size.Y.Offset==18,'Icon detached or resized control')
 check(icon.BackgroundTransparency==1 and icon.Active==false and icon.Selectable==false and icon.Interactable==false,'Icon intercepts input')
 local bars=0
 for i=start+2,#made do local o=made[i]
  check(o.ClassName=='Frame' or o.ClassName=='UICorner','Unexpected asset or independent object')
  if o.ClassName=='Frame' then
   bars+=1;check(o.Parent==icon,'Glyph escapes owned icon')
   check(o.Active==false and o.Selectable==false and o.Interactable==false,'Glyph intercepts input')
   check(o.Position.X.Scale>=0 and o.Position.Y.Scale>=0 and o.Position.X.Scale+o.Size.X.Scale<=1 and o.Position.Y.Scale+o.Size.Y.Scale<=1,'Glyph exceeds local bounds')
   check(o.Color==nil and o.BackgroundColor3==gold,'Glyph tint not supplied')
  end
 end
 check(bars==spec[2],'Unexpected icon complexity')
end
local color={};local object={BackgroundColor3=color,Size={},Position={},Active=true,Text='BEAMS: OFF'}
local size,pos=object.Size,object.Position;local n=#made
academy.surface(object,gold)
check(#made==n+2,'Surface allocation not bounded')
check(object.Size==size and object.Position==pos and object.Active==true and object.Text=='BEAMS: OFF' and object.BackgroundColor3==color,'Surface changed control semantics')
check(made[n+1].ClassName=='UIStroke' and made[n+2].ClassName=='UIGradient','Surface inserts layout children')
check(made[n+1].Parent==object and made[n+2].Parent==object,'Surface ownership escaped')
check(made[n+1].ApplyStrokeMode=='Border' and made[n+1].Thickness==1,'Border affects text readability')
check(made[n+2].Rotation==90,'Depth lighting direction changed')
print('PASS '..checks..' actual presentation decorator assertions')
'''
def run(source):
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',prefix='tmp_hud_',dir=ROOT/'tests',delete=False)as f:p=Path(f.name);f.write(build(source))
 try:return subprocess.run(['luau',str(p)],cwd=ROOT,capture_output=True,text=True)
 finally:p.unlink()
RETAINED_CONTRACTS=['zone.BackgroundColor3=dark;zone.BackgroundTransparency=.08', 'saveNotice.BackgroundColor3=dark;saveNotice.BackgroundTransparency=.08', 'UDim2.fromOffset(242,94),UDim2.new(0,14,1,-108)', 'local meterText=label(meter,"LIVE MIC 0%\\nHold attack before speaking",UDim2.new(1,-20,0,40),UDim2.fromOffset(10,3),12,white)']
SURFACE_CONTRACTS=['academy.surface(zone)', 'academy.surface(saveNotice,gold)', 'academy.surface(sprintButton)', 'academy.surface(talkButton,gold)', 'academy.surface(conversationPanel,gold)']
def check_contracts(source):
 for c in RETAINED_CONTRACTS+SURFACE_CONTRACTS:assert c in source,c
def main():
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args();source=CLIENT.read_text(encoding='utf-8')
 r=run(source);assert r.returncode==0,r.stdout+r.stderr;print(r.stdout.strip())
 check_contracts(source)
 print(f'PASS {len(RETAINED_CONTRACTS)} retained authored-rectangle/status contracts')
 print(f'PASS {len(SURFACE_CONTRACTS)} HUD/dialogue surface contracts')
 if args.negative_controls:
  cases=[('icon.Interactable=false','icon.Interactable=true','Icon intercepts input'),('f.Active=false','f.Active=true','Glyph intercepts input'),('bar(.74,.26,.12,.48)','bar(.94,.26,.12,.48)','Glyph exceeds local bounds'),('stroke.Thickness=1','stroke.Thickness=5','Border affects text readability')]
  start=source.index('local academy={}')
  end=source.index('-- Original, static menu glyphs.',start);helpers=source[start:end]
  for old,new,diagnostic in cases:
   assert helpers.count(old)==1;result=run(source[:start]+helpers.replace(old,new)+source[end:]);assert result.returncode and diagnostic in result.stderr,result.stdout+result.stderr
  for c in SURFACE_CONTRACTS:
   assert source.count(c)==1
   try:check_contracts(source.replace(c,''))
   except AssertionError as exc:assert c in str(exc),str(exc)
   else:raise AssertionError(f'Negative control did not fail for {c}')
  print(f'PASS {len(cases)+len(SURFACE_CONTRACTS)} targeted negative controls')
if __name__=='__main__':main()

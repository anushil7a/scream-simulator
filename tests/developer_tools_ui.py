"""Actual test-tool button list with synthetic layout/events; no native UI claim."""
from pathlib import Path
import argparse, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8')
start=source.index('local testCommands=')
fragment=source[start:source.index('local testButton=',start)]
visibility=next(line for line in source.splitlines() if 'testButton.Visible=data.devAccess' in line)
setup="""
local checks=0;local function check(ok,message)assert(ok,message);checks+=1 end
local Config={MaxLevel=100};local studio=false;local Run={IsStudio=function()return studio end}
local UDim2={fromOffset=function(x,y)return {X=x,Y=y}end}
local testContent={};local calls={};local buttons={}
local action={FireServer=function(_,verb,arg)table.insert(calls,{verb,arg})end}
local function button(parent,key,text,size,pos,callback)
 buttons[key]={text=text,size=size,pos=pos,call=callback}
end
local function render(isStudio)
 studio=isStudio;buttons={};calls={}
"""
checks="""
end
for _,isStudio in ipairs({false,true}) do
 render(isStudio)
 check(buttons.AddLevels~=nil,'Missing +10 test-level control')
 check(buttons.AddLevels.text=='+10 levels','Wrong +10 label')
 buttons.AddLevels.call()
 check(#calls==1 and calls[1][1]=='DevCommand' and calls[1][2]=='AddLevels','Button sends wrong command or client amount')
 check((buttons.StudioMovement~=nil)==isStudio,'Studio-only movement exposed incorrectly')
 local n=0;for _,b in pairs(buttons)do
  n+=1;check(b.size.X>=44 and b.size.Y>=44,'Test target below minimum touch size')
  check(b.pos.Y+b.size.Y<=testContent.CanvasSize.Y,'Test control outside scroll canvas')
 end
 check(n==(isStudio and 12 or 11),'Existing test tools lost or duplicated')
end
local testButton={Visible=false}
local function update(data)
"""
endchecks="""
end
for _,value in ipairs({false,true,1,'true'})do
 update({devAccess=value});check(testButton.Visible==(value==true),'Test-tools visibility trusts nonboolean access')
end
update({});check(testButton.Visible==false,'Missing authorization leaves test tools visible')
print('PASS '..checks..' actual test-tool UI checks; synthetic geometry and events only')
"""
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:
  path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out
   print('PASS negative control:',expected)
  else:
   print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
 code=setup+fragment+checks+visibility+endchecks
 run(code)
 if args.negative_controls:
  run(code.replace('{"AddLevels","+10 levels"},',''),'Missing +10 test-level control')
  run(code.replace('math.ceil(#testCommands/2)*47','47'),'Test control outside scroll canvas')
  run(code.replace('data.devAccess==true','data.devAccess~=nil'),'Test-tools visibility trusts nonboolean access')

"""Actual test-tool button list with synthetic layout/events; no native UI claim."""
from pathlib import Path
import argparse, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8')
start=source.index('local testCommands=')
fragment=source[start:source.index('\n end\n testContent.XP.Modal=true',start)]
visibility=source[source.index('function academy.canShowTestLauncher()'):source.index('\n-- Flight controls exist only',source.index('function academy.canShowTestLauncher()'))]+'\nacademy.refreshTestLauncher()'
setup="""
local checks=0;local function check(ok,message)assert(ok,message);checks+=1 end
local clientDestroyed=false
local GuiService={MenuIsOpen=false};local modal={Visible=false};local conversationPanel={Visible=false}
local Config={MaxLevel=100};local studio=false;local Run={IsStudio=function()return studio end}
local contentWidth=196
local UDim2={fromOffset=function(x,y)return {X=x,Y=y}end,new=function(xs,x,ys,y)return {X=contentWidth*(xs or 0)+(x or 0),Y=y or 0}end}
local localFlightTools=false
local capability
local data={devAccess=true,testBeamAvailable=true}
local remotes={GetAttribute=function()return capability end}
local academy={}
local testContent={};local calls={};local buttons={}
local action={FireServer=function(_,verb,arg)table.insert(calls,{verb,arg})end}
local function button(parent,key,text,size,pos,callback)
 local b={text=text,size=size,Position=pos,call=callback};buttons[key]=b;return b
end
local function render(isStudio,flight,online)
 capability=online;data.devAccess=true;data.testBeamAvailable=true
 localFlightTools=flight==true;studio=isStudio;buttons={};calls={};academy.testerToolsVisible=nil
"""
capability_helper=source[source.index('function academy.testToolsAllowed()'):source.index('\ndevPanel=frame',source.index('function academy.testToolsAllowed()'))]
setup=setup.replace('local testContent={}',capability_helper+'\nlocal testContent={}')
checks="""
 academy.layoutTestCommands(academy.testToolsAllowed())
end
for _,isStudio in ipairs({false,true}) do
 render(isStudio)
 check(buttons.AddLevels~=nil,'Missing +10 test-level control')
 check(buttons.AddLevels.text=='+10 levels','Wrong +10 label')
 buttons.AddLevels.call()
 check(#calls==1 and calls[1][1]=='DevCommand' and calls[1][2]=='AddLevels','Button sends wrong command or client amount')
 check((buttons.StudioMovement~=nil)==isStudio,'Studio-only movement exposed incorrectly')
 check((buttons.ResetBots~=nil)==isStudio,'Live reset-bots control exposed')
 local n=0;for _,b in pairs(buttons)do
  if b.Visible==false then continue end
  n+=1;check(b.size.X>=44 and b.size.Y>=44,'Test target below minimum touch size')
  check(b.Position.Y+b.size.Y<=testContent.CanvasSize.Y,'Test control outside scroll canvas')
  check(b.Position.X+b.size.X<=contentWidth,'Test control clipped on narrow panel')
 end
 check(n==(isStudio and 12 or 10),'Existing test tools lost or duplicated')
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
render(true,true);check(buttons.Fly.Position.Y==164,'Fly not visible beneath Beam Test');check(buttons.Fly~=nil,'Guarded fixture Fly missing');buttons.Fly.call();check(calls[1][1]=='DevCommand' and calls[1][2]=='Fly','Fly command changed')
render(false,false,true);check(buttons.Fly.Visible and buttons.Fly.Position.Y==164,'Online capability did not add Fly with original Beam spacing')
capability=false;buttons.Fly.call();check(#calls==0,'Queued Fly dispatched after capability revoke')
academy.layoutTestCommands(academy.testToolsAllowed());check(not buttons.Fly.Visible and buttons.XP.Position.Y==0,'Revoke did not restore original normal-command layout')
for _,v in ipairs({false,1,'true'})do render(false,false,v);check(not buttons.Fly.Visible,'Malformed/missing online capability showed Fly')end
render(false,false,true);data.devAccess=false;buttons.Fly.call();check(#calls==0,'Fly bypassed per-user State gate')
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
  run(code.replace('math.ceil(index/2)*47','47'),'Test control outside scroll canvas')
  run(code.replace('data.devAccess==true','data.devAccess~=nil'),'Test-tools visibility trusts nonboolean access')

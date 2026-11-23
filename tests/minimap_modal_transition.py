"""Actual Client menu transitions and CityMap hide path, mocked GUI scheduling only."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1]
def assemble(s):
 creation=s[s.index('local miniMapButton='):s.index('local function card(',s.index('local miniMapButton='))]
 helper=s[s.index('function academy.hideMiniMapForMenu()'):s.index('\nlocal function card(',s.index('function academy.hideMiniMapForMenu()'))]
 close=s[s.index('local function closeMenu()'):s.index('\nbutton(modal,"Close"')]
 toggle=s[s.index('local function toggleTab('):s.index('\nlocal shop=button(top,')]
 conversation=s[s.index('showConversation=function(info)'):].splitlines()[1]
 visible=s[s.index(' local miniVisible='):s.index('\nend)',s.index(' local miniVisible='))]
 notice_map=next(line for line in s.splitlines() if line.startswith(' local noticeMap='))
 m=(R/'src/StarterPlayer/StarterPlayerScripts/CityMap.luau').read_text()
 update=m[m.index('function CityMap.MiniUpdate('):m.index('\nCityMap.legend=')]
 return r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local academy={refreshTestLauncher=function()end};local CityMap={update=function(v)v.dot.Visible=true end}
local modal={Visible=false};local conversationPanel={Visible=false};local devPanel={Visible=false}
local miniMapButton={Visible=true};local miniMapHolder={Visible=true}
local miniMapView={map={Parent=true},dot={Visible=true},nextUpdate=5,lastRoot={}}
local miniMapAvailable=true;local windowFocused=true;local gameplayVisible=true
local root={Parent=true};local selected='Shop';local renderRevision=0;local renderedMenuKey
local function hidden(where)check(not miniMapButton.Visible and not miniMapView.dot.Visible,'Minimap leaked before '..where)end
local function clearShop()end
local function cancelCapture()hidden('conversation dispatch')end
local function closeConversation()conversationPanel.Visible=false end
local function render()hidden('modal render')end
local action={FireServer=function()hidden('ShopRefresh dispatch')end}
'''+update+'\n'+helper+'\n'+close+'\n'+toggle+'''
local function frame()
'''+visible+'''
end
local function openConversation()
'''+conversation+'''
end
for _,size in ipairs({'320x568','390x844','844x390','2042x912'})do
 for _,access in ipairs({false,true})do -- map visibility is not developer authorization.
  for i=1,100 do
   modal.Visible=false;conversationPanel.Visible=false;academy.testLauncherBlocked=false
   miniMapAvailable=true;windowFocused=true;gameplayVisible=true;frame()
   check(miniMapButton.Visible and miniMapView.dot.Visible,'Normal minimap did not restore')
   toggleTab('Shop');hidden('first frame');check(miniMapView.nextUpdate==nil and miniMapView.lastRoot==nil,'Hidden marker cache retained')
   -- Model a cached gameplayVisible=true from an earlier point in the same frame.
   frame();hidden('stale frame');toggleTab('Quests');hidden('tab switch')
   closeMenu();frame();check(miniMapButton.Visible,'Close broke ordinary frame restoration')
   toggleTab('Shop');toggleTab('Shop');frame();check(miniMapButton.Visible,'Same-tab close did not restore map')
   openConversation();hidden('conversation construction');frame();hidden('conversation handoff frame')
   conversationPanel.Visible=true;academy.testLauncherBlocked=false;frame();hidden('conversation frame')
   toggleTab('Map');hidden('conversation to Map');check(modal.Visible and selected=='Map','Menu behavior changed')
   closeMenu();frame();check(miniMapButton.Visible,'Map close did not restore map')
   devPanel.Visible=true;frame();check(miniMapButton.Visible,'Authorized tools panel now hides minimap')
   devPanel.Visible=false;miniMapAvailable=false;frame();check(not miniMapButton.Visible,'Unavailable minimap shown')
   miniMapAvailable=true;windowFocused=false;frame();check(not miniMapButton.Visible,'Unfocused minimap shown')
  end
 end
end
local cityNoticeLayout={available=true,width=100}
local viewport,touch,data={},false,{devAccess=false}
CityMap.MiniLayout=function()return cityNoticeLayout end
local function noticeMapLayout()
'''+notice_map+'''
 return noticeMap
end
check(noticeMapLayout()==cityNoticeLayout,'City notice lost the map reservation')
academy.hideMap=true;modal.Visible=false;selected='Shop'
check(noticeMapLayout()==nil,'Hall notice reserved absent map space')
toggleTab('Map')
check(not modal.Visible and selected=='Shop','Hall Map shortcut opened its menu')
do
local gui={}
local UDim2={fromOffset=function()end,new=function()end}
local function button()error('Hall created a minimap')end
'''+creation+'''
check(not miniMapButton and not miniMapView and not miniMapAvailable,'Hall created a minimap')
academy.hideMiniMapForMenu()
end
print('PASS '..n..' actual-source minimap transition assertions; mocked frame ordering, not native devices')
'''
def run(s,negative=False):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False)as f:f.write(assemble(s));p=Path(f.name)
 try:
  r=subprocess.run(['luau',str(p)],capture_output=True,text=True);out=r.stdout+r.stderr
  if negative:
   assert r.returncode and (negative is True or negative in out),out
   print('PASS negative control:',out.splitlines()[0])
  else:assert not r.returncode,out;print(out,end='')
 finally:p.unlink()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args();s=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text();run(s)
 if a.negative_controls:
  run(s.replace(' if academy.hideMiniMapForMenu then academy.hideMiniMapForMenu() end\n','',1),True)
  run(s.replace('if academy.hideMiniMapForMenu then academy.hideMiniMapForMenu() end;','',1),True)
  run(s.replace(' and not modal.Visible and not (conversationPanel and conversationPanel.Visible) and not academy.testLauncherBlocked','',1),True)
  run(s.replace(' if name=="Map" and academy.hideMap then return end','',1),'Hall Map shortcut opened its menu')
  run(s.replace('local miniMapButton=not academy.hideMap and button','local miniMapButton=button',1),'Hall created a minimap')
  run(s.replace('local noticeMap=not academy.hideMap and','local noticeMap=false and',1),'City notice lost the map reservation')

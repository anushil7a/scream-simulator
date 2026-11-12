"""Build a manual-input-only disposable notice fixture. Does not launch Studio."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1];out=R/'build'
subprocess.run([sys.executable,str(R/'tests/build_ui_preview.py'),'640','360'],cwd=R,check=True)
s=(out/'StudioUIPreview.luau').read_text();s=s[:s.rindex('local report={}')]
profile=(R/'src/ServerScriptService/Profiles.luau').read_text()
warning=re.search(r'local RECOVERY_NOTICE="([^"]+)"',profile).group(1)+' Another session owns this profile; progress here is temporary. Rejoin shortly.'
assert len(warning)==142 and 'Another session owns this profile; progress here is temporary. Rejoin shortly.' in profile
config='-- MANUAL FIXTURE SETTINGS: edit these constants while STOPPED, before Play.\nlocal reviewWidth,reviewHeight=320,315\nlocal reviewTouch=true\nlocal reviewTestTools=true\nlocal reviewWarning=__WARNING__\n-- Synthetic frame inside actual safe-area ScreenGui; not a physical device viewport.\n'.replace('__WARNING__',json.dumps(warning))
s=s.replace('local fixtureTouch=true','local fixtureTouch=reviewTouch',1)
assert 'gui.Size=UDim2.fromOffset(640,360)' in s
s=s.replace('gui.Size=UDim2.fromOffset(640,360)','gui.Size=UDim2.fromOffset(reviewWidth,reviewHeight)',1)
s=s.replace('Vector2.new(640,360)','Vector2.new(reviewWidth,reviewHeight)')
s=s.replace('ready=true,power=.55,status="UI preview: simulated mic"','ready=true,power=0,status="UI preview: simulated mic"',1)
# No price lookup/purchase API is needed for this manual UI fixture.
s=s.replace('game:GetService("MarketplaceService")','({GetProductInfoAsync=function() error("Manual notice fixture blocks marketplace calls") end})')
tail='\nmic.ready=true;mic.power=0;windowFocused=true;micSetupOpen=false\nmodal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false\nsample.devAccess=reviewTestTools;data.devAccess=reviewTestTools\n-- One bounded initialization wait only. No scrolling, selection, repeated refresh or input overrides.\nfor _=1,3 do Run.RenderStepped:Wait() end\ntask.wait(.2)\nnotifications=modules.NotificationQueue.new();notify(reviewWarning,true,"save")\nprint("NOTICE_INPUT_READY manual only; synthetic "..reviewWidth.."x"..reviewHeight.." touch="..tostring(reviewTouch).." testTools="..tostring(reviewTestTools).." warningChars="..#reviewWarning)\n'
source=config+s+tail
assert 'IsStudio() and game.PlaceId==0' in source
assert 'local remotes={GetAttribute=' in source and 'local remotes=RS:WaitForChild("ScreamRemotes")' not in source
assert 'DataStoreService' not in source and 'modules.Microphone.new()' not in source
assert 'SelectedObject=' not in tail and 'CanvasPosition=' not in tail and 'InputBegan' not in tail
view=(R/'src/StarterPlayer/StarterPlayerScripts/NoticeView.luau').read_text().replace('require(script.Parent.NoticeLayout)','modules.NoticeLayout')
assert view in source,'Current NoticeView not embedded exactly except dependency resolution'
client=out/'NoticeInputReview.client.luau';client.write_text(source,encoding='utf8')
subprocess.run(['luau-compile',str(client)],stdout=subprocess.DEVNULL,check=True)
project={'name':'NoticeInputReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(client)}}},'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[40,1,40],'Position':[0,-5,0]}}}}}
assert 'ServerScriptService' not in project['tree'] and 'ReplicatedStorage' not in project['tree']
p=out/'NoticeInputReview.project.json';p.write_text(json.dumps(project,indent=2))
subprocess.run(['rojo','build',str(p),'-o',str(out/'NoticeInputReview.rbxl')],check=True)
for f in [client,p,out/'NoticeInputReview.rbxl',R/'src/StarterPlayer/StarterPlayerScripts/NoticeView.luau']:
 print('SHA256',f.name,hashlib.sha256(f.read_bytes()).hexdigest())
print('Built and compiled only. No native execution, selection, scrolling or PASS marker.')

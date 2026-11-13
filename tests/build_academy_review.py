"""Build-only exact-source environment comparison; no profiles, gameplay or launch."""
from pathlib import Path
import hashlib, json, subprocess, zlib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'academy-review'
BASE = '5622daa54424e639e7d3f671b2e453ff377b2cb6'
CITY = 'src/ServerScriptService/CompactCity.luau'
OUT.mkdir(parents=True, exist_ok=True)
before = subprocess.check_output(['git', 'show', BASE + ':' + CITY], cwd=ROOT)
after = (ROOT / CITY).read_bytes()
sources = {'BeforeCity': before, 'AfterCity': after}
for name, source in sources.items():
    (OUT / (name + '.luau')).write_bytes(source)

client = r'''
local RunService=game:GetService("RunService")
assert(RunService:IsStudio() and game.GameId==0 and game.PlaceId==0,"LOCAL DISPOSABLE ONLY")
local player=game.Players.LocalPlayer
local root,mode
local deadline=os.clock()+10
repeat RunService.Heartbeat:Wait() until (player.Character and player.Character:FindFirstChild("HumanoidRootPart") and workspace.CurrentCamera and workspace.CurrentCamera.ViewportSize.Y>1) or os.clock()>deadline
local hrp=assert(player.Character and player.Character:FindFirstChild("HumanoidRootPart"),"Avatar not ready")
local camera=assert(workspace.CurrentCamera,"Camera not ready")
local playerGui=assert(player:FindFirstChild("PlayerGui"),"PlayerGui missing")
local prior={anchored=hrp.Anchored,cframe=hrp.CFrame,cameraType=camera.CameraType,cameraCFrame=camera.CFrame,subject=camera.CameraSubject}
local control,cleaned
local function cleanup()
 if cleaned then return end;cleaned=true
 if root then root:Destroy();root=nil end
 if hrp.Parent then hrp.Anchored=prior.anchored;hrp.CFrame=prior.cframe end
 camera.CFrame=prior.cameraCFrame;camera.CameraSubject=prior.subject;camera.CameraType=prior.cameraType
 if control then control:Destroy() end
end
local cameras={west={Vector3.new(-175,7,50),Vector3.new(-120,17,50)},east={Vector3.new(-65,7,50),Vector3.new(-120,17,50)},spawn={Vector3.new(-270,8,130),Vector3.new(-120,17,50)}}
local function snapshot()
 local art=root and root:FindFirstChild("CoastalAcademyArt")
 local signs={}
 if art then for _,n in art:GetDescendants()do if n:IsA("TextLabel") then
  table.insert(signs,{text=n.Text,textFits=n.TextFits,textBounds={n.TextBounds.X,n.TextBounds.Y},absoluteSize={n.AbsoluteSize.X,n.AbsoluteSize.Y},face=n.Parent.Face.Name,alwaysOnTop=n.Parent.AlwaysOnTop,maxDistance=n.Parent.MaxDistance})
 end end end
 local camera=workspace.CurrentCamera
 return {gameId=game.GameId,placeId=game.PlaceId,mode=mode,artParts=art and #art:GetChildren() or 0,signs=signs,physicalViewport={camera.ViewportSize.X,camera.ViewportSize.Y},cameraPosition={camera.CFrame.Position.X,camera.CFrame.Position.Y,camera.CFrame.Position.Z}}
end
local function invoke(action,view)
 assert(RunService:IsStudio() and game.GameId==0 and game.PlaceId==0,"LOCAL ONLY")
 if action=="cleanup" then
  cleanup();return {cleaned=true,gameId=game.GameId,placeId=game.PlaceId}
 end
 assert(action=="BeforeCity" or action=="AfterCity","Unknown review mode")
 if mode~=action then
  if root then root:Destroy() end
  root=Instance.new("Model");root.Name="AcademyReviewScene";root.Parent=workspace
  require(game.ReplicatedStorage[action]).Build(root);mode=action
 end
 local camera=workspace.CurrentCamera
 assert(camera and camera.ViewportSize.X>1 and camera.ViewportSize.Y>1,"Camera not ready")
 local shot=assert(cameras[view],"Unknown review view")
 camera.CameraType=Enum.CameraType.Scriptable;camera.CFrame=CFrame.lookAt(shot[1],shot[2])
 RunService.Heartbeat:Wait();RunService.Heartbeat:Wait()
 return snapshot()
end
hrp.Anchored=true;hrp.CFrame=CFrame.new(-270,5,130)
control=Instance.new("BindableFunction");control.Name="AcademyReviewControl"
control.OnInvoke=function(action,view)
 local ok,result=xpcall(function()return invoke(action,view)end,debug.traceback)
 if not ok then cleanup();error(result) end
 return result
end
control.Parent=playerGui
task.delay(300,cleanup)
'''
(OUT / 'Review.client.luau').write_text(client, encoding='utf8')
tree = {'$className': 'DataModel', 'ReplicatedStorage': {'$className': 'ReplicatedStorage',
    'Shared': {'$className': 'Folder', 'CompactLayout': {'$path': str(ROOT / 'src/ReplicatedStorage/Shared/CompactLayout.luau')}},
    **{name: {'$path': str(OUT / (name + '.luau'))} for name in sources}},
    'StarterPlayer': {'$className': 'StarterPlayer', 'StarterPlayerScripts': {'$className': 'StarterPlayerScripts', 'AcademyReview': {'$path': str(OUT / 'Review.client.luau')}}}}
project = OUT / 'AcademyReview.project.json'
project.write_text(json.dumps({'name': 'AcademyReview_DO_NOT_PUBLISH', 'tree': tree}, indent=2), encoding='utf8')
place = OUT / 'AcademyReview.rbxl'
subprocess.run(['luau-compile', str(OUT / 'Review.client.luau')], stdout=subprocess.DEVNULL, check=True)
subprocess.run(['rojo', 'build', str(project), '-o', str(place)], check=True, cwd=ROOT)
sha = lambda data: hashlib.sha256(data).hexdigest()
files = {name: {'sha256': sha(source), 'normalizedBytes': len(source.replace(b'\r\n', b'\n')), 'normalizedAdler32': zlib.adler32(source.replace(b'\r\n', b'\n'))} for name, source in sources.items()}
files['CompactLayout'] = {'sha256': sha((ROOT / 'src/ReplicatedStorage/Shared/CompactLayout.luau').read_bytes())}
report = {'baseline': BASE, 'gitHead': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), 'sources': files, 'artifactSha256': sha(place.read_bytes()), 'clientSha256': sha((OUT/'Review.client.luau').read_bytes()), 'projectSha256': sha(project.read_bytes()), 'builderSha256': sha(Path(__file__).read_bytes()), 'scope': 'Exact static constructor comparison only. Local-only client fixture; no Bootstrap, profiles, combat, remotes or saves. Build does not launch or play.'}
(OUT / 'provenance.json').write_text(json.dumps(report, indent=2), encoding='utf8')
print(json.dumps(report))

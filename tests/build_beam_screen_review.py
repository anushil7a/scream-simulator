"""Build isolated presentation-only native review; never launches Studio."""
from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];out=R/'build';out.mkdir(exist_ok=True)
provenance=out/'BeamScreenReview.provenance.json'
if provenance.exists():provenance.unlink()
module=R/'src/StarterPlayer/StarterPlayerScripts/BeamScreenFeedback.luau'
copy=out/'BeamScreenReview.module.luau';copy.write_bytes(module.read_bytes())
source=r'''
local Run=game:GetService("RunService")
if not Run:IsStudio() or game.PlaceId~=0 then error("Beam screen review requires an unpublished local Studio place") end
local Players=game:GetService("Players");local Http=game:GetService("HttpService")
local Feedback=require(script.Parent:WaitForChild("Feedback"))
local gui=Instance.new("ScreenGui");gui.Name="BeamScreenReview";gui.ScreenInsets=Enum.ScreenInsets.None;gui.DisplayOrder=-1;gui.ResetOnSpawn=false;gui.ZIndexBehavior=Enum.ZIndexBehavior.Sibling
local holder=Instance.new("Frame");holder.Name="SyntheticViewport";holder.BackgroundTransparency=1;holder.Active=false;holder.Parent=gui
local aimGui=Instance.new("ScreenGui");aimGui.Name="BeamReviewAim";aimGui.ScreenInsets=Enum.ScreenInsets.None;aimGui.ResetOnSpawn=false
local reticle=Instance.new("TextLabel");reticle.Name="AimReference";reticle.Text="+";reticle.BackgroundTransparency=1;reticle.Size=UDim2.fromOffset(24,24);reticle.Position=UDim2.new(.5,-12,.5,-12);reticle.Parent=aimGui
local hudGui=Instance.new("ScreenGui");hudGui.Name="BeamReviewDefaultInsetHUD";hudGui.ResetOnSpawn=false
local hud=Instance.new("Frame");hud.BackgroundTransparency=1;hud.Size=UDim2.fromScale(1,1);hud.Parent=hudGui
local feedback;local finished=false;local checks=0;local rows={}
local function cleanup()if feedback then feedback:Destroy();feedback=nil end;gui:Destroy();aimGui:Destroy();hudGui:Destroy()end
local function check(v,m)assert(v,m);checks+=1 end
local function settle()Run.RenderStepped:Wait();Run.RenderStepped:Wait();assert(not finished,"Review timed out")end
local function near(a,b)return math.abs(a-b)<.00001 end
local function bounds(part)
 local p,s=part.AbsolutePosition,part.AbsoluteSize;local rad=math.rad(part.Rotation)
 local w=math.abs(math.cos(rad))*s.X+math.abs(math.sin(rad))*s.Y
 local h=math.abs(math.sin(rad))*s.X+math.abs(math.cos(rad))*s.Y
 return p.X+s.X/2-w/2,p.Y+s.Y/2-h/2,w,h
end
local function clearCenter(part)
 local x,y,w,h=bounds(part);local p,s=holder.AbsolutePosition,holder.AbsoluteSize
 local cx,cy=p.X+s.X/2,p.Y+s.Y/2
 return x+w<=cx-20 or x>=cx+20 or y+h<=cy-20 or y>=cy+20
end
-- Timeout cleans the disposable GUI, not the Studio session or other apps.
task.delay(20,function()if not finished then finished=true;cleanup();print('BEAM_SCREEN_RESULT '..Http:JSONEncode({passed=false,reason='timeout',synthetic=true}))end end)
local ok,err=xpcall(function()
 gui.Parent=Players.LocalPlayer:WaitForChild("PlayerGui",5);check(gui.Parent~=nil,"PlayerGui unavailable")
 aimGui.Parent=gui.Parent;hudGui.Parent=gui.Parent
 holder.Size=UDim2.fromScale(1,1);feedback=Feedback.new(holder);settle()
 local root=feedback.root;local center=root.AbsolutePosition+root.AbsoluteSize/2
 local aimCenter=reticle.AbsolutePosition+reticle.AbsoluteSize/2
 check((center-aimCenter).Magnitude<.5,"Feedback center differs from None-inset aim center")
 check(root.AbsoluteSize.X>0 and root.AbsoluteSize.Y>0,"Native viewport has no measured size")
 check(gui.ScreenInsets==Enum.ScreenInsets.None and aimGui.ScreenInsets==Enum.ScreenInsets.None,"Aim/feedback inset mismatch")
 check(hudGui.ScreenInsets~=Enum.ScreenInsets.None,"HUD no longer exercises default inset")
 check(gui.DisplayOrder<aimGui.DisplayOrder and gui.DisplayOrder<hudGui.DisplayOrder,"Feedback covers HUD layer")
 table.insert(rows,{stage="actual-viewport-centers",rootCenter=tostring(center),aimCenter=tostring(aimCenter),rootPosition=tostring(root.AbsolutePosition),rootSize=tostring(root.AbsoluteSize),defaultHudPosition=tostring(hud.AbsolutePosition),defaultHudSize=tostring(hud.AbsoluteSize),defaultHudInset=tostring(hudGui.ScreenInsets),synthetic=false,physicalReachabilityTested=false})
 feedback:Destroy();feedback=nil
 for _,view in ipairs({{320,568},{390,844},{844,390},{1280,720}})do
  holder.Size=UDim2.fromOffset(view[1],view[2]);feedback=Feedback.new(holder);settle()
  local root=feedback.root;check(#root:GetDescendants()==12,"Unexpected GUI pool")
  local objects={root};for _,v in ipairs(root:GetDescendants())do table.insert(objects,v)end
  for _,v in ipairs(objects)do check(v:IsA("Frame") and not v.Active and not v.Selectable and not v.Interactable and v.ZIndex==0,"Interactive or foreground object")end
  check(root.BackgroundTransparency==1,"Full-screen background visible")
  local geometry={}
  for _,v in ipairs(root:GetDescendants())do
   check(clearCenter(v),"Mark enters central40px sightline: "..v.Name)
   local x,y,w,h=bounds(v);local p,s=holder.AbsolutePosition,holder.AbsoluteSize
   check(x>=p.X and y>=p.Y and x+w<=p.X+s.X and y+h<=p.Y+s.Y,"Mark exceeds synthetic viewport")
   table.insert(geometry,{name=v.Name,x=x-p.X,y=y-p.Y,width=w,height=h})
  end
  check(feedback:Begin(1,1,Color3.fromRGB(255,220,90),true),"Launch rejected");feedback:Step(1,true,false)
  check(root.Visible and near(feedback.rays[1].BackgroundTransparency,.88),"Launch alpha mismatch")
  feedback:Step(1.225,true,false);check(near(feedback.rays[1].BackgroundTransparency,.94),"Launch fade mismatch")
  feedback:Step(1.45,true,false);check(not root.Visible,"Launch expiry failed")
  check(feedback:Hit(2,true),"Hit rejected");feedback:Step(2,true,false);check(near(feedback.marks[1].BackgroundTransparency,.6),"Hit alpha mismatch")
  check(not feedback:Hit(2.1,true),"Hit restarted early");feedback:Step(2.25,true,false);check(not root.Visible,"Hit expiry failed")
  feedback:Begin(2,3,nil,true);feedback:Step(3,true,true);check(not root.Visible,"Reduced effects not cleared")
  feedback:Step(3.1,true,false);check(not root.Visible,"Reduced effect replayed")
  feedback:Begin(3,4,nil,true);feedback:Step(4,false,false);check(not root.Visible,"Hidden effect not cleared")
  feedback:Begin(4,5,nil,true);feedback:Clear();check(not root.Visible and not feedback:Begin(4,5,nil,true),"Clear reset start floor")
  check(#root:GetDescendants()==12,"Events grew GUI pool")
  table.insert(rows,{viewport=view,geometry=geometry,instances=13,synthetic=true,physicalReachabilityTested=false})
  feedback:Destroy();feedback:Destroy();check(root.Parent==nil and #holder:GetChildren()==0,"Destroy left GUI");feedback=nil
 end
end,debug.traceback)
if not finished then
 finished=true;cleanup()
 local result={passed=ok,checks=checks,rowCount=#rows,synthetic=true,scope='Actual module/native viewport inset-center comparison and synthetic-size geometry; synthetic time, no full gameplay HUD overlap/input/device validation'}
 if not ok then result.error=tostring(err)end
 for i,row in ipairs(rows)do print('BEAM_SCREEN_ROW '..i..' '..Http:JSONEncode(row))end
 print('BEAM_SCREEN_RESULT '..Http:JSONEncode(result))
end
'''
script=out/'BeamScreenReview.client.luau';script.write_text(source,encoding='utf-8')
project={'name':'BeamScreenReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel','StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(script)},'Feedback':{'$path':str(copy)}}}}}
project_path=out/'BeamScreenReview.project.json';project_path.write_text(json.dumps(project),encoding='utf-8')
for path in (copy,script):subprocess.run(['luau-compile',str(path)],check=True,stdout=subprocess.DEVNULL)
artifact=out/'BeamScreenReview.rbxl';subprocess.run(['rojo','build',str(project_path),'-o',str(artifact)],check=True)
assert module.read_bytes()==copy.read_bytes(),'Module changed during build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
provenance.write_text(json.dumps({'nativeExecuted':False,'scope':'Isolated module only; native checks pending','sourceSha256':sha(module),'fixtureSha256':sha(script),'artifactSha256':sha(artifact),'viewports':[[320,568],[390,844],[844,390],[1280,720]]},indent=2),encoding='utf-8')
print('PASS isolated beam screen review compiled/built; native assertions NOT executed')
print(provenance.read_text())

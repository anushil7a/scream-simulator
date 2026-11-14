local Run=game:GetService("RunService")
assert(Run:IsStudio() and game.PlaceId==0 and game.GameId==0,"LOCAL HUMANOID DISPLAY FIXTURE ONLY")
local Players=game:GetService("Players");local Http=game:GetService("HttpService")
local terminal=false;local cleanup=function()end
local destroyConnection=script.Destroying:Connect(function()terminal=true;cleanup()end)
local function bounded(get,label)
 local deadline=os.clock()+15
 repeat if terminal then error("Review destroyed during startup")end;local v=get();if v then return v end;task.wait(.05)until os.clock()>deadline
 error("Timed out waiting for "..label)
end
local player=bounded(function()return Players.LocalPlayer end,"LocalPlayer")
local character=bounded(function()return player.Character end,"Character")
local viewer=bounded(function()return character:FindFirstChildOfClass("Humanoid")end,"Humanoid")
local playerGui=bounded(function()return player:FindFirstChildOfClass("PlayerGui")end,"PlayerGui")
local root=bounded(function()return character:FindFirstChild("HumanoidRootPart")end,"Root")
local camera=bounded(function()return workspace.CurrentCamera end,"Camera")
local props={"DisplayDistanceType","NameDisplayDistance","HealthDisplayDistance","HealthDisplayType","NameOcclusion","DisplayName"}
local function capture(h)local r={};for _,k in ipairs(props)do r[k]=h[k]end;return r end
local function serial(h)local r={};for _,k in ipairs(props)do r[k]=tostring(h[k])end;r.Health=h.Health;r.MaxHealth=h.MaxHealth;return r end
local viewerOriginal=capture(viewer);local rootOriginal=root.CFrame;local anchorOriginal=root.Anchored
local camType,camSubject,camFrame=camera.CameraType,camera.CameraSubject,camera.CFrame
local folder,template,subject,blocker,control,watchdog;local lastRoot,lastCamera;local lastViewer={};local baseline;local current;local sequence=0
cleanup=function()
 local function attempt(label,fn)local success,message=pcall(fn);if not success then warn("PLAYER_TAG_CLEANUP",label,tostring(message))end end
 local c,f,t=control,folder,template;control,folder,template=nil,nil,nil
 if c then attempt("control",function()c:Destroy()end)end
 if f then attempt("folder",function()f:Destroy()end)end
 if t then attempt("template",function()t:Destroy()end)end
 for k,v in pairs(lastViewer)do attempt(k,function()if viewer[k]==v then viewer[k]=viewerOriginal[k]end end)end
 attempt("root frame",function()if root.Parent and root.CFrame==lastRoot then root.CFrame=rootOriginal end end)
 attempt("root anchor",function()if root.Parent and root.Anchored then root.Anchored=anchorOriginal end end)
 local ownCamera=workspace.CurrentCamera==camera and camera.CameraType==Enum.CameraType.Scriptable
 if ownCamera then
  attempt("camera frame",function()if camera.CFrame==lastCamera then camera.CFrame=camFrame end end)
  attempt("camera subject",function()camera.CameraSubject=camSubject end)
  attempt("camera type",function()camera.CameraType=camType end)
 end
 local dc=destroyConnection;destroyConnection=nil;if dc then attempt("destroy connection",function()dc:Disconnect()end)end
 local w=watchdog;watchdog=nil;if w and w~=coroutine.running()then attempt("watchdog",function()task.cancel(w)end)end
end
watchdog=task.delay(900,function()watchdog=nil;terminal=true;cleanup();warn("PLAYER_TAG_TIMEOUT disposed after15minutes")end)
local ok,err=xpcall(function()
 local archivable=character.Archivable;character.Archivable=true
 local clonedOk,cloned=pcall(function()return character:Clone()end);character.Archivable=archivable;assert(clonedOk and cloned,"Avatar clone unavailable")
 template=cloned;template.Parent=nil
 for _,d in ipairs(template:GetDescendants())do if d:IsA("LuaSourceContainer")then d:Destroy()elseif d:IsA("BasePart")then d.Anchored=true;d.CanCollide=false;d.CanTouch=false end end
 local th=assert(template:FindFirstChildOfClass("Humanoid"));assert(template:FindFirstChild("Head"),"Head required")
 baseline={viewer=serial(viewer),subjectBeforeLabel=serial(th),viewerPlayer=player.Name,subjectKind="script-stripped local avatar clone, NOT another Player",placeId=game.PlaceId,gameId=game.GameId}
 print("PLAYER_TAG_BASELINE",Http:JSONEncode(baseline))
 folder=Instance.new("Folder");folder.Name="LocalHumanoidDisplayReview";folder.Parent=workspace
 root.Anchored=true;lastRoot=CFrame.new(0,3,0);root.CFrame=lastRoot
 camera.CameraType=Enum.CameraType.Scriptable
 local presets={
  {name="UntouchedDamaged",mode="untouched",distance=20},
  {name="ViewerNear",mode="Viewer",distance=20},{name="ViewerNameOnly",mode="Viewer",distance=30},{name="ViewerFar",mode="Viewer",distance=55},
  {name="SubjectNear",mode="Subject",distance=30},{name="SubjectNameOnly",mode="Subject",distance=60},{name="SubjectFar",mode="Subject",distance=85},
  {name="NoneNear",mode="None",distance=20},
  {name="OpaqueOcclude",mode="Subject",distance=20,wall=0},{name="Point99Occlude",mode="Subject",distance=20,wall=.99},{name="Point995Occlude",mode="Subject",distance=20,wall=.995},
  {name="OpaqueNoOcclusion",mode="Subject",distance=20,wall=0,noOcclusion=true},
  {name="HumanoidBlocker",mode="Subject",distance=20,wall=0,humanoidBlocker=true},
  {name="CameraOnlyOffset",mode="Subject",distance=30,cameraOffset=Vector3.new(20,0,0)},
 }
 local function snapshot()
  local h=subject and subject:FindFirstChildOfClass("Humanoid");local sr=subject and subject:FindFirstChild("HumanoidRootPart")
  return {sequence=sequence,case=current,baseline=baseline,viewer=serial(viewer),subject=h and serial(h),viewerRoot=tostring(root.Position),camera=tostring(camera.CFrame),rootDistance=sr and (root.Position-sr.Position).Magnitude,cameraDistance=sr and (camera.CFrame.Position-sr.Position).Magnitude,viewport=tostring(camera.ViewportSize),subjectIsPlayer=subject and Players:GetPlayerFromCharacter(subject)~=nil,scope="Configured state only; screenshots required for native visibility. No Player/team/network/respawn proof."}
 end
 local function apply(index,overrides)
  assert(not terminal,"Stopped");assert(type(index)=="number" and index%1==0 and presets[index],"Case index1..14 required")
  local c=table.clone(presets[index]);overrides=overrides or {};assert(type(overrides)=="table","Overrides must be table")
  for k,v in pairs(overrides)do
   assert(k=="distance" or k=="healthFraction" or k=="healthDisplay" or k=="nameRange" or k=="healthRange","Unsupported override")
   if k=="healthDisplay"then assert(v=="AlwaysOn" or v=="AlwaysOff" or v=="DisplayWhenDamaged","Invalid health display")else assert(type(v)=="number" and v==v and v>=0 and v<=(k=="healthFraction" and 1 or 150),"Invalid numeric override")end;c[k]=v
  end
  if subject then subject:Destroy()end;if blocker then blocker:Destroy();blocker=nil end
  for _,k in ipairs(props)do viewer[k]=viewerOriginal[k];lastViewer[k]=viewer[k]end
  subject=template:Clone();subject.Name="HumanoidFixture_NOT_PLAYER";local h=assert(subject:FindFirstChildOfClass("Humanoid"))
  h.DisplayName="HUMANOID FIXTURE";subject.Parent=folder;subject:PivotTo(CFrame.new(0,3,-c.distance));h.Health=h.MaxHealth*(c.healthFraction or .5)
  if c.mode~="untouched"then
   viewer.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.Viewer;viewer.NameDisplayDistance=50;viewer.HealthDisplayDistance=25
   h.DisplayDistanceType=Enum.HumanoidDisplayDistanceType[c.mode];h.NameDisplayDistance=c.nameRange or 80;h.HealthDisplayDistance=c.healthRange or 40
   h.HealthDisplayType=Enum.HumanoidHealthDisplayType[c.healthDisplay or "DisplayWhenDamaged"];h.NameOcclusion=Enum.NameOcclusion.OccludeAll;viewer.NameOcclusion=c.noOcclusion and Enum.NameOcclusion.NoOcclusion or Enum.NameOcclusion.OccludeAll
   if c.mode=="Viewer"then viewer.NameDisplayDistance=c.nameRange or 50;viewer.HealthDisplayDistance=c.healthRange or 25 end
  end
  for _,k in ipairs(props)do lastViewer[k]=viewer[k]end
  lastCamera=CFrame.lookAt(Vector3.new(0,6,8)+(c.cameraOffset or Vector3.zero),subject.Head.Position);camera.CFrame=lastCamera
  if c.wall~=nil then
   blocker=Instance.new("Model");blocker.Name=c.humanoidBlocker and "HumanoidContainingOccluder" or "OrdinaryOccluder"
   local wall=Instance.new("Part");wall.Name="Head";wall.Size=Vector3.new(12,12,1);wall.Anchored=true;wall.CanCollide=false;wall.Transparency=c.wall
   wall.CFrame=CFrame.lookAt((camera.CFrame.Position+subject.Head.Position)/2,subject.Head.Position);wall.Parent=blocker
   if c.humanoidBlocker then local bh=Instance.new("Humanoid");bh.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.None;bh.Parent=blocker end
   blocker.Parent=folder
  end
  sequence+=1;current=c.name;local caseSequence=sequence;task.wait(.35);assert(not terminal and sequence==caseSequence,"Case cancelled/replaced during settle");return snapshot()
 end
 control=Instance.new("BindableFunction");control.Name="PlayerTagReviewControl";control.Parent=playerGui
 assert(control.Parent,"PlayerGui unavailable")
 control.OnInvoke=function(command,index,overrides)
  if command=="Case"then return apply(index,overrides)elseif command=="Snapshot"then return snapshot()elseif command=="Cases"then local names={};for i,c in ipairs(presets)do names[i]=c.name end;return names elseif command=="Stop"then terminal=true;cleanup();return "Stopped; owned objects removed and best-effort restoration"else error("Use Case/Snapshot/Cases/Stop")end
 end
 local ready=apply(1);assert(not terminal,"Review stopped before ready");print("PLAYER_TAG_READY",Http:JSONEncode(ready))
end,debug.traceback)
if not ok then terminal=true;cleanup();warn("PLAYER_TAG_SETUP_FAILED",err)end

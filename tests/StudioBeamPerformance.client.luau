-- Local Studio measurement only: synthetic overlapping visuals, not combat/network/device proof.
local buildIdentity="__BEAM_PERFORMANCE_BUILD_ID__"
local Run=game:GetService("RunService")
assert(Run:IsStudio() and game.PlaceId==0,"Requires unpublished Studio place")
local startupDestroyed=false
local startupConnection=script.Destroying:Connect(function()startupDestroyed=true end)
local Http=game:GetService("HttpService")
local RS=game:GetService("ReplicatedStorage")
local Visuals=require(RS.BeamVisuals);if startupDestroyed then startupConnection:Disconnect();return end
local Beams=require(RS.SustainedBeams);if startupDestroyed then startupConnection:Disconnect();return end
local Style=require(RS.Shared.BeamStyle);if startupDestroyed then startupConnection:Disconnect();return end
local camera=assert(workspace.CurrentCamera,"Camera unavailable")
local original={type=camera.CameraType,cf=camera.CFrame,fov=camera.FieldOfView}
local manager=Beams.new(Visuals.Create,Visuals.Update,Visuals.Destroy)
local beamFrame=0;local tracked={};local connection,destruction,watchdog
local done=false;local checks=0;local phase=1;local phaseStart=os.clock();local nextPulse=0
local sampleFirst,sampleLast
local names={"baseline","regular24","reduced24"};local frames,costs={},{};local rows={}
local function check(v,m)assert(v,m);checks+=1 end
local function summary(values)
 table.sort(values);local n=#values;assert(n>0,"No samples")
 local function q(p)return values[math.clamp(math.ceil(n*p),1,n)]*1000 end
 return {n=n,p50=q(.5),p95=q(.95),p99=q(.99),max=q(1)}
end
local function finish(ok,reason)
 if done then return end;done=true
 if connection then connection:Disconnect()end
 if destruction then destruction:Disconnect()end
 if watchdog and coroutine.running()~=watchdog then task.cancel(watchdog)end
 local errors={}
 local function attempt(name,fn)local ok,err=pcall(fn);if not ok then table.insert(errors,name..": "..tostring(err))end end
 attempt("manager",function()manager:Destroy()end)
 attempt("visuals",function()Visuals.Clear()end)
 attempt("cameraType",function()camera.CameraType=original.type end)
 attempt("cameraFrame",function()camera.CFrame=original.cf end)
 attempt("cameraFov",function()camera.FieldOfView=original.fov end)
 attempt("budget",function()
  local allocated,cached=Visuals.Budget()
  check(manager.count==0 and next(manager.entries)==nil and allocated==0 and cached==0,"Terminal budget leak")
 end)
 attempt("parts",function()for part in pairs(tracked)do check(part.Parent==nil,"Fixture part remains parented")end end)
 print("BEAM_PERFORMANCE_RESULT "..Http:JSONEncode({buildIdentity=buildIdentity,ok=ok and #errors==0,error=reason,cleanupErrors=errors,checks=checks,rows=#rows,disconnected=not connection or not connection.Connected,studioOnly=true,gpuTiming=false}))
end
destruction=script.Destroying:Connect(function()finish(false,"Script destroyed")end)
startupConnection:Disconnect()
watchdog=task.delay(35,function()finish(false,"35-second scheduler watchdog")end)
camera.CameraType=Enum.CameraType.Scriptable;camera.CFrame=CFrame.lookAt(Vector3.new(0,8,24),Vector3.new(0,8,-20));camera.FieldOfView=60
local fixedFrame=camera.CFrame;local fixedFov=camera.FieldOfView
local fixedViewport=camera.ViewportSize
local quality="unknown";pcall(function()quality=tostring(UserSettings():GetService("UserGameSettings").SavedQualityLevel)end)
print("BEAM_PERFORMANCE_START "..Http:JSONEncode({buildIdentity=buildIdentity,viewport={camera.ViewportSize.X,camera.ViewportSize.Y},savedQualityPreference=quality,rendererQualityControlled=false,warmSeconds=2,sampleSeconds=5,maxBeams=24,animationCadence="accumulated dt >=1/30 then reset0 (Client)",clock="os.clock",units="ms",limitations="Studio frame intervals and instrumented script section elapsed duration only; no GPU/phone/network claim"}))
connection=Run.RenderStepped:Connect(function(dt)
 if done then return end
 local ok,err=xpcall(function()
  local now=os.clock()
  check(camera.ViewportSize==fixedViewport,"Viewport changed; comparison invalid")
  check(workspace.CurrentCamera==camera and camera.CameraType==Enum.CameraType.Scriptable and camera.CFrame==fixedFrame and camera.FieldOfView==fixedFov,"Camera changed; comparison invalid")
  if phase==4 then
   manager:Expire(now)
   if manager.count==0 then finish(true)end
   return
  end
  local started=os.clock()
  if phase>1 then
   if now>=nextPulse then
    nextPulse=now+.2
    for id=1,24 do check(manager:Update(id,now,Vector3.new(0,8,0),-Vector3.zAxis,40,7,Color3.fromRGB(70,220,255),100,phase==3),"Admission rejected")end
   end
   manager:Expire(now)
   beamFrame+=dt
   if beamFrame>=1/30 then
    beamFrame=0
    for _,entry in pairs(manager.entries)do Visuals.Animate(entry.visual,now,camera.CFrame.Position,phase==3)end
   end
  end
  local cost=os.clock()-started
  if now-phaseStart>=2 then sampleFirst=sampleFirst or now;sampleLast=now;table.insert(frames,dt);table.insert(costs,cost)end
  if now-phaseStart>=7 then
   local allocated,cached=Visuals.Budget();local visible=0
   check(allocated<=Style.MaxParts,"Allocation cap exceeded")
   for _,entry in pairs(manager.entries)do
    for _,part in ipairs(entry.visual.parts)do
     tracked[part]=true;visible+=1
     check(part.Parent==workspace and not part.CanCollide and not part.CanQuery and not part.CanTouch,"Invalid cosmetic part")
    end
    check(#entry.visual.parts>=(phase==3 and 4 or 5),"Core starved")
   end
   check(manager.count==(phase==1 and 0 or 24),"Manager cardinality")
   if phase==3 then check(visible==96,"Reduced geometry count")end
   if phase>1 then check(not manager:Update(25,now,Vector3.zero,Vector3.xAxis,40,7,Color3.new(1,1,1),100,false),"25th admission accepted")end
   local row={buildIdentity=buildIdentity,phase=names[phase],sampleSpanSeconds=sampleLast-sampleFirst,sampledFrameSeconds=0,frame=summary(frames),script=summary(costs),allocated=allocated,cached=cached,visible=visible,count=manager.count}
   for _,value in ipairs(frames)do row.sampledFrameSeconds+=value end
   table.insert(rows,row);print("BEAM_PERFORMANCE_ROW "..Http:JSONEncode(row))
   phase+=1;phaseStart=now;frames={};costs={};nextPulse=0;beamFrame=0;sampleFirst=nil;sampleLast=nil
   -- Preserve live entries and pooled Parts across the real reduced-effects transition.
  end
 end,debug.traceback)
 if not ok then finish(false,tostring(err))end
end)

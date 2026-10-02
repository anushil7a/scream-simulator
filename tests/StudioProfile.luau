-- Run using Studio execute_luau on Client; @rbx/LibMP is a Studio tool shortcut.
-- Inclusive per-thread scopes are work volume; do not sum them as frame time.
local lib=require("@rbx/LibMP")
lib.Control:SetFrameLimit(128);lib.Control:EnableProfiler(true);lib.Control:EnableCapture(true)
task.wait(5)
local snapshot=lib.Control:CaptureToBufferSync()
lib.Control:EnableProfiler(false)
local session=assert(lib.Session.OpenFromBuffer(snapshot))
local first=math.max(session:GetFrameIdMin()+1,session:GetFrameIdMax()-40)
local last=session:GetFrameIdMax()-1
local tick=session:FetchGlobalDesc().TickToMsCpu
local scopes,frames={},{}
local iterator=session:CreateLogIterator()
iterator:Configure({SkipGpuThreads=true,SkipEvents=true,EmitThreadFrameEnd=true,StartFrameId=first-1,EndFrameId=last})
local state=iterator:GetState()
local function sample(frame,thread,timer,start,finish)
 if frame<first or frame>last or finish<start then return end
 local key=thread..":"..timer
 local entry=scopes[key]
 if not entry then entry={thread=session:FetchThreadDesc(thread).ThreadName,timer=session:FetchTimerDesc(timer).TimerName,ms=0};scopes[key]=entry end
 entry.ms+=(finish-start)*tick
end
while iterator:Step() do
 if state:IsThreadFrameEnd() then
  for depth=state:ThreadStackDepth()-1,0,-1 do
   local el=iterator:GetCurrentThreadStackElement(depth)
   if el then sample(state:FrameId(),state:ThreadId(),el:EnterTimerId(),el:EnterTimestampFrameLocal(),state:Timestamp()) end
  end
 elseif state:IsExit() and not state:ThreadStackWasOverflowed() then
  local start
  if not state:ThreadStackIsUnderflowed() then
   local el=iterator:GetCurrentThreadStackElement(state:ThreadStackDepth());start=el:EnterTimestampFrameLocal()
  else start=session:FetchFrameDesc(state:FrameId()).TickStartCpu end
  sample(state:FrameId(),state:ThreadId(),state:TimerId(),start,state:Timestamp())
 end
end
for id=first,last do
 local f=session:FetchFrameDesc(id)
 table.insert(frames,{id=id,absoluteId=f.FrameAbsoluteId,ms=(f.TickEndCpu-f.TickStartCpu)*tick})
end
local ordered={};for _,v in pairs(scopes) do v.meanMs=v.ms/#frames;table.insert(ordered,v) end
table.sort(ordered,function(a,b)return a.ms>b.ms end)
local top={};for i=1,math.min(20,#ordered) do top[i]=ordered[i] end
-- Sleeping workers and whole-thread spans otherwise crowd useful scopes out of the report.
-- Keep the original inclusive report; neither list is an additive frame-time breakdown.
local nonIdle={}
for _,entry in ordered do
 if entry.timer~="Sleep" and not string.match(entry.timer,"^Thread") then
  table.insert(nonIdle,entry);if #nonIdle==20 then break end
 end
end
iterator:Dispose();session:Dispose()
return {frames=frames,topInclusiveCpuScopes=top,topNonIdleCpuScopes=nonIdle}

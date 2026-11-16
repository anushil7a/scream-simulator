-- Pure replicated-attribute event gate; no local damage inference or late replay.
local Events={}
local function serial(v)return type(v)=='number' and v%1==0 and v>=0 and v<=1e9 and v or 0 end
function Events.new(play,cancel)
 local self={seen={}}
 function self:Step(source,id,number,deadline,impactNumber,impactAt,state,now,position,eligible)
  local current,impact=serial(number),serial(impactNumber)
  local entry=self.seen[id]
  if not entry or entry.source~=source then
   if entry then cancel(id,true) end
   self.seen[id]={source=source,serial=current,impact=impact,impactTime=type(impactAt)=='number' and impactAt or 0,tell=true}
   return -- joining/streaming in never replays historical attacks
  end
  if current>entry.serial then
   entry.serial=current;entry.tell=false;entry.pendingAt=now;entry.expectedAt=nil
  end
  if not entry.tell then
   if state=='Windup' and type(deadline)=='number' and deadline>now and deadline-now<=4 then
    entry.tell=true;entry.expectedAt=deadline
    if eligible then play(id,'tell',current,position,now) end
   elseif now-(entry.pendingAt or now)>.3 then entry.tell=true end
  end
  if impact>entry.impact then
   if entry.pendingImpact~=impact then entry.pendingImpact=impact;entry.impactSeenAt=now end
   -- Impact serial/time may replicate separately; a brief retry never extends cue freshness.
   local fresh=type(impactAt)=='number' and impactAt>entry.impactTime and now>=impactAt and now-impactAt<=.25
    and (not entry.expectedAt or impactAt>=entry.expectedAt-.25)
   if fresh then
    entry.impact=impact;entry.impactTime=impactAt
    if eligible and impact==entry.serial then cancel(id);play(id,'impact',impact,position,now) end
   elseif now-(entry.impactSeenAt or now)>.3 then entry.impact=impact end
  end
  if not eligible or (state~='Windup' and entry.impact~=entry.serial) then cancel(id) end
 end
 function self:RemoveAbsent(present)
  for id in pairs(self.seen) do if not present[id] then cancel(id,true);self.seen[id]=nil end end
 end
 function self:Clear()for id in pairs(self.seen)do cancel(id,true)end;table.clear(self.seen)end
 return self
end
return Events

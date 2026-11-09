-- Cosmetic timing/mixing only. No voice recording, damage or server requests.
local Mix={};Mix.__index=Mix
function Mix.new(settings,create,update,destroy)
 return setmetatable({settings=settings,create=create,update=update,destroy=destroy,
  entries={},count=0,enabled=true,duck=1},Mix)
end
function Mix:Remove(id)
 local entry=self.entries[id];if not entry then return end
 self.entries[id]=nil;self.count-=1;self.destroy(entry.sound)
end
function Mix:Clear()
 for id in pairs(self.entries) do self:Remove(id) end
end
function Mix:SetEnabled(enabled)
 self.enabled=enabled==true
 if not self.enabled then self:Clear() end
end
function Mix:Pulse(id,now,position,isLocal,tier)
 if self.destroyed or not self.enabled then return false end
 local entry=self.entries[id]
 if entry and entry.stopped then return false end -- never revive a fading attack
 if not entry then
  if self.count>=self.settings.Limit then return false end
  local sound=self.create(position,tier);if not sound then return false end
  entry={sound=sound,started=now,isLocal=isLocal};self.entries[id]=entry;self.count+=1
 end
 entry.position=position;entry.lastPulse=now
 return true
end
function Mix:Stop(id,now)
 local entry=self.entries[id];if entry and not entry.stopped then entry.stopped=now end
end
function Mix:Step(now,dt,voiceActive,calibrating)
 if self.destroyed then return end
 dt=math.clamp(dt,0,.25)
 local target=voiceActive and self.settings.VoiceDuck or 1
 self.duck+=(target-self.duck)*(1-math.exp(-dt*(voiceActive and 30 or 5)))
 for id,entry in pairs(self.entries) do
  if not entry.stopped and (now-entry.lastPulse>=self.settings.Timeout or now-entry.started>=self.settings.MaxLifetime) then
   entry.stopped=math.min(entry.lastPulse+self.settings.Timeout,entry.started+self.settings.MaxLifetime)
  end
  if entry.stopped and now-entry.stopped>=self.settings.FadeOut then self:Remove(id) end
 end
 local gain=calibrating and 0 or self.settings.TotalVolume/math.max(1,self.count)*self.duck
 for _,entry in pairs(self.entries) do
  local age=math.max(0,now-entry.started)
  local envelope=math.clamp(age/self.settings.FadeIn,0,1)
  local pitch=1 -- preserve the supplied recording's pitch and timing
  if entry.stopped then
   local release=math.clamp((now-entry.stopped)/self.settings.FadeOut,0,1)
   envelope*=1-release
  end
  self.update(entry.sound,entry.position,gain*envelope*(entry.isLocal and self.settings.LocalMultiplier or 1),pitch)
 end
end
function Mix:Destroy()
 if self.destroyed then return end
 self.destroyed=true;self:Clear()
end
return Mix

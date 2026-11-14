-- Bounded presentation-only one-shots. Never records voice or sends remotes.
local Mix={};Mix.__index=Mix
local function finite(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
function Mix.new(settings,create,update,destroy)
 return setmetatable({settings=settings,create=create,update=update,destroy=destroy,
  entries={},lastPlayed={},enabled=true,duck=1,voiceActive=false,suppressed=false},Mix)
end
function Mix:Clear()
 for _,entry in ipairs(self.entries) do self.destroy(entry.handle) end
 table.clear(self.entries)
end
function Mix:SetEnabled(enabled)
 if self.destroyed then return end
 self.enabled=enabled==true
 if not self.enabled then self:Clear() end
end
function Mix:SetContext(voiceActive,suppressed)
 if self.destroyed then return end
 self.voiceActive=voiceActive==true;self.suppressed=suppressed==true
 if self.voiceActive then self.duck=self.settings.VoiceDuck end
 if self.suppressed then self:Clear() end
end
function Mix:Play(kind,now,position)
 if self.destroyed or not self.enabled or self.suppressed or not finite(now) then return false end
 local cue=self.settings.Cues[kind]
 if not cue or not self.settings.Asset(kind) or (cue.Spatial and not position) then return false end
 local last=self.lastPlayed[kind]
 if last and now-last<cue.Cooldown then return false end
 if #self.entries>=self.settings.Limit then return false end
 local handle=self.create(kind,position)
 if not handle then return false end
 self.lastPlayed[kind]=now
 table.insert(self.entries,{handle=handle,started=now,expires=now+cue.Lifetime})
 -- Rebudget older voices before the new handle starts. The original WAVs
 -- have baked onset fades; a frame-driven fade would erase short transients.
 self:Step(now,0)
 return true
end
function Mix:ObserveLevel(level,temporary,now)
 if not finite(level) or level%1~=0 or level<1 or level>100 then return false end
 local previous,wasTemporary=self.level,self.temporary
 self.level=level;self.temporary=temporary==true
 if not previous or level<=previous or self.temporary or wasTemporary then return false end
 return self:Play("LevelUp",now)
end
function Mix:Step(now,dt)
 if self.destroyed or not finite(now) or not finite(dt) then return end
 if self.suppressed then self:Clear();return end
 if not self.voiceActive then self.duck+=(1-self.duck)*(1-math.exp(-math.clamp(dt,0,.25)*5)) end
 for i=#self.entries,1,-1 do
  local entry=self.entries[i]
  if now>=entry.expires then self.destroy(entry.handle);table.remove(self.entries,i) end
 end
 local gain=self.settings.TotalVolume/math.max(1,#self.entries)*self.duck
 for _,entry in ipairs(self.entries) do
  local envelope=math.clamp((entry.expires-now)/self.settings.FadeOut,0,1)
  self.update(entry.handle,gain*envelope)
 end
end
function Mix:Destroy()
 if self.destroyed then return end
 self.destroyed=true;self:Clear();table.clear(self.lastPlayed)
end
return Mix

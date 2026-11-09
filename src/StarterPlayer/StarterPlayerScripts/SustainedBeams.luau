-- Bounded client visual lifetime, independent of damage and microphone input.
local Beams={}
Beams.__index=Beams
Beams.Limit=24
Beams.Timeout=.5

function Beams.new(create,update,destroy)
 return setmetatable({create=create,update=update,destroy=destroy,entries={},count=0},Beams)
end
function Beams:Remove(id)
 local entry=self.entries[id]
 if not entry then return end
 self.entries[id]=nil
 self.count-=1
 self.destroy(entry.visual)
end
function Beams:Expire(now)
 for id,entry in pairs(self.entries) do
  if now>=entry.expires then self:Remove(id) end
 end
end
function Beams:Update(id,now,...)
 local entry=self.entries[id]
 if not entry then
  if self.count>=Beams.Limit then self:Expire(now) end
  if self.count>=Beams.Limit then return false end
  entry={visual=self.create()}
  self.entries[id]=entry
  self.count+=1
 end
 entry.expires=now+Beams.Timeout
 self.update(entry.visual,...)
 return true
end
function Beams:Clear()
 for id in pairs(self.entries) do self:Remove(id) end
end
return Beams

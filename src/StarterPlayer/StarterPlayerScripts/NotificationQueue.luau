-- Bounded UI notices. Time advances only on visible rendered frames.
local Queue={};Queue.__index=Queue
Queue.Limit=8
function Queue.new() return setmetatable({pending={}},Queue) end
local function duration(text) return math.clamp(utf8.len(text) or #text,88,264)/22 end
function Queue:Remove(key)
 if key==nil then return end
 for i=#self.pending,1,-1 do if self.pending[i].key==key then table.remove(self.pending,i) end end
 -- Removing active status opens a slot for existing queued work first.
 if self.active and self.active.key==key then self.active=table.remove(self.pending,1) end
end
function Queue:Push(text,urgent,key)
 if type(text)~="string" or text=="" then return end
 urgent=urgent==true
 if self.active and self.active.text==text then return end
 for _,entry in ipairs(self.pending) do if entry.text==text then return end end
 -- Stateful keys coalesce obsolete guidance; save has one highest-priority entry.
 if key then self:Remove(key) end
 local priority=key=="save" and 2 or urgent and 1 or 0
 local entry={text=text,urgent=urgent,key=key,priority=priority,remaining=duration(text)}
 if self.active and priority>self.active.priority then
  self.active.remaining=duration(self.active.text);self.active.presented=false
  table.insert(self.pending,1,self.active);self.active=nil
 end
 if not self.active then self.active=entry
 elseif priority>0 then
  local index=1
  while self.pending[index] and self.pending[index].priority>=priority do index+=1 end
  table.insert(self.pending,index,entry)
 else table.insert(self.pending,entry) end
 if #self.pending>Queue.Limit then
  local drop=1
  for i,item in ipairs(self.pending) do if item.priority<self.pending[drop].priority then drop=i end end
  table.remove(self.pending,drop)
 end
end
function Queue:Step(dt,visible)
 local entry=self.active
 if not entry then return "" end
 if visible then
  if entry.presented then entry.remaining-=math.clamp(dt,0,.1) end
  entry.presented=true
  if entry.remaining<=0 then self.active=table.remove(self.pending,1);entry=self.active end
 end
 return entry and entry.text or ""
end
return Queue

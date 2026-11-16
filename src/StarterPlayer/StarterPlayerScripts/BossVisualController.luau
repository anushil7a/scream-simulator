-- One nearby boss at a time; tokens cancel stale asynchronous visual construction.
local Controller={}
function Controller.new(options)
 local self={current=nil,generation=0,stopped=false}
 function self:Clear()
  self.generation+=1
  if self.current then
   if self.current.motion then self.current.motion:Destroy() end
   self.current.visual:Destroy();self.current=nil
  end
 end
 function self:Step(origin,candidates)
  if self.stopped then return end
  local chosen,best=nil,180
  if origin then
   for _,candidate in ipairs(candidates) do
    local distance=((candidate.home or candidate.center)-origin).Magnitude
    if distance<best then chosen=candidate;best=distance end
   end
  end
  if self.current and chosen and self.current.source==chosen.source and self.current.scale==chosen.scale and self.current.id==chosen.id then
   self.current.candidate=chosen;return
  end
  self:Clear()
  if not chosen then return end
  local generation=self.generation;local visual=options.create(chosen.id)
  self.current={source=chosen.source,visual=visual,scale=chosen.scale,center=chosen.center,id=chosen.id,candidate=chosen,ready=false}
  options.spawn(function()
   local function alive()return not self.stopped and self.generation==generation and chosen.source.Parent~=nil and visual.Parent~=nil end
   if not alive() then if self.generation==generation then self:Clear() end;return end
   local ok,result=pcall(options.build,visual,chosen.id,chosen.center,alive,options.pause,chosen.scale)
   if self.generation==generation then
    if not ok or not result or not alive() then self:Clear();return end
    if options.prepare then
     local prepared,motion=pcall(options.prepare,visual,chosen.id,chosen.center,chosen.scale)
     if not prepared then self:Clear();return end
     self.current.motion=motion
    end
    self.current.ready=true
   end
  end)
 end
 function self:Animate(now,dt,reduced)
  local current=self.current
  if self.stopped or not current then return end
  if not current.source.Parent or not current.visual.Parent then self:Clear();return end
  if current.ready and options.animate then
   local ok,healthy=pcall(options.animate,current,now,dt,reduced)
   if not ok or healthy==false then self:Clear() end
  end
 end
 function self:Destroy() self.stopped=true;self:Clear() end
 return self
end
return Controller

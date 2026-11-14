-- Actual engine navigation check for both public passages through each court.
-- Does not prove physical seating, player traversal or final visual quality.
return function(world)
 assert(game:GetService("RunService"):IsRunning() and game.PlaceId==0,"Local Play required")
 local count,failures,themes=0,{},{}
 for _,court in ipairs(world:GetDescendants()) do
  local center=court:GetAttribute("CourtCenter")
  if center then
   local theme=court:GetAttribute("CourtyardTheme");themes[theme]=(themes[theme] or 0)+1
   for _,axis in ipairs({Vector3.new(50,0,0),Vector3.new(0,0,50)}) do
    local path=game:GetService("PathfindingService"):CreatePath({AgentRadius=2,AgentHeight=5,AgentCanJump=false,AgentCanClimb=false})
    local ok,err=pcall(function() path:ComputeAsync(center+axis+Vector3.new(0,3,0),center-axis+Vector3.new(0,3,0)) end)
    count+=1
    if not ok or path.Status~=Enum.PathStatus.Success then table.insert(failures,{court=court:GetFullName(),status=ok and path.Status.Name or tostring(err)}) end
    path:Destroy()
   end
  end
 end
 return {routes=count,failures=failures,themes=themes,passed=count>0 and #failures==0}
end

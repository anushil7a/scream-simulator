-- State packets contain plain, acyclic tables and Roblox value types.
local Snapshot={}

function Snapshot.Equal(left,right)
 if left==right then return true end
 if type(left)~="table" or type(right)~="table" then return false end
 for key,value in pairs(left) do
  if not Snapshot.Equal(value,right[key]) then return false end
 end
 for key in pairs(right) do
  if left[key]==nil then return false end
 end
 return true
end

function Snapshot.Copy(packet)
 local copy=table.clone(packet)
 for key,value in pairs(packet) do
  if type(value)=="table" then copy[key]=Snapshot.Copy(value) end
 end
 return copy
end

return Snapshot

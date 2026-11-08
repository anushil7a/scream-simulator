-- Reconstruct aim from a trusted server origin. Cover and target eligibility
-- must still be resolved from that origin by the server on each damage tick.
local function finite(n) return n==n and math.abs(n)<math.huge end
return function(origin,aim)
 if typeof(aim)~="Vector3" or not finite(aim.X) or not finite(aim.Y) or not finite(aim.Z) then return nil end
 local delta=aim-origin
 local distance=delta.Magnitude
 if not finite(distance) or distance<.01 or distance>2048 then return nil end
 return delta.Unit
end

local make = require("./OverworldSpecs")
local scale = require("./AcademyWorldScale")
local original, _, authoredLayout = make()
local compact, _, sharedLayout = make()
local mapped = scale.Apply(compact, sharedLayout)

local function checkVector(actual, before)
 assert(#actual == #before)
 for i, component in ipairs(before) do
  assert(math.abs(actual[i] - component * .4) < 1e-8)
 end
end

assert(#compact.parts == #original.parts and #compact.routes == #original.routes)
for i, before in ipairs(original.parts) do
 local part = compact.parts[i]
 assert(part.id == before.id and part.zone == before.zone and part.collidable == before.collidable)
 checkVector(part.position, before.position)
 checkVector(part.size, before.size)
 for axis, angle in ipairs(before.rotation) do assert(part.rotation[axis] == angle) end
end
for i, before in ipairs(original.routes) do
 local route = compact.routes[i]
 assert(route.id == before.id and route.class == before.class and route.width == before.width * .4)
 checkVector(route.a, before.a)
 checkVector(route.b, before.b)
end
checkVector(mapped.boundsXZ, {-1600, 1600, -1600, 1600})
assert(mapped.arteryWidth == 32 * .4 and authoredLayout.arteryWidth == 32)
for id, before in pairs(authoredLayout.districts) do
 checkVector(mapped.districts[id].center, before.center)
 checkVector(mapped.districts[id].size, before.size)
end
for id, points in pairs(authoredLayout.worldLinks) do
 for i, point in ipairs(points) do checkVector(mapped.worldLinks[id][i], point) end
end
assert(authoredLayout.districts["01"].center[2] == 50 and mapped.districts["01"].center[2] == 20)
print(("PASS 40%% transform for %d Overworld parts, %d routes and all authored district/link markers"):format(#compact.parts, #compact.routes))

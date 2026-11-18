-- The playable Academy fixture uses 40% of each authored world dimension.
local Scale = {Factor = .4}

function Scale.Point(point)
 local scaled = table.create(#point)
 for i, axis in ipairs(point) do
  scaled[i] = axis * Scale.Factor
 end
 return scaled
end

function Scale.Apply(builder, layout)
 for _, part in ipairs(builder.parts) do
  part.position = Scale.Point(part.position)
  part.size = Scale.Point(part.size)
 end
 for _, route in ipairs(builder.routes) do
  route.a = Scale.Point(route.a)
  route.b = Scale.Point(route.b)
  route.width *= Scale.Factor
 end

 local scaled = table.clone(layout)
 scaled.boundsXZ = Scale.Point(layout.boundsXZ)
 scaled.arteryWidth = layout.arteryWidth * Scale.Factor
 scaled.districts = {}
 for id, district in pairs(layout.districts) do
  local spec = table.clone(district)
  spec.center = Scale.Point(district.center)
  spec.size = Scale.Point(district.size)
  scaled.districts[id] = spec
 end
 scaled.worldLinks = {}
 for id, points in pairs(layout.worldLinks) do
  local link = {}
  for i, point in ipairs(points) do
   link[i] = Scale.Point(point)
  end
  scaled.worldLinks[id] = link
 end
 return scaled
end

return Scale

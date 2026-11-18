local build=require("./OverworldSpecs")
local b,_,layout=build(...=="--academy")
if ...=="--academy" then
 local scale=require("./AcademyWorldScale")
 scale.Apply(b,layout)
 print("S|"..scale.Factor)
end
local function p(t) return table.concat(t,",") end
for _,s in ipairs(b.parts) do
 print(table.concat({"P",s.id,p(s.position),p(s.size),p(s.rotation),p(s.color),s.shape,s.material,
  tostring(s.collidable),tostring(s.queryable),s.collisionRole,s.zone,p(s.tags)},"|"))
end
for _,r in ipairs(b.routes) do print(table.concat({"R",r.id,p(r.a),p(r.b),r.width,r.class,p(r.link or {})},"|")) end

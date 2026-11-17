-- Luau CLI only. Execute the real constructor against minimal Roblox doubles,
-- then emit the exact same spec data for independent ray/visual review.
local parts = {}
local tags = {}
local entry = {}
function entry.GetService(_, name)
 assert(name=="CollectionService")
 return {AddTag=function(_,node,tag)
  tags[node] = tags[node] or {};table.insert(tags[node],tag)
 end}
end
local enums=setmetatable({},{__index=function() return setmetatable({},{__index=function(_,k)return k end}) end})
local origin={}; local cf=setmetatable({},{__mul=function(a,b) return a end})
local old=require("./Zone05Geometry")
local globals=getfenv(old.Build)
globals.game = entry
globals.Enum = enums
globals.Vector3 = {new=function(...) return {...} end}
globals.Color3 = {fromRGB=function(...) return {...} end}
globals.CFrame = {new=function(...) return cf end,Angles=function(...) return cf end}
globals.Instance = {new=function(class)
 local node={ClassName=class,attrs={}}
 function node:SetAttribute(name,value) self.attrs[name]=value end
 if class=="Part" then table.insert(parts,node) end
 return node
end}
local model=old.Build(origin)
assert(model.Parent==origin and model.attrs.PreviewOnly==true and model.Name=="Zone05_TidalBellFoundry")
local specs=old.GetSpecs();assert(#parts==#specs)
local seen={}
local function pack(t) return table.concat(t,",") end
for i,p in ipairs(parts) do
 local s=specs[i]
 assert(not seen[s.id] and p.Name==s.id and p.Parent==model and p.Anchored)
 seen[s.id]=true
 assert(p.CanQuery==s.collidable and p.CanCollide==s.collidable and p.CanTouch==false)
 assert(pack(p.Size)==pack(s.size) and pack(p.Color)==pack(s.color) and p.Shape==s.shape and p.Material==s.material)
 assert(p.attrs.ZoneId=="Zone05" and pack(tags[p] or {})==pack(s.tags))
 print(table.concat({"P",s.id,pack(s.position),pack(s.size),pack(s.rotation),pack(s.color),s.shape,s.material,tostring(s.collidable),pack(s.tags)},"|"))
end
for _,r in ipairs(old.Routes) do print(table.concat({"R",r.id,pack(r.a),pack(r.b),r.width},"|")) end

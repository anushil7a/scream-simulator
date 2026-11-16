local Catalog=require(game:GetService("ReplicatedStorage").Shared.BossCatalog)
local Rules=require(game:GetService("ReplicatedStorage").Shared.BossRules)
local Service={}
local function label(b,text)
 if b.displayText~=text then b.displayText=text;b.label.Text=text end
end
local function part(parent,name,size,position,color)
 local p=Instance.new("Part");p.Name=name;p.Size=size;p.Position=position;p.Color=color
 p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.Parent=parent;return p
end
function Service.new(parent,callbacks)
 local self={bosses={},callbacks=callbacks,cooldowns={}}
 local folder=Instance.new("Folder");folder.Name="BossEncounters";folder.Parent=parent
 for _,spec in ipairs(Catalog.Entries) do
  local model=Instance.new("Model");model.Name=spec.id;model.Parent=folder
  local center=Vector3.new(spec.x,0,spec.z);local color=Color3.fromRGB(table.unpack(spec.color))
  local root=part(model,"Core",Vector3.new(5,7,4),center+Vector3.new(0,5,0),color)
  for side=-1,1,2 do
   part(model,"Shoulder",Vector3.new(2,3,3),center+Vector3.new(side*3,7,0),color)
   part(model,"Leg",Vector3.new(2,3,2),center+Vector3.new(side*1.5,2,0),Color3.fromRGB(45,45,65))
  end
  part(model,"Visor",Vector3.new(3,.7,.5),center+Vector3.new(0,8.8,-2.1),Color3.fromRGB(245,235,180)).Material=Enum.Material.Neon
  for i=1,24 do
   local a=i*math.pi/12
   part(model,"Boundary",Vector3.new(1,.15,1),center+Vector3.new(math.cos(a)*spec.radius,.3,math.sin(a)*spec.radius),color).Material=Enum.Material.Neon
  end
  local board=Instance.new("BillboardGui");board.Size=UDim2.fromOffset(230,66);board.StudsOffset=Vector3.new(0,7,0);board.MaxDistance=80;board.Parent=root
  local label=Instance.new("TextLabel");label.Size=UDim2.fromScale(1,1);label.BackgroundTransparency=.25;label.BackgroundColor3=Color3.fromRGB(20,20,35);label.TextColor3=color;label.TextSize=14;label.TextWrapped=true;label.Parent=board
  local b=Rules.New(spec);b.spec=spec;b.model=model;b.root=root;b.center=center;b.label=label;b.targets={}
  local heading=spec.name.." · Lv "..spec.level.."+\nAttack inside the ring to join\n"
  b.idleText=heading.."Optional encounter";b.warningText=heading..spec.attack.." · MOVE!"
  table.insert(self.bosses,b)
 end
 function self:Valid(b,p,now)
  local c=self.callbacks.context(p,now)
  if not c or c.level<b.spec.level then return nil end
  local d=c.position-b.center
  if math.abs(d.Y)>12 or Vector3.new(d.X,0,d.Z).Magnitude>b.spec.radius then return nil end
  return c
 end
 function self:CanHit(b,p,now) return b.health>0 and now>=b.readyAt and self:Valid(b,p,now)~=nil end
 function self:Hit(b,p,damage,now)
  if not self:CanHit(b,p,now) then return 0 end
  local c=self:Valid(b,p,now)
  local actual=Rules.Hit(b,b.spec,p.UserId,c.identity,damage,now)
  if b.health<=0 then
   if b.warning then b.warning:Destroy();b.warning=nil end;b.strike=nil;b.readyAt=now+Catalog.Respawn
   for id,entry in pairs(b.credit) do
    local player=self.callbacks.player(id);local ctx=player and self:Valid(b,player,now)
    local key=b.spec.id..":"..id
    if ctx and Rules.Eligible(entry,ctx.identity,b.spec,now) and now>=(self.cooldowns[key] or 0) then
     self.cooldowns[key]=now+Catalog.RewardCooldown;self.callbacks.reward(player,b.spec,math.min(1,entry.damage/b.spec.health))
    end
   end
   b.credit={};table.clear(b.targets)
  end
  return actual
 end
 function self:Step(now)
  if now<(self.nextStep or 0) then return end;self.nextStep=now+.1
  for key,expiry in pairs(self.cooldowns) do if now>=expiry then self.cooldowns[key]=nil end end
  for _,b in ipairs(self.bosses) do
   if b.health<=0 then
    local seconds=math.ceil(math.max(0,b.readyAt-now))
    if b.displaySeconds~=seconds then
     b.displaySeconds=seconds;label(b,b.spec.name.." · returns in "..seconds.."s")
    end
    if now>=b.readyAt then Rules.Reset(b,b.spec,now) end
    continue
   end
   b.displaySeconds=nil;label(b,b.strike and b.warningText or b.idleText)
   if now-b.lastHit>Catalog.ResetAfter and b.health<b.spec.health then
    if b.warning then b.warning:Destroy();b.warning=nil end;Rules.Reset(b,b.spec,now)
   end
   local targets=b.targets;table.clear(targets)
   if next(b.credit)==nil and not b.strike then continue end
   for id,entry in pairs(b.credit) do
    local p=self.callbacks.player(id);local c=p and self:Valid(b,p,now)
    if c and c.identity==entry.identity and now-entry.at<=Catalog.CreditExpiry then table.insert(targets,{player=p,context=c}) else b.credit[id]=nil end
   end
   if b.strike then
    if now>=b.strike.at then
     local strike=b.strike;b.strike=nil
     if b.warning then b.warning:Destroy();b.warning=nil end
     for _,t in ipairs(targets) do
      local d=t.context.position-strike.position
      if Vector3.new(d.X,0,d.Z).Magnitude<=strike.radius then self.callbacks.damage(t.player,b.spec.damage,now) end
     end
    end
   elseif #targets>0 and now>=b.nextAttack then
    table.sort(targets,function(a,c) return a.player.UserId<c.player.UserId end)
    b.turn=(b.turn or 0)+1;local t=targets[(b.turn-1)%#targets+1]
    local radius=b.spec.radii[(b.turn-1)%#b.spec.radii+1]
    -- Clip hazard footprint to encounter boundary; no damage to nonparticipants.
    local d=t.context.position-b.center;d=Vector3.new(d.X,0,d.Z)
    if d.Magnitude>b.spec.radius-radius then d=d.Unit*(b.spec.radius-radius) end
    local pos=b.center+d
    b.strike={at=now+b.spec.windup,position=pos,radius=radius};b.nextAttack=now+b.spec.interval
    b.warning=part(b.model,"DodgeWarning",Vector3.new(.12,radius*2,radius*2),pos+Vector3.new(0,.5,0),Color3.fromRGB(255,110,45))
    b.warning.Shape=Enum.PartType.Cylinder;b.warning.CFrame=CFrame.new(pos+Vector3.new(0,.5,0))*CFrame.Angles(0,0,math.pi/2);b.warning.Material=Enum.Material.Neon;b.warning.Transparency=.45
   end
  end
 end
 return self
end
return Service

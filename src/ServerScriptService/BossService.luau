local Catalog=require(game:GetService("ReplicatedStorage").Shared.BossCatalog)
local Rules=require(game:GetService("ReplicatedStorage").Shared.BossRules)
local Patterns=require(game:GetService("ReplicatedStorage").Shared.BossPatterns)
local Motion=require(game:GetService("ReplicatedStorage").Shared.BossMotion)
local Service={}
local function phase(b,name)
 if b.phase~=name then
  b.phase=name;local at=workspace:GetServerTimeNow()
  b.model:SetAttribute("BossState",name);b.model:SetAttribute("BossStateAt",at)
  b.model:SetAttribute("BossWindupUntil",name=="Windup" and at+b.spec.windup or 0)
 end
end
local function pose(b)
 local m=b.motion
 b.root.CFrame=CFrame.new(b.center+Vector3.new(m.x,b.spec.aimHeight,m.z))*CFrame.Angles(0,m.yaw,0)
end
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
  local center=Vector3.new(spec.x,spec.y or 0,spec.z);local color=Color3.fromRGB(table.unpack(spec.color))
  local root=part(model,"Core",Vector3.new(5,7,4)*spec.scale,center+Vector3.new(0,spec.aimHeight,0),color)
  -- Ground-aligned enlarged anchor; client uses the same catalog scale/aimHeight.
  root.Transparency=1
  for i=1,24 do
   local a=i*math.pi/12
   part(model,"Boundary",Vector3.new(1,.15,1),center+Vector3.new(math.cos(a)*spec.radius,.3,math.sin(a)*spec.radius),color).Material=Enum.Material.Neon
  end
  local board=Instance.new("BillboardGui");board.Size=UDim2.fromOffset(260,96);board.StudsOffset=Vector3.new(0,8,0);board.MaxDistance=90;board.Parent=root
  local label=Instance.new("TextLabel");label.Size=UDim2.fromScale(1,1);label.BackgroundTransparency=.25;label.BackgroundColor3=Color3.fromRGB(20,20,35);label.TextColor3=color;label.TextSize=14;label.TextWrapped=true;label.Parent=board
  local b=Rules.New(spec);b.spec=spec;b.model=model;b.root=root;b.center=center;b.label=label;b.targets={};b.motion=Motion.New();phase(b,"Idle")
  local heading=spec.name.." · Lv "..spec.level.."+\nAttack within "..spec.radius.." studs to join\n"
  b.idleText=heading.."Optional encounter"
  table.insert(self.bosses,b)
 end
 function self:Valid(b,p,now)
  local c=self.callbacks.context(p,now)
  if not c or c.level<b.spec.level then return nil end
  local d=c.position-b.center
  if d.X~=d.X or d.Y~=d.Y or d.Z~=d.Z or math.abs(d.Y)>b.spec.engageHeight or d.X*d.X+d.Z*d.Z>b.spec.radius*b.spec.radius then return nil end
  return c
 end
 function self:CanHit(b,p,now) return b.health>0 and now>=b.readyAt and self:Valid(b,p,now)~=nil end
 function self:Hit(b,p,damage,now)
  if not self:CanHit(b,p,now) then return 0 end
  local c=self:Valid(b,p,now)
  local actual=Rules.Hit(b,b.spec,p.UserId,c.identity,damage,now)
  if b.health<=0 then
   phase(b,"Defeated")
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
  local dt=math.clamp(now-(self.lastStep or now),0,.25);self.lastStep=now
  for key,expiry in pairs(self.cooldowns) do if now>=expiry then self.cooldowns[key]=nil end end
  for _,b in ipairs(self.bosses) do
   if b.health<=0 then
    local seconds=math.ceil(math.max(0,b.readyAt-now))
    if b.displaySeconds~=seconds then
     b.displaySeconds=seconds;label(b,b.spec.name.." · returns in "..seconds.."s")
    end
    if now>=b.readyAt then Rules.Reset(b,b.spec,now);b.motion=Motion.New();pose(b);phase(b,"Idle") end
    continue
   end
   b.displaySeconds=nil;label(b,b.strike and (b.spec.name.." · Lv "..b.spec.level.."+\n"..b.strike.name.."\nMOVE off the colored ground") or b.idleText)
   if now-b.lastHit>Catalog.ResetAfter and b.health<b.spec.health then
    if b.warning then b.warning:Destroy();b.warning=nil end;Rules.Reset(b,b.spec,now)
   end
   if not b.strike then
    if now<(b.recoverUntil or 0) then phase(b,"Recovery")
    else Motion.Step(b.motion,b.spec,dt);pose(b);phase(b,"Moving") end
   end
   local targets=b.targets;table.clear(targets)
   if next(b.credit)==nil and not b.strike then continue end
   for id,entry in pairs(b.credit) do
    local p=self.callbacks.player(id);local c=p and self:Valid(b,p,now)
    if c and c.identity==entry.identity and now-entry.at<=Catalog.CreditExpiry then table.insert(targets,{player=p,context=c}) else b.credit[id]=nil end
   end
   if #targets==0 and b.strike then
    if b.warning then b.warning:Destroy();b.warning=nil end
    b.strike=nil;b.nextAttack=now+2;b.recoverUntil=now+b.spec.recovery;phase(b,"Recovery")
   end
   if b.strike then
    if now>=b.strike.at then
     local strike=b.strike;b.strike=nil;b.recoverUntil=now+b.spec.recovery;phase(b,"Recovery")
     b.model:SetAttribute("BossAttackImpactAt",workspace:GetServerTimeNow())
     b.model:SetAttribute("BossAttackImpactSerial",strike.serial)
     if b.warning then b.warning:Destroy();b.warning=nil end
     for _,t in ipairs(targets) do
      local d=t.context.position-b.center
      if strike.participants[t.player.UserId]==t.context.identity and Patterns.Hits(strike,d.X,d.Z) then self.callbacks.damage(t.player,b.spec.damage,now) end
     end
    end
   elseif #targets>0 and now>=b.nextAttack then
    table.sort(targets,function(a,c) return a.player.UserId<c.player.UserId end)
    b.turn=(b.turn or 0)+1;local t=targets[(b.turn-1)%#targets+1]
    local d=t.context.position-b.center
    local m=b.motion
    if (d.X-m.x)^2+(d.Z-m.z)^2>.01 then m.yaw=math.atan2(-(d.X-m.x),-(d.Z-m.z));pose(b) end
    local strike=Patterns.Build(b.spec.id,b.turn,d.X-m.x,d.Z-m.z)
    -- Commit both pose and ground shapes once. Never follow a target during the tell.
    for _,shape in ipairs(strike.shapes) do shape.x+=m.x;shape.z+=m.z end
    phase(b,"Windup")
    strike.participants={}
    for _,target in ipairs(targets) do strike.participants[target.player.UserId]=target.context.identity end
    b.attackSerial=(b.attackSerial or 0)+1;strike.serial=b.attackSerial
    b.model:SetAttribute("BossAttackAt",workspace:GetServerTimeNow()+b.spec.windup)
    b.model:SetAttribute("BossAttackSerial",strike.serial)
    strike.at=now+b.spec.windup;b.strike=strike;b.nextAttack=now+b.spec.interval
    local warning=Instance.new("Folder");warning.Name="DodgeWarning";warning.Parent=b.model;b.warning=warning
    for _,shape in ipairs(strike.shapes) do
     local pos=b.center+Vector3.new(shape.x,.5,shape.z)
     local size=shape.kind=="disk" and Vector3.new(.12,shape.radius*2,shape.radius*2) or Vector3.new(shape.width,.12,shape.length)
     local marker=part(warning,"Hazard",size,pos,Color3.fromRGB(table.unpack(b.spec.color)))
     if shape.kind=="disk" then marker.Shape=Enum.PartType.Cylinder;marker.CFrame=CFrame.new(pos)*CFrame.Angles(0,0,math.pi/2)
     else marker.CFrame=CFrame.new(pos)*CFrame.Angles(0,shape.angle,0) end
     marker.Material=Enum.Material.Neon;marker.Transparency=.45
    end
   end
  end
 end
 return self
end
return Service

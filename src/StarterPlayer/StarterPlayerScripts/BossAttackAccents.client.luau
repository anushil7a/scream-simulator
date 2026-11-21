-- One bounded accent set per nearby encounter. Authoritative warnings always remain.
local Players=game:GetService("Players")
local Run=game:GetService("RunService")
local Gui=game:GetService("GuiService")
local Effects=require(script.Parent:WaitForChild("BossAttackEffects"))
local states={};local stopped=false;local connection
local function clear(model)
 local s=states[model];if s and s.effect then s.effect:Destroy() end;states[model]=nil
end
local function reduced()
 local ok,value=pcall(function()return Gui.ReducedMotionEnabled end)
 return not ok or value==true or Players.LocalPlayer:GetAttribute("BossReducedEffects")~=false
end
local elapsed=0
connection=Run.Heartbeat:Connect(function(dt)
 if stopped then return end
 elapsed+=dt;if elapsed<.05 then return end;elapsed=0
 local player=Players.LocalPlayer;local root=player.Character and player.Character:FindFirstChild("HumanoidRootPart")
 local world=workspace:FindFirstChild("ScreamSimulatorWorld");local bosses=world and world:FindFirstChild("BossEncounters")
 local now=workspace:GetServerTimeNow();local seen={};local count=0
 if root and bosses and not reduced() then
  for _,model in ipairs(bosses:GetChildren()) do
   local core=model:FindFirstChild("Core")
   if core and (core.Position-root.Position).Magnitude<=Effects.Distance and count<5 then
    count+=1;seen[model]=true
    local serial=model:GetAttribute("BossAttackSerial")
    local warning=model:FindFirstChild("DodgeWarning")
    local s=states[model]
    if s and s.serial~=serial then clear(model);s=nil end
    local deadline=model:GetAttribute("BossAttackAt")
    if not s and type(serial)=="number" and warning and model:GetAttribute("BossState")=="Windup"
     and type(deadline)=="number" and deadline>now and deadline-now<=4
     and model:GetAttribute("BossAttackImpactSerial")~=serial then
     -- Replication can expose the folder before all of its committed parts.
     local expected=warning:GetAttribute("BossMarkerCount")
     if warning:GetAttribute("BossAttackSerial")==serial and type(expected)=="number" and expected>=1 and expected<=16 then
      local children=warning:GetChildren()
      if #children==expected then
       local markers={}
       for _,p in ipairs(children) do
        if p:IsA("Part") and p.Name=="Hazard" then
         table.insert(markers,{position=p.Position,frame=p.CFrame,size=p.Size,disk=p.Shape==Enum.PartType.Cylinder})
        end
       end
       if #markers==expected then
        s={serial=serial,markers=markers,mode="warning",effect=Effects.Build(workspace,model.Name,markers,false)};states[model]=s
       end
      end
     end
    end
    if s then
     local impact=model:GetAttribute("BossAttackImpactSerial");local at=model:GetAttribute("BossAttackImpactAt")
     if (s.mode=="warning" or s.mode=="awaiting") and impact==serial and type(at)=="number" and now>=at and now-at<=Effects.Lifetime then
      if s.effect then s.effect:Destroy() end;s.effect=Effects.Build(workspace,model.Name,s.markers,true);s.mode="impact";s.at=at
     elseif s.mode=="warning" and not warning then
      -- Hold only bookkeeping for replication reordering near the committed deadline.
      -- Never render an impact without its matching server confirmation.
      local deadline=model:GetAttribute("BossAttackAt")
      if type(deadline)=="number" and math.abs(now-deadline)<=.25 and model:GetAttribute("BossState")~="Defeated" then
       s.effect:Destroy();s.effect=nil;s.mode="awaiting";s.untilAt=now+.2
      else clear(model);s=nil end
     end
     if s then
      if (s.mode=="impact" and now-s.at>Effects.Lifetime) or (s.mode=="awaiting" and now>s.untilAt) then clear(model)
      elseif s.effect then s.effect:Step(s.mode=="impact" and now-s.at or 0) end
     end
    end
   end
  end
 end
 for model in pairs(states) do if not seen[model] then clear(model) end end
end)
script.Destroying:Connect(function()
 stopped=true;if connection then connection:Disconnect() end
 for model in pairs(states) do clear(model) end
end)

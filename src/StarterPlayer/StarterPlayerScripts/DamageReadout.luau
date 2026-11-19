local View={};View.__index=View
local W,H=150,44
local function finite(v)
 return type(v)=="number" and v==v and v>=0 and v<math.huge
end
local function formatNumber(v)
 if v>=1e9 then return string.format("%.2g",v) end
 if v%1~=0 then return string.format("%.1f",v) end
 return tostring(math.floor(v+.5))
end
function View.new(gui,frame,label,surface,gold,muted)
 local root=frame(gui,"DamageReadout",UDim2.fromOffset(W,H),UDim2.new())
 root.BackgroundTransparency=.05
 root.Active=false;root.Selectable=false;root.Interactable=false;root.Visible=false
 surface(root,gold)
 local header=label(root,"",UDim2.new(1,-20,0,15),UDim2.fromOffset(10,4),11,muted)
 local value=label(root,"",UDim2.new(1,-20,0,19),UDim2.fromOffset(10,19),14,gold)
 header.Name="Caption";value.Name="DamageValue";value.Font=Enum.Font.GothamBold
 for _,text in ipairs({header,value}) do
  text.TextWrapped=false;text.TextScaled=true;text.Active=false;text.Selectable=false;text.Interactable=false
  local size=Instance.new("UITextSizeConstraint");size.MinTextSize=10;size.MaxTextSize=text==header and 11 or 14;size.Parent=text
 end
 return setmetatable({root=root,header=header,value=value,enabled=false,phase=nil},View)
end
function View:Clear()
 self.phase=nil;self.root.Visible=false
end
function View:SetEnabled(enabled)
 self.enabled=enabled==true
 if not self.enabled then self:Clear() end
end
function View:Receive(phase,dps,total,now)
 if phase=="clear" then self:Clear();return end
 if not self.enabled or (phase~="active" and phase~="recap") or not finite(dps) or not finite(total) or total==0 then return end
 -- Let the recap finish only while it can be read, with a cap on stale popups.
 self.phase=phase;self.expires=now+(phase=="recap" and 12 or 13);self.left=5
 self.header.Text=phase=="recap" and "FIGHT RECAP" or "BEAM DAMAGE"
 local amount=formatNumber(total)
 self.value.Text=phase=="recap" and amount.." TOTAL DAMAGE" or formatNumber(dps).." DPS  /  "..amount.." TOTAL"
end
local function fits(x,y,v,origin,blocked)
 if x<8 or y<8 or x+W>v.X-8 or y+H>v.Y-8 then return false end
 for _,obstacle in ipairs(blocked) do
  if obstacle.Visible then
   local a=obstacle.AbsolutePosition-origin;local s=obstacle.AbsoluteSize
   if s.X>0 and s.Y>0 and x<a.X+s.X+5 and x+W+5>a.X and y<a.Y+s.Y+5 and y+H+5>a.Y then return false end
  end
 end
 return true
end
function View:Step(now,dt,available,gui,hud,tracked,guide,...)
 if not self.phase then return end
 if now>=self.expires or (self.phase=="recap" and self.left<=0) then self:Clear();return end
 if not available then self.root.Visible=false;return end
 local v,origin=gui.AbsoluteSize,gui.AbsolutePosition
 local healthY=hud.AbsolutePosition.Y-origin.Y
 local questBottom=tracked.Visible and tracked.AbsolutePosition.Y-origin.Y+tracked.AbsoluteSize.Y or healthY+hud.AbsoluteSize.Y
 local guideBottom=guide.Visible and guide.AbsolutePosition.Y-origin.Y+guide.AbsoluteSize.Y or 0
 local blocked={hud,tracked,guide,...}
 local x,y
 local landscape=v.Y<=v.X and not (v.X>=820 and healthY>=v.Y*.45)
 if v.X>=820 and healthY>=v.Y*.45 then
  x,y=14,healthY-H-8
 elseif v.Y>v.X then
  x,y=14,math.max(160,questBottom,guideBottom)+8
 else
  -- Landscape touch controls occupy the right column unusually high on a
  -- short safe area. Use the lane beside player HP, above aim/hit feedback.
  x,y=hud.AbsolutePosition.X-origin.X+hud.AbsoluteSize.X+10,74
 end
 if landscape and not fits(x,y,v,origin,blocked) then
  -- An optional guide or Talk prompt may occupy the left-center lane.
  x=math.floor(v.X*.5+68)
 end
 if not fits(x,y,v,origin,blocked) then
  -- Full notices and other gameplay UI are always higher priority.
  x,y=v.X-W-14,math.max(80,math.min(questBottom+8,140))
  if not fits(x,y,v,origin,blocked) then self.root.Visible=false;return end
 end
 local position=UDim2.fromOffset(x,y)
 if self.root.Position~=position then self.root.Position=position end
 self.root.Visible=true
 if self.phase=="recap" then self.left-=dt end
end
return View

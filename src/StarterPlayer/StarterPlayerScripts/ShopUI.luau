local Marketplace=game:GetService("MarketplaceService")
local UIS=game:GetService("UserInputService")
local Catalog=require(game:GetService("ReplicatedStorage").Shared.ShopCatalog)
local Config=require(game:GetService("ReplicatedStorage").Shared.Config)
local Shop={}
local connections,timers={},{}
local prices={}
local generation=0
local accent=Color3.fromRGB(79,225,255)
local violet=Color3.fromRGB(173,139,255)
local gold=Color3.fromRGB(255,209,111)
local ink=Color3.fromRGB(9,14,28)
local soft=Color3.fromRGB(160,178,208)
function Shop.Clear()
 generation+=1
 for _,connection in ipairs(connections) do connection:Disconnect() end
 table.clear(connections);table.clear(timers)
end
local function stroke(parent,color,thickness)
 local edge=Instance.new("UIStroke");edge.Color=color;edge.Transparency=.65;edge.Thickness=thickness or 1;edge.Parent=parent
end
local function gradient(parent,colors,rotation)
 local g=Instance.new("UIGradient");g.Color=ColorSequence.new(colors);g.Rotation=rotation or 0;g.Parent=parent;return g
end
function Shop.Tick()
 for _,timer in ipairs(timers) do
  local remaining=math.max(0,math.ceil(timer.ends-timer.serverNow-(os.clock()-timer.received)))
  local text=not timer.ready and "Boost status unavailable" or remaining>0 and string.format("ACTIVE · %02d:%02d remaining",math.floor(remaining/60),remaining%60) or "Not active"
  if timer.label.Text~=text then timer.label.Text=text end
 end
end
local function purchaseButton(item,parent,owned,data,ui,action,size,pos)
 local id=item.key=="Movement" and Config.MovementPassId or item.id
 local text=owned and "OWNED" or id<=0 and "COMING SOON" or "CHECKING PRICE…"
 local available=false
 local b=ui.button(parent,"Buy"..item.key,text,size,pos,function()
  if available then action:FireServer("ShopPurchase",item.key) end
 end,owned and Color3.fromRGB(32,75,73) or ink)
 b.TextSize=13;stroke(b,accent)
 if owned or id<=0 then b.AutoButtonColor=false;return end
 local revision=generation
 local function apply(info)
  if revision~=generation or not b.Parent then return end
  available=info and info.IsForSale==true and type(info.PriceInRobux)=="number" and data.savingAvailable==true
  b.Text=available and ("R$ "..tostring(info.PriceInRobux)) or data.savingAvailable~=true and "TEST / UNAVAILABLE" or "UNAVAILABLE"
  b.AutoButtonColor=available
 end
 local key=item.kind..":"..id;local cached=prices[key]
 if cached and os.clock()-cached.at<60 then apply(cached.info);return end
 task.spawn(function()
  local ok,info=pcall(Marketplace.GetProductInfoAsync,Marketplace,id,item.kind=="pass" and Enum.InfoType.GamePass or Enum.InfoType.Product)
  if ok then prices[key]={info=info,at=os.clock()} end
  apply(ok and info or nil)
 end)
end
function Shop.Render(data,ui,action)
 Shop.Clear()
 local narrow=ui.narrow
 local hero=ui.card(narrow and 300 or 260);hero.Name="SpectrumFeature"
 hero.BackgroundColor3=Color3.new(1,1,1)
 gradient(hero,{ColorSequenceKeypoint.new(0,Color3.fromRGB(30,49,76)),ColorSequenceKeypoint.new(1,Color3.fromRGB(39,24,61))},25)
 stroke(hero,accent)
 ui.label(hero,"01 / MAKE IT YOURS",UDim2.new(1,-32,0,20),UDim2.fromOffset(16,12),12,accent)
 local heading=ui.label(hero,"SPECTRUM",UDim2.new(1,-32,0,38),UDim2.fromOffset(16,35),30);heading.Font=Enum.Font.GothamBlack
 ui.label(hero,"One pass. Every beam color. Forever.",UDim2.new(1,-32,0,38),UDim2.fromOffset(16,78),15)
 local beam=ui.frame(hero,"SpectrumBeam",UDim2.new(1,-48,0,12),UDim2.fromOffset(24,137),Color3.new(1,1,1))
 local keys={};for i=0,6 do table.insert(keys,ColorSequenceKeypoint.new(i/6,Color3.fromHSV(i/6,.8,1))) end
 gradient(beam,keys)
 ui.frame(beam,"HotCore",UDim2.new(1,0,0,3),UDim2.fromOffset(0,4),Color3.new(1,1,1))
 for i=1,4 do
  local ring=ui.frame(hero,"EnergyRing",UDim2.fromOffset(14,42),UDim2.new(i/5,-7,0,122),accent)
  ring.BackgroundTransparency=1;stroke(ring,Color3.fromHSV(i/5,.5,1),2)
 end
 ui.label(hero,"Includes the full color mixer. Your free colors stay free.",UDim2.new(1,-32,0,narrow and 42 or 30),UDim2.fromOffset(16,167),13,soft)
 purchaseButton(Catalog.Get("Spectrum"),hero,data.spectrumPass,data,ui,action,UDim2.new(1,-32,0,44),UDim2.fromOffset(16,narrow and 238 or 206))
 for index,key in ipairs({"XP","Coins"}) do
  local item=Catalog.Get(key);local tint=key=="XP" and violet or gold
  local c=ui.card(narrow and 244 or 210);c.Name="Boost"..key;stroke(c,tint)
  local badge=ui.frame(c,"Multiplier",UDim2.fromOffset(54,54),UDim2.fromOffset(16,16),ink)
  local badgeText=ui.label(badge,"2×",UDim2.fromScale(1,1),UDim2.new(),27,tint);badgeText.TextXAlignment=Enum.TextXAlignment.Center;badgeText.Font=Enum.Font.GothamBlack
  ui.label(c,"0"..(index+1).." / "..item.tag,UDim2.new(1,-100,0,20),UDim2.fromOffset(84,13),12,tint)
  ui.label(c,item.name,UDim2.new(1,-100,0,32),UDim2.fromOffset(84,34),narrow and 18 or 22)
  ui.label(c,item.description.." Starts automatically on confirmed delivery.",UDim2.new(1,-32,0,narrow and 56 or 40),UDim2.fromOffset(16,80),14,soft)
  local shop=data.shop or {};local inventory=shop.inventory or {};local ends=shop.ends or {}
  local status=ui.label(c,shop.ready==true and "Not active" or "Boost status unavailable",UDim2.new(1,-32,0,24),UDim2.fromOffset(16,narrow and 143 or 124),13,tint)
  table.insert(timers,{label=status,ready=shop.ready==true,ends=ends[item.boost] or 0,serverNow=shop.serverNow or os.time(),received=os.clock()})
  local y=narrow and 184 or 158
  local count=inventory[item.boost] or 0
  purchaseButton(item,c,false,data,ui,action,UDim2.new(count>0 and .5 or 1,count>0 and -22 or -32,0,44),UDim2.fromOffset(16,y))
  if count>0 then
   local b=ui.button(c,"Activate"..key,"USE SAVED ("..count..")",UDim2.new(.5,-22,0,44),UDim2.new(.5,6,0,y),function()
    if shop.ready then action:FireServer("ActivateBoost",item.boost) end
   end,ink);b.TextSize=13;b.TextColor3=tint;b.AutoButtonColor=shop.ready==true
  end
 end
 local movement=ui.card(narrow and 202 or 170);stroke(movement,accent)
 ui.label(movement,"04 / FREERUNNER",UDim2.new(1,-32,0,28),UDim2.fromOffset(16,12),20,accent)
 ui.label(movement,"Chain jumps and rolls through the safe city. Standard movement rules apply inside the PvP arena.",UDim2.new(1,-32,0,narrow and 70 or 48),UDim2.fromOffset(16,48),14,soft)
 purchaseButton(Catalog.Get("Movement"),movement,data.movementPass,data,ui,action,UDim2.new(1,-32,0,44),UDim2.fromOffset(16,narrow and 142 or 110))
 ui.info("New boosts activate automatically on confirmed delivery and stack time, not multiplier. Previously saved boosts remain usable.")
 Shop.Tick()
end
function Shop.ColorMixer(data,ui,action)
 local c=ui.card(370);c.Name="ColorMixer";stroke(c,violet)
 ui.label(c,"SIGNATURE COLOR",UDim2.new(1,-32,0,28),UDim2.fromOffset(16,12),20,violet)
 ui.label(c,data.spectrumPass and "Mix any color, then equip it." or "Preview any color · unlock with Spectrum in the shop.",UDim2.new(1,-32,0,42),UDim2.fromOffset(16,44),14,soft)
 local color=data.customColor and Color3.fromHex(data.customColor) or accent
 local h,s,v=color:ToHSV();local values={h,s,v}
 local preview=ui.frame(c,"Preview",UDim2.new(1,-32,0,18),UDim2.fromOffset(16,96),color)
 ui.frame(preview,"Core",UDim2.new(1,-12,0,3),UDim2.fromOffset(6,7),Color3.new(1,1,1))
 local code=Instance.new("TextBox");code.Name="HexColor";code.Size=UDim2.new(.5,-22,0,44);code.Position=UDim2.fromOffset(16,310);code.BackgroundColor3=ink;code.TextColor3=accent;code.Font=Enum.Font.GothamBold;code.TextSize=16;code.ClearTextOnFocus=false;code.Parent=c
 local knobs,tracks={},{ }
 local function update()
  color=Color3.fromHSV(values[1],values[2],values[3]);preview.BackgroundColor3=color;code.Text="#"..color:ToHex():upper()
  for i,knob in ipairs(knobs) do knob.Position=UDim2.new(values[i],-10*values[i],.5,-10) end
  if tracks[2] then tracks[2].Color=ColorSequence.new(Color3.new(1,1,1),Color3.fromHSV(values[1],1,1)) end
  if tracks[3] then tracks[3].Color=ColorSequence.new(Color3.new(0,0,0),Color3.fromHSV(values[1],values[2],1)) end
 end
 local drag,dragInput
 for i,name in ipairs({"HUE","SATURATION","BRIGHTNESS"}) do
  ui.label(c,name,UDim2.new(1,-32,0,20),UDim2.fromOffset(16,126+(i-1)*58),12,soft)
  local bar=ui.frame(c,name,UDim2.new(1,-32,0,24),UDim2.fromOffset(16,148+(i-1)*58),Color3.new(1,1,1));bar.Active=true
  local colors={ColorSequenceKeypoint.new(0,Color3.new(0,0,0)),ColorSequenceKeypoint.new(1,accent)}
  if i==1 then colors={};for j=0,6 do table.insert(colors,ColorSequenceKeypoint.new(j/6,Color3.fromHSV(j/6,1,1))) end end
  tracks[i]=gradient(bar,colors)
  local knob=ui.frame(bar,"Thumb",UDim2.fromOffset(10,20),UDim2.new(),Color3.new(1,1,1));stroke(knob,ink);knobs[i]=knob
  bar.InputBegan:Connect(function(input)
   if input.UserInputType==Enum.UserInputType.MouseButton1 or input.UserInputType==Enum.UserInputType.Touch then
    drag={index=i,bar=bar};dragInput=input
    values[i]=math.clamp((input.Position.X-bar.AbsolutePosition.X)/math.max(1,bar.AbsoluteSize.X),0,1);update()
   end
  end)
 end
 table.insert(connections,UIS.InputChanged:Connect(function(input)
  if drag and (input==dragInput or input.UserInputType==Enum.UserInputType.MouseMovement and dragInput.UserInputType==Enum.UserInputType.MouseButton1) then
   values[drag.index]=math.clamp((input.Position.X-drag.bar.AbsolutePosition.X)/math.max(1,drag.bar.AbsoluteSize.X),0,1);update()
  end
 end))
 table.insert(connections,UIS.InputEnded:Connect(function(input) if input==dragInput then drag=nil;dragInput=nil end end))
 code.FocusLost:Connect(function()
  local hex=Catalog.Hex(code.Text)
  if hex then local a,b,d=Color3.fromHex(hex):ToHSV();values={a,b,d} end
  update()
 end)
 local equip=ui.button(c,"EquipCustom",data.spectrumPass and "EQUIP COLOR" or "PASS REQUIRED",UDim2.new(.5,-22,0,44),UDim2.new(.5,6,0,310),function()
  if data.spectrumPass then action:FireServer("SetCustomColor",color:ToHex()) end
 end,ink);equip.TextSize=13;stroke(equip,violet)
 update()
end
return Shop

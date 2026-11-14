-- Full text stays in one scroll viewport; no copied queue or per-message jobs.
local Layout=require(script.Parent.NoticeLayout)
local TextService=game:GetService("TextService")
local GOLD=Color3.fromRGB(235,190,105)
local View={};View.__index=View
function View.new(parent,text)
 local root=Instance.new("Frame");root.Name="NoticeViewport";root.BackgroundColor3=text.BackgroundColor3;root.BackgroundTransparency=.08;root.BorderSizePixel=0;root.ZIndex=30;root.Visible=false;root.Parent=parent
 local corner=Instance.new("UICorner");corner.Name="NoticeCorner";corner.CornerRadius=UDim.new(0,6);corner.Parent=root
 local stroke=Instance.new("UIStroke");stroke.Name="NoticeStroke";stroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Border;stroke.Color=GOLD;stroke.Thickness=1;stroke.Transparency=.55;stroke.Parent=root
 local scroll=Instance.new("ScrollingFrame");scroll.Name="FullNotice";scroll.BackgroundTransparency=1;scroll.BorderSizePixel=0;scroll.ScrollBarThickness=4;scroll.ScrollingDirection=Enum.ScrollingDirection.Y;scroll.Active=true;scroll.ZIndex=31;scroll.Parent=root
 text.Parent=scroll;text.AnchorPoint=Vector2.zero;text.Position=UDim2.fromOffset(6,4);text.BackgroundTransparency=1;text.ZIndex=31;text.TextWrapped=true;text.TextYAlignment=Enum.TextYAlignment.Top
 local hint=Instance.new("TextLabel");hint.Name="NoticeScrollHint";hint.BackgroundColor3=Color3.fromRGB(48,42,28);hint.BackgroundTransparency=.15;hint.BorderSizePixel=0;hint.Active=false;hint.Selectable=false;hint.Interactable=false;hint.TextColor3=Color3.fromRGB(255,214,128);hint.Font=text.Font;hint.TextSize=12;hint.ZIndex=32;hint.TextWrapped=true;hint.TextYAlignment=Enum.TextYAlignment.Top;hint.Text="Scroll for full notice";hint.Parent=scroll
 local hintCorner=Instance.new("UICorner");hintCorner.Name="NoticeScrollHintCorner";hintCorner.CornerRadius=UDim.new(0,4);hintCorner.Parent=hint
 local hintStroke=Instance.new("UIStroke");hintStroke.Name="NoticeScrollHintStroke";hintStroke.ApplyStrokeMode=Enum.ApplyStrokeMode.Border;hintStroke.Color=GOLD;hintStroke.Thickness=1;hintStroke.Transparency=.65;hintStroke.Parent=hint
 local self=setmetatable({root=root,corner=corner,stroke=stroke,scroll=scroll,text=text,hint=hint,hintCorner=hintCorner,hintStroke=hintStroke,message="",connections={},hover=false,pauseUntil=0,atBottom=false,destroyed=false},View)
 local function connect(signal,fn)table.insert(self.connections,signal:Connect(fn))end
 connect(scroll.MouseEnter,function()self.hover=true end);connect(scroll.MouseLeave,function()self.hover=false end)
 connect(scroll.InputBegan,function()self.pauseUntil=os.clock()+1 end)
 connect(scroll:GetPropertyChangedSignal("CanvasPosition"),function()self.pauseUntil=os.clock()+1 end)
 return self
end
function View:Update(message,layout,visible,now,textSize,entry)
 if self.destroyed then return end
 local fresh=false
 if message~=self.message or entry~=self.entry then self.entry=entry;self.message=message;fresh=true;self.text.Text=message;self.scroll.CanvasPosition=Vector2.zero;self.atBottom=false;self.key=nil;self.renderedHeight=nil;self.renderedHintHeight=nil end
 self.layout=layout;self.visible=visible==true and layout.available and message~=""
 self.root.Visible=self.visible;self.text.Visible=message~=""
 if not self.visible then self.hover=false;return end
 self.root.Position=UDim2.fromOffset(layout.x,layout.y)
 local rendered=self.text.TextBounds
 if not fresh and rendered and self.measuredHeight and rendered.Y>self.measuredHeight then self.renderedHeight=rendered.Y;self.key=nil end
 local hintBounds=self.hint.TextBounds
 if not fresh and self.overflow and hintBounds and self.measuredHintHeight and hintBounds.Y>self.measuredHintHeight then self.renderedHintHeight=hintBounds.Y;self.key=nil end
 local key=tostring(layout.width)..":"..layout.height..":"..textSize
 if key~=self.key then
  self.key=key;self.atBottom=false;fresh=true
  self.root.Position=UDim2.fromOffset(layout.x,layout.y);self.root.Size=UDim2.fromOffset(layout.width,layout.height)
  self.text.TextSize=textSize
  local measured=TextService:GetTextSize(message,textSize,self.text.Font,Vector2.new(layout.width-16,100000)).Y
  -- UDim offsets use whole pixels; round up so fractional text metrics never clip.
  measured=math.ceil(math.max(measured,self.renderedHeight or 0));self.measuredHeight=measured
  self.textHeight=measured+8;self.panelHeight=math.min(layout.height,math.max(44,self.textHeight));self.overflow=self.textHeight>self.panelHeight
  self.root.Size=UDim2.fromOffset(layout.width,self.panelHeight)
  -- A measured header scrolls with the body; it never covers the last line.
  local hintHeight=TextService:GetTextSize(self.hint.Text,self.hint.TextSize,self.hint.Font,Vector2.new(layout.width-16,100000)).Y
  self.measuredHintHeight=math.ceil(math.max(hintHeight,self.renderedHintHeight or 0))
  self.headerHeight=self.overflow and self.measuredHintHeight+8 or 0
  self.visibleHeight=self.panelHeight;self.contentHeight=self.textHeight+self.headerHeight
  self.scroll.Size=UDim2.new(1,0,0,self.visibleHeight);self.scroll.CanvasSize=UDim2.fromOffset(0,self.contentHeight)
  self.text.Position=UDim2.fromOffset(6,4+self.headerHeight);self.text.Size=UDim2.fromOffset(layout.width-16,measured)
  self.hint.Position=UDim2.fromOffset(6,4);self.hint.Size=UDim2.fromOffset(layout.width-16,self.measuredHintHeight);self.hint.Visible=self.overflow
 end
 self.layout={x=layout.x,y=layout.y,width=layout.width,height=self.panelHeight}
 if not self.overflow or self.scroll.CanvasPosition.Y+self.visibleHeight>=self.contentHeight-1 then self.atBottom=true end
 self.canAdvance=not fresh and self.atBottom and not self.hover and now>=self.pauseUntil
end
function View:CanAdvance()return not self.destroyed and self.visible==true and self.canAdvance==true end
function View:Overlaps(object,gui,other)
 if not self.visible or not object.Visible then return false end
 local p=object.AbsolutePosition-gui.AbsolutePosition;local s=object.AbsoluteSize
 local area=self.layout
 if other then
  if not other.Visible then return false end
  local op,os=other.AbsolutePosition-gui.AbsolutePosition,other.AbsoluteSize
  area={x=op.X,y=op.Y,width=os.X,height=os.Y}
 end
 return Layout.Overlaps(area,{x=p.X,y=p.Y,width=s.X,height=s.Y})
end
function View:Destroy()
 if self.destroyed then return end;self.destroyed=true
 for _,c in ipairs(self.connections)do c:Disconnect()end;self.connections={};self.root:Destroy()
end
return View

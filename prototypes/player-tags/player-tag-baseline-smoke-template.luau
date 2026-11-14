local function V(x,y,z)
 return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},{__add=function(a,b)return V(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end,__sub=function(a,b)return V(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end,__div=function(a,n)return V(a.X/n,a.Y/n,a.Z/n)end,__index=function(a,k)if k=="Magnitude"then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z)end end})
end
Vector3={new=V,zero=V()}
CFrame={new=function(x,y,z)return {Position=V(x,y,z)}end,lookAt=function(pos,target)return {Position=pos,target=target}end}
Enum=setmetatable({},{__index=function(t,k)local e=setmetatable({},{__index=function(_,n)return n end});rawset(t,k,e);return e end})
local activePlayer,activeCamera,objects,logs,warnings,waitHook,watch,cloneError,destroyError
local function event()local e={};function e:Connect(f)self.callback=f;return {Disconnect=function()e.callback=nil end}end;return e end
local function object(class)
 local o={ClassName=class,Name=class,children={},Anchored=false,CFrame=CFrame.new(),Size=V(2,2,1),Transparency=0}
 if class=="Humanoid"then for k,v in pairs({DisplayDistanceType="Viewer",NameDisplayDistance=100,HealthDisplayDistance=100,HealthDisplayType="DisplayWhenDamaged",NameOcclusion="NoOcclusion",DisplayName="Original",Health=100,MaxHealth=100})do o[k]=v end end
 function o:IsA(c)return self.ClassName==c or c=="BasePart" and self.ClassName=="Part" or c=="LuaSourceContainer" and self.ClassName=="LocalScript"end
 function o:FindFirstChild(n)for _,c in ipairs(self.children)do if c.Name==n and not c.destroyed then return c end end end
 function o:FindFirstChildOfClass(c)for _,v in ipairs(self.children)do if v.ClassName==c and not v.destroyed then return v end end end
 function o:GetDescendants()local result={};local function visit(p)for _,c in ipairs(p.children)do table.insert(result,c);visit(c)end end;visit(self);return result end
 function o:Destroy()if destroyError and self.Name=="PlayerTagReviewControl"then error("mock destroy error")end;self.destroyed=true;self.Parent=nil end
 function o:PivotTo(cf)for _,c in ipairs(self.children)do if c:IsA("BasePart")then c.CFrame=cf end end end
 function o:Clone()
  if cloneError and self==activePlayer.Character then error("mock clone error")end
  local n=object(self.ClassName);for k,v in pairs(self)do if type(v)~="function" and k~="children" and k~="Parent" and k~="destroyed"then n[k]=v end end
  for _,c in ipairs(self.children)do if not c.destroyed then c:Clone().Parent=n end end;return n
 end
 function o:Invoke(...)return self.OnInvoke(...)end
 setmetatable(o,{__index=function(t,k)if k=="Position"then return t.CFrame.Position end;return t:FindFirstChild(k)end,__newindex=function(t,k,v)rawset(t,k,v);if k=="Parent" and v then table.insert(v.children,t)end end})
 table.insert(objects,o);return o
end
Instance={new=object}
local function reset()
 objects={};logs={};warnings={};waitHook=nil;cloneError=false;destroyError=false
 workspace={CurrentCamera={CameraType="Custom",CameraSubject="original",CFrame=CFrame.new(3,5,7),ViewportSize=V(1280,720)}};activeCamera=workspace.CurrentCamera;workspace.children={}
 local character=object("Model");character.Archivable=false
 local root=object("Part");root.Name="HumanoidRootPart";root.CFrame=CFrame.new(8,3,9);root.Parent=character
 local head=object("Part");head.Name="Head";head.Parent=character
 local hum=object("Humanoid");hum.Parent=character
 local scriptCopy=object("LocalScript");scriptCopy.Parent=character
 activePlayer=object("Player");activePlayer.Name="LocalViewer";activePlayer.Character=character
 local pg=object("PlayerGui");pg.Parent=activePlayer
 local players={LocalPlayer=activePlayer,GetPlayerFromCharacter=function(_,c)if c==character then return activePlayer end end}
 local http={JSONEncode=function(_,v)return v end,JSONDecode=function(_,v)return v end}
 game={PlaceId=0,GameId=0,GetService=function(_,name)return ({RunService={IsStudio=function()return true end},Players=players,HttpService=http})[name]end}
 script={Destroying=event()}
 task={wait=function()if waitHook then local f=waitHook;waitHook=nil;f()end end,delay=function(_,fn)watch={fn=fn};return watch end,cancel=function(t)t.cancelled=true end}
 print=function(...)table.insert(logs,{...})end;warn=function(...)table.insert(warnings,{...})end
 return root,hum,pg
end
local function run()
__SOURCE__
end
local assertions=0;local function check(v,m)assert(v,m);assertions+=1 end
local root,hum,pg=reset();local old=root.CFrame;local cam=activeCamera.CFrame;run()
local control=pg:FindFirstChild("PlayerTagReviewControl");check(control~=nil,"Startup control");check(#logs==2 and logs[2][1]=="PLAYER_TAG_READY","Actual startup reaches ready");check(activePlayer.Character.Archivable==false,"Archivable restored")
local snap=control:Invoke("Case",9);check(snap.viewer.NameOcclusion=="OccludeAll" and snap.subject.NameOcclusion=="OccludeAll","Occlusion9")
snap=control:Invoke("Case",12);check(snap.viewer.NameOcclusion=="NoOcclusion" and snap.subject.NameOcclusion=="OccludeAll","Occlusion12 isolates viewer")
check(#control:Invoke("Cases")==14,"Case count")
destroyError=true;control:Invoke("Stop");check(root.CFrame==old and not root.Anchored,"Root restored despite destroy error");check(activeCamera.CameraType=="Custom" and activeCamera.CFrame==cam,"Camera restored despite error");check(hum.NameOcclusion=="NoOcclusion","Properties restored");check(watch.cancelled,"Timer cancelled")
root,hum,pg=reset();cloneError=true;run();check(#warnings>0 and warnings[#warnings][1]=="PLAYER_TAG_SETUP_FAILED","Setup error caught");check(not root.Anchored and activeCamera.CameraType=="Custom","Error no mutation");check(activePlayer.Character.Archivable==false,"Error archivable restore")
root,hum,pg=reset();run();control=pg:FindFirstChild("PlayerTagReviewControl");waitHook=function()control:Invoke("Stop")end;local ok=pcall(function()control:Invoke("Case",2)end);check(not ok,"Stop during settle rejects result");check(not root.Anchored and activeCamera.CameraType=="Custom","Cancelled cleanup")
root,hum,pg=reset();run();watch.fn();check(not root.Anchored and activeCamera.CameraType=="Custom","Automatic disposal")
return assertions

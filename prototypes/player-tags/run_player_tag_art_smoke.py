from pathlib import Path
import subprocess
b=Path(__file__).resolve().parent;out=b.parents[1]/'build'/'player-tag-prototype-smoke';out.mkdir(parents=True,exist_ok=True);s=(b/'player-tag-baseline-smoke-template.luau').read_text(encoding='utf-8-sig')
s=s.replace('Vector3={new=V,zero=V()}','Vector3={new=V,zero=V()}\nVector2={new=V};UDim={new=function(a,b)return {a,b}end};UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end,fromScale=function(...)return {...}end};Color3={fromRGB=function(...)return {...}end}')
s=s.replace('local o={ClassName=class,','local o={TextFits=true,TextBounds=V(100,16),AbsoluteSize=V(200,34),ClassName=class,')
s=s.replace('RunService={IsStudio=function()return true end},Players=players','RunService={IsStudio=function()return true end,RenderStepped={Wait=function()if waitHook then local f=waitHook;waitHook=nil;f()end end}},TextService={GetTextSize=function(_,text)return V(#text*8,16)end},Players=players')
needle='check(#control:Invoke("Cases")==14,"Case count")'
addition='''
for i=1,6 do
 local a=control:Invoke("Prototype",i)
 check(a.prototype and a.prototype.healthEquivalent==false,"Art scope")
 check(a.subject.DisplayDistanceType=="None" and a.viewer.DisplayDistanceType=="Viewer","Only dummy suppressed")
 check(a.viewer.NameOcclusion=="NoOcclusion","Untouched viewer occlusion for prototype")
 check(a.prototype.maxDistance==80 and not a.prototype.alwaysOnTop,"Bounded occluding billboard")
end
local again=control:Invoke("Case",2);check(again.prototype==nil and again.subject.DisplayDistanceType=="Viewer","Baseline restored after art")
'''
s=s.replace(needle,needle+addition)
source=(b/'player-tag-art.client.luau').read_text(encoding='utf-8');p=out/'player-tag-art-smoke.luau';p.write_text('local realPrint=print\nlocal function smoke()\n'+s.replace('__SOURCE__',source)+'\nend\nrealPrint("WHOLE_ART_FIXTURE_SMOKE",smoke())\n',encoding='utf-8')
r=subprocess.run(['luau',str(p)],capture_output=True,text=True,encoding='utf-8');print(r.stdout);assert r.returncode==0,r.stderr

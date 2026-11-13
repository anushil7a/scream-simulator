"""Disposable native layout fixture: actual client with fake microphone/remotes.
No profiles, purchases, live stores, network input or publication.
"""
from pathlib import Path
import json, subprocess, sys
root=Path(__file__).resolve().parents[1]
out=root/'build'
subprocess.run([sys.executable,str(root/'tests/build_ui_preview.py'),'390','844'],check=True)
source=(out/'StudioUIPreview.luau').read_text(encoding='utf-8')
source=source[:source.rindex('local report={}')] + r'''
;(function()
local checks=0
local function check(ok,message) assert(ok,message);checks+=1 end
local report={}
local cases={
 {name="new-locked",aura="Gold",pass=false},
 {name="legacy-free",aura="Mint",pass=false},
 {name="saved-custom",aura="Gold",pass=true,custom="0A2F53",equipped=true},
 {name="inactive-custom",aura="Violet",pass=true,custom="A0B0C0",equipped=false},
 {name="new-owner",aura="Gold",pass=true},
}
for _,view in ipairs({{390,844,true},{844,390,true},{1280,720,false}}) do
 gui.Size=UDim2.fromOffset(view[1],view[2]);fixtureTouch=view[3]
 Run.RenderStepped:Wait();Run.RenderStepped:Wait()
 check(tabs.Screams.Text=="BEAMS","Visible collection tab not renamed")
 for _,case in ipairs(cases) do
  data.aura=case.aura;data.spectrumPass=case.pass;data.customColor=case.custom;data.useCustomColor=case.equipped==true
  selected="Style";modal.Visible=true;renderedMenuKey=nil;render()
  Run.RenderStepped:Wait();Run.RenderStepped:Wait()
  local mixer=content:FindFirstChild("ColorMixer")
  check(mixer~=nil,"Mixer missing")
  local hue=mixer:FindFirstChild("HUE")
  check(hue and hue.AbsoluteSize.Y>=44,"Hue touch target too small")
  check(not mixer:FindFirstChild("Preview") and not mixer:FindFirstChild("SATURATION") and not mixer:FindFirstChild("BRIGHTNESS") and not mixer:FindFirstChild("HexColor"),"Retired controls remain")
  local equip=mixer:FindFirstChild("EquipCustom")
  check(equip and equip.AbsoluteSize.Y>=44,"Equip touch target too small")
  check(equip.Text==(case.pass and "EQUIP COLOR" or "PASS REQUIRED"),"Ownership display wrong")
  local base=content:FindFirstChild("BaseColor",true)
  check(base and base.AbsoluteSize.Y>=44,"Yellow base control missing")
  check(data.customColor==case.custom and data.aura==case.aura,"Rendering changed saved color")
  local expected=case.custom or Config.Auras[case.aura]:ToHex():upper()
  check(mixer.SelectedColor.Text=="Selected color #"..expected,"Saved shade not preserved in display")
  local clipped={}
  for _,obj in ipairs(content:GetDescendants()) do
   if (obj:IsA("TextLabel") or obj:IsA("TextButton")) and obj.Visible and obj.Text~="" then
    if not obj.TextFits then table.insert(clipped,obj.Text) end
   end
   check(not obj:IsA("TextBox"),"Editable hex bypass remains")
  end
  check(#clipped==0,"Clipped style text: "..table.concat(clipped," | "))
  table.insert(report,{viewport=tostring(gui.AbsoluteSize),case=case.name,clipped=clipped,hueSize=tostring(hue.AbsoluteSize),selected=mixer.SelectedColor.Text})
 end
end
local result={checks=checks,cases=report,limits="Synthetic state and microphone; layout only. No real input, ownership service or persistence."}
local encoded=game:GetService("HttpService"):JSONEncode(result)
workspace:SetAttribute("StyleReviewResult",encoded)
print("STYLE_REVIEW_RESULT "..encoded)
end)()
'''
(out/'StyleReview.client.luau').write_text(source,encoding='utf-8')
project={'name':'StyleReview_DO_NOT_PUBLISH','tree':{'$className':'DataModel',
 'ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(root/'src/ReplicatedStorage/Shared')}},
 'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(out/'StyleReview.client.luau')}}},
 'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[40,1,40],'Position':[0,-5,0]}}}}}
project_path=out/'StyleReview.project.json';project_path.write_text(json.dumps(project))
subprocess.run(['rojo','build',str(project_path),'-o',str(out/'StyleReview.rbxl')],check=True)
subprocess.run(['luau-compile',str(out/'StyleReview.client.luau')],check=True,stdout=subprocess.DEVNULL)
print('Built/compiled native style fixture; not executed by this builder.')

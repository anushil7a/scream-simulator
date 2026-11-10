"""Build local visual previews; fake UI state, no saves or purchase prompts."""
from pathlib import Path
import json,subprocess,sys
root=Path(__file__).resolve().parents[1]
out=root/'build'
subprocess.run([sys.executable,str(root/'tests/build_ui_preview.py'),'390','844'],check=True)
ui=(out/'StudioUIPreview.luau').read_text()
ui=ui.replace('return report', '''for _,row in ipairs(report) do print("SHOP_LAYOUT_ROW "..game:GetService("HttpService"):JSONEncode(row)) end
mic.ready=true;modal.Visible=true;selected="Shop";render();toastUntil=0
''')
(out/'ShopReview.client.luau').write_text(ui)
for name,client in [('ShopReviewVerified',out/'ShopReview.client.luau'),('BeamReview',root/'tests/StudioBeamVisuals.client.luau')]:
    project={'name':name+'_DO_NOT_PUBLISH','tree':{'$className':'DataModel',
        'ReplicatedStorage':{'$className':'ReplicatedStorage','Shared':{'$path':str(root/'src/ReplicatedStorage/Shared')},'BeamVisuals':{'$path':str(root/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau')}},
        'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':str(client)}}},
        'Lighting':{'$className':'Lighting','$properties':{'Technology':'Future','ClockTime':0,'Brightness':0,'Ambient':[0.04,0.06,0.12],'OutdoorAmbient':[0.04,0.06,0.12]}},
        'Workspace':{'$className':'Workspace','Floor':{'$className':'Part','$properties':{'Anchored':True,'Size':[400,1,400],'Position':[0,-5,0]}}}
    }}
    path=out/(name+'.project.json');path.write_text(json.dumps(project))
    subprocess.run(['rojo','build',str(path),'-o',str(out/(name+'.rbxl'))],check=True)

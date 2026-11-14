"""Actual gameplay Settings label/callback and cue mixer; fake handles, no playback."""
from pathlib import Path
import argparse, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
src=(ROOT/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text(encoding='utf-8')
a=src.index('  local cueCard=card(58);local cueButton');b=src.index('\n  info(',a);fragment=src[a:b]
old='local function cueLabel()return not gameplayAudioSettings.Ready() and "GAMEPLAY SFX: PENDING UPLOAD" or "GAMEPLAY SFX: "..(gameplayAudio.enabled and "LOW" or "OFF") end'
def replace_label(fragment,label):
 start=fragment.index('local function cueLabel()');end=fragment.index('\n  cueButton=',start)
 return fragment[:start]+label+fragment[end:]
setup=r'''
local settings=require('../src/ReplicatedStorage/Shared/GameplayAudioConfig')
local Mix=require('../src/StarterPlayer/StarterPlayerScripts/CueAudioMix')
local n=0;local function check(v,m)assert(v,m);n+=1 end
local UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end}
local function card()return {}end
local rendered
local function button(_,name,text,size,pos,callback)rendered={Text=text,callback=callback};return rendered end
local gameplayAudioSettings=settings;local destroyed=0
local gameplayAudio=Mix.new(settings,function()return {}end,function()end,function()destroyed+=1 end)
local function render()
'''
checks=r'''
 return rendered
end
local keys={};for key in pairs(settings.Cues)do table.insert(keys,key)end;table.sort(keys)
for _,mode in ipairs({'empty','partial','all'})do
 for _,key in ipairs(keys)do settings.Cues[key].AssetId=''end
 if mode~='empty'then settings.Cues[keys[1]].AssetId='123'end
 if mode=='all'then for _,key in ipairs(keys)do settings.Cues[key].AssetId='123'end end
 local expectedReady=mode~='empty';check(settings.Ready()==expectedReady,'Readiness any-cue semantics changed')
 local ids={};for _,key in ipairs(keys)do ids[key]=settings.Cues[key].AssetId end
 gameplayAudio:SetEnabled(false)
 local ui=render();check(ui.Text=='GAMEPLAY SFX: OFF','OFF state hidden by pending upload')
 ui.callback();check(gameplayAudio.enabled,'Enable callback failed')
 local on=expectedReady and 'GAMEPLAY SFX: LOW' or 'GAMEPLAY SFX: LOW (PENDING)'
 check(ui.Text==on,'Enabled label missing LOW or pending distinction')
 ui=render();check(ui.Text==on and gameplayAudio.enabled,'Reopen lost enabled label/state')
 local before=destroyed
 if expectedReady then check(gameplayAudio:Play(keys[1],100,{}),'Configured fake cue not admitted')
 else check(not gameplayAudio:Play(keys[1],100,{}),'Empty cue assets unexpectedly played')end
 ui.callback();check(not gameplayAudio.enabled and ui.Text=='GAMEPLAY SFX: OFF','Disable callback or label failed')
 check(#gameplayAudio.entries==0 and destroyed==before+(expectedReady and 1 or 0),'OFF failed to clear existing fake cue')
 check(not gameplayAudio:Play(keys[1],101,{}),'Disabled fake cue played')
 ui=render();check(ui.Text=='GAMEPLAY SFX: OFF' and not gameplayAudio.enabled,'Reopen lost OFF state')
 for _,key in ipairs(keys)do check(settings.Cues[key].AssetId==ids[key],'UI altered configured asset IDs')end
 gameplayAudio.lastPlayed={}
end
print('PASS',n,'actual cue Settings/mixer assertions; fake audio handles only')
'''
def run(fragment,error=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:f.write(setup+fragment+checks);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if error:assert r.returncode and error in out,out;print('PASS negative control:',error)
 else:assert r.returncode==0,out;print(out.strip())
if args.baseline:run(replace_label(fragment,old),'OFF state hidden by pending upload')
else:
 run(fragment)
 if args.negative_controls:
  run(replace_label(fragment,old),'OFF state hidden by pending upload')
  mutant=fragment.replace('gameplayAudio:SetEnabled(not gameplayAudio.enabled)','gameplayAudio:SetEnabled(true)');assert mutant!=fragment
  run(mutant,'Disable callback or label failed')
  mutant=fragment.replace('cueButton.Text=cueLabel()','cueButton.Text="GAMEPLAY SFX: OFF"');assert mutant!=fragment
  run(mutant,'Enabled label missing LOW or pending distinction')

"""Actual Client event/render/HUD slices and real control/hit/rig modules; synthetic events only."""
from pathlib import Path
import argparse
import subprocess
import tempfile
import beam_contact_visuals as support

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / 'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'


def fragments(client):
    helpers = client[client.index('local function blocked()'):client.index('local function beginCapture(')]
    start = client.index('connectClient(remotes.Effect.OnClientEvent,function(')
    event = client[start:client.index('\nlocal elapsed=0', start)]
    render_end = client.index(' -- A current local acknowledgement,', client.index('connectClient(Run.RenderStepped'))
    render_start = client.rfind(' if sustainedBeams then', 0, render_end)
    render = client[render_start:render_end]
    hud_start = client.index(' local confirmed=hitFeedback:Read(')
    hud = client[hud_start:client.index(' meter.Visible=', hud_start)]
    assert event.count('BeamVisuals.Contact(') == render.count('BeamVisuals.Animate(') == 1
    return helpers, event, render, hud


SETUP = r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local BeamVisuals=Visuals
local Hits=require('../src/StarterPlayer/StarterPlayerScripts/HitFeedback')
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local Beams=require('../src/StarterPlayer/StarterPlayerScripts/SustainedBeams')
local hitFeedback=Hits.new();local sustainedBeams=Beams.new(BeamVisuals.Create,BeamVisuals.Update,BeamVisuals.Destroy)
local attrs={};local root={Position=Vector3.zero};local h={Health=100,PlatformStand=false}
local character={FindFirstChild=function()return root end,FindFirstChildOfClass=function()return h end}
local p={UserId=7,Character=character,GetAttribute=function(_,key)return attrs[key]end}
workspace.GetServerTimeNow=function()return clock end
workspace.CurrentCamera={CFrame={Position=Vector3.zero}}
local GuiService={MenuIsOpen=false};local typing;local UIS={GetFocusedTextBox=function()return typing end}
local modal={Visible=false};local devPanel={Visible=false};local conversationPanel={Visible=false}
local mic={ready=true};local data={voiceEligible=true,settings={reducedShake=false}}
local clientDestroyed=false;local windowFocused=true;local platformReducedMotion=false
local gate={Cancel=function(self)self.next=nil end,Step=function(self)local n=self.next;self.next=nil;return n end}
local sent={};local sustainedControl=Controls.new(gate,function(verb,arg)table.insert(sent,{verb,arg})end,function()return {}end)
local callbacks={};local function connectClient(signal,callback)callbacks[signal]=callback end
local remotes={Effect={OnClientEvent={}}};local gold=color
local Players={GetPlayerByUserId=function(_,id)return (id==7 or id==8) and {} or nil end}
local Config={Auras={Gold=color},GetSound=function()return nil end}
local attackAudioSettings={Range=100};local stops,pulses,cues,screenHits,screenClears=0,0,0,0,0
local attackAudio={Stop=function()stops+=1 end,Remove=function()end,Pulse=function()pulses+=1 end}
local beamScreenFeedback={Hit=function()screenHits+=1 end,Begin=function()end,Clear=function()screenClears+=1 end}
local function playGameplayCue(kind)check(kind=='Hit','Hit changed sound cue');cues+=1 end
local beamFrame=0;local gameplayVisible=true;local hitText={}
'''

CHECKS = r'''
local send=callbacks[remotes.Effect.OnClientEvent]
local function beam(id)send('SustainedBeam',Vector3.zero,id or 7,'Gold',Vector3.zAxis,40,7,nil,100)end
local anchor=vec(2,1,24)
local function make(ack)
 sustainedBeams:Clear();BeamVisuals.Clear();hitFeedback=Hits.new();sustainedControl:Cancel();sustainedControl:SetArmed(true)
 clock+=1;beamFrame=0;windowFocused=true;platformReducedMotion=false;GuiService.MenuIsOpen=false;typing=nil
 modal.Visible=false;devPanel.Visible=false;conversationPanel.Visible=false;h.Health=100;h.PlatformStand=false
 mic.ready=true;data.voiceEligible=true;data.settings.reducedShake=false;workspace.CurrentCamera.CFrame.Position=Vector3.zero
 attrs={SustainedActive=false};cues=0;screenHits=0
 gate.next='start';sustainedControl:Step(.001,clock,0,true,true,false,0)
 local id=sustainedControl.attack.sequence;attrs.SustainedActive=true;attrs.SustainedSequence=id
 if ack~=false then sustainedControl:Step(.001,clock,0,true,true,true,id)end
 beam();local rig=sustainedBeams.entries[7].visual;frame(1/30)
 check(not rig.contactPosition and #rig.contact.parts==0,'Beam packet inferred hit')
 return rig,id
end
local function hit(id,total,pos)send('SustainedHit',pos,id,total);hud()end
local function retained(total)
 check(cues==1 and screenHits==1 and hitFeedback:Read(clock)==total and hitText.Visible and hitText.Text==total..' DAMAGE','Accepted hit lost retained sound/HUD')
end
local rig,id=make();check(sustainedControl.attack.acknowledged,'Real Controls did not acknowledge')
hit(id,10,anchor);retained(10);frame(1/30)
check(rig.contactPosition==anchor and rig.contactSequence==id and #rig.contact.parts==16,'Current accepted hit missing contact')
local born=rig.contactBorn;clock+=.1;hit(id,11,vec(3,2,25));frame(1/30)
check(cues==2 and hitText.Text=='11 DAMAGE' and rig.contactBorn==born and rig.contactPosition==anchor,'Increasing total extended contact cooldown')
clock=born+.4;beam();frame(1/30);check(#rig.contact.parts==0,'Expired pulse remained')
for _,total in ipairs({11,10,1})do hit(id,total,anchor);frame(1/30);check(cues==2 and #rig.contact.parts==0,'Duplicate/backward total replayed contact')end
hit(id-1,20,anchor);check(cues==2 and not rig.contactPosition,'Stale accepted history replayed contact')
hit(id,12,anchor);frame(1/30);check(cues==3 and #rig.contact.parts==16 and hitText.Text=='12 DAMAGE','Increasing confirmed total after cooldown rejected')
-- A monotonic HitFeedback result alone cannot decorate a newer current rig.
for _,case in ipairs({
 {'stale sequence',function(n)return n-1 end},
 {'future sequence',function(n)return n+1 end},
 {'no acknowledgement',nil,function()sustainedControl.attack.acknowledged=false end},
 {'no local attack',nil,function()sustainedControl:Cancel()end},
 {'inactive server',nil,function()attrs.SustainedActive=false end},
 {'server sequence mismatch',nil,function(n)attrs.SustainedSequence=n+1 end},
 {'local sequence mismatch',nil,function(n)sustainedControl.attack.sequence=n+1 end},
 {'expired entry',nil,function()sustainedBeams.entries[7].expires=clock end},
 {'missing rig',nil,function()sustainedBeams:Remove(7)end},
 {'ended rig',nil,function()send('SustainedBeamEnd',nil,7)end},
})do
 rig,id=make();if case[3]then case[3](id)end
 local packet=case[2] and case[2](id) or id
 hit(packet,10,anchor);retained(10)
 check(not rig.contactPosition,'Ineligible hit decorated new rig: '..case[1]);frame(1/30)
 check(not rig.contactPosition and #rig.contact.parts==0,'Ineligible hit decorated new rig: '..case[1])
end
for _,position in ipairs({false,'bad',{},vec(0/0,1,24),vec(1,math.huge,24),vec(0,0,181)})do
 rig,id=make();if position==false then hit(id,10,nil)else hit(id,10,position)end;retained(10);frame(1/30)
 check(not rig.contactPosition and #rig.contact.parts==0,'Missing/malformed target decorated rig')
end
rig,id=make(false);hit(id,10,anchor);retained(10);frame(1/30);check(not rig.contactPosition,'Unacknowledged real control decorated rig')
local blockers={
 function(v)windowFocused=not v end,function(v)mic.ready=not v end,function(v)data.voiceEligible=not v end,
 function(v)GuiService.MenuIsOpen=v end,function(v)typing=v and {} or nil end,
 function(v)modal.Visible=v end,function(v)devPanel.Visible=v end,function(v)conversationPanel.Visible=v end,
 function(v)h.Health=v and 0 or 100 end,function(v)h.PlatformStand=v end,
 function(v)attrs.ProtectionEnds=v and clock+1 or 0 end,function(v)attrs.DodgeEnds=v and clock+1 or 0 end,
 function(v)attrs.KnockdownEnds=v and clock+1 or 0 end}
for i,block in ipairs(blockers)do
 rig,id=make();block(true);hit(id,10,anchor);retained(10)
 check(not rig.contactPosition,'Blocked hit created contact '..i);frame(1/30)
 check(not rig.contactPosition and #rig.contact.parts==0,'Blocked hit created contact '..i)
 block(false)
 rig,id=make();hit(id,10,anchor);frame(1/30);check(#rig.contact.parts==16,'Cleanup fixture contact missing')
 block(true);clock+=.01;frame(1/30)
 check(not rig.contactPosition and #rig.contact.parts==0,'Blocked frame retained contact '..i)
 block(false);frame(1/30);check(#rig.contact.parts==0,'Unblock replayed contact '..i)
end
for _,case in ipairs({
 {'cancel',function()sustainedControl:Cancel()end},
 {'disarm',function()sustainedControl:SetArmed(false)end},
 {'inactive',function()attrs.SustainedActive=false end},
 {'mismatch',function(n)attrs.SustainedSequence=n+1 end},
 {'lost acknowledgement',function()sustainedControl.attack.acknowledged=false end},
 {'contact owner mismatch',function(n,r)r.contactSequence=n-1 end}})do
 rig,id=make();hit(id,10,anchor);frame(1/30);check(#rig.contact.parts==16,'Current contact fixture missing')
 case[2](id,rig);clock+=.01;frame(1/30)
 check(not rig.contactPosition and #rig.contact.parts==0,'Current-state frame gate retained contact: '..case[1])
end
rig,id=make();hit(id,10,anchor);frame(1/30)
local before=#rig.parts;platformReducedMotion=true;clock+=.02;frame(1/30)
check(#rig.contact.parts==8 and #rig.parts==before and rig.parts[1].Material==Enum.Material.SmoothPlastic,'OS quiet contact changed core tier or missed quiet mode')
data.settings.reducedShake=true;clock+=.02;frame(1/30);check(#rig.contact.parts==8 and #rig.parts==4,'Game reduced mode missed contact/core policy')
data.settings.reducedShake=false;platformReducedMotion=false;workspace.CurrentCamera.CFrame.Position=vec(0,0,111);frame(1/30)
check(#rig.contact.parts==8 and #rig.parts==4,'Far contact/core policy changed')
workspace.CurrentCamera.CFrame.Position=vec(0,0,181);frame(1/30);check(#rig.contact.parts==0 and not rig.contactPosition,'Culled client retained contact')
workspace.CurrentCamera.CFrame.Position=Vector3.zero;frame(1/30);check(#rig.contact.parts==0,'Client return replayed culled contact')
rig,id=make();hit(id,10,anchor);frame(1/30);send('SustainedBeamEnd',nil,8);check(sustainedBeams.entries[7]~=nil,'Remote end removed local rig')
send('SustainedBeamEnd',nil,7);check(not sustainedBeams.entries[7] and #rig.contact.parts==0 and stops>0 and screenClears>0,'Local end retained contact/audio/screen state')
rig,id=make();hit(id,10,anchor);frame(1/30);clock=sustainedBeams.entries[7].expires;frame(1/30)
check(not sustainedBeams.entries[7] and #rig.parts==0 and #rig.contact.parts==0,'Expired client entry retained contact')
sustainedBeams:Destroy();sustainedControl:Destroy();BeamVisuals.Clear();check(BeamVisuals.Budget()==0 and made==dead,'Integrated cleanup leaked')
print('PASS',checks,'actual Client contact integration checks; real acknowledgement/hit/manager/renderer, mocked transport/HUD/audio')
'''


def build(client, visual):
    helpers, event, render, hud = fragments(client)
    return support.fixture(visual, SETUP + helpers + event + '\nlocal function frame(dt)\n' + render + '\nend\nlocal function hud()\n' + hud + '\nend\n' + CHECKS)


def run(client, visual, expected=None):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', prefix='tmp_contact_client_', dir=ROOT / 'tests', delete=False) as f:
        path = Path(f.name)
        f.write(build(client, visual))
    try:
        result = subprocess.run(['luau', str(path)], cwd=ROOT, capture_output=True, text=True, timeout=30)
    finally:
        path.unlink()
    output = result.stdout + result.stderr
    if expected:
        assert result.returncode and expected in output, output
        print('PASS control:', expected)
    else:
        assert result.returncode == 0, output
        print(output.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    client = CLIENT.read_text(encoding='utf-8-sig')
    visual = support.VISUAL.read_text(encoding='utf-8-sig')
    run(client, visual)
    if args.negative_controls:
        helpers, event, render, hud = fragments(client)
        cases = [
            (event, 'if hitFeedback:Accept(id,aura,os.clock()) then', 'if (function()hitFeedback:Accept(id,aura,os.clock());return true end)() then', 'Duplicate/backward total replayed'),
            (event, 'attack and attack.acknowledged and attack.sequence==id', 'attack and attack.sequence==id', 'Ineligible hit decorated new rig: no acknowledgement'),
            (event, 'and attack.sequence==id', '', 'Ineligible hit decorated new rig: local sequence mismatch'),
            (event, 'and p:GetAttribute("SustainedActive")==true', '', 'Ineligible hit decorated new rig: inactive server'),
            (event, 'and p:GetAttribute("SustainedSequence")==id', '', 'Ineligible hit decorated new rig: server sequence mismatch'),
            (event, 'now<entry.expires', 'true', 'Ineligible hit decorated new rig: expired entry'),
            (event, 'and windowFocused and not beamBlocked()', '', 'Blocked hit created contact'),
            (event, 'playGameplayCue("Hit");', '', 'Accepted hit lost retained sound/HUD'),
            (hud, 'hitText.Visible=gameplayVisible and confirmed~=nil', 'hitText.Visible=false', 'Accepted hit lost retained sound/HUD'),
            (render, 'windowFocused and not beamBlocked() and attack', 'attack', 'Blocked frame retained contact'),
            (render, 'attack and attack.acknowledged', 'attack', 'Current-state frame gate retained contact: lost acknowledgement'),
            (render, 'and p:GetAttribute("SustainedActive")==true', '', 'Current-state frame gate retained contact: inactive'),
            (render, 'and p:GetAttribute("SustainedSequence")==attack.sequence', '', 'Current-state frame gate retained contact: mismatch'),
            (render, 'entry.visual.contactSequence==attack.sequence', 'true', 'Current-state frame gate retained contact: contact owner mismatch'),
            (render, 'platformReducedMotion)', 'false)', 'OS quiet contact changed core tier or missed quiet mode'),
        ]
        for fragment, old, new, expected in cases:
            assert fragment.count(old) == 1, old
            assert client.count(fragment) == 1
            run(client.replace(fragment, fragment.replace(old, new)), visual, expected)


if __name__ == '__main__':
    main()

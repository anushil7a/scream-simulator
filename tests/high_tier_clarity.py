"""Actual high-tier styling against b76c94f; mocked Parts/orientation, no native clarity claim."""
from pathlib import Path
import argparse
import subprocess
import tempfile
import beam_contact_visuals as support
from review_baseline import contact_renderer

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b76c94fafd65be4cec85f1c5f2caa4355262e43b'
CHECKS = r'''
local white=Color3.fromRGB(245,252,255);local black=Color3.fromRGB(0,0,0)
local function sameColor(a,b)return a and b and near(a.R,b.R) and near(a.G,b.G) and near(a.B,b.B) end
local function hierarchy(rig,spec,tint,age)
 local collarEnd=5+spec.rings*10;local ribbonEnd=collarEnd+spec.strands*12
 for i,p in ipairs(rig.parts)do
  if i>=6 and i<=collarEnd then
   local ring=math.floor((i-6)/10)+1;local travel=(age*(.6+spec.tier*.025)+ring/spec.rings)%1
   check(p.Material==(ring==1 and Enum.Material.Neon or Enum.Material.SmoothPlastic),'High-tier collar material hierarchy lost')
   check(near(p.Size.Y,ring==1 and .16+spec.tier*.012 or .1) and p.Size.Y==p.Size.Z,'High-tier collar thickness hierarchy lost')
   check(equal(p.Color,ring==1 and tint or tint:Lerp(black,.2)),'High-tier support tint changed')
   check(near(p.Transparency,ring==1 and .26+travel*.32 or .6+travel*.25),'High-tier support alpha changed')
  elseif i>collarEnd and i<=ribbonEnd then
   check(p.Material==Enum.Material.SmoothPlastic and equal(p.Color,tint:Lerp(white,.12)) and p.Transparency==.42,'High-tier ribbon stayed a white emissive net')
  elseif i>ribbonEnd then
   check(p.Material==Enum.Material.SmoothPlastic and equal(p.Color,tint) and p.Transparency==.55,'High-tier corona competed with contact')
  end
 end
 local bright=0;for i=6,#rig.parts do if rig.parts[i].Material==Enum.Material.Neon then bright+=1 end end
 check(bright==10,'High-tier lost exactly one bright collar')
 check(rig.parts[1].Transparency==.78,'High-tier outer shell transparency stayed opaque')
 check(rig.parts[2].Transparency==.7,'High-tier body transparency stayed opaque')
end
-- Frozen profile identities include every ten-level unlock and threshold boundary.
local prior
for _,level in ipairs({1,9,10,19,20,29,30,39,40,49,50,59,60,69,70,79,80,89,90,99,100})do
 local current=StyleSource.Detail(level,false,0);local old=OldStyle.Detail(level,false,0)
 for _,key in ipairs({'tier','rings','strands','sparks','collar','ribbon','turns'})do check(current[key]==old[key],'Milestone profile changed: '..key)end
 local identity=current.rings..current.strands..current.sparks..current.collar..current.ribbon..current.turns
 if level==1 or level%10==0 then check(identity~=prior,'Ten-level identity collapsed');prior=identity end
end
for _,level in ipairs({79,80,89,90,99,100})do
 for _,tint in ipairs({color,Color3.fromRGB(65,100,220)})do
  for _,age in ipairs({.04,.6,1.1})do
   local spec=StyleSource.Detail(level,false,0);local current=create(level);local old=Baseline.Create()
   Visuals.Update(current,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
   Baseline.Update(old,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
   local time=clock+age;Visuals.Animate(current,time,Vector3.zero,false);Baseline.Animate(old,time,Vector3.zero,false)
   unchanged(old.parts,current.parts,level>=80 and spec or nil)
   if level>=80 then hierarchy(current,spec,tint,age)end
   check(Visuals.Contact(current,vec(2,1,24),time,7) and Baseline.Contact(old,vec(2,1,24),time,7),'Contact differential setup failed')
   for _,mode in ipairs({{false,0,false},{false,0,true},{true,0,false},{false,0,false,true},{false,111,false},{false,181,false}})do
    local viewer=vec(0,0,mode[2])
    Visuals.Update(current,Vector3.zero,Vector3.zAxis,40,7,tint,level,mode[4] or false)
    Baseline.Update(old,Vector3.zero,Vector3.zAxis,40,7,tint,level,mode[4] or false)
    Visuals.Animate(current,time+.07,viewer,mode[1],true,mode[3]);Baseline.Animate(old,time+.07,viewer,mode[1],true,mode[3])
    local highSpec=level>=80 and not mode[1] and not mode[4] and mode[2]==0 and spec or nil
    unchanged(old.parts,current.parts,highSpec)
    if mode[1] or mode[3] or mode[4] or mode[2]>110 then
     unchanged(old.contact.parts,current.contact.parts)
    else
     local progress=.25;local ease=1-(1-progress)^3;local heat=(1-progress)^2;local fade=progress*progress
     local extent=1.65+ease*.75;local inner=extent*(.52+ease*.24)
     spokes(current.contact.parts,vec(2,1,24),8,extent,inner,.2-.08*progress,.12-.07*progress)
     local backing,core=current.contact.parts[1],current.contact.parts[2]
     check(backing.Material==Enum.Material.SmoothPlastic and core.Material==Enum.Material.Neon,'High-tier contact material hierarchy changed')
     check(near(backing.Transparency,.1+fade*.82) and near(core.Transparency,.05+fade*.9),'High-tier regular contact alpha changed')
     check(sameColor(backing.Color,tint:Lerp(black,.8)),'High-tier regular contact backing color changed')
     check(sameColor(core.Color,tint:Lerp(white,.2+.55*heat)),'High-tier regular contact core color changed')
    end
   end
   Visuals.Destroy(current);Baseline.Destroy(old)
  end
 end
end
Visuals.Clear();Baseline.Clear();check(Visuals.Budget()==0 and Baseline.Budget()==0 and made==dead,'High-tier differential cleanup leaked')
print('PASS',checks,'high-tier hierarchy/frozen-property/contact/profile assertions; pool/lifetime covered by retained contact suite')
'''


def run(source, baseline, expected=None):
    prefix = support.CHECKS[:support.CHECKS.index('-- Preserve the original oracle')]
    body = support.fixture(source, baseline + prefix + CHECKS)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', prefix='tmp_high_tier_', dir=ROOT / 'tests', delete=False) as f:
        path = Path(f.name)
        f.write(body)
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
    source = support.VISUAL.read_text(encoding='utf-8-sig')
    old_visual = contact_renderer().decode('utf-8')
    old_style = subprocess.check_output(['git', 'show', '5622daa54424e639e7d3f671b2e453ff377b2cb6:src/ReplicatedStorage/Shared/BeamStyle.luau'], cwd=ROOT, text=True)
    old_visual = old_visual.replace('require(game:GetService("ReplicatedStorage").Shared.BeamStyle)', 'OldStyle')
    baseline = '\nlocal OldStyle=(function()\n' + old_style + '\nend)()\nlocal Baseline=(function()\n' + old_visual + '\nend)()\n'
    run(source, baseline)
    if args.negative_controls:
        cases = [
            ('local high=tier>=8', 'local high=tier>=7', 'Original beam property changed'),
            ('local high=tier>=8', 'local high=tier>=9', 'High-tier collar material hierarchy lost'),
            ('local support=high and ring>1', 'local support=false', 'High-tier collar material hierarchy lost'),
            ('support and .1 or .16+tier*.012', 'support and .2 or .16+tier*.012', 'High-tier collar thickness hierarchy lost'),
            ('support and .6+travel*.25', 'support and .3+travel*.25', 'High-tier support alpha changed'),
            ('color:Lerp(white,high and .12 or .4)', 'color:Lerp(white,.4)', 'High-tier ribbon stayed a white emissive net'),
            ('high and .55 or .3', 'high and .3 or .3', 'High-tier corona competed with contact'),
            ('radius*(detailed and .10 or .28)', 'radius*(detailed and .11 or .28)', 'Original beam property changed'),
            ('rig.contactPosition-contactDir*.7', 'rig.contactPosition-contactDir*.6', 'Contact stroke left target front plane'),
            ('high and .7 or .18', '.18', 'High-tier body transparency stayed opaque'),
            ('high and .78 or .55', '.55', 'High-tier outer shell transparency stayed opaque'),
            ('local ease=1-(1-progress)^3', 'local ease=progress', 'Contact stroke lost open center'),
            ('color:Lerp(white,quietContact and .3 or .2+.55*heat)', 'color:Lerp(white,.3)', 'High-tier regular contact core color changed'),
            ('quietContact and .1 or .12-.07*progress', '.1', 'Contact stroke thickness mismatch'),
        ]
        for old, new, expected in cases:
            assert source.count(old) == 1, old
            run(source.replace(old, new), baseline, expected)


if __name__ == '__main__':
    main()

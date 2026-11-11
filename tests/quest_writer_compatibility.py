"""Offline actual Profiles acquisition/claim compatibility; fake store, not a deployment guard."""
from pathlib import Path
import argparse,hashlib,json,subprocess,tempfile
import combat_quests as fixture
ROOT=Path(__file__).resolve().parents[1]
PIN=ROOT/'tests/fixtures/quest-writer-7a0b044'

def build(mutation=None):
    meta=json.loads((PIN/'provenance.json').read_text())
    for name,item in meta['files'].items():
        assert hashlib.sha256((PIN/name).read_bytes()).hexdigest()==item['sha256'], 'Historical fixture hash mismatch: '+name
    old_profile=(PIN/'Profiles.luau').read_text()
    old_lease=(PIN/'ProfileLease.luau').read_text()
    old_catalog=(PIN/'QuestCatalog.luau').read_text()
    code=fixture.build()
    code=code[:-len(fixture.CHECKS)]
    if mutation=='candidate_drops_claims':
        code=code.replace('local old=raw.quests[q.id]', 'local old=(q.id~="practice_beams" and q.id~="arena_assist") and raw.quests[q.id]')
    if mutation=='claim_replay':
        code=code.replace('if v and not v.claimed and v.progress>=q.goal then', 'if v and v.progress>=q.goal then')
    historical="local oldConfig=table.clone(Config)\ndo local Config=oldConfig\n"+old_catalog+"\nend\n"
    historical+="function oldConfig.GetQuest(id) for _,q in ipairs(oldConfig.Quests) do if q.id==id then return q end end end\n"
    historical+="local oldLease=(function()\n"+old_lease+"\nend)()\n"
    historical+="local function oldProfileFactory() local outerRequire=require;local require=function(name) if name=='Config' then return oldConfig elseif name=='Lease' then return oldLease else return outerRequire(name) end end\n"+old_profile+"\nend\n"
    if mutation=='old_knows_new':
        historical+="table.insert(oldConfig.Quests,Config.GetQuest('practice_beams'));table.insert(oldConfig.Quests,Config.GetQuest('arena_assist'))\n"
    return code+historical+CHECKS

CHECKS=r"""
local n=0;local function check(ok,message)assert(ok,message);n+=1 end
-- Verify catalog parity independently of the current additive entries.
local ids={nick=true,garden=true,beach=true,delivery=true,crowd=true,sprint=true,dodge=true,arena=true}
local legacyCount=0
for _,q in ipairs(oldConfig.Quests)do
 if ids[q.id] then local current=Config.GetQuest(q.id);check(current.goal==q.goal and current.xp==q.xp and current.coins==q.coins and current.event==q.event,'Legacy reward/catalog parity changed');legacyCount+=1 end
end
check(legacyCount==8,'Historical catalog lost original IDs')
local function moduleFor(old) return old and oldProfileFactory() or loadProfiles() end
local function acquire(module)
 now+=10;clock+=10;local d,ok=module.Load(7);check(ok,'Fake acquisition failed');return d
end
local function release(module,data)check(module.Save(7,data,true),'Fake release failed')end
local function attach(data) local s={data=data,collected={}};sessions[p]=s;return s end
local function completeAndClaim(data,id)
 local s=attach(data);local q=Config.GetQuest(id);accept(p,s,id)
 for i=1,q.goal do questProgress(p,q.event)end
 claim(p,s,id);return s
end
for _,id in ipairs({'practice_beams','arena_assist'})do
 local q=Config.GetQuest(id)
 -- Old initial profile -> new legitimate claim -> compatible current rejoin.
 durable=P.Default();durable.quests.garden={progress=3,claimed=true};durable.availableQuests.garden=true
 earned=0
 local original=moduleFor(true);local originalData=acquire(original);release(original,originalData)
 local candidate=moduleFor(false);local data=acquire(candidate);completeAndClaim(data,id)
 check(data.coins==q.coins and earned==q.xp and data.quests[id].claimed,'First candidate reward failed')
 release(candidate,data)
 local compatible=moduleFor(false);local compatibleData=acquire(compatible)
 check(compatibleData.quests[id] and compatibleData.quests[id].claimed,'Current-current lost claim')
 local currentSession=attach(compatibleData);claim(p,currentSession,id);claim(p,currentSession,id)
 check(compatibleData.coins==q.coins and earned==q.xp,'Current-current replayed claim')
 check(compatibleData.quests.garden.claimed,'Current writer lost old claim');release(compatible,compatibleData)
 -- Historical acquisition alone commits destructive sanitization, before Save.
 local old=moduleFor(true);local oldData=acquire(old)
 check(durable.quests[id]==nil and oldData.quests[id]==nil,'Historical acquisition did not erase additive claim')
 check(durable.coins==q.coins and oldData.coins==q.coins,'Historical writer discarded earned coins')
 check(durable.quests.garden.claimed and oldData.quests.garden.claimed,'Historical writer lost known claim')
 release(old,oldData)
 local nextCandidate=moduleFor(false);local nextData=acquire(nextCandidate)
 completeAndClaim(nextData,id)
 check(nextData.coins==2*q.coins and earned==2*q.xp and nextData.quests[id].claimed,'Mixed writer duplicate reward not reproduced')
 release(nextCandidate,nextData)
 check(durable.coins==2*q.coins and durable.quests.garden.claimed,'Mixed writer replay not durably demonstrated')
 print('REPRO',id,'historical acquisition erases claim; coins',q.coins,'->',durable.coins,'XP callback total',earned)
end
print('PASS',n,'writer compatibility assertions; exact pinned historical persistence/catalog, fake store and reward callbacks; not full historical server or deployment safety')
"""

def writer_probe_source(profiles_source, lease_source, quest_catalog_source):
    """Assemble mocked writer modules from caller-verified repository source.

    quest_catalog_source is executable exact Config.Quests assignment/additions,
    not an entire Config module. Caller owns extraction and provenance checks.
    This is necessary compatibility evidence, not a full writer-safety proof.
    """
    code=fixture.build();code=code[:-len(fixture.CHECKS)]
    code+="local probeConfig=table.clone(Config)\ndo local Config=probeConfig\n"+quest_catalog_source+"\nend\n"
    code+="local probeLease=(function()\n"+lease_source+"\nend)()\n"
    code+="local probe=(function() local outerRequire=require;local require=function(name) if name=='Config' then return probeConfig elseif name=='Lease' then return probeLease else return outerRequire(name) end end\n"+profiles_source+"\nend)()\n"
    return code

def _probe_writer(config_source, profiles_source, lease_source, timeout):
    """Offline full writer acquire/release -> candidate reload retention probe.

    Exact writer catalog and Profiles/Lease; unrelated Config methods deliberately
    use current fixture implementations. Not complete historical game execution.
    Unsupported catalog boundaries fail closed. No Git/network dependency here.
    """
    start='Config.Quests={'
    end='local questGivers='
    if config_source.count(start)!=1 or config_source.count(end)!=1:
        return False,'Unsupported writer quest catalog boundaries'
    a=config_source.index(start);b=config_source.index(end,a)
    catalog=config_source[a:b]
    if 'function Profiles.Load(' not in profiles_source or 'function Profiles.Save(' not in profiles_source:
        return False,'Unsupported writer profile lifecycle'
    code=writer_probe_source(profiles_source,lease_source,catalog)
    code+=r"""
local function independentCopy(value)
 if type(value)~='table' then return value end
 local result={};for key,item in pairs(value) do result[key]=independentCopy(item) end;return result
end
local function verify(data,seed,stage)
 for id in pairs(seed.availableQuests) do
  local wanted=seed.quests[id];local v=data.quests[id]
  if wanted then
   assert(v and v.progress==wanted.progress and v.claimed==wanted.claimed,'Writer altered quest '..id..' at '..stage)
  else assert(v==nil,'Writer invented quest progress '..id..' at '..stage) end
  assert(data.availableQuests[id]==true,'Writer lost discovery '..id..' at '..stage)
 end
 assert(data.coins==seed.coins and data.level==seed.level and data.xp==seed.xp,'Writer changed unrelated economy')
end
for _,kind in ipairs({'partial','completed-unclaimed','claimed','discovered-only'}) do
 local seed=P.Default();seed.coins=177;seed.level=20;seed.xp=7
 for _,q in ipairs(Config.Quests) do
  if kind~='discovered-only' then
   seed.quests[q.id]={progress=kind=='partial' and math.max(0,q.goal-1) or q.goal,claimed=kind=='claimed'}
  end
  seed.availableQuests[q.id]=true
 end
 local expected=independentCopy(seed)
 durable=seed;now+=10;clock+=10
 local loaded,allowed=probe.Load(7);assert(allowed,'Writer acquisition failed')
 verify(loaded,expected,'writer load');verify(durable,expected,'writer acquisition storage')
 assert(probe.Save(7,loaded,true),'Writer release failed');verify(durable,expected,'writer release')
 now+=10;clock+=10
 local current=loadProfiles();local reloaded,writable=current.Load(7);assert(writable,'Candidate rejoin failed')
 verify(reloaded,expected,'candidate reload');assert(current.Save(7,reloaded,true),'Candidate release failed');verify(durable,expected,'candidate release')
end
print('PASS all current quest partial/completed-unclaimed/claimed/discovered-only states through writer acquisition/release and candidate reload; mocked noncatalog configuration')
"""
    path=None
    try:
        with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False) as f:
            path=Path(f.name);f.write(code)
        result=subprocess.run(['luau',str(path)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8',timeout=timeout)
        return result.returncode==0,result.stdout+result.stderr
    finally:
        if path is not None:path.unlink(missing_ok=True)

def probe_writer(config_source, profiles_source, lease_source, *, timeout=10):
    """Fail closed on unsupported source, setup/runtime failure or bounded process timeout."""
    try:
        if not 0<timeout<=10:return False,'Invalid probe timeout'
        return _probe_writer(config_source,profiles_source,lease_source,timeout)
    except subprocess.TimeoutExpired:
        return False,f'Writer probe timeout after {timeout} seconds'
    except Exception as error:
        return False,f'Writer probe setup/runtime failure: {type(error).__name__}: {error}'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
    result=fixture.run(build());print(result.stdout+result.stderr,end='');assert result.returncode==0
    current_config=(ROOT/'src/ReplicatedStorage/Shared/Config.luau').read_text()
    current_profiles=(ROOT/'src/ServerScriptService/Profiles.luau').read_text()
    current_lease=(ROOT/'src/ReplicatedStorage/Shared/ProfileLease.luau').read_text()
    ok,output=probe_writer(current_config,current_profiles,current_lease);assert ok,output
    print('PASS current writer lifecycle probe (all current IDs, four explicit states)')
    old_config=(PIN/'QuestCatalog.luau').read_text()+'local questGivers={}'
    ok,output=probe_writer(old_config,(PIN/'Profiles.luau').read_text(),(PIN/'ProfileLease.luau').read_text())
    assert not ok and 'Writer altered quest' in output and 'at writer load' in output,output
    print('PASS historical writer lifecycle probe rejects claim/progress loss')
    if args.negative_controls:
        availability='for _,q in ipairs(Config.Quests) do if raw.availableQuests[q.id]==true then data.availableQuests[q.id]=true end end'
        assert current_profiles.count(availability)==1
        changed=current_profiles.replace(availability,'-- intentionally omit discovered-only preservation')
        ok,output=probe_writer(current_config,changed,current_lease)
        assert not ok and 'Writer lost discovery' in output,output
        print('PASS negative control: discovered_only_loss')
        progress='progress=wholeNumber(old.progress,0,0,q.goal)'
        assert current_profiles.count(progress)==1
        changed=current_profiles.replace(progress,'progress=(old.claimed~=true and old.progress==q.goal) and 0 or wholeNumber(old.progress,0,0,q.goal)')
        ok,output=probe_writer(current_config,changed,current_lease)
        assert not ok and 'Writer altered quest' in output,output
        print('PASS negative control: completed_unclaimed_loss')
        destructive=current_profiles.replace('function Profiles.Sanitize(raw)', 'function Profiles.Sanitize(raw) if type(raw)=="table" and type(raw.quests)=="table" then for _,v in pairs(raw.quests) do if type(v)=="table" then v.progress=0;v.claimed=false end end end')
        assert destructive!=current_profiles
        ok,output=probe_writer(current_config,destructive,current_lease)
        assert not ok and 'Writer altered quest' in output,output
        print('PASS negative control: in_place_raw_mutation')
        hanging=current_profiles.replace('function Profiles.Load(userId)','function Profiles.Load(userId) while true do end')
        assert hanging!=current_profiles
        ok,output=probe_writer(current_config,hanging,current_lease,timeout=.2)
        assert not ok and 'timeout' in output,output
        print('PASS negative control: hung_writer_timeout')
        ok,output=probe_writer('local questGivers={} Config.Quests={}',current_profiles,current_lease)
        assert not ok and 'setup/runtime failure' in output,output
        print('PASS negative control: reversed_catalog_setup')
        for name,old,new in [('probe_claim_loss','claimed=old.claimed==true','claimed=false'),('probe_partial_loss','wholeNumber(old.progress,0,0,q.goal)','0')]:
            changed=current_profiles.replace(old,new);assert changed!=current_profiles
            ok,output=probe_writer(current_config,changed,current_lease)
            assert not ok and 'Writer altered quest' in output,output
            print('PASS negative control:',name)
        ok,output=probe_writer('unsupported',current_profiles,current_lease)
        assert not ok and 'Unsupported' in output
        print('PASS negative control: unsupported_catalog')
        for mutation,message in [('candidate_drops_claims','Current-current lost claim'),('claim_replay','Current-current replayed claim'),('old_knows_new','Historical acquisition did not erase additive claim')]:
            result=fixture.run(build(mutation));output=result.stdout+result.stderr
            assert result.returncode and message in output,output
            print('PASS negative control:',mutation)
if __name__=='__main__':main()

"""Actual Config/Profiles/lease/quest handlers and reward helpers; isolated mocked store only."""
from pathlib import Path
import argparse,subprocess
import combat_quests as f
ROOT=Path(__file__).resolve().parents[1]
def build(mutation=None,baseline=False):
 def change(c,p,b):
  if baseline:
   c=f.inline_compact_layout(subprocess.check_output(['git','show','53d6213:src/ReplicatedStorage/Shared/Config.luau'],cwd=ROOT,text=True,encoding='utf-8'),ROOT)
   b=subprocess.check_output(['git','show','53d6213:src/ServerScriptService/Bootstrap.server.luau'],cwd=ROOT,text=True,encoding='utf-8')
  if mutation:c,p,b=mutation(c,p,b)
  return c,p,b
 code=f.build(mutation=change);code=code[:-len(f.CHECKS)]
 server=f.read('src/ServerScriptService/Bootstrap.server.luau')
 helpers=server[server.index('local function coins('):server.index('local function questProgress(')]
 old="local function coins(p,amount)sessions[p].data.coins+=amount;return amount end\nlocal function xp(p,amount)earned+=amount;if reenter then local f=reenter;reenter=nil;f()end;return amount end"
 assert old in code
 code=code.replace(old,"local function parts()return nil,nil,nil end\nlocal VoiceCombat=Combat\n"+helpers)
 return code+CHECKS
CHECKS=r'''
local n=0;local function check(ok,m)assert(ok,m);n+=1 end
local q=Config.GetQuest('practice_beams')
check(q and q.retired==true and q.goal==3 and q.xp==60 and q.coins==25 and q.event=='PracticeBeam','Retirement tombstone changed')
check(q.menuAvailable~=true and q.description==nil,'Retired objective still advertised')
local kinds={'absent','discovered','zero','partial1','partial2','complete','claimed'}
for _,kind in ipairs(kinds)do
 local seed=P.Default();seed.level=20;seed.xp=7;seed.coins=123;seed.achievements.FirstBeam=true
 seed.quests.garden={progress=1,claimed=false};seed.availableQuests.garden=true
 local wanted=kind=='zero' and 0 or kind=='partial1' and 1 or kind=='partial2' and 2 or 3
 if kind~='absent' then seed.availableQuests.practice_beams=true end
 if kind~='absent' and kind~='discovered' then seed.quests.practice_beams={progress=wanted,claimed=kind=='claimed'}end
 local function preserved(d)
  local v=d.quests.practice_beams
  check((kind=='absent' or kind=='discovered') and v==nil or v and v.progress==wanted and v.claimed==(kind=='claimed'),'Retired counter/claim lost')
  check(d.availableQuests.practice_beams==(kind~='absent' and true or nil),'Retired discovery lost')
  check(d.achievements.FirstBeam==true and d.quests.garden.progress==1 and not d.quests.garden.claimed,'Historical/unrelated state lost')
  check(d.level==20 and d.xp==7 and d.coins==123,'Sanitizer changed economy')
 end
 local clean=seed;for _=1,3 do clean=P.Sanitize(clean);preserved(clean)end
 durable=clean;now+=10;clock+=10
 local loaded,allowed=P.Load(7);check(allowed,'Retirement fake acquisition failed');preserved(loaded)
 check(P.Save(7,loaded,true),'Retirement fake save failed');now+=10;clock+=10
 local data,writable=P.Load(7);check(writable,'Retirement fake reload failed');preserved(data)
 local s={data=data,collected={},activeQuest='garden'};sessions[p]=s
 accept(p,s,'practice_beams');check(s.activeQuest=='garden','Retired accept changed active task')
 local v=data.quests.practice_beams
 check((kind=='absent' or kind=='discovered') and v==nil or v and v.progress==wanted,'Retired accept rewrote progress')
 s.activeQuest='practice_beams';local noticeBefore=notices
 questProgress(p,'PracticeBeam',3)
 check(notices==noticeBefore and ((v==nil and data.quests.practice_beams==nil) or v.progress==wanted),'Retired progress/event accepted')
 s.activeQuest='garden'
 local repeated=false
 Commerce.Multiplier=function()
  if not repeated then repeated=true;claim(p,s,'practice_beams')end
  return 1
 end
 claim(p,s,'practice_beams');claim(p,s,'practice_beams');Commerce.Multiplier=function()return 1 end
 local rewarded=kind=='complete'
 check(data.coins==123+(rewarded and 25 or 0) and data.xp==7+(rewarded and 60 or 0) and data.level==20,'Retired reward paid incorrectly/repeatedly')
 check(s.activeQuest=='garden' and data.quests.garden.progress==1,'Retired claim reset unrelated active task')
 if rewarded then check(data.quests.practice_beams.claimed==true,'Earned retirement reward not consumed')end
 check(P.Save(7,data,true),'Postclaim fake save failed');now+=10;clock+=10
 local rejoined,ok=P.Load(7);check(ok,'Postclaim fake rejoin failed');sessions[p]={data=rejoined,collected={}}
 claim(p,sessions[p],'practice_beams');claim(p,sessions[p],'practice_beams')
 check(rejoined.coins==data.coins and rejoined.xp==data.xp,'Retired reward replayed after reload')
 check(P.Save(7,rejoined,true),'Final fake release failed')
end
print('PASS '..n..' retirement assertions with actual sanitizer/lease/reward handlers; fake store only')
'''
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
 result=f.run(build(baseline=args.baseline));out=result.stdout+result.stderr
 if args.baseline:
  assert result.returncode and 'Retirement tombstone changed' in out,out;print('PASS pinned pre-retirement baseline lacks tombstone')
 else:
  assert result.returncode==0,out;print(out.strip())
 if args.negative_controls:
  for index,old,new,message in [(0,'retired=true','retired=false','Retirement tombstone changed'),(2,'if q and q.retired==true then return end','','Retired accept changed active task'),(2,' or q.retired==true','','Retired progress/event accepted'),(2,'v.claimed=true;if q.id=="nick"','if q.id=="nick"','Retired reward paid incorrectly/repeatedly'),(1,'local old=raw.quests[q.id]','local old=q.id~="practice_beams" and raw.quests[q.id]','Retired counter/claim lost'),(1,'if raw.availableQuests[q.id]==true','if q.id~="practice_beams" and raw.availableQuests[q.id]==true','Retired discovery lost'),(1,'"FoundNick","NickChampion","FirstBeam"','"FoundNick","NickChampion"','Historical/unrelated state lost')]:
   def mutation(c,p,b):
    values=[c,p,b];assert old in values[index],old;values[index]=values[index].replace(old,new,1);return tuple(values)
   result=f.run(build(mutation));out=result.stdout+result.stderr
   assert result.returncode and message in out,out;print('PASS negative control:',message)

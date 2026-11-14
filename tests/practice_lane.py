"""Retired mic-lane source contracts and exact preserved archive; no native execution."""
from pathlib import Path
import argparse,hashlib,json,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
FILES=['src/ServerScriptService/City.luau','src/ServerScriptService/CompactCity.luau','src/ReplicatedStorage/Shared/CompactLayout.luau']
def check(sources):
 for name,source in sources.items():
  for token in ('MicPracticeLane','MicPracticeTarget','MIC PRACTICE','PracticeTarget','PracticeBackstop'):
   assert token not in source,'Retired mic area token remains: '+name+'/'+token
 assert 'Layout.Soccer=' in sources[FILES[2]] and 'NickPracticeGoalLeft' in sources[FILES[1]],'Unrelated soccer practice removed'
 assert 'Layout.TrainingHomes=' in sources[FILES[2]] and 'TrainingPad1' in sources[FILES[2]],'Training area removed'
 assert 'FlowerKiosk' in sources[FILES[0]],'Unrelated fallback plaza removed'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
 sources={name:(ROOT/name).read_text(encoding='utf-8') for name in FILES};check(sources)
 archive=ROOT/'assets/drafts/original-city-2026-11-11/72c886cb6f8a60ab26dff962e28da77e4b2d4609'
 meta=json.loads((archive/'manifest.json').read_text());raw=(archive/'original-city-source.zip').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==meta['zipSha256'],'Original archive ZIP changed'
 with zipfile.ZipFile(archive/'original-city-source.zip')as z:
  for name,entry in meta['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==entry['sha256'],'Archived source changed:'+name
 print('PASS runtime mic-area absence, retained training/soccer and '+str(len(meta['files']))+' byte-identical archived files')
 if args.baseline:
  old=subprocess.check_output(['git','show','53d6213:'+FILES[0]],cwd=ROOT,text=True,encoding='utf-8')
  a=old.index(' -- A sheltered practice lane beside spawn');b=old.index(' local kx,kz=x-64,z-65',a)
  assert old[:a]+old[b:]==sources[FILES[0]],'Fallback changed outside retired lane'
  before=dict(sources);before[FILES[0]]=old
  try:check(before)
  except AssertionError as e:assert 'Retired mic area token' in str(e)
  else:raise AssertionError('Historical mic area accepted')
  print('PASS exact pinned fallback deletion only; historical runtime lane rejected')
 if args.negative_controls:
  for name in FILES[:2]:
   changed=dict(sources);changed[name]+='\n-- MicPracticeTarget'
   try:check(changed)
   except AssertionError as e:assert 'Retired mic area token' in str(e);print('PASS retired token control:',name)
   else:raise AssertionError('Retired token accepted')

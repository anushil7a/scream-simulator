from pathlib import Path
import subprocess
b=Path(__file__).resolve().parent;out=b.parents[1]/'build'/'player-tag-prototype-smoke';out.mkdir(parents=True,exist_ok=True);s=(b/'player-tag-baseline-smoke-template.luau').read_text(encoding='utf-8-sig');source=(b/'player-tag-baseline.client.luau').read_text(encoding='utf-8')
def run(code,name):
 p=out/('player-tag-baseline-smoke-'+name+'.luau');p.write_text('local realPrint=print\nlocal function smoke()\n'+s.replace('__SOURCE__',code)+'\nend\nrealPrint("WHOLE_FIXTURE_SMOKE",smoke())\n',encoding='utf-8');return subprocess.run(['luau',str(p)],capture_output=True,text=True,encoding='utf-8')
r=run(source,'candidate');print(r.stdout);assert r.returncode==0,r.stderr
old='local character=bounded(function()return player.Character end,"Character")';assert source.count(old)==1
r=run(source.replace(old,'local character=nil'),'missing-startup');assert r.returncode!=0,'Missing startup mutant survived'
old='assert(not terminal and sequence==caseSequence,"Case cancelled/replaced during settle")';assert source.count(old)==1
r=run(source.replace(old,'do end'),'missing-stop-fence');assert r.returncode!=0 and 'Stop during settle rejects result' in r.stderr,'Stop fence control must fail intended runtime assertion: '+r.stderr
print('2 negative controls rejected')

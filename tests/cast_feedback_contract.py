"""Actual server feedback branch compared to native fixture expectations; no native cast claim."""
from pathlib import Path
import argparse,json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
SERVER='src/ServerScriptService/Bootstrap.server.luau'
FIXTURE='tests/StudioCastFeedback.server.luau'

def assemble(server,fixture):
 start=server.index(' if knockoutMessage then castMessage=knockoutMessage')
 branch=server[start:server.index(' state(p,castMessage)',start)]
 expected=re.findall(r'assert\(message=="([^"\n]+)"',fixture)
 assert len(expected)==4,('Native feedback oracle inventory changed',expected)
 setup='local function feedback(totalHits,obstruction)\n local castMessage,knockoutMessage;local evades=0;local sound={damage=18}\n'
 code=setup+branch+' return castMessage\nend\n'
 for i,expression in enumerate(['feedback(0,nil)','feedback(0,{})','feedback(0,{})','feedback(1,nil)']):
  code+='assert('+expression+'=='+json.dumps(expected[i],ensure_ascii=False)+','+json.dumps('Native cast feedback expectation '+str(i+1)+' diverges from actual server branch')+')\n'
 return code+"print('PASS 4 actual server feedback/native fixture oracle comparisons')\n"

def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=ROOT/'tests',encoding='utf-8',delete=False)as f:
  f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],capture_output=True,text=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');a=p.parse_args()
 server=(ROOT/SERVER).read_text(encoding='utf-8');fixture=(ROOT/FIXTURE).read_text(encoding='utf-8')
 run(assemble(server,fixture))
 if a.negative_controls:
  run(assemble(server,fixture.replace('"Beam missed"','"Scream missed"',1)),'Native cast feedback expectation 1 diverges')
  run(assemble(server,fixture.replace('"Beam stopped by cover"','"Practice hit"')),'Native cast feedback expectation 2 diverges')
  run(assemble(server,fixture.replace('Hit 1 target','Hit 2 targets')),'Native cast feedback expectation 4 diverges')

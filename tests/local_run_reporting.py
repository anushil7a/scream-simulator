"""Synthetic local reporter lifecycle checks; no aggregate/native/network execution."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
from local_run_report import Report,snapshot
n=0
def check(ok,message):
 global n
 assert ok,message;n+=1
with tempfile.TemporaryDirectory(prefix="local-report-") as directory:
 root=Path(directory);(root/"src").mkdir();(root/"tests").mkdir();(root/"tools").mkdir();(root/"vault").mkdir()
 (root/"src/A.luau").write_text("return 1")
 (root/"tests/tmp-preserve.luau").write_text("excluded")
 (root/"vault/secret.py").write_text("excluded")
 check(list(snapshot(root))==["src/A.luau"],"Fingerprint included excluded files")
 def read(r):return json.loads(r.path.read_text())
 r=Report(root,"build/pass.json",["synthetic"])
 check(read(r)["status"]=="RUNNING","Initial report falsely passed")
 with r.session():
  r.run([sys.executable,"-c","import sys;print('output');print('error',file=sys.stderr)"],os.environ.copy(),True)
 d=read(r);log=r.logpath.read_bytes()
 check(d["status"]=="PASSED" and d["inputsUnchanged"],"Successful run not recorded")
 check(d["commands"][0]["exitCode"]==0 and d["commands"][0]["elapsedSeconds"]>=0,"Command result missing")
 check(b'output' in log and b'error' in log and hashlib.sha256(log).hexdigest()==d["log"]["sha256"],"Log incomplete/hash mismatch")
 check(d["execution"]=="local-not-CI" and 'testedCommit' not in d,"Overstated commit/CI")
 check(d["baseCommit"] is None and d["workingTreeDirty"] is None,"Nonrepository metadata invented")
 check(all(v is None for v in d["referenceSha256"].values()),"Missing references invented")
 for mode in ('failed','interrupted','error','changed'):
  q=Report(root,"build/"+mode+".json",[mode])
  raised=False
  try:
   with q.session():
    if mode=='failed':q.run([sys.executable,'-c','raise SystemExit(7)'],os.environ.copy(),True)
    elif mode=='interrupted':raise KeyboardInterrupt()
    elif mode=='error':q.run(['nonexistent-local-report-command'],os.environ.copy())
    else:(root/'src/A.luau').write_text('return 2')
  except (KeyboardInterrupt,subprocess.CalledProcessError,FileNotFoundError,RuntimeError):raised=True
  check(raised,"Non-success run returned successful exit "+mode)
  d=read(q);check(d['status']=={'failed':'FAILED','interrupted':'INTERRUPTED','error':'ERROR','changed':'INPUTS_CHANGED'}[mode],'False completion '+mode)
  check('endedAtUtc' in d and q.log.closed,'Finalization omitted '+mode)
  if mode=='failed':check(d['commands'][0]['exitCode']==7,'Wrong failure exit')
  if mode=='error':check(d['commands'][0]['status']=='ERROR' and d['commands'][0]['exitCode'] is None,'Launch error pretends exit')
 try:Report(root,'tests/overwrite.json',[])
 except ValueError:check(True,'outside denied')
 else:raise AssertionError('Report permitted outside build')
 # Finalization failures fail the caller, while original child failures survive.
 import local_run_report as reporting
 original_snapshot=reporting.snapshot
 for fail_child in (False,True):
  q=Report(root,'build/finalize.json',[]);calls=[0]
  def broken_snapshot(root):
   calls[0]+=1
   if calls[0]>1:raise OSError('synthetic finalization failure')
   return original_snapshot(root)
  reporting.snapshot=broken_snapshot
  try:
   try:
    with q.session():
     if fail_child:raise subprocess.CalledProcessError(9,['synthetic'])
   except subprocess.CalledProcessError as exc:check(fail_child and exc.returncode==9,'Original exception replaced')
   except RuntimeError:check(not fail_child,'Finalization masked child error')
   else:raise AssertionError('Finalization failure returned success')
   check(read(q)['status']=='ERROR','Finalization did not record ERROR')
  finally:reporting.snapshot=original_snapshot
 # A directory named like a project is not a file to hash.
 (root/'fake.project.json').mkdir()
 (root/'.hidden.project.json').write_text('{}');(root/'tmp-project.project.json').write_text('{}')
 check(not any(k.startswith(('.', 'tmp')) for k in snapshot(root)),'Hidden/tmp project inputs included')
 check('fake.project.json' not in snapshot(root),'Directory included as project')
 from unittest.mock import patch
 target=root/'link.project.json';target.write_text('{}')
 original_link=Path.is_symlink
 with patch.object(Path,'is_symlink',lambda p:p==target or original_link(p)):
  try:snapshot(root)
  except ValueError:check(True,'Project symlink rejected')
  else:raise AssertionError('Project symlink followed')
 target.unlink()
 # Abrupt stop representation is deliberately nonterminal, not inherited PASS.
 q=Report(root,'build/pass.json',['new unfinished run'])
 check(read(q)['status']=='RUNNING','Old pass survived new initialization');q.log.close()
 check(not list((root/'build').glob('*.tmp')),'Atomic temporary files leaked')
# Exercise the actual runner entry point without running its aggregate.
import verify_local
with tempfile.TemporaryDirectory(prefix="runner-dispatch-") as directory:
 root=Path(directory);(root/'src').mkdir();(root/'tests').mkdir();(root/'tools').mkdir()
 oldroot,oldargv,oldverify=verify_local.ROOT,sys.argv,verify_local.verify
 try:
  verify_local.ROOT=root;sys.argv=['verify_local.py','--report','build/run.json']
  seen=[]
  def fake_verify(args,report=None):
   seen.append((args.build,report is not None))
   report.run([sys.executable,'-c','print("dispatched")'],os.environ.copy(),True)
  verify_local.verify=fake_verify;verify_local.main()
  check(seen==[(False,True)],'Actual runner did not dispatch report')
  check(json.loads((root/'build/run.json').read_text())['status']=='PASSED','Actual entry lost success')
  verify_local.verify=oldverify;oldwhich=verify_local.shutil.which;verify_local.shutil.which=lambda *a,**k:None
  try:
   try:verify_local.main()
   except SystemExit:pass
   else:raise AssertionError('Missing tool accepted')
   check(json.loads((root/'build/run.json').read_text())['status']=='ERROR','Missing tool retained prior PASS')
  finally:verify_local.shutil.which=oldwhich
  sys.argv=['verify_local.py'];verify_local.verify=lambda args,report=None:seen.append(report)
  verify_local.main();check(seen[-1] is None,'Default invocation enabled reporting')
 finally:verify_local.ROOT=oldroot;verify_local.verify=oldverify;sys.argv=oldargv
print('PASS',n,'local reporter lifecycle assertions; synthetic child commands only')

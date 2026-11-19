"""Fail-closed local prelaunch-tools release check. No deployment or fleet verification."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
ACCESS=ROOT/'src/ServerScriptService/DeveloperAccess.luau'
# Exact reviewed owner/Studio-only module with the prelaunch flag false. Any change needs review.
DISABLED_REVIEWED_SHA256='c0167a31c4b05d539d9526c9ca11bb8da4d01970cda0148c27155a0ec9a2cbad'
def release_gate(source=None):
 try:
  source=ACCESS.read_text(encoding='utf8') if source is None else source
  digest=hashlib.sha256(source.encode()).hexdigest()
  flags=re.findall(r'^Access\.PrelaunchAllTesters\s*=\s*(.*?)\s*$',source,re.M)
  if len(flags)!=1 or flags[0] not in ('true','false'):
   reason='Missing, duplicate or unparseable server prelaunch flag'
  elif flags[0]=='true':
   reason='Temporary all-tester tools enabled; disable and review before public release'
  elif digest!=DISABLED_REVIEWED_SHA256:
   reason='Disabled module differs from reviewed owner/Studio-only authorization; review required'
  else:
   return {'status':'PASS_LOCAL_DISABLED_CONFIG_ONLY','sourceSha256':digest,'limits':'This checks local reviewed source only, not deployed servers, other release gates or publication authorization.'}
  return {'status':'BLOCKED','reason':reason,'sourceSha256':digest,'limits':'Draft/disposable builds remain allowed. This does not prevent manual publication or verify any serving fleet.'}
 except (OSError,UnicodeError) as error:
  return {'status':'BLOCKED','reason':'Cannot read server prelaunch configuration: '+str(error),'limits':'No release authorization.'}
def main():
 gate=release_gate();print(json.dumps(gate,indent=2));return 0 if gate['status']=='PASS_LOCAL_DISABLED_CONFIG_ONLY' else 2
if __name__=='__main__':raise SystemExit(main())

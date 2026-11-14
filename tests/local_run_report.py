"""Optional local-run evidence. Not CI, deployment approval, or native validation."""
import contextlib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

def utc(): return datetime.now(timezone.utc).isoformat()
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot(root):
    paths=[]
    for folder, suffixes in (("src", {".luau"}), ("tests", {".py", ".luau"}), ("tools", {".py"})):
        for p in (root/folder).rglob("*"):
            rel=p.relative_to(root)
            if p.is_file() and p.suffix in suffixes and not any(x.startswith((".", "tmp")) or x=="__pycache__" for x in rel.parts):
                if p.is_symlink(): raise ValueError("Symlink in evidence scope")
                paths.append(p)
    for p in root.glob("*.project.json"):
        if p.name.startswith((".", "tmp")): continue
        if p.is_symlink(): raise ValueError("Symlink in project evidence scope")
        if p.is_file(): paths.append(p)
    if len(paths)>2000: raise ValueError("Evidence scope exceeds 2000 files")
    if any(p.stat().st_size>8*1024*1024 for p in paths): raise ValueError("Evidence file exceeds 8 MiB")
    return {p.relative_to(root).as_posix():digest(p) for p in sorted(paths)}

def git_metadata(root):
    try:
        head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True,stderr=subprocess.DEVNULL,timeout=5).strip()
        dirty=bool(subprocess.check_output(["git","status","--porcelain","--untracked-files=normal"],cwd=root,stderr=subprocess.DEVNULL,timeout=5))
        return {"baseCommit":head,"workingTreeDirty":dirty}
    except (OSError,subprocess.SubprocessError): return {"baseCommit":None,"workingTreeDirty":None}

class Report:
    def __init__(self, root, destination, command):
        self.root=Path(root).resolve();self.path=Path(destination)
        if not self.path.is_absolute(): self.path=self.root/self.path
        self.path=self.path.resolve()
        if self.path.suffix!=".json" or not self.path.is_relative_to(self.root/"build"):
            raise ValueError("Report must be a .json file within build/")
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.logpath=self.path.with_name(self.path.stem+"."+uuid.uuid4().hex+".log")
        self.start=time.monotonic()
        self.data={"schemaVersion":1,"execution":"local-not-CI","status":"RUNNING","startedAtUtc":utc(),"command":list(command),"commands":[],"scope":"src/**/*.luau; tests/**/*.py,luau; tools/**/*.py; root *.project.json. Input selection excludes hidden/tmp paths, vault, build outputs and evidence JSON. This is path selection, not secret detection.","limits":["baseCommit is metadata, not a testedCommit claim","Default aggregate does not enable optional negative controls","Native references are historical; mismatch does not fail local tests","Release gates remain separate; no publication approval"],**git_metadata(self.root)}
        self.log=self.logpath.open("w",encoding="utf8")
        self.save()
    def save(self):
        tmp=self.path.with_name(self.path.name+"."+uuid.uuid4().hex+".tmp")
        try:
            tmp.write_text(json.dumps(self.data,indent=2)+"\n",encoding="utf8");os.replace(tmp,self.path)
        finally: tmp.unlink(missing_ok=True)
    def write(self,text): self.log.write(text);self.log.flush()
    def run(self, command, env, quiet=False):
        row={"command":[str(x) for x in command],"startedAtUtc":utc(),"status":"RUNNING","exitCode":None};self.data["commands"].append(row);self.save();start=time.monotonic();proc=None
        self.write("\n$ "+json.dumps(row["command"])+"\n")
        try:
            proc=subprocess.Popen(command,cwd=self.root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf8",errors="replace")
            for line in proc.stdout:
                self.write(line)
                if not quiet: print(line,end="",flush=True)
            row["exitCode"]=proc.wait();row["status"]="PASSED" if proc.returncode==0 else "FAILED"
            if proc.returncode: raise subprocess.CalledProcessError(proc.returncode,command)
        except BaseException as exc:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=2)
                except subprocess.TimeoutExpired: proc.kill();proc.wait(timeout=2)
            if row["status"]=="RUNNING": row["status"]="INTERRUPTED" if isinstance(exc,KeyboardInterrupt) else "ERROR"
            if proc is not None: row["exitCode"]=proc.returncode
            raise
        finally:
            row["endedAtUtc"]=utc();row["elapsedSeconds"]=time.monotonic()-start;self.save()
    @contextlib.contextmanager
    def session(self):
        original_error=False
        try:
            self.data["inputsBefore"]=snapshot(self.root);self.save()
            yield self
            self.data["status"]="PASSED"
        except BaseException as exc:
            original_error=True
            self.data["status"]="INTERRUPTED" if isinstance(exc,KeyboardInterrupt) else "FAILED" if isinstance(exc,subprocess.CalledProcessError) else "ERROR"
            self.data["errorType"]=type(exc).__name__
            raise
        finally:
            try:
                self.data["inputsAfter"]=snapshot(self.root)
                self.data["inputsUnchanged"]=self.data.get("inputsBefore")==self.data["inputsAfter"]
                if self.data["status"]=="PASSED" and not self.data["inputsUnchanged"]: self.data["status"]="INPUTS_CHANGED"
                refs={}
                for name in ("build/AutomaticVoiceCandidate.provenance.json","tests/evidence/native-input-2026-11-12.json","tests/evidence/prelaunch-test-tools-2026-11-12.json"):
                    p=self.root/name;refs[name]=digest(p) if p.is_file() else None
                self.data["referenceSha256"]=refs
            except Exception as exc:
                self.data["status"]="ERROR";self.data["finalizationErrorType"]=type(exc).__name__
            try:
                self.log.close();self.data["log"]={"path":self.logpath.relative_to(self.root).as_posix(),"sha256":digest(self.logpath),"scope":"Combined child stdout/stderr, unredacted, including quiet compiler output; runner summary is in JSON."}
            except Exception as exc:
                self.data["status"]="ERROR";self.data["finalizationErrorType"]=type(exc).__name__
            self.data["endedAtUtc"]=utc();self.data["elapsedSeconds"]=time.monotonic()-self.start
            try: self.save()
            except Exception:
                if not original_error: raise
            if not original_error and self.data["status"]!="PASSED":
                raise RuntimeError("Local report verification ended with "+self.data["status"])

"""Single-attempt authorized sanitizer blocks, no network or pull."""
import hashlib,json,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/evidence'
IMAGE='sha256:468b5b959b5f4025724d8549f45550c6ad38a32474733cbf130f8f2c1bc80805';BASE=['docker','--context','desktop-linux']
def call(args,timeout=15):
 r=subprocess.run(BASE+args,capture_output=True,text=True,encoding='utf-8',timeout=timeout);assert r.returncode==0,r.stderr;return r.stdout
def inventory():return [json.loads(x) for x in call(['ps','-a','--format','{{json .}}']).splitlines()]
def main():
 prepared=E/'stack-build-input-approved';prepared.mkdir(exist_ok=True)
 for n in ['control.c','observed.c']:prepared.joinpath(n).write_bytes((E/'stack-native-lf-repaired'/n).read_bytes())
 driver=(E/'stack-linux-input-prepared/driver.sh').read_text(encoding='utf-8')
 metrics="set -euo pipefail\ncapture_metrics() {\n cat /sys/fs/cgroup/memory.peak > /results/cgroup-memory-peak.txt 2>/dev/null || true\n cat /sys/fs/cgroup/cpu.stat > /results/cgroup-cpu-stat.txt 2>/dev/null || true\n}\ntrap capture_metrics EXIT"
 driver=driver.replace('/tmp/control','/build/control').replace('/tmp/observed','/build/observed')
 preflight="""awk '$5=="/build" {print; found=1} END {if(!found)exit 1}' /proc/self/mountinfo > /results/build-mountinfo.txt
read -ra mount_fields < /results/build-mountinfo.txt
mount_opts=",${mount_fields[5]},"
case "$mount_opts" in *,noexec,*) printf 'build noexec\n' >&2; exit 70;; esac
case "$mount_opts" in *,nosuid,*) ;; *) exit 71;; esac
case "$mount_opts" in *,nodev,*) ;; *) exit 72;; esac
stat -c '%a %u %g %n' /build/control /build/observed > /results/binary-modes.txt
test -x /build/control && test -x /build/observed
printf '{"job":"preflight","mount_exec":true,"both_binaries_executable":true}\n'
"""
 driver=driver.replace("printf '{\"job\":\"case\",\"name\":\"control-nominal\"}\\n'",preflight+"printf '{\"job\":\"case\",\"name\":\"control-nominal\"}\\n'")
 assert 'build-mountinfo.txt' in driver,'Preflight insertion failed; no execution'
 (prepared/'driver.sh').write_bytes(driver.replace('set -euo pipefail',metrics).replace('\r\n','\n').encode('utf-8'))
 before=inventory();(E/'stack-build-containers-before.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
 image=json.loads(call(['image','inspect',IMAGE]))[0];assert image['Id']==IMAGE and image['Os']=='linux' and image['Architecture']=='amd64'
 results=[]
 for mode in ['address','undefined']:
  name='vs-stack-build-'+mode+'-20261014';out=E/('stack-build-approved-'+mode)
  assert not out.exists(),'Single-attempt directory exists; do not repeat'
  assert not any(x['Names']==name for x in before),'Owned name exists'
  out.mkdir();record={'mode':mode,'name':name,'image':IMAGE,'attempt':1,'limit_seconds':120,'limit_bytes':2147483648,'limit_cpu':1,'input_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in prepared.iterdir()}}
  (out/'attempt-started.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
  call(['create','--pull=never','--name',name,'--network=none','--memory=2g','--memory-swap=2g','--cpus=1','--pids-limit=64','--read-only','--tmpfs','/tmp:rw,size=256m','--tmpfs','/build:rw,exec,nosuid,nodev,size=256m','--mount',f'type=bind,src={prepared},dst=/input,readonly','--mount',f'type=bind,src={out},dst=/results',IMAGE,'bash','/input/driver.sh',mode])
  info=json.loads(call(['inspect',name]))[0];h=info['HostConfig']
  checks={'memory':h['Memory']==2147483648,'swap':h['MemorySwap']==2147483648,'cpu':h['NanoCpus']==1000000000,'network':h['NetworkMode']=='none','readonly':h['ReadonlyRootfs'] is True,'pids':h['PidsLimit']==64,'image':info['Image']==IMAGE,'inputro':any(m['Destination']=='/input' and not m['RW'] and Path(m['Source'])==prepared for m in info['Mounts']),'results':len(info['Mounts'])==2 and any(m['Destination']=='/results' and m['RW'] and Path(m['Source'])==out for m in info['Mounts']),'tmpfs':h['Tmpfs'].get('/tmp')=='rw,size=256m' and h['Tmpfs'].get('/build')=='rw,exec,nosuid,nodev,size=256m'}
  record['prestart_limits_verified']=checks
  (out/'prestart-limits.json').write_text(json.dumps({'checks':checks,'host_config':{k:h[k] for k in ['Memory','MemorySwap','NanoCpus','NetworkMode','ReadonlyRootfs','PidsLimit','Tmpfs']}},indent=2),encoding='utf-8')
  if not all(checks.values()):
   record['status']='BLOCKED_PRESTART';call(['rm',name]);(out/'report.json').write_text(json.dumps(record,indent=2),encoding='utf-8');results.append(record);continue
  start=time.monotonic()
  with (out/'stdout.log').open('w',encoding='utf-8') as stdout,(out/'stderr.log').open('w',encoding='utf-8') as stderr:
   proc=subprocess.Popen(BASE+['start','-a',name],stdout=stdout,stderr=stderr)
   try:record['docker_start_exit_code']=proc.wait(timeout=120)
   except subprocess.TimeoutExpired:
    record['deadline_reached']=True;call(['kill',name],timeout=10)
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
  record['elapsed_seconds']=round(time.monotonic()-start,3)
  info=json.loads(call(['inspect',name]))[0];record['state']={k:info['State'][k] for k in ['Status','Running','OOMKilled','ExitCode','Error','StartedAt','FinishedAt']}
  peak=out/'cgroup-memory-peak.txt';record['peak_cgroup_bytes']=int(peak.read_text().strip()) if peak.exists() and peak.read_text().strip().isdigit() else None
  cpu=out/'cgroup-cpu-stat.txt';record['cpu_stat']=cpu.read_text() if cpu.exists() else None
  text=(out/'stdout.log').read_text(encoding='utf-8');record['diagnostic_stderr']=(out/'stderr.log').read_text(encoding='utf-8');record['complete_marker_seen']='"job":"complete"' in text
  record['status']='PASS' if record['state']['ExitCode']==0 and record['complete_marker_seen'] and not record.get('deadline_reached') and not record['state']['OOMKilled'] else 'FAIL_SINGLE_ATTEMPT'
  (out/'report.json').write_text(json.dumps(record,indent=2),encoding='utf-8');results.append(record);call(['rm',name]);print(json.dumps({k:record.get(k) for k in ['mode','status','elapsed_seconds','peak_cgroup_bytes','diagnostic_stderr']}),flush=True)
 after=inventory();(E/'stack-build-containers-after.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
 preserved=all(any(a['ID']==b['ID'] and a['Names']==b['Names'] and a['State']==b['State'] for a in after) for b in before)
 report={'blocks':results,'existing_containers_preserved':preserved,'existing_count_before':len(before),'existing_count_after':len(after),'scope':'Pila observer ASan/UBSan nominal and mallocNULL; plain C17 control; LSan disabled; not13TAD.'}
 (E/'stack-build-approved-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert preserved
if __name__=='__main__':main()

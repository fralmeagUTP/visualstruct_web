"""Exact prepared graph/color caller and independent live-reserve observation variants."""
import json,shutil,subprocess
from pathlib import Path

def verify_equivalent(trace,review,case,target,header):
 target.mkdir();shutil.copyfile(header,target/'tad_rojo_negro.h')
 source='#include <stdlib.h>\n#include "tad_rojo_negro.h"\n'+trace['source_code']
 (target/'equivalent.c').write_text(source,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
 def runbuild(args):
  result=subprocess.run([gcc,*flags,*args],capture_output=True,text=True,timeout=30);assert result.returncode==0 and not result.stderr,result.stderr
 runbuild([str(target/'equivalent.c'),'-o',str(target/'equivalent.exe')]);exact=subprocess.run([str(target/'equivalent.exe')],capture_output=True,text=True,timeout=5);assert exact.returncode==0 and exact.stdout==''
 initial=next(e for e in review['events'] if e['case']==case)['records'] if case<5 else []
 expected_frees=[e['result'] for e in review['events'] if e['case']==case and e['phase']=='free']
 observer=r'''#include <stdio.h>
#include <stdlib.h>
#include "tad_rojo_negro.h"
static RBT refs[128];static int live[128],count,releases;
void *audit_malloc(size_t n){void*p=malloc(n);if(p){refs[count]=p;live[count++]=1;}return p;}
void audit_free(void*p){int id=-1;for(int i=0;i<count;i++)if(live[i]&&refs[i]==p){id=i;break;}if(id<0)exit(71);printf("FREE:%d\n",id+1);live[id]=0;releases++;free(p);}
static RBT current_ref(int id){return id?refs[id-1]:NULL;}
'''
 observer+='void audit_verify(RBT root){if(root!=current_ref('+str(1 if initial else 0)+')||count!='+str(len(initial))+')exit(72);\n'
 for n in initial:
  color='ROJO' if n['color_before_free']==ord('r') else 'NEGRO'
  observer+=f'if(refs[{n["id"]-1}]->nro!={n["value_before_free"]}||refs[{n["id"]-1}]->rbt_color!={color}||refs[{n["id"]-1}]->izq!=current_ref({n["left_identity"]})||refs[{n["id"]-1}]->der!=current_ref({n["right_identity"]})||refs[{n["id"]-1}]->padre!=current_ref({n["parent_identity"]}))exit(73);\n'
 observer+='}\nvoid audit_verify_end(RBT root){if(root!=NULL||count!=releases)exit(74);for(int i=0;i<count;i++)if(live[i])exit(75);printf("MEMORY:%d %d\\n",count,releases);}\n'
 (target/'observer.c').write_text(observer,encoding='utf-8')
 variant=source.replace('    RBT arbol = preparar_ejemplo();','    RBT arbol = preparar_ejemplo();\n    audit_verify(arbol);').replace('    arbol = NULL;','    arbol = NULL;\n    audit_verify_end(arbol);')
 variant='#include "tad_rojo_negro.h"\nvoid audit_verify(RBT);void audit_verify_end(RBT);\n'+variant
 (target/'variant.c').write_text(variant,encoding='utf-8');runbuild(['-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(target/'variant.c'),'-o',str(target/'variant.o')]);runbuild([str(target/'variant.o'),str(target/'observer.c'),'-o',str(target/'observed.exe')])
 run=subprocess.run([str(target/'observed.exe')],capture_output=True,text=True,timeout=5)
 expected=''.join(f'FREE:{i}\n' for i in expected_frees)+f'MEMORY:{len(initial)} {len(initial)}\n';assert run.returncode==0 and run.stdout==expected,(run.returncode,run.stdout,expected)
 (target/'observer-stdout.log').write_text(run.stdout,encoding='utf-8')
 doxygen=Path(r'C:\Users\fralm\Documents\Codex\2026-09-30\task-2\doxygen-tool\doxygen.exe');warn=target/'warnings.log';cfg=target/'Doxyfile'
 cfg.write_text('\n'.join(['PROJECT_NAME = "RBT exact prepared equivalent caller"','INPUT = "'+(target/'equivalent.c').as_posix()+'"','OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([str(doxygen),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',(docs.stderr,warn.read_text(encoding='utf-8'))
 return {'strict_compile':True,'stdout':exact.stdout,'prepared_graph_and_color_matches_native':True,'free_order':expected_frees,'allocations':len(initial),'frees':len(initial),'doxygen_warnings':0,'observer_variant_distinct_from_exact_program':True,'preparation_outside_clear_trace':True}

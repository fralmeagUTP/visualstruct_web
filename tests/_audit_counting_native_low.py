"""New outside-four real C observers; frozen bodies reused, closed algorithms untouched."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,struct,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.domain.sorting.counting_sparse_instructions import run_counting_sparse_trace
from app.domain.sorting.counting_sparse_tape import expand_small
CHANGE=ROOT/'openspec/changes/audit-local-quality-and-unified-controls'
OLD=CHANGE/'evidence/visible-sorting-counting-baseline-low/native-final'
E=CHANGE/'evidence/visible-sorting-counting-native-fault-low'
CASES={'n5_k5':[5,4,3,2,1],'n2_k6':[0,5],'n8_k17':[0,16,8,0,16,4,12,8],'n80_k1':[2]*80,'n80_k80':list(range(79,-1,-1)),'near_min':[-2147483643,-2147483648],'near_max':[2147483647,2147483642],'n2_k1001':[0,1000]}
MASK=(1<<64)-1;NULL=0xD1B54A32D192ED03
TOKENS=sorted({json.loads(line)['token'] for line in (OLD/'native.jsonl').read_text().splitlines()})
TOKEN_ID={name:i for i,name in enumerate(TOKENS)}
PACK=struct.Struct('<18Q')

def native_base():
    return (OLD/'observed.c').read_text(encoding='utf-8').split('int main(void){')[0]

def compile_source(out,code):
    out.mkdir(parents=True,exist_ok=True)
    for ext in ['c','h']:
        data=(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext)).read_bytes()
        assert data==(OLD/('tad_ordenamiento.'+ext)).read_bytes()
        (out/('tad_ordenamiento.'+ext)).write_bytes(data)
    (out/'observed.c').write_text(code,encoding='utf-8')
    cmd=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed.c'),'-o',str(out/'observed.exe')]
    result=subprocess.run(cmd,capture_output=True,text=True);(out/'compile.log').write_text(result.stdout+result.stderr,encoding='utf-8');assert result.returncode==0,result.stderr
    return out/'observed.exe'

def c_case(values,case_id=0):
    return '{int a[]={'+','.join(map(str,values))+'};root=a;count=sizeof(a)/sizeof(a[0]);case_id='+str(case_id)+';counts=NULL;have_min=have_max=iw=ih=ir=io=comparisons=moves=allocs=frees=0;emit("initial",-1);if(ordenar_counting_sort(a,count)!=ORDENAMIENTO_OK)return 2;}'

def full_oracles():
    out=E/'outside-four-full';code=native_base()+'int main(void){\n'+''.join(c_case(v,i) for i,v in enumerate(CASES.values()))+'return 0;}\n'
    exe=compile_source(out,code)
    with (out/'native.jsonl').open('wb') as target:
        result=subprocess.run([str(exe)],stdout=target,stderr=subprocess.PIPE,timeout=20)
    assert result.returncode==0 and (out/'native.jsonl').stat().st_size<32*1024*1024
    rows=[];all_native={i:[] for i in range(len(CASES))}
    with (out/'native.jsonl').open(encoding='utf-8') as source:
        for line in source:
            event=json.loads(line);all_native[event['case']].append(event)
    for i,(name,values) in enumerate(CASES.items()):
        native=all_native[i];tape=run_counting_sparse_trace(values)['steps'];assert len(native)==len(tape)
        # Compare complete native state and previous/lifetime data against HTTP, page at a time.
        app=create_app();c=app.test_client();assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
        response=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'}).get_json();trace=response['execution_trace']
        frames=[]
        if trace.get('schema')=='counting-paged-trace/v1':
            for start in range(0,len(tape),128):frames.extend(c.get(trace['page_url'],query_string={'start':start,'limit':128}).get_json()['steps'])
        else:frames=trace['steps']
        assert len(frames)==len(native)
        previous_vars={}
        for index,(raw,frame) in enumerate(zip(native,frames)):
            expected={k:v for k,v in raw.items() if k!='case'}
            event=dict(frame['debug']['instruction_event'])
            if isinstance(event['conteo'],dict):event['conteo']=expand_small(event['conteo'])
            assert event==expected,(name,index,event,expected)
            assert frame['state_after']['items']==raw['array'] and frame['state_snapshot']['items']==native[max(0,index-1)]['array']
            before=frame['state_snapshot']['auxiliary_array'];after=frame['state_after']['auxiliary_array']
            if isinstance(before,dict):before=expand_small(before)
            if isinstance(after,dict):after=expand_small(after)
            assert before==native[max(0,index-1)]['conteo'] and after==raw['conteo']
            p=frame['pedagogy'];assert (p['condition']['result'] if p['condition'] else None)==raw['condition'] and p['invariant']['holds']
            assert frame['line_text']==('' if frame['line_index'] is None else trace['source_code'].splitlines()[frame['line_index']])
            for var in p['variables']:
                key=(var['scope'],var['name']);old=previous_vars.get(key)
                assert var['previous']==(old['value'] if old else None)
                assert var['changed']==(old is None or (old['value'],old['initialized'])!=(var['value'],var['initialized']))
            previous_vars={(v['scope'],v['name']):v for v in p['variables']}
            assert any(ptr['name']=='conteo' for ptr in p['pointers'])==(raw['conteo'] is not None)
            ctx=frame['state_after']['counting_context'];assert ctx['allocations']==raw['allocations'] and ctx['frees']==raw['frees']
            assert ctx['written']==ctx['consumed']+ctx['pending_decrement']
            if raw['conteo'] is not None:assert sum(raw['conteo'])==ctx['filled']-ctx['consumed']
        assert native[-1]['allocations']==native[-1]['frees']==1 and not frames[-1]['pedagogy']['variables'] and not frames[-1]['pedagogy']['call_stack']
        row=dict(case=name,input=values,events=len(native),full_native_HTTP_events_equal=True,allocations=1,frees=1,live=0);rows.append(row)
        (out/(name+'.json')).write_text(json.dumps(dict(case=row,native=native,response_summary={k:v for k,v in response.items() if k!='execution_trace'}),separators=(',',':')),encoding='utf-8')
    (out/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');return rows

def fields(index,event):
    a=event['array'];snapshot=event['conteo'];nz=snapshot['nonzero'] if isinstance(snapshot,dict) else enumerate(snapshot) if snapshot is not None else []
    nz=list(nz);ah=[sum((i+1)**power*v for i,v in enumerate(a))&MASK for power in [1,2]];ch=[sum((i+1)**power*v for i,v in nz)&MASK for power in [1,2]]
    scalar=lambda name:NULL if event[name] is None else event[name]&MASK
    return [index,TOKEN_ID[event['token']],2 if event['condition'] is None else int(event['condition']),*ah,scalar('minimo'),scalar('maximo'),scalar('i'),scalar('helper_i'),scalar('rango'),scalar('indice'),*ch,int(snapshot is not None),event['comparisons'],event['moves'],event['allocations'],event['frees']]

def expected_stream(tape,samples):
    sha=hashlib.sha256();selected={};start=0
    for record,end in zip(tape.records,tape.ends):
        event=tape[start]['instruction_event'];row=fields(start,event)
        if record['kind']=='zero_span':
            index=start
            for i in range(record['start'],record['end']+1):
                for stage,token in enumerate(['rebuild_test','bucket_test','rebuild_increment']):
                    row[0]=index;row[1]=TOKEN_ID[token];row[2]=[1,0,2][stage];row[7]=i+(stage==2)
                    data=PACK.pack(*row);sha.update(data)
                    if index in samples:selected[index]=list(row)
                    index+=1
        else:
            assert end==start+1;sha.update(PACK.pack(*row))
            if start in samples:selected[start]=row
        start=end
    return sha.hexdigest(),selected

def max_streaming():
    code=native_base();begin=code.index('static void emit(');end=code.index('static int cond(',begin)
    names=','.join('"'+name+'"' for name in TOKENS)
    emit=r'''static uint64_t event_index, count_h1, count_h2;
_Static_assert(sizeof(size_t)==8,"safe size_t64 observer only");
static void emit(const char*t,int condition){
 static const char*names[]={TOKENS}; size_t id=0;uint64_t a1=0,a2=0;
 for(id=0;id<sizeof(names)/sizeof(names[0]);id++)if(!strcmp(t,names[id]))break;
 if(id==sizeof(names)/sizeof(names[0]))exit(8);
 for(size_t z=0;z<count;z++){uint64_t weight=(uint64_t)z+1,value=(uint64_t)(int64_t)root[z];a1+=weight*value;a2+=weight*weight*value;}
 uint64_t nil=UINT64_C(0xD1B54A32D192ED03);
 uint64_t row[]={event_index++,(uint64_t)id,(uint64_t)(condition<0?2:condition),a1,a2,have_min?(uint64_t)(int64_t)minv:nil,have_max?(uint64_t)(int64_t)maxv:nil,iw?(uint64_t)wi:nil,ih?(uint64_t)hi:nil,ir?(uint64_t)range:nil,io?(uint64_t)output:nil,counts?count_h1:0,counts?count_h2:0,counts?1:0,(uint64_t)comparisons,(uint64_t)moves,(uint64_t)allocs,(uint64_t)frees};
 if(fwrite(row,sizeof(row),1,stdout)!=1)exit(9);
}
'''.replace('TOKENS',names)
    code=code[:begin]+emit+code[end:]
    code=code.replace('++conteo[arreglo[i]-minimo];moves++;','++conteo[arreglo[i]-minimo];count_h1+=(uint64_t)(arreglo[i]-minimo)+1;count_h2+=((uint64_t)(arreglo[i]-minimo)+1)*((uint64_t)(arreglo[i]-minimo)+1);moves++;')
    code=code.replace('--conteo[i];moves++;','--conteo[i];count_h1-=(uint64_t)i+1;count_h2-=((uint64_t)i+1)*((uint64_t)i+1);moves++;')
    rows=[]
    for name,values in [('cap_two',[999999,0]),('wide_eighty',[int(i*999999/79) for i in range(80)])]:
        out=E/('stream-'+name+'-binary');program='#include <io.h>\n#include <fcntl.h>\n'+code+'int main(void){_setmode(_fileno(stdout),_O_BINARY);uint16_t endian=1;if(*(unsigned char*)&endian!=1)return 7;'+c_case(values)+'fprintf(stderr,"EVENTS %llu ALLOCS %d FREES %d\\n",(unsigned long long)event_index,allocs,frees);return 0;}'
        exe=compile_source(out,program);tape=run_counting_sparse_trace(values)['steps'];samples={0,1,2,len(tape)//2,len(tape)-3,len(tape)-2,len(tape)-1};start=0
        for record,end in zip(tape.records,tape.ends):
            if record['kind']=='zero_span':samples.update([start,end-1])
            start=end
        sha=hashlib.sha256();observed={};counted=0;started=time.perf_counter()
        with (out/'stderr.log').open('wb') as err:
            proc=subprocess.Popen([str(exe)],stdout=subprocess.PIPE,stderr=err)
            while True:
                chunk=proc.stdout.read(PACK.size*4096)
                if not chunk:break
                assert len(chunk)%PACK.size==0;sha.update(chunk);records=len(chunk)//PACK.size
                for index in samples:
                    if counted<=index<counted+records:observed[index]=list(PACK.unpack_from(chunk,(index-counted)*PACK.size))
                counted+=records
            assert proc.wait(timeout=10)==0
        native_seconds=time.perf_counter()-started;assert counted==len(tape)
        started=time.perf_counter();expected,selected=expected_stream(tape,samples);assert sha.hexdigest()==expected and observed==selected
        row=dict(case=name,input=values,logical_events=counted,stream_bytes=counted*PACK.size,retained_stream_bytes=0,native_stream_seconds=native_seconds,expected_stream_seconds=time.perf_counter()-started,sha256=expected,samples=len(samples),digest_matches=True,allocations=1,frees=1,live=0,record_schema='18 little-endian uint64 fields; array/count two weighted checksums, not complete arrays',limitation='SHA covers all ordered scalar/fingerprint records, weighted array/count checksums can collide; combined with full small-range oracles and boundary samples, not proof of complete million-cell contents or all paths')
        (out/'samples.json').write_text(json.dumps({'expected':selected,'native':observed},indent=2),encoding='utf-8');(out/'report.json').write_text(json.dumps(row,indent=2),encoding='utf-8');rows.append(row)
    return rows

def native_faults():
    out=E/'native-faults';code=native_base();code=code.replace('conteo=(int*)calloc(rango,sizeof(int));','conteo=(int*)fault_calloc(rango,sizeof(int));')
    header='static int fail_reserve;static void* fault_calloc(size_t n,size_t size){return fail_reserve?NULL:calloc(n,size);}'
    spot=code.index('static int arreglo_valido');code=code[:spot]+header+'\n'+code[spot:]
    setup='static void setup(int*a,size_t n,int id){root=a;count=n;case_id=id;counts=NULL;have_min=have_max=iw=ih=ir=io=comparisons=moves=allocs=frees=fail_reserve=0;emit("initial",-1);}'
    result=r'''static void result(const char*name,int status,int unchanged){printf("{\"fault_result\":\"%s\",\"status\":%d,\"array_or_output_expected\":%s,\"allocations\":%d,\"frees\":%d,\"live\":%s}\n",name,status,unchanged?"true":"false",allocs,frees,counts?"true":"false");}'''
    main=r'''int main(void){
    _Static_assert(sizeof(size_t)==8,"safe size_t64 only");
    {int a[]={5,0};setup(a,0,0);int status=ordenar_counting_sort(a,0);result("empty",status,a[0]==5&&a[1]==0);}
    {setup(NULL,0,1);int status=ordenar_counting_sort(NULL,2);result("null",status,1);}
    {int a[]={0,1000000};setup(a,2,2);int status=ordenar_counting_sort(a,2);result("range",status,a[0]==0&&a[1]==1000000);}
    {int a[]={5,0};setup(a,2,3);fail_reserve=1;int status=ordenar_counting_sort(a,2);result("calloc",status,a[0]==5&&a[1]==0);setup(a,2,4);status=ordenar_counting_sort(a,2);result("retry",status,a[0]==0&&a[1]==5);}
    {int a[]={5,0},m=99;setup(a,2,5);int status=obtener_minimo_maximo(a,2,NULL,&m);result("helper_null_min",status,m==99&&a[0]==5&&a[1]==0);}
    {int a[]={5,0},m=99;setup(a,2,6);int status=obtener_minimo_maximo(a,2,&m,NULL);result("helper_null_max",status,m==99&&a[0]==5&&a[1]==0);}
    {int a[]={5,0},m=99,x=98;setup(a,0,7);int status=obtener_minimo_maximo(a,0,&m,&x);result("helper_empty",status,m==99&&x==98&&a[0]==5&&a[1]==0);}
    return 0;}
    '''
    exe=compile_source(out,code+setup+result+main)
    r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);(out/'native.jsonl').write_text(r.stdout,encoding='utf-8');(out/'stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0
    data=[json.loads(x) for x in r.stdout.splitlines()];rows=[x for x in data if 'fault_result' in x]
    for row in rows:
        assert row['status']==(1 if row['fault_result']=='retry' else 0) and row['array_or_output_expected'] and not row['live']
        assert row['allocations']==row['frees']==(1 if row['fault_result']=='retry' else 0)
    assert next(x for x in data if x.get('case')==3 and x.get('token')=='count_init')['conteo'] is None
    assert next(x for x in data if x.get('case')==3 and x.get('token')=='allocation_guard')['condition'] is True
    (out/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');return rows

if __name__=='__main__':
    E.mkdir(exist_ok=True);print(json.dumps({'streaming':max_streaming()} if len(sys.argv)>1 and sys.argv[1]=='streaming' else {'faults':native_faults()} if len(sys.argv)>1 and sys.argv[1]=='faults' else {'full':full_oracles(),'streaming':max_streaming()},indent=2))

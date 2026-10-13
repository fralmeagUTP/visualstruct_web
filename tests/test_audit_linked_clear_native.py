"""Visible Limpiar: independent downloaded C instruction/heap/alias oracle."""
import collections,json,re,shutil,subprocess
import pytest

@pytest.fixture
def clear_native_events(client,tmp_path):
    if shutil.which('gcc') is None:
        pytest.skip('gcc unavailable: native instruction equivalence unverified')
    response=client.get('/help/source/linked_list/source')
    assert response.status_code==200
    source=response.data
    work=tmp_path
    original=source.decode('utf-8-sig');start=original.index('void lista_limpiar(');end=original.index('\n}',start)+2;body=original[start:end]
    body=body.replace('if (lista == NULL)', 'if ((audit_emit("if (lista == NULL) {",lista,0,lista==NULL),lista == NULL))')
    body=body.replace('Tlista q;', 'Tlista q; int audit_q=0;')
    body=body.replace('while (*lista != NULL)', 'while ((audit_emit("while (*lista != NULL) {",lista,audit_q,*lista!=NULL),*lista != NULL))')
    body=body.replace('q = *lista;', 'q = *lista; audit_q=audit_id(q); audit_emit("q = *lista;",lista,audit_q,-1);')
    body=body.replace('*lista = q->sgte;', '*lista = q->sgte; audit_emit("*lista = q->sgte;",lista,audit_q,-1);')
    body=body.replace('free(q);', 'audit_live[audit_q-1]=0; free(q); audit_emit("free(q);",lista,audit_q,-1);')
    proto='static int audit_id(Tlista); static void audit_emit(const char *,Tlista *,int,int); static int audit_live[16];\n'
    src=original[:start]+proto+body+original[end:]+r'''
    static Tlista audit_nodes[16];static int audit_case,audit_count;
    static int audit_id(Tlista n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&n==audit_nodes[i])return i+1;return -1;}
    static void audit_emit(const char *line,Tlista *root,int q,int condition){
     printf("{\"case\":%d,\"line\":\"%s\",\"q_id\":%d,\"condition\":%d,\"live\":[",audit_case,line,q,condition);
     int comma=0;for(int i=0;i<audit_count;i++)if(audit_live[i]){if(comma++)putchar(',');printf("%d",i+1);}printf("],\"reachable_values\":[");comma=0;if(root)for(Tlista n=*root;n;n=n->sgte){if(comma++)putchar(',');printf("%d",n->nro);}puts("]}");
    }
    int main(void){int sizes[]={0,1,3,3};int values[][3]={{0,0,0},{7,0,0},{7,8,9},{7,7,9}};
     for(audit_case=0;audit_case<4;audit_case++){Tlista list=NULL;audit_count=sizes[audit_case];for(int i=0;i<16;i++)audit_live[i]=0;
     for(int j=0;j<audit_count;j++){lista_insertar_final(&list,values[audit_case][j]);}
     int i=0;for(Tlista n=list;n;n=n->sgte){audit_nodes[i]=n;audit_live[i++]=1;}lista_limpiar(&list);}
     return 0;}
    '''
    src=src.replace('puts("]}");',r'''printf("],\"root\":%d,\"nodes\":[",root?audit_id(*root):0);comma=0;for(int i=0;i<audit_count;i++)if(audit_live[i]){if(comma++)putchar(',');printf("{\"id\":%d,\"value\":%d,\"next\":%d}",i+1,audit_nodes[i]->nro,audit_id(audit_nodes[i]->sgte));}puts("]}");''')
    p=work/'instrumented_download.c';p.write_text(src,encoding='utf-8');exe=work/'oracle.exe'
    build=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(p),'-o',str(exe)],capture_output=True,text=True);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stderr;(work/'native-stdout.txt').write_text(run.stdout,encoding='utf-8')
    events=[json.loads(x) for x in run.stdout.splitlines() if x.startswith('{')]
    return events

@pytest.mark.parametrize('case,seed',[(0,[]),(1,[7]),(2,[7,8,9]),(3,[7,7,9])])
def test_visible_clear_matches_native_instructions_memory_and_aliases(client,clear_native_events,case,seed):
    for value in seed:
        assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':value}}).get_json()['success']
    data=client.post('/sequential/linked_list/operate',json={'operation':'limpiar','payload':{}}).get_json()
    assert data['success'] and data['visual_state']['items']==[]
    norm=lambda text:re.sub(r'\s+',' ',text.strip())
    lookup=collections.defaultdict(collections.deque)
    for step in data['execution_trace']['steps']:
        lookup[norm(step['line_text'])].append(step)
    events=[event for event in clear_native_events if event['case']==case]
    assert len(events)==2+4*len(seed)
    for event in events:
        assert lookup[norm(event['line'])],event
        step=lookup[norm(event['line'])].popleft()
        after=step['state_after'];frame=step['pedagogy']
        assert [item['value'] for item in after['items']]==event['reachable_values']
        assert [node['id'] for node in after['heap_nodes']]==[f'N{i}' for i in event['live']]
        assert [obj['id'] for obj in frame['heap_objects']]==[f'N{i}' for i in event['live']]
        assert after['head']==(f'N{event["root"]}' if event['root'] else 'NULL')
        assert [{"id":node['id'],"value":node['value'],"next":node['next']} for node in after['heap_nodes']]==[{"id":f'N{node["id"]}',"value":node['value'],"next":f'N{node["next"]}' if node['next'] else 'NULL'} for node in event['nodes']]
        assert after['lista']=='&cabeza'
        pointers={pointer['name']:pointer for pointer in frame['pointers']}
        assert pointers['lista']['type']=='Tlista *' and pointers['lista']['target']=='&cabeza'
        assert next(v for v in frame['variables'] if v['name']=='lista')['type']=='Tlista *'
        assert frame['call_stack'][0]['parameters']['lista']=='&cabeza'
        if event['condition']!=-1:
            assert frame['condition']['result']==bool(event['condition'])
            if 'if (lista' in event['line']:
                assert frame['condition']['substituted']=='&cabeza == NULL'
            else:
                expected_head=after['node_ids'][0] if after['node_ids'] else 'NULL'
                assert frame['condition']['substituted']==expected_head+' != NULL'
        if event['line']=='q = *lista;':
            assert after['q']==f'N{event["q_id"]}'
            assert pointers['q']['target']==after['q']
            assert frame['heap_transition']['freed']==[]
        if event['line']=='*lista = q->sgte;':
            detached=[node for node in after['heap_nodes'] if node['status']=='detached']
            assert len(detached)==1 and detached[0]['id']==f'N{event["q_id"]}'
            assert after['q']==detached[0]['id']
            assert frame['heap_transition']['freed']==[]
        if event['line']=='free(q);':
            assert after['q']==f'indeterminado (liberado N{event["q_id"]})'
            assert [obj['id'] for obj in frame['heap_transition']['freed']]==[f'N{event["q_id"]}']
            assert all(obj['freed'] for obj in frame['heap_transition']['freed'])
        assert frame['invariant']['holds']
        assert not step.get('console')

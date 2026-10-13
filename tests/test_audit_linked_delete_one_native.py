"""Visible first-occurrence deletion compared with actual downloaded native C."""
import collections,json,re,shutil,subprocess
import pytest
from app import create_app

@pytest.fixture(scope='module')
def native_delete_oracle(tmp_path_factory):
    if not shutil.which('gcc'):pytest.skip('gcc unavailable: native deletion fidelity unverified')
    client=create_app().test_client()
    response=client.get('/help/source/linked_list/source');assert response.status_code==200
    source=response.data
    D=tmp_path_factory.mktemp('native_delete_one')
    original=source.decode('utf-8-sig').replace('\r\n','\n')
    ops={'insertar_inicio':'lista_insertar_inicio','insertar_final':'lista_insertar_final','lista_insertar_elemento':'lista_insertar_elemento','eliminar_elemento':'lista_eliminar_elemento','buscar_elemento':'lista_buscar_elemento','eliminar_repetidos':'lista_eliminar_repetidos'}
    slots={'q':0,'p':1,'t':2,'ant':3,'temp':4};modified=original
    for name in reversed(list(ops.values())):
     start=modified.index('void '+name+'(');end=modified.index('\n}',start)+2;body=modified[start:end];out=[]
     for line in body.splitlines():
      text=line.strip()
      if not text or text.startswith(('/*','*','//')):out.append(line);continue
      if text.startswith(('if (','while (')):
       match=re.match(r'(\s*(?:if|while)\s*\()(.*)(\)\s*\{\s*)$',line)
       if match:
        expr=match.group(2);out.append(match.group(1)+'(audit_emit('+json.dumps(text)+',('+expr+')),('+expr+'))'+match.group(3));continue
      update=[]
      if text.startswith('Tlista ') and '=' in text:
       for var in slots:
        if re.search(r'\b'+var+r'\s*=',text):update.append(f'audit_alias[{slots[var]}]=audit_id({var});')
      else:
       for var in slots:
        if re.match(re.escape(var)+r'\s*=',text):update.append(f'audit_alias[{slots[var]}]=audit_id({var});')
      for var,index in [('i',0),('encontrado',1)]:
       if re.search(r'\b'+var+r'\s*(?:=|\+\+)',text):update.append(f'audit_scalars[{index}]={var}; audit_scalar_known[{index}]=1;')
      if text.startswith('return;'):
       out.append('audit_emit('+json.dumps(text)+',-1); '+line);continue
      out.append(line)
      if text.endswith(';') and not text.startswith(('void ',)):
       out.append(' '.join(update)+' audit_emit('+json.dumps(text)+',-1);')
     modified=modified[:start]+'\n'.join(out)+modified[end:]
    # Seed allocation and C helper allocation share registry, but emit only the audited call.
    modified=modified.replace('(Tlista) malloc(sizeof(struct NodoLista))','(Tlista) audit_malloc(sizeof(struct NodoLista))')
    modified=re.sub(r'(?m)^(\s*)free\(', r'\1audit_free(',modified)
    helpers=r'''
    static Tlista audit_nodes[64];static int audit_live[64],audit_count,audit_case,audit_active;
    static Tlista *audit_root;static int audit_alias[5],audit_scalars[2],audit_scalar_known[2];
    static int audit_id(Tlista n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_live[i]&&n==audit_nodes[i])return i+1;return -1;}
    static void *audit_malloc(size_t size){void *p=malloc(size);if(p){audit_nodes[audit_count]=p;audit_live[audit_count++]=1;}return p;}
    static void audit_free(void *p){if(p){int id=audit_id(p);if(id>0)audit_live[id-1]=0;}free(p);}
    static void audit_emit(const char *line,int condition){if(!audit_active)return;
     printf("AUDITJSON {\"case\":%d,\"line\":",audit_case);putchar('"');for(const char *c=line;*c;c++){if(*c=='"'||*c=='\\')putchar('\\');putchar(*c);}printf("\",\"condition\":%d,\"root\":%d,\"aliases\":[",condition,audit_id(*audit_root));
     for(int i=0;i<5;i++){if(i)putchar(',');printf("%d",audit_alias[i]);}printf("],\"scalars\":[");for(int i=0;i<2;i++){if(i)putchar(',');if(audit_scalar_known[i])printf("%d",audit_scalars[i]);else printf("null");}
     printf("],\"nodes\":[");int comma=0;for(int i=0;i<audit_count;i++)if(audit_live[i]){if(comma++)putchar(',');printf("{\"id\":%d,\"value\":%d,\"next\":%d}",i+1,audit_nodes[i]->nro,audit_id(audit_nodes[i]->sgte));}
     printf("],\"reachable_values\":[");comma=0;for(Tlista n=*audit_root;n;n=n->sgte){if(comma++)putchar(',');printf("%d",n->nro);}puts("]}");
    }
    '''
    point=modified.index('\n',modified.index('typedef struct NodoLista* Tlista;'))+1;modified=modified[:point]+helpers+modified[point:]
    cases=[]
    for op in ['insertar_inicio','insertar_final']:
     for seed in [[],[7],[7,8,9],[7,7,9]]:cases.append({'operation':op,'seed':seed,'payload':{'value':7}})
    for seed,pos in [([],1),([],2),([7],1),([7],2),([7,8,9],2),([7,8,9],3),([7,8,9],4),([7,7,9],2)]:cases.append({'operation':'lista_insertar_elemento','seed':seed,'payload':{'value':7,'position':pos}})
    for seed,value in [([],7),([7],7),([7],9),([7,8,9],7),([7,8,9],8),([7,8,9],9),([7,8,9],99),([7,7,9],7)]:cases.append({'operation':'eliminar_elemento','seed':seed,'payload':{'value':value}})
    for seed,value in [([],7),([7],7),([7,8,9],8),([7,7,9],7),([7,8,9],99)]:cases.append({'operation':'buscar_elemento','seed':seed,'payload':{'value':value}})
    for seed,value in [([],7),([7],7),([7],9),([7,7,9],7),([7,8,7],7),([9,7,7],7),([7,7,7],7),([7,8,9],99)]:cases.append({'operation':'eliminar_repetidos','seed':seed,'payload':{'value':value}})
    cases=[case for case in cases if case['operation']=='eliminar_elemento']
    main=['int main(void){']
    for index,case in enumerate(cases):
     main+=['{Tlista list=NULL;audit_root=&list;audit_active=0;audit_count=0;for(int k=0;k<5;k++){audit_alias[k]=-2;}for(int k=0;k<2;k++){audit_scalar_known[k]=0;}']
     main+=['lista_insertar_final(&list,'+str(value)+');' for value in case['seed']]
     payload=case['payload'];arg='list' if case['operation']=='buscar_elemento' else '&list';call=ops[case['operation']]+'('+arg+','+str(payload['value'])+(','+str(payload['position']) if 'position' in payload else '')+');'
     main+=['for(int k=0;k<5;k++){audit_alias[k]=-2;}for(int k=0;k<2;k++){audit_scalar_known[k]=0;}']
     main+=[f'audit_case={index};audit_active=1;printf("AUDITBEGIN %d\\n",audit_case);',call,'audit_active=0;lista_limpiar(&list);}']
    main+=['return 0;}'];modified+='\n'+'\n'.join(main)
    p=D/'instrumented_download.c';p.write_text(modified,encoding='utf-8');exe=D/'oracle.exe'
    build=subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(p),'-o',str(exe)],capture_output=True,text=True);assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True);assert run.returncode==0,run.stderr;(D/'native-stdout.txt').write_text(run.stdout,encoding='utf-8')
    events=[];console=[];current=None
    for line in run.stdout.splitlines():
     if line.startswith('AUDITBEGIN '):current=int(line.split()[1]);console=[]
     elif line.startswith('AUDITJSON '):
      event=json.loads(line[len('AUDITJSON '):]);event['console_since_previous']=[s for s in console if s.strip()];console=[];events.append(event)
     else:console.append(line)
    return events

@pytest.mark.parametrize('case,seed,value',[(0,[],7),(1,[7],7),(2,[7],9),(3,[7,8,9],7),(4,[7,8,9],8),(5,[7,8,9],9),(6,[7,8,9],99),(7,[7,7,9],7)])
def test_visible_delete_instruction_identity_alias_memory_and_console(client,native_delete_oracle,case,seed,value):
    for x in seed:assert client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':x}}).get_json()['success']
    data=client.post('/sequential/linked_list/operate',json={'operation':'eliminar_elemento','payload':{'value':value}}).get_json()
    assert data['success'];trace=data['execution_trace']
    assert trace['steps'][-1]['state_after']==trace['final_state']==data['visual_state']
    lookup=collections.defaultdict(collections.deque);norm=lambda text:re.sub(r'\s+',' ',text.strip())
    for step in trace['steps']:
        lookup[norm(step['line_text'])].append(step)
        assert step['pedagogy']['memory_state']['items']==step['state_after']['items']
    for event in [row for row in native_delete_oracle if row['case']==case]:
        assert lookup[norm(event['line'])],event
        step=lookup[norm(event['line'])].popleft();frame=step['pedagogy'];view=frame['memory_state']
        assert [x['value'] for x in step['state_after']['items']]==event['reachable_values']
        expected_nodes=[{'id':f'N{x["id"]}','value':x['value'],'next':f'N{x["next"]}' if x['next'] else 'NULL'} for x in event['nodes']]
        assert [{k:x[k] for k in ['id','value','next']} for x in view['heap_nodes']]==expected_nodes
        assert [obj['id'] for obj in frame['heap_objects']]==[node['id'] for node in expected_nodes]
        assert view['head']==(f'N{event["root"]}' if event['root'] else 'NULL')
        assert view['lista']=='&cabeza'
        if event['line']=='return;':
            assert view['scope_ended'] and 'p' not in view and 'ant' not in view
            alias_state=step['state_snapshot']
        else:alias_state=view
        live_ids={x['id'] for x in event['nodes']}
        for name,index in [('p',1),('ant',3)]:
            target=event['aliases'][index]
            expected=None if target==-2 else 'NULL' if target==0 else f'N{target}' if target in live_ids else f'indeterminado (liberado N{target})'
            assert alias_state.get(name)==expected
        if event['condition']!=-1:
            assert frame['condition']['result']==bool(event['condition'])
            expr=frame['condition']['substituted']
            assert '*NULL' not in expr and "*'NULL'" not in expr
            if 'lista == NULL' in event['line']:assert expr==f'&cabeza == NULL || {view["head"]} == NULL'
            if 'p->nro' in event['line']:
                node=next(x for x in event['nodes'] if x['id']==event['aliases'][1])
                assert expr==f'{node["value"]} == {value}'
        if event['line']=='free(p);':
            assert len(frame['heap_transition']['freed'])==1
            assert frame['heap_transition']['freed'][0]['id']==f'N{event["aliases"][1]}'
        else:assert frame['heap_transition']['freed']==[]
        assert [x.strip() for x in step.get('console',[]) if x.strip()]==[x.strip() for x in event['console_since_previous'] if x.strip()]
        assert frame['invariant']['holds']

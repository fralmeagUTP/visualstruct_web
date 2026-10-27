"""Immutable source/ABI profile for the exact book graph implementation."""
from pathlib import Path
import hashlib
import re
ROOT=Path(__file__).resolve().parents[3]
HASHES={'tad_grafo.c':'13c1bd9ae77ee91fb32aa72ba09f8c33e4d063dd29d3cea4358d23486c3fcc0a','tad_grafo.h':'b7bc7f3a97e49e0f61e2d34d111bfe3b69abdad7440210309da3dc6c8c81c80a'}
FIELDS={'Grafo':{'v':'ListaVertice','a':'ListaArco'},'struct NodoV':{'dato':'int','sig':'ListaVertice','marcado':'int'},'struct NodoA':{'origen':'int','destino':'int','costo':'int','sig':'ListaArco'},'Trabajo':{'n':'int','vertices':'int *','prev':'int *','usado':'int *','alcanzable':'int *','dist':'long long *'},'Conjunto':{'padre':'int *','n':'int'}}
STATUS_NAMES=('GRAFO_OK','GRAFO_MEMORIA','GRAFO_NO_EXISTE','GRAFO_PESO_NEGATIVO','GRAFO_CICLO_NEGATIVO','GRAFO_DESCONECTADO','GRAFO_ARGUMENTO','GRAFO_RANGO')

def canonical_source():
 for name,digest in HASHES.items():
  data=(ROOT/'docs/tads_C'/name).read_bytes()
  if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Book graph source drift: '+name)
 return (ROOT/'docs/tads_C/tad_grafo.c').read_text(encoding='utf-8')

def verify_source(source):
 if hashlib.sha256(source.encode('utf-8')).hexdigest()!=HASHES['tad_grafo.c']:raise ValueError('Only byte-exact canonical book graph source is accepted')

def function_names(source):
 return frozenset(re.findall(r'^(?:static\s+)?(?:Grafo|int|void|ListaVertice|ListaArco)\s+(\w+)\s*\(',source,re.M))

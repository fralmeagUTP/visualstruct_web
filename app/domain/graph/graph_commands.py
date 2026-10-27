"""Host-only deterministic graph preparation, separate from canonical C calls."""
from __future__ import annotations
import random
from app.adapters.base_adapter import BaseAdapter
from .educational_capacity import MAX_VERTICES


def materialize_random_commands(payload, directed=False, *, require_seed=False):
    """Return (seed, user-level insertion commands) without invoking a TAD.

    The RNG order is the existing classroom generator's order. Each edge command
    is interpreted by the caller policy (one arc directed, two calls undirected).
    A saved history must contain its seed; exporting it never invents randomness.
    """
    count = BaseAdapter._require_int(payload, 'vertices_count', 'cantidad de vértices')
    if not 1 <= count <= MAX_VERTICES:
        raise ValueError(f'La aplicación permite entre 1 y {MAX_VERTICES} vértices.')
    raw = payload.get('seed')
    if raw is None or str(raw).strip() == '':
        if require_seed:
            raise ValueError('El historial aleatorio no contiene semilla; no se puede reconstruir de forma fiel.')
        seed = random.randint(1, 999_999_999)
    else:
        seed = BaseAdapter._require_int(payload, 'seed', 'semilla')
    rng = random.Random(seed)
    vertices = list(range(1, count + 1))
    commands = [{'operation': 'insert_vertex', 'payload': {'vertex': v}} for v in vertices]
    keys = set()
    def add_edge(origin, target, weight):
        commands.append({'operation':'insert_edge','payload':{'origin':origin,'target':target,'weight':weight}})
        keys.add((origin,target) if directed else (min(origin,target),max(origin,target)))
    if count > 1:
        shuffled = vertices[:]; rng.shuffle(shuffled)
        for index in range(1, len(shuffled)):
            current = shuffled[index]; parent = shuffled[rng.randrange(0,index)]
            add_edge(parent,current,rng.randint(1,20))
    max_edges = count*(count-1) if directed else count*(count-1)//2
    extra = rng.randint(0,min(max(0,max_edges-max(0,count-1)),max(1,count)))
    attempts = 0; maximum = max(30,extra*20)
    while extra > 0 and attempts < maximum:
        attempts += 1; origin = rng.choice(vertices); target = rng.choice(vertices)
        if origin == target:continue
        key = (origin,target) if directed else (min(origin,target),max(origin,target))
        if key in keys:continue
        add_edge(origin,target,rng.randint(1,20));extra -= 1
    return seed,commands

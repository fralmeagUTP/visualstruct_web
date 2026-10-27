"""Strict catalog schema; only Radix carries its C negative-reversal caveat."""
IDS={"intercambio","seleccion","insercion","burbuja","shell","quicksort","mergesort","heapsort","counting_sort","binsort","radixsort"}
FIELDS={"best","average","worst","memory","stable","in_place"}
def assert_sorting_catalog_consumer(algorithms,learning,theory):
    ids=[x["id"] for x in algorithms]
    assert len(ids)==len(set(ids))==11 and set(ids)==IDS
    assert set(learning)==set(theory)==IDS
    for profile in learning.values():
        for field in ("objective","prior","mastery"):assert profile[field]
    for algorithm,profile in theory.items():
        assert set(profile)==FIELDS|({"stability_note"} if algorithm=="radixsort" else set())
        for field in ("best","average","worst","memory"):assert type(profile[field]) is str and profile[field].strip()
        for field in ("stable","in_place"):assert type(profile[field]) is bool
        if algorithm=="radixsort":
            assert profile["stable"] is False
            note=profile["stability_note"]
            assert type(note) is str and all(word in note.casefold() for word in ("invers","negativ","estab","registros"))

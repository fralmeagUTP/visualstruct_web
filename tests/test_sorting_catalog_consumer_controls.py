"""Pure schema controls; no sorting operation executed."""
from pathlib import Path
import json
import pytest
from _sorting_catalog_consumer_oracle import assert_sorting_catalog_consumer
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-catalog-consumer-low/catalog-consumer-baseline-values.json"
def data():return json.loads(P.read_text(encoding="utf-8"))
def test_frozen_catalog_schema():
    d=data();assert_sorting_catalog_consumer(d["algorithms"],d["learning"],d["theory"])
@pytest.mark.parametrize("defect",("missing_algorithm","duplicate_algorithm","learning_coverage","empty_objective","missing_theory","unknown_field","note_on_other","missing_note","empty_note","wrong_note","integer_boolean","empty_complexity","radix_stable"))
def test_rejects_catalog_schema_defect(defect):
    d=data();a,l,t=d["algorithms"],d["learning"],d["theory"]
    if defect=="missing_algorithm":a.pop()
    elif defect=="duplicate_algorithm":a.append(a[0].copy())
    elif defect=="learning_coverage":l.pop("radixsort")
    elif defect=="empty_objective":l["radixsort"]["objective"]=""
    elif defect=="missing_theory":t.pop("radixsort")
    elif defect=="unknown_field":t["burbuja"]["future_field"]=True
    elif defect=="note_on_other":t["burbuja"]["stability_note"]=t["radixsort"]["stability_note"]
    elif defect=="missing_note":t["radixsort"].pop("stability_note")
    elif defect=="empty_note":t["radixsort"]["stability_note"]=""
    elif defect=="wrong_note":t["radixsort"]["stability_note"]="Todo siempre estable"
    elif defect=="integer_boolean":t["burbuja"]["stable"]=1
    elif defect=="empty_complexity":t["radixsort"]["memory"]=" "
    else:t["radixsort"]["stable"]=True
    with pytest.raises(AssertionError):assert_sorting_catalog_consumer(a,l,t)

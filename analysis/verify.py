"""Validate portable derived-data reproduction without model or image access."""
from pathlib import Path
import hashlib,json,math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'provenance/files.json').read_text())
for item in manifest['files']:
    p=ROOT/item['path']
    assert p.stat().st_size==item['bytes'],item['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['path']
df=pd.read_csv(ROOT/'data/derived/attempts_screened30.csv')
key=['scan','reference_id','model','depth','requested_cv','raster']
assert not df.duplicated(key).any()
assert df.groupby(['scan','reference_id','model']).size().eq(48).all()
assert df.groupby(['scan','reference_id'])[['reference_width_m','reference_height_m']].nunique().eq(1).all().all()
assert df.numeric_measurement.equals(df.width_m.notna()&df.height_m.notna())
assert df.scan.nunique()==30 and len(df)==22464
assert df[df.primary27].scan.nunique()==27 and len(df[df.primary27])==20736
assert df.groupby(['model','depth','requested_cv','raster']).size().eq(52).all()
assert df[df.primary27].groupby(['model','depth','requested_cv','raster']).size().eq(48).all()
for axis in ['width','height']:
    assert np.allclose((df[f'{axis}_m']-df[f'reference_{axis}_m'])[df.numeric_measurement],df[f'{axis}_error_m'][df.numeric_measurement],atol=1e-14)
actual=json.loads((ROOT/'results/native_measurements_summary.json').read_text())
expected=json.loads((ROOT/'config/expected_native_summary.json').read_text())
checks=0
for cohort,values in expected.items():
    for name,value in values.items():
        if name=='metrics':
            for metric,v in value.items():
                assert math.isclose(actual[cohort]['metrics'][metric]['equal_scan'],v,abs_tol=1e-9),metric
                checks+=1
        else:assert actual[cohort][name]==value,name;checks+=1
# Independent denominator and macro-aggregation calculations.
for cohort,x in [('comparison30',df),('primary27',df[df.primary27])]:
    expected_availability=x.groupby('scan').numeric_measurement.mean().mean()*100
    assert math.isclose(actual[cohort]['metrics']['availability_pct']['equal_scan'],expected_availability,abs_tol=1e-10)
    assert actual[cohort]['opportunities']==len(x)
    assert actual[cohort]['numeric_results']==int(x.numeric_measurement.sum())
print(json.dumps({'status':'passed','source_hashes_checked':len(manifest['files']),'frozen_summary_values_checked':checks,'screened_captures':30,'primary_captures':27,'rows_including_failures':len(df)}))

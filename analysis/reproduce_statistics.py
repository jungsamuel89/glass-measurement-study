"""Recompute the publication comparison pool after post-hoc technical screening.

Writes results/native_measurements_summary.json within this repository. The primary27 cohort is fixed.
The screened30 pool is not described as the total originally collected series.
"""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
SRC=ROOT/'data/derived/attempts_screened30.csv'
EXCLUDED=[4,19,25,33]
PRIMARY=[1,2,3,5,6,7,8,9,10,12,13,14,15,16,18,20,21,22,23,24,26,27,29,30,31,32,34]
SEED=20261110
NBOOT=10000
df=pd.read_csv(SRC,low_memory=False)
df=df[~df.scan.isin(EXCLUDED)].copy()
assert df.scan.nunique()==30
keys=['scan','reference_id','model','depth','requested_cv','raster']
assert not df.duplicated(keys).any()
assert df.groupby(['scan','reference_id','model']).size().eq(48).all()
df['availability_pct']=df.numeric_measurement.astype(float)*100
df['full_budget_pct']=(df.numeric_measurement&df.accepted_frames.eq(df.requested_cv)).astype(float)*100
df['width_mae_mm']=(df.width_m-df.reference_width_m).abs()*1000
df['height_mae_mm']=(df.height_m-df.reference_height_m).abs()*1000
df['dimension_mae_mm']=(df.width_mae_mm+df.height_mae_mm)/2
for t in [5,10,20]:
    df[f'S{t}_pct']=(df.numeric_measurement&df.width_mae_mm.le(t)&df.height_mae_mm.le(t)).astype(float)*100
MET=['availability_pct','full_budget_pct','width_mae_mm','height_mae_mm','dimension_mae_mm','S5_pct','S10_pct','S20_pct']

def macro(per,cols):
    sums=per.groupby(level=0)[cols].sum(min_count=1).fillna(0).to_numpy(float)
    counts=per.groupby(level=0)[cols].count().to_numpy(float)
    front=per.groupby(level=0)[cols].mean()
    ix=np.random.default_rng(SEED).integers(len(front),size=(NBOOT,len(front)))
    den=counts[ix].sum(axis=1)
    samples=np.divide(sums[ix].sum(axis=1),den,out=np.full_like(den,np.nan),where=den>0)
    return {c:{'equal_scan':float(per[c].mean()),'equal_front_sensitivity':float(front[c].mean()),'cluster_percentile95':np.nanquantile(samples[:,j],[.025,.975]).tolist(),'captures_defined':int(per[c].notna().sum()),'fronts_defined':int(front[c].notna().sum())} for j,c in enumerate(cols)}

def summary(x):
    per=x.groupby(['front_group','scan'])[MET].mean()
    return {'captures':int(x.scan.nunique()),'fronts':int(x.front_group.nunique()),'target_references':len(x[['scan','reference_id']].drop_duplicates()),'opportunities':len(x),'numeric_results':int(x.numeric_measurement.sum()),'full_budget_results':int(x.full_budget_pct.eq(100).sum()),'S10_successes':int(x.S10_pct.eq(100).sum()),'S20_successes':int(x.S20_pct.eq(100).sum()),'numeric_captures':int(x[x.numeric_measurement].scan.nunique()),'metrics':macro(per,MET),'accepted_frames_median':float(x.loc[x.numeric_measurement,'accepted_frames'].median()),'per_capture':per.reset_index().to_dict('records')}

def paired(a,b,full=False):
    kk=[k for k in keys if k!='requested_cv']
    z=df[df.requested_cv.eq(a)].merge(df[df.requested_cv.eq(b)],on=kk,suffixes=('_a','_b'),validate='one_to_one')
    z['front_group']=z.front_group_a
    common=z.numeric_measurement_a&z.numeric_measurement_b
    if full:common&=z.full_budget_pct_a.eq(100)&z.full_budget_pct_b.eq(100)
    cols=[]
    for c in MET:
        cc='delta_'+c
        z[cc]=z[c+'_b']-z[c+'_a']
        if c in ['width_mae_mm','height_mae_mm','dimension_mae_mm']:z.loc[~common,cc]=np.nan
        cols.append(cc)
    per=z.groupby(['front_group','scan'])[cols].mean()
    e=z[common].groupby(['front_group','scan'])[['width_mae_mm_a','height_mae_mm_a','dimension_mae_mm_a','width_mae_mm_b','height_mae_mm_b','dimension_mae_mm_b']].mean().mean()
    return {'factor':'requested_cv','a':a,'b':b,'full_budget_only':full,'opportunities':len(z),'numeric_pairs':int(common.sum()),'paired_captures':int(z.loc[common,'scan'].nunique()),'metrics':macro(per,cols),'paired_mean_axis_error_a_mm':float(e.dimension_mae_mm_a),'paired_mean_axis_error_b_mm':float(e.dimension_mae_mm_b),'paired_dimension_errors':e.to_dict()}

coverage=df.groupby('scan').numeric_measurement.mean()
assert coverage[coverage.gt(.4)].index.tolist()==PRIMARY
fixed=df[df.model.eq('rfdetr-seg-small-full-seed42')&df.depth.eq('sceneDepth')&df.requested_cv.eq(10)&df.raster.eq(10)]
out={
 'schema':'paper27_screened30_sensitivity/1',
 'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
 'cohort':{'description':'Thirty captures retained after post-hoc technical screening; the 27-capture primary analysis applies a further pooled availability >40% rule within this screened comparison pool.','pool_capture_ids':sorted(df.scan.unique().tolist()),'primary_capture_ids':PRIMARY,'additional_sensitivity_captures':sorted(set(df.scan)-set(PRIMARY)),'screening_post_hoc':True,'primary_selection_post_hoc':True,'not_total_collected_count':True,'independent_validation':False},
 'bootstrap':{'seed':SEED,'resamples':NBOOT,'unit':'visually assigned front group; physical identity not independently verified','estimand':'equal capture mean; cluster resampling of capture sums and counts','scope':'exploratory, conditional on the fixed post-hoc screened pool, not multiplicity corrected'},
 'comparison30':summary(df),
 'primary27':summary(df[df.scan.isin(PRIMARY)]),
 'budget':{str(k):summary(df[df.requested_cv.eq(k)]) for k in [1,2,5,10]},
 'budget_pairs':[paired(1,10),paired(1,10,True)],
 'fixed_candidate':{'model':'rfdetr-seg-small-full-seed42','depth':'sceneDepth','requested_cv':10,'raster':10,'selection_note':'Chosen previously by maximum equal-capture S20 on the primary27; applied unchanged to the screened30 sensitivity pool.','summary':summary(fixed)}
}
out['fixed_candidate']['summary']['all_targets_numeric_captures']=int(fixed.groupby('scan').numeric_measurement.all().sum())
out['fixed_candidate']['summary']['all_targets_S20_captures']=int(fixed.groupby('scan').S20_pct.min().eq(100).sum())
def finite_json(value):
    if isinstance(value,dict):return {str(k):finite_json(v) for k,v in value.items()}
    if isinstance(value,list):return [finite_json(v) for v in value]
    if isinstance(value,(float,np.floating)):return float(value) if np.isfinite(value) else None
    if isinstance(value,np.integer):return int(value)
    return value
out=finite_json(out)
(OUT/'native_measurements_summary.json').write_text(json.dumps(out,indent=2,allow_nan=False))
def compact(s):
    return {**{k:s[k] for k in ['captures','fronts','target_references','opportunities','numeric_results','numeric_captures','S10_successes','S20_successes','accepted_frames_median']},'metrics':{m:s['metrics'][m]['equal_scan'] for m in ['availability_pct','width_mae_mm','height_mae_mm','dimension_mae_mm','S10_pct','S20_pct']}}
print(json.dumps({'overall30':compact(out['comparison30']),'K1':compact(out['budget']['1']),'K10':compact(out['budget']['10']),'paired_K1_K10':out['budget_pairs'][0],'fixed_candidate':compact(out['fixed_candidate']['summary']),'output':str(OUT/'native_measurements_summary.json')},indent=2))

from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
SRC=ROOT/'data/derived/attempts_screened30.csv'
ids = [1,2,3,5,6,7,8,9,10,12,13,14,15,16,18,20,21,22,23,24,26,27,29,30,31,32,34]
df = pd.read_csv(SRC, low_memory=False)
df = df[df.scan.isin(ids)].copy()
keys = ['model','depth','requested_cv','raster']
assert len(df) == 20736
assert not df.duplicated(['scan','reference_id']+keys).any()
assert df.groupby(keys).size().eq(48).all()
assert df.groupby(keys).scan.nunique().eq(27).all()
# Recompute errors from measured and reference dimensions, independent of exported error columns.
df['W'] = (df.width_m-df.reference_width_m).abs()*1000
df['H'] = (df.height_m-df.reference_height_m).abs()*1000
assert np.allclose(df.loc[df.numeric_measurement,'W'],df.loc[df.numeric_measurement,'width_error_m'].abs()*1000)
assert np.allclose(df.loc[df.numeric_measurement,'H'],df.loc[df.numeric_measurement,'height_error_m'].abs()*1000)
assert df.W.notna().equals(df.numeric_measurement)
assert df.H.notna().equals(df.numeric_measurement)
df['A'] = df.numeric_measurement.astype(float)*100
df['S20'] = (df.numeric_measurement & df.W.le(20) & df.H.le(20)).astype(float)*100
df['S10'] = (df.numeric_measurement & df.W.le(10) & df.H.le(10)).astype(float)*100
df['D'] = (df.W+df.H)/2
df['full'] = df.numeric_measurement & df.accepted_frames.eq(df.requested_cv)

per = df.groupby(keys+['scan'])[['A','W','H','D','S20','S10']].mean()
table = per.groupby(keys).mean().reset_index()
raw = df.groupby(keys).agg(opportunities=('scan','size'),numeric=('numeric_measurement','sum'),success20=('S20',lambda v:int(v.eq(100).sum())),success10=('S10',lambda v:int(v.eq(100).sum())),full_budget=('full','sum'))
scans = df.groupby(keys).apply(lambda g:pd.Series({'numeric_scans':g.loc[g.numeric_measurement,'scan'].nunique(),'success20_scans_any':g.loc[g.S20.eq(100),'scan'].nunique(),'all_targets_available_scans':g.groupby('scan').numeric_measurement.all().sum(),'all_targets_success20_scans':g.groupby('scan').S20.min().eq(100).sum(),'accepted_median':g.loc[g.numeric_measurement,'accepted_frames'].median()}),include_groups=False)
table = table.merge(raw,on=keys).merge(scans,on=keys)
# Primary exploratory ranking uses joint successful-output yield, then availability, then error.
ranked = table.sort_values(['S20','A','D'],ascending=[False,False,True])
availrank = table.sort_values(['A','S20','D'],ascending=[False,False,True])
maerank = table.sort_values('D')
best = ranked.groupby('model',sort=False).head(1)
for name,t in [('all_fixed_ranked',ranked),('best_per_model',best),('availability_ranked',availrank),('mae_ranked',maerank)]:
    t.to_csv(OUT/(name+'.csv'),index=False)
winner=ranked.iloc[0]
common = table[table.depth.eq(winner.depth)&table.requested_cv.eq(winner.requested_cv)&table.raster.eq(winner.raster)].sort_values(['S20','A','D'],ascending=[False,False,True])
common.to_csv(OUT/'paper27_fixed_common_winner_setting.csv',index=False)
fullmodels=table[table.model.str.contains('-full-')]
fullbest=fullmodels.sort_values(['S20','A','D'],ascending=[False,False,True]).groupby('model',sort=False).head(1)
fullbest.to_csv(OUT/'paper27_fixed_full_models_best_per_model.csv',index=False)
for name,t in [('TOP S20',ranked.head(12)),('TOP AVAILABILITY',availrank.head(8)),('TOP MAE',maerank.head(5)),('BEST PER MODEL',best),('COMMON WINNER SETTING',common)]:
    print('\n'+name+'\n'+t.to_string(index=False,float_format=lambda x:f'{x:.6f}'))
meta = {'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'scans':ids,'fronts':int(df.front_group.nunique()),'targets_by_scan':df.groupby('scan').reference_id.nunique().to_dict(),'rank':'S20 descending, availability descending, conditional mean W/H absolute error ascending','same_reference_check':not bool(df.groupby(['scan','reference_id'])[['reference_width_m','reference_height_m']].nunique().gt(1).any().any())}
(OUT/'paper27_fixed_meta.json').write_text(json.dumps(meta,indent=2))
print('\nMETA\n'+json.dumps(meta,indent=2))

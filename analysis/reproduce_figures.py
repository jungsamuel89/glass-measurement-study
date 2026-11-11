"""Plot aggregate native results and deduplicated original report timings."""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
d=json.loads((OUT/'native_measurements_summary.json').read_text())
fig,axes=plt.subplots(1,3,figsize=(10,3.4),layout='constrained')
budgets=[1,2,5,10]
for ax,metric,label in zip(axes,['availability_pct','width_mae_mm','height_mae_mm'],['Numeric availability (%)','Conditional width MAE (mm)','Conditional height MAE (mm)']):
    vals=[d['budget'][str(k)]['metrics'][metric]['equal_scan'] for k in budgets]
    ax.plot(budgets,vals,'o-',color='#185f8d')
    ax.set(xlabel='Requested frames K',ylabel=label,xticks=budgets)
    ax.grid(alpha=.2)
fig.suptitle('Original native results: screened 30-capture comparison pool')
fig.savefig(OUT/'native_budget_summary.png',dpi=180)
fig.savefig(OUT/'native_budget_summary.svg')
plt.close(fig)

df=pd.read_csv(ROOT/'data/derived/attempts_screened30.csv')
cols=['model_load_seconds','original_model_inference_seconds','original_model_geometry_seconds','original_model_raster_seconds','original_model_report_total_seconds']
df=df[df.primary27].groupby(['scan','model'])[cols].first().reset_index()
timing=df.groupby('model')[cols].median()
timing.to_csv(OUT/'original_report_time_medians.csv')
ax=timing[['original_model_inference_seconds','original_model_report_total_seconds']].plot.barh(figsize=(9,5),color=['#38859a','#143f68'])
ax.set(xlabel='Seconds; median original ten-frame report',ylabel='Model',title='Fixed 27-capture cohort: original native compute time')
ax.legend(['Segmentation','Full report'])
ax.figure.tight_layout()
ax.figure.savefig(OUT/'original_report_time.png',dpi=180)
ax.figure.savefig(OUT/'original_report_time.svg')
plt.close(ax.figure)
print('Generated native budget and original report timing figures.')

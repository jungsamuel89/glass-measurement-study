"""Plot fixed TEST147 original-model CPU operating-point interpretation."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/validation'
models=json.loads((OUT/'test_summary.json').read_text())['models']
labels=[]
for m in models:
    mid=m['model_id']
    family='RF-DETR' if mid.startswith('rfdetr') else 'RTMDet' if mid.startswith('rtmdet') else 'Mask R-CNN'
    size='100%' if '-full-' in mid else '25%' if '-p025-' in mid else '50%'
    labels.append(f'{family} {size}')
y=np.arange(len(models))
fig,axes=plt.subplots(1,2,figsize=(11,5.8),sharey=True,layout='constrained')
for ax,metric,label in zip(axes,['macro_pq_like','exact_set_success'],['Image-mean PQ-like score (%)','Exact matched instance set (%)']):
    ax.barh(y-.18,[100*m['old_fixed_primary'][metric] for m in models],height=.34,label='Original fixed point',color='#a8b9c4')
    ax.barh(y+.18,[100*m['primary'][metric] for m in models],height=.34,label='Validation-selected point',color='#155c86')
    ax.set(yticks=y,yticklabels=labels,xlabel=label,xlim=(0,100))
    ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
axes[0].invert_yaxis()
axes[1].legend(loc='lower right',fontsize=8)
fig.suptitle('TEST147: original-model CPU segmentation interpretation',fontsize=11)
fig.savefig(OUT/'test_operating_points.png',dpi=180)
fig.savefig(OUT/'test_operating_points.svg')
plt.close(fig)
print('Generated fixed-test operating-point interpretation figure.')

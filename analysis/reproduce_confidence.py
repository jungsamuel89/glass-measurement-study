"""Reproduce validation-only operating points from anonymised score/IoU arrays.

These inputs reproduce matching and metrics, not mask generation or calculation
of the IoU matrices. Original masks, annotations and inference remain private.
"""
from pathlib import Path
import argparse,csv,gzip,json,math
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    if path.suffix=='.gz':
        with gzip.open(path,'rt',encoding='utf-8') as stream:return json.load(stream)
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def matching(ious,cutoff):
    """Maximum valid-edge cardinality, then maximum sum of matched IoUs."""
    ious=np.asarray(ious,dtype=float)
    assert ious.ndim==2 and np.isfinite(ious).all()
    assert ((ious>=0)&(ious<=1)).all() and 0<=cutoff<=1
    if 0 in ious.shape:return []
    valid=ious>=cutoff
    bonus=min(ious.shape)+1
    row,col=linear_sum_assignment(-(valid*(bonus+ious)))
    return [(int(i),int(j),float(ious[i,j])) for i,j in zip(row,col) if valid[i,j]]

def prepare(images):
    assert len({im['image'] for im in images})==len(images)
    result=[]
    for im in images:
        scores=np.asarray(im['candidate_scores'],dtype=float)
        assert scores.ndim==1 and len(scores)<=100 and np.isfinite(scores).all()
        assert ((scores>=0)&(scores<=1)).all()
        gt=im['ground_truth_instances']
        assert isinstance(gt,int) and gt>=0
        ious=np.asarray(im['instance_iou'],dtype=float).reshape(gt,len(scores))
        assert np.isfinite(ious).all() and ((ious>=0)&(ious<=1)).all()
        result.append(dict(im,scores=scores,ious=ious))
    return result

def image_metrics(samples,threshold,cutoff=.5,with_union=False):
    rows=[]
    for im in samples:
        keep=np.flatnonzero(im['scores']>=threshold)
        pairs=matching(im['ious'][:,keep],cutoff)
        ng=im['ground_truth_instances'];npred=len(keep);tp=len(pairs)
        fp=npred-tp;fn=ng-tp;s=sum(p[2] for p in pairs)
        denom=tp+.5*fp+.5*fn
        empty=(ng==npred==0)
        q=s/tp if tp else float(empty)
        f=tp/denom if denom else 1.
        row={'image':im['image'],'group':im['group'],'ground_truth_instances':ng,
             'predicted_instances':npred,'tp':tp,'fp':fp,'fn':fn,
             'matched_iou_sum':s,'Q':q,'F':f,'pq_like':q*f,
             'correct_count':ng==npred,'exact_set':tp==ng==npred}
        if with_union:
            # This scalar is preserved from the private masks. It is NOT derived
            # from the pairwise instance-IoU matrix, which is insufficient for it.
            row['union_iou']=im['mask_union_iou_at_reported_thresholds'][f'{threshold:.2f}']
        rows.append(row)
    return rows

def aggregate(rows):
    assert rows
    n=len(rows)
    tp,fp,fn=(sum(r[k] for r in rows) for k in ['tp','fp','fn'])
    s=sum(r['matched_iou_sum'] for r in rows)
    groups=sorted({r['group'] for r in rows})
    means={g:sum(r['pq_like'] for r in rows if r['group']==g)/sum(r['group']==g for r in rows) for g in groups}
    return {'images':n,'gt_instances':tp+fn,'predicted_instances':tp+fp,'tp':tp,'fp':fp,'fn':fn,
            'macro_pq_like':sum(r['pq_like'] for r in rows)/n,'macro_Q':sum(r['Q'] for r in rows)/n,
            'macro_F':sum(r['F'] for r in rows)/n,'micro_pq_like':s/(tp+.5*fp+.5*fn) if tp+fp+fn else 1.,
            'matched_iou':s/tp if tp else None,'precision':tp/(tp+fp) if tp+fp else 0.,
            'recall':tp/(tp+fn) if tp+fn else 0.,'instance_f1':2*tp/(2*tp+fp+fn) if tp+fp+fn else 1.,
            'exact_count_images':sum(r['correct_count'] for r in rows),'exact_set_images':sum(r['exact_set'] for r in rows),
            'exact_count_accuracy':sum(r['correct_count'] for r in rows)/n,'exact_set_success':sum(r['exact_set'] for r in rows)/n,
            'mean_union_iou':sum(r['union_iou'] for r in rows)/n if 'union_iou' in rows[0] else None,
            'proxy_group_pq_like':means,'equal_proxy_group_pq_like':sum(means.values())/len(means)}

def compare(actual,expected,path='result'):
    """Compare all expected aggregate fields against an independent recalculation."""
    if isinstance(expected,dict):
        for k,v in expected.items():compare(actual[k],v,path+'.'+k)
    elif isinstance(expected,list):
        assert len(actual)==len(expected),path
        for i,(a,b) in enumerate(zip(actual,expected)):compare(a,b,f'{path}[{i}]')
    elif isinstance(expected,float):assert math.isclose(actual,expected,rel_tol=1e-11,abs_tol=1e-12),(path,actual,expected)
    else:assert actual==expected,(path,actual,expected)

def run(output):
    protocol=read(ROOT/'config/validation_protocol.json')
    frozen=read(ROOT/'config/validation_thresholds.json')
    validation=read(ROOT/'data/derived/validation_score_iou.json.gz')
    test=read(ROOT/'data/derived/test_score_iou.json.gz')
    expected_val=read(ROOT/'data/derived/validation_summary.json')
    expected_test=read(ROOT/'data/derived/test_summary.json')
    valmodels={m['model_id']:m for m in validation['models']}
    testmodels={m['model_id']:m for m in test['models']}
    assert len(valmodels)==len(testmodels)==9
    assert set(valmodels)==set(testmodels)=={m['model_id'] for m in frozen['models']}
    output.mkdir(parents=True,exist_ok=True)
    sweep_rows=[];selected=[];vals=[];tests=[]
    # All nine thresholds are selected from validation before any test metrics.
    for model in frozen['models']:
        mid=model['model_id'];samples=prepare(valmodels[mid]['images'])
        assert len(samples)==149
        sweep=[{'confidence':t,**aggregate(image_metrics(samples,t))} for t in protocol['threshold_grid']]
        best=max(r['macro_pq_like'] for r in sweep)
        chosen=min(r['confidence'] for r in sweep if best-r['macro_pq_like']<=1e-12)
        assert chosen==model['confidence'],mid
        selected.append({'model_id':mid,'confidence':chosen})
        value={'model_id':mid,'confidence':chosen,'primary':aggregate(image_metrics(samples,chosen,with_union=True)),
               'iou075':aggregate(image_metrics(samples,chosen,.75,with_union=True))}
        expect=next(m for m in expected_val['models'] if m['model_id']==mid)
        compare(value,expect)
        vals.append(value)
        for row in sweep:sweep_rows.append({'model_id':mid,**{k:v for k,v in row.items() if not isinstance(v,dict)}})
    for model in selected:
        mid=model['model_id'];chosen=model['confidence'];samples=prepare(testmodels[mid]['images'])
        assert len(samples)==147
        old=protocol['original_fixed_thresholds'][mid]
        value={'model_id':mid,'confidence':chosen,'primary':aggregate(image_metrics(samples,chosen,with_union=True)),
               'iou075':aggregate(image_metrics(samples,chosen,.75,with_union=True)),
               'old_fixed_threshold':old,'old_fixed_primary':aggregate(image_metrics(samples,old,with_union=True))}
        compare(value,next(m for m in expected_test['models'] if m['model_id']==mid))
        tests.append(value)
    write(output/'validation_summary.json',{'models':vals})
    write(output/'test_summary.json',{'models':tests})
    write(output/'thresholds.json',{'models':selected})
    with (output/'validation_sweep.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(sweep_rows[0]));writer.writeheader();writer.writerows(sweep_rows)
    qa={'status':'passed','models':9,'validation_images_per_model':149,'test_images_per_model':147,
        'thresholds_reselected_from_validation_only':True,'new_test_sweep':False,
        'all_reported_operating_point_metrics_match':True,'union_iou_source':'Preserved derived mask-union scalars; not reconstructed from pairwise IoUs',
        'mask_generation_and_iou_calculation_reproduced':False,'physical_measurement_replay':False}
    write(output/'verification.json',qa);print(json.dumps(qa))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/validation')
    run(parser.parse_args().output)

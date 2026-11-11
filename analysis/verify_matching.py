"""Independent exhaustive matching/metric check on 300 synthetic cases."""
import itertools
import numpy as np
from reproduce_confidence import matching,image_metrics

rng=np.random.default_rng(71);cases=0
for ng in range(5):
    for npred in range(5):
        for repeat in range(12):
            iou=rng.choice([0,.1,.49,.5,.51,.7,.99,1.],size=(ng,npred))
            got=matching(iou,.5);best=(0,0.)
            for count in range(1,min(ng,npred)+1):
                for gs in itertools.combinations(range(ng),count):
                    for ps in itertools.permutations(range(npred),count):
                        values=[iou[g,p] for g,p in zip(gs,ps)]
                        if all(v>=.5 for v in values):best=max(best,(count,sum(values)))
            assert len(got)==best[0] and abs(sum(m[2] for m in got)-best[1])<1e-10
            sample={'image':f'S{cases}','group':'G1','ground_truth_instances':ng,'scores':np.ones(npred)*.7,'ious':iou}
            row=image_metrics([sample],.5)[0]
            tp=len(got);fp=npred-tp;fn=ng-tp;den=tp+.5*fp+.5*fn
            pq=sum(m[2] for m in got)/den if den else 1.
            assert abs(row['pq_like']-pq)<1e-12
            assert row['fp']==fp and row['fn']==fn
            assert row['correct_count']==(ng==npred)
            assert row['exact_set']==(tp==ng==npred)
            cases+=1
print(f'Passed {cases} exhaustive synthetic matching and denominator cases.')

"""Standalone plot of the frozen row outcomes and conditional reliability."""
import json
import os
from pathlib import Path

HERE=Path(__file__).resolve().parent
RAW=HERE.parents[1]/'data/raw/2026-10-07-helsinki1979-digitization'
for key in ('TMP','TEMP','MPLCONFIGDIR'):os.environ[key]=str(RAW/'tmp')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    result=json.loads((HERE/'evaluation/2026-10-07-frozen-v1/metrics.json').read_text())['summary']
    out=HERE/'figures';out.mkdir(exist_ok=True)
    targets=[result['row_crop_correctness'],result['drawn_unit_count_agreement'],result['inscription_number_accuracy'],
             result['strict_top1']['whole_rows_all_sample'],result['strict_top5']['whole_rows_all_sample']]
    labels=['Clean\ncrop','Correct\nunit count','Correct\nnumber','Whole row\ntop one','Whole row\ntop five']
    rates=np.array([r['rate'] for r in targets])*100
    errors=np.array([[r['rate']-r['ci95'][0] for r in targets],[r['ci95'][1]-r['rate'] for r in targets]])*100
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,(left,right)=plt.subplots(1,2,figsize=(11.8,4.8),gridspec_kw={'width_ratios':[1.5,1]},layout='constrained')
    left.bar(np.arange(5),rates,color='#315b7c',width=.65,yerr=errors,capsize=4)
    left.set_xticks(np.arange(5),labels);left.set_ylim(0,100);left.set_ylabel('Rows (%)')
    left.set_title('60 printed source rows; Wilson 95% intervals',loc='left',fontsize=12)
    for i,r in enumerate(targets):left.text(i,5,f"{r['success']}/{r['total']}",ha='center',va='bottom',color='white',fontweight='bold')
    left.grid(axis='y',alpha=.2);left.set_axisbelow(True)
    bins=[b for b in result['calibration']['bins'] if b['n']]
    right.plot([0,1],[0,1],color='#777777',linestyle='--',linewidth=1)
    right.scatter([b['mean_confidence'] for b in bins],[b['accuracy'] for b in bins],
                  s=[20+b['n']*3 for b in bins],color='#ad6331',edgecolor='white',linewidth=.7,zorder=3)
    for b in bins:right.annotate(str(b['n']),(b['mean_confidence'],b['accuracy']),
        xytext=(5,8 if b['accuracy']<.1 else -12),textcoords='offset points',fontsize=9)
    right.set_xlim(0,1);right.set_ylim(-.03,1.06);right.set_xlabel('Mean fitted confidence');right.set_ylabel('Candidate-compatible units')
    right.set_title('Reliability on 140 equal-count positions',loc='left',fontsize=12)
    right.grid(alpha=.2)
    fig.suptitle('Helsinki 1979 frozen font pipeline',fontsize=15,fontweight='bold')
    fig.savefig(out/'validation.png',dpi=180);fig.savefig(out/'validation.svg');plt.close(fig)


if __name__=='__main__':main()

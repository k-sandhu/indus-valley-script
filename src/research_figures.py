"""Scientific figures from saved results; no raster image editing."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/'.vendor'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUT=ROOT/'output/figures';OUT.mkdir(parents=True,exist_ok=True)
BLUE='#24486c';TEAL='#2b847a';ORANGE='#b96535';GRAY='#75818a'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
    'axes.spines.right':False,'axes.labelcolor':'#263744','text.color':'#263744',
    'axes.edgecolor':'#b4c0c7','xtick.color':'#425460','ytick.color':'#425460',
    'figure.facecolor':'white','axes.facecolor':'white','savefig.dpi':200})


def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def finish(fig,name):
    fig.savefig(OUT/(name+'.png'),bbox_inches='tight');plt.close(fig)


def main():
    r=load('results/restoration/benchmark.json');g=load('results/gap_restoration/gap_benchmark.json')
    fig,axs=plt.subplots(1,2,figsize=(10.4,3.8),gridspec_kw={'width_ratios':[1.25,1]})
    positions=['initial','internal','final'];xx=np.arange(3);w=.34
    for j,(name,color,label) in enumerate([('baseline',GRAY,'Position/site/type'),('local',TEAL,'Local sign context')]):
        vals=[r['models'][name]['positions'][p]['top1']*100 for p in positions]
        axs[0].bar(xx+(j-.5)*w,vals,width=w,color=color,label=label)
        for x,y in zip(xx+(j-.5)*w,vals):axs[0].text(x,y+1.2,f'{y:.1f}',ha='center',fontsize=9)
    axs[0].set(xticks=xx,xticklabels=['Initial','Internal','Final'],ylabel='Exact glyph prediction (%)',ylim=(0,70))
    axs[0].set_title('One missing sign, known slot count',loc='left',fontweight='bold')
    axs[0].legend(loc='upper left',frameon=False,fontsize=8)
    bars=[r['models']['local']['top1']*100,g['models']['local']['exact_count_accuracy']*100,
          g['models']['local']['constant_one_glyph_design_control_accuracy']*100]
    axs[1].bar(range(3),bars,color=[TEAL,BLUE,GRAY],width=.65)
    axs[1].set(xticks=range(3),xticklabels=['Glyph\nidentity','Erased\ncount','Always\none sign'],ylim=(0,70),ylabel='Exact accuracy (%)')
    for x,y in enumerate(bars):axs[1].text(x,y+1.2,f'{y:.1f}',ha='center',fontsize=9)
    axs[1].set_title('Different tasks, different limits',loc='left',fontweight='bold')
    fig.text(.02,-.025,'Glyph:8,009 held-out slots. Count:1,596 texts with artificial internal erasures. The one-sign control applies only to the count task.',fontsize=8)
    fig.tight_layout();finish(fig,'restoration_limits')

    fig,ax=plt.subplots(figsize=(6.2,4.2));ax.plot([0,1],[0,1],color=GRAY,ls='--',lw=1,label='Calibrated reference')
    a=r['models']['local']['confidence_audit'];b=g['models']['local']['calibration']
    for values,label,color in [(a,'Known one-sign slot',TEAL),(b,'Unknown erased count',ORANGE)]:
        xx=[v['mean_model_mass'] for v in values if v['mean_model_mass'] is not None]
        yy=[v.get('exact_accuracy',v.get('accuracy')) for v in values if v['mean_model_mass'] is not None]
        ax.plot(xx,yy,'o-',color=color,label=label,lw=1.5)
    ax.set(xlim=(0,1),ylim=(0,1),xlabel='Mean highest model mass in bin',ylabel='Observed exact accuracy')
    ax.set_title('Model masses overstate empirical correctness',loc='left',fontweight='bold')
    ax.legend(frameon=False,fontsize=9);ax.grid(alpha=.12);fig.tight_layout();finish(fig,'calibration')

    nested=load('research/methods/results/nested_primary/nested_results.json')
    templates=load('research/methods/results/templates_extended/template_results.json')
    control=load('research/methods/results/workflow_templates/template_results.json')
    fig,axs=plt.subplots(1,2,figsize=(10,3.6));names=['Independent','32/64 templates','Previous sign']
    ind=[nested['observed']['baseline_noninitial_cross_entropy_bits'],
         templates['outer_cross_entropy_bits']['TEMPLATE'],nested['observed']['dependent_noninitial_cross_entropy_bits']]
    office=[control['outer_cross_entropy_bits'][k] for k in ['BASELINE','TEMPLATE','PMB']]
    for ax,vals,title in zip(axs,[ind,office],['Indus transcriptions','Nonphonetic office-route control']):
        ax.barh(range(3),vals,color=[GRAY,BLUE,TEAL]);ax.set(yticks=range(3),yticklabels=names,xlim=(0,7),xlabel='Cross-entropy (bits per noninitial sign)')
        ax.invert_yaxis();ax.set_title(title,loc='left',fontweight='bold')
        for i,x in enumerate(vals):ax.text(x+.06,i,f'{x:.2f}',va='center',fontsize=9)
    fig.text(.02,-.035,'Lower is better within each corpus. Absolute values across corpora are not a language test. Both systems benefit from local dependencies.',fontsize=8)
    fig.tight_layout();finish(fig,'structural_specificity')

    independent=load('results/independent_annotator/candidate_event_test.json')
    labels=['All 74 faces','Unique 73 P texts','Unspecified seal subtype','All candidates supported (54)']
    keys=['all_clear_weighting','unique_P_text_sensitivity','unspecified_seal_subtype_sensitivity','all_fine_candidates_training_supported_sensitivity']
    values=[independent[k] for k in keys];means=np.array([z['gain_bits_per_noninitial_candidate_event'] for z in values]);ci=np.array([z['conditional_cluster_bootstrap_95_ci'] for z in values])
    fig,ax=plt.subplots(figsize=(7.8,3.4));ax.errorbar(means,np.arange(4),xerr=np.vstack([means-ci[:,0],ci[:,1]-means]),fmt='o',color=TEAL,capsize=4)
    ax.axvline(0,color=GRAY,lw=1);ax.set(yticks=range(4),yticklabels=labels,xlabel='Gain in bits per noninitial candidate event',xlim=(-.05,1.2));ax.invert_yaxis()
    ax.set_title('Independent-annotator sensitivity supports sign order',loc='left',fontweight='bold')
    fig.text(.02,-.025,'Shared CISI sources and catalogue compatibility; overlapping candidate events are not a normalized Mayig-label predictor. Intervals condition on fitted models.',fontsize=8)
    fig.tight_layout();finish(fig,'independent_annotator')

    print('Wrote4 scientific figures from saved JSON results.')


if __name__=='__main__':main()

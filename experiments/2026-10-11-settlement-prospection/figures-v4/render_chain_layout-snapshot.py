"""Repair the observation diagram's right-edge border without new calculations."""
from pathlib import Path
import argparse, hashlib, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BASE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=BASE/'run-v3/synthetic-scenarios.json')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    data=json.loads(a.input.read_text(encoding='utf-8'))
    examples=data['observation_nonidentifiability_examples']
    a.output.mkdir(parents=True)
    navy='#213c50';teal='#24786e';grey='#708397'
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':10})
    fig,(chain,example)=plt.subplots(2,1,figsize=(9,6.5),gridspec_kw={'height_ratios':[1.15,1]})
    chain.set(xlim=(0,1),ylim=(0,1));chain.axis('off')
    chain.set_title('How occupied places become published records',loc='left',pad=20)
    labels=['Occupied\nplaces','Surviving\ndeposits','Surveyed\ndeposits','Method-detected\ndeposits','Dated or attributed\nevidence','Published\nrecords']
    width=.147;xs=[.005+i*.168 for i in range(6)]
    assert xs[-1]+width+.005 < 1
    for i,(x,label) in enumerate(zip(xs,labels)):
        chain.add_patch(FancyBboxPatch((x,.44),width,.3,boxstyle='round,pad=0.005,rounding_size=0.013',linewidth=1,facecolor='#edf2f3',edgecolor=navy))
        chain.text(x+width/2,.59,label,ha='center',va='center',fontsize=8.8)
        if i<5:
            chain.add_patch(FancyArrowPatch((x+width+.002,.59),(xs[i+1]-.008,.59),arrowstyle='-|>',mutation_scale=11,color=grey))
    chain.text(.005,.18,'Each stage conditions the next. The chain rule does not assume independent losses.',fontsize=10,color=grey)
    example.barh([1,0],[r['constructed_true_sites'] for r in examples],color='#dce5e8',height=.58,label='Constructed true total')
    example.barh([1,0],[r['expected_recorded_sites'] for r in examples],color=teal,height=.58,label='Expected records')
    example.set_yticks([1,0],['200 places × 0.5 recording','1,000 places × 0.1 recording'])
    example.set_xlim(0,1100);example.set_xlabel('Constructed number of places')
    example.set_title('The same expected record count can arise from different totals',loc='left',fontsize=12,pad=12)
    for r,y in zip(examples,[1,0]):
        example.text(r['constructed_true_sites']+12,y,f"{r['constructed_true_sites']:,}",va='center',fontsize=10)
        example.text(50,y,'100',ha='center',va='center',color='white',fontsize=9)
    example.legend(loc='upper right',frameon=False,fontsize=9)
    example.grid(axis='x',alpha=.18);example.set_axisbelow(True)
    fig.text(.015,.01,'SYNTHETIC examples: probabilities and totals are constructed. They illustrate missing-total nonidentifiability.',fontsize=9)
    fig.subplots_adjust(left=.25,bottom=.13,right=.99,top=.89,hspace=.47)
    chain.set_position([.02,.56,.96,.32])
    for ext in ('png','svg'):
        fig.savefig(a.output/f'observation-chain.{ext}',dpi=200,bbox_inches='tight',facecolor='white')
    plt.close(fig)
    script=Path(__file__).resolve()
    (a.output/'render_chain_layout-snapshot.py').write_bytes(script.read_bytes())
    def record(path):
        return dict(path=path.as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    files=[record(f) for f in sorted(a.output.iterdir()) if f.is_file()]
    result=dict(status='layout-only repair',input=record(a.input),code=record(script),files=files,
        change='Box spacing .169 to .168 keeps the final rounded border inside the diagram axes.',
        numerical_change=False,constructed_examples=examples,
        layout_guard=dict(last_box_right_with_padding=xs[-1]+width+.005,axes_right=1))
    (a.output/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Created revised observation diagram from frozen synthetic inputs; no numerical rerun.')

if __name__=='__main__':main()

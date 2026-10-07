"""Ideal independent-unit power targets; assumptions are Synthetic, tests remain Proposed."""
import argparse, json, math
from pathlib import Path
from statistics import NormalDist
OWN=Path(__file__).resolve().parent
def binomial(n,p):
    return [math.exp(math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)+k*math.log(p)+(n-k)*math.log1p(-p))for k in range(n+1)]
def rare(n,p0,p1,alpha):
    a=binomial(n,p0);b=binomial(n,p1)
    for k in range(n+1):
        if sum(a[k:])<=alpha:return dict(n=n,reject_at_least=k,null_size=sum(a[k:]),power=sum(b[k:]))
    return dict(n=n,reject_at_least=n+1,null_size=0,power=0)
def difference(p0,p1,n,alpha):
    z=NormalDist().inv_cdf(1-alpha);sd=math.sqrt((p0*(1-p0)+p1*(1-p1))/n)
    return dict(per_group_effective_n=n,p0=p0,p1=p1,alpha=alpha,approximate_power=NormalDist().cdf((p1-p0)/sd-z))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Use a fresh output path.')
    first=next(rare(n,.01,.05,.0025)for n in range(50,1001)if rare(n,.01,.05,.0025)['power']>=.8)
    data=dict(status='Synthetic',test_status='Proposed',assumptions='Independent effective units, fixed null rates, one-sided family-adjusted tests. Clustering, estimated controls, missingness and multiple route constraints require simulation before application.',
        design1=dict(null_rate=.01,alternative_rate=.05,alpha=.0025,minimum_n_under_assumptions=first,acquisition_target=300,power_at_target=rare(300,.01,.05,.0025)),
        design2=difference(.20,.30,600,.0025),design4=difference(.10,.20,400,.0025),
        design7_graphic=difference(.10,.25,250,.0025),design7_alignment=rare(60,.20,.50,.0025),
        design3=dict(target_assemblages=12,independent_marked_objects_per_assemblage=30,sites=3,total_effective_objects=360,
            copying_rho=.70,mutation_mu=.10,detectable_gain_bits_per_object=.10,required_simulated_power=.80,
            null_and_alternative_simulations_each=1000,power_estimated=False))
    out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print(json.dumps(data,indent=2))
if __name__=='__main__':main()

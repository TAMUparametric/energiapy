"""Historical-data validation; requires local case-study CSVs and baseline Git objects."""
import argparse, ast, hashlib, importlib.util, json, pathlib, subprocess, sys, warnings
import numpy as np
import pandas as pd
import sklearn, scipy
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import StandardScaler
from enum import Enum, auto
from dataclasses import dataclass
from itertools import product
ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BASELINE = "0604a26ee45a564bcd83c736077944cb1c59a50d"
parser = argparse.ArgumentParser(description="Compare historical and current AHC selections.")
parser.add_argument("--data-dir", required=True, type=pathlib.Path)
parser.add_argument("--output", type=pathlib.Path, default=ROOT / "results.json")
args = parser.parse_args()
DATA = args.data_dir
sources = {}
for filename, relative in [("legacy_time.py", "components/temporal_scale.py"),
                           ("legacy_math.py", "utils/math_utils.py"),
                           ("legacy_ahc.py", "aggregation/ahc.py")]:
    sources[filename] = subprocess.check_output(
        ["git", "show", f"{BASELINE}:src/energiapy/{relative}"], cwd=REPO, text=True
    )
# Execute exact historical definitions, excluding imports of the full legacy model.
ns=dict(numpy=np,pandas=pd,AgglomerativeClustering=AgglomerativeClustering,NearestCentroid=NearestCentroid,StandardScaler=StandardScaler,Enum=Enum,auto=auto,dataclass=dataclass,product=product)
for filename,names in [('legacy_time.py',{'TemporalScale'}),('legacy_math.py',{'scaler','find_euclidean_distance','generate_connectivity_matrix'}),('legacy_ahc.py',{'IncludeAHC','agg_hierarchial'})]:
 tree=ast.parse(sources[filename])
 tree.body=[node for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names]
 exec(compile(tree,filename,'exec'),ns)
spec=importlib.util.spec_from_file_location('current_ahc',REPO / 'src/energia/surrogate/aggregation/ahc.py')
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)

def run(name,frame,k):
 captures=[]
 def trace(frame,event,arg):
  if event=='return' and frame.f_code.co_name=='agg_hierarchial': captures.append(frame.f_locals.copy())
 sys.setprofile(trace)
 try:
  with warnings.catch_warnings(record=True) as caught:
   warnings.simplefilter('always')
   old,_,info=ns['agg_hierarchial'](ns['TemporalScale']([1,365,24]),1,k,[ns['IncludeAHC'].CAPACITY],capacity_factor={'site':{str(i):frame.iloc[:,i].to_numpy() for i in range(frame.shape[1])}})
 finally: sys.setprofile(None)
 new=mod.ahc(*(frame.iloc[:,i].to_numpy() for i in range(frame.shape[1])),periods=k,period_length=24,selection="nearest_centroid")
 legacy=mod.ahc(*(frame.iloc[:,i].to_numpy() for i in range(frame.shape[1])),periods=k,period_length=24)
 assert legacy.selection == "legacy"
 loc=captures[0]; labels=loc['cluster_labels']; groups=[np.flatnonzero(labels==c) for c in np.unique(labels)];groups.sort(key=lambda x:x[0])
 canonical=np.empty(365,dtype=int)
 for i,g in enumerate(groups):canonical[g]=i
 scaled=loc['scaled_array']
 reps=[]; sse=0.; recon=0.
 for g in groups:
  d=((scaled[g]-scaled[g].mean(axis=0))**2).sum(axis=1)
  r=g[np.flatnonzero(np.isclose(d,d.min(),rtol=1e-12,atol=1e-12))[0]];reps.append(int(r));sse+=float(d.sum());recon+=float(((scaled[g]-scaled[r])**2).sum())
 old_reps=[int(old[(0,i,0)]['rep_period'][1]) for i in range(k)]
 old_weights=[int(old[(0,i,0)]['cluster_wt']) for i in range(k)]
 # Compare weighted original-unit totals, rather than assuming representative positions identify clusters.
 profiles=frame.to_numpy().reshape(365,24,-1)
 ot=(profiles[old_reps]*np.array(old_weights)[:,None,None]).sum(axis=(0,1))
 nt=(new.representatives*new.weights[:,None,None]).sum(axis=(0,1))
 np.testing.assert_array_equal(legacy.representative_indices,old_reps)
 np.testing.assert_array_equal(legacy.weights,old_weights)
 np.testing.assert_array_equal(legacy.representatives,profiles[old_reps])
 np.testing.assert_array_equal(canonical,new.labels)
 np.testing.assert_array_equal(reps,new.representative_indices)
 np.testing.assert_allclose(sse,new.inertia,rtol=1e-12)
 np.testing.assert_allclose(recon,new.reconstruction_error,rtol=1e-12)
 return dict(legacy_mode_representatives=legacy.representative_indices.tolist(),legacy_mode_weights=legacy.weights.tolist(),legacy_mode_inertia=legacy.inertia,legacy_mode_reconstruction_error=legacy.reconstruction_error,legacy_profiles_equal=True,legacy_labels=legacy.labels.tolist(),nearest_centroid_labels=new.labels.tolist(),historical_canonical_labels=canonical.tolist(),dataset=name,clusters=k,partition_equal=bool(np.array_equal(canonical,new.labels)),canonical_weights_equal=bool(np.array_equal([len(g) for g in groups],new.weights)),legacy_representatives=old_reps,nearest_centroid_representatives=new.representative_indices.tolist(),legacy_weights=old_weights,nearest_centroid_weights=new.weights.tolist(),representative_positions_equal=int(np.sum(np.array(old_reps)==new.representative_indices)),legacy_unique_representatives=len(set(old_reps)),corrected_legacy_representatives_equal=bool(np.array_equal(reps,new.representative_indices)),legacy_reported_wcss=float(info['wcss_sum']),legacy_partition_centroid_sse=sse,nearest_centroid_inertia=new.inertia,nearest_centroid_reconstruction_error=new.reconstruction_error,corrected_legacy_reconstruction_sse=recon,legacy_weighted_totals=ot.tolist(),nearest_centroid_weighted_totals=nt.tolist(),columns=frame.columns.tolist(),warnings=sorted(set(str(w.message) for w in caught)))
sets={
 'houston_legacy_solar_wind':pd.concat([pd.read_csv(DATA/'ho_solar.csv',index_col=0),pd.read_csv(DATA/'ho_wind.csv',index_col=0)],axis=1),
 'houston_2019':pd.read_csv(DATA/'ho_solar19.csv',index_col=0),
 'sandiego_2019':pd.read_csv(DATA/'sd_solar19.csv',index_col=0),
 'newyork_2019_weather':pd.read_csv(DATA/'ny_solar19.csv')[['DNI','Wind Speed']],
 'newyork_2018_load':pd.read_csv(DATA/'NYC_load.csv')[['Load']],
}
results=[]
for name,frame in sets.items():
 assert frame.shape[0]==8760 and np.isfinite(frame.to_numpy()).all()
 for k in [20,35]:
  r=run(name,frame,k);results.append(r)
  print(name,k,'partition',r['partition_equal'],'reps',r['representative_positions_equal'],'/',k,'corrected',r['corrected_legacy_representatives_equal'],'SSE',r['legacy_reported_wcss'],r['nearest_centroid_inertia'],flush=True)
report=dict(default_selection='legacy',current_source_sha256=hashlib.sha256((REPO/'src/energia/surrogate/aggregation/ahc.py').read_bytes()).hexdigest(),baseline='0604a26ee45a564bcd83c736077944cb1c59a50d',environment=dict(python=sys.version,numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,scipy=scipy.__version__),input_sha256={f:hashlib.sha256((DATA/f).read_bytes()).hexdigest() for f in ['ho_solar.csv','ho_wind.csv','ho_solar19.csv','sd_solar19.csv','ny_solar19.csv','NYC_load.csv']},results=results)
args.output.write_text(json.dumps(report,indent=2)+'\n')

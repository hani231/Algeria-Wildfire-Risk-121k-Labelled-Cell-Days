"""Reproduire les contrôles d’audit et les métriques 2024 sans entraîner de modèle."""
import json,sys,subprocess,warnings
from pathlib import Path
import pandas as pd,numpy as np,joblib,sklearn
from pandas.testing import assert_frame_equal
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,average_precision_score,confusion_matrix
ROOT=Path(__file__).resolve().parents[1]
from src.cleaning_guide import clean_data
from src.train_decision_tree import build_temporal_splits
from src.statistical_analysis import analyse_training

def main():
    raw=pd.read_csv(ROOT/'Dataset/dataset.csv');df,_=clean_data(raw)
    assert_frame_equal(df,pd.read_csv(ROOT/'data/processed/dataset_clean.csv',parse_dates=['date']))
    protocol=json.loads((ROOT/'results/protocole_propose.json').read_text())
    train=df[df.split.eq('train')].sort_values(['date','cell_id']).reset_index(drop=True);v=df[df.split.eq('val')]
    folds=build_temporal_splits(train,protocol['cv_annees_validation'])
    assert len(folds)==5
    fold_rows=[]
    for tr,va in folds:
     fold_rows.append(dict(train_fin=int(train.iloc[tr].year.max()),validation=int(train.iloc[va].year.min()),n_train=len(tr),n_validation=len(va)))
    assert_frame_equal(pd.DataFrame(fold_rows),pd.read_csv(ROOT/'results/plis_temporels.csv'))
    principal,_,_=analyse_training(df); saved=pd.read_csv(ROOT/'results/analyses_statistiques.csv')
    assert_frame_equal(principal[saved.columns],saved,check_exact=False,atol=1e-12,rtol=1e-12)
    metric_records=[]
    paths={'Zero-R':'zeror_developpement.joblib','GaussianNB':'naive_bayes_developpement.joblib','DecisionTree':'arbre_decision_developpement.joblib'}
    saved=pd.concat([pd.read_csv(ROOT/'results/resultats_zeror_nb_validation.csv'),pd.read_csv(ROOT/'results/resultats_arbre_decision_validation.csv')]).set_index('model')
    for name,f in paths.items():
     with warnings.catch_warnings(record=True) as ws: model=joblib.load(ROOT/'models'/f)
     pred=model.predict(v[protocol['features']]); scores=model.predict_proba(v[protocol['features']])[:,list(model.classes_).index(1)]
     metrics={'accuracy':accuracy_score(v.label,pred),'precision':precision_score(v.label,pred,zero_division=0),'recall':recall_score(v.label,pred,zero_division=0),'f1':f1_score(v.label,pred,zero_division=0),'roc_auc':roc_auc_score(v.label,scores),'average_precision':average_precision_score(v.label,scores)}
     for k,value in metrics.items(): assert np.isclose(value,saved.loc[name,'val2024_'+k],atol=1e-12)
     cm=confusion_matrix(v.label,pred,labels=[0,1]).ravel().tolist()
     assert cm==saved.loc[name,['tn','fp','fn','tp']].tolist()
     metric_records.append({'model':name,**metrics,'confusion_tn_fp_fn_tp':cm,'warnings':[str(w.message) for w in ws]})
    summary={'base_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'clean_csv_equivalent':True,'five_temporal_folds_verified':True,'principal_statistics_reproduced':True,'sklearn_runtime':sklearn.__version__,'validation_2024_reproduced':metric_records,'test_2025_evaluated':False}
    (ROOT/'results/audit_siad03').mkdir(parents=True, exist_ok=True)
    (ROOT/'results/audit_siad03/verification_existant.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
    print('Données nettoyées identiques ; 5 plis conformes ; statistiques et 3 métriques modèles reproduites sur 2024.')


if __name__ == '__main__':
    main()

"""Independent checks of accounting, aggregation and saved-model consistency."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits
from backend.main import app
from backend.services.data_service import DataService
from ml.preprocess import aggregate_rfm

ROOT=Path(__file__).resolve().parents[1]
client=TestClient(app)

def test_independent_rfm_accounting():
    transactions=pd.read_parquet(ROOT/'data/processed/cleaned_transactions.parquet')
    rfm=pd.read_csv(ROOT/'data/processed/rfm_raw.csv').set_index('CustomerID')
    audit=json.loads((ROOT/'data/processed/preprocessing_audit.json').read_text())
    previous=audit['raw_rows']
    for step in audit['steps']:
        assert previous-step['excluded']==step['remaining']
        previous=step['remaining']
    assert previous==len(transactions)==audit['total_clean_rows']
    assert not transactions['CustomerID'].isna().any()
    assert (transactions[['Quantity','UnitPrice']]>0).all().all()
    assert not transactions['InvoiceNo'].astype(str).str.upper().str.startswith('C').any()
    assert not transactions.duplicated(subset=['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']).any()
    assert rfm.index.is_unique
    expected=transactions.groupby('CustomerID')['InvoiceNo'].nunique()
    pd.testing.assert_series_equal(rfm.Frequency,expected,check_names=False)
    np.testing.assert_allclose(rfm.Monetary,transactions.groupby('CustomerID')['Revenue'].sum().round(2))
    reference=pd.Timestamp(audit['reference_date'])
    expected_r=(reference-transactions.groupby('CustomerID')['InvoiceDate'].max()).dt.days
    pd.testing.assert_series_equal(rfm.Recency,expected_r,check_names=False)
    assert round(rfm.Monetary.sum(),2)==audit['total_revenue_gbp']
    assert rfm.Frequency.sum()==audit['total_orders']==transactions.InvoiceNo.nunique()

def test_frequency_counts_orders_not_lines():
    data=pd.DataFrame({'CustomerID':[1,1,1,2], 'InvoiceNo':['a','a','b','c'], 'InvoiceDate':pd.to_datetime(['2011-01-01','2011-01-01','2011-01-03','2011-01-02']), 'Revenue':[3.,4.,10.,2.]})
    result=aggregate_rfm(data,pd.Timestamp('2011-01-04')).set_index('CustomerID')
    assert result.loc[1].to_dict()=={'Recency':1.,'Frequency':2.,'Monetary':17.}
    assert result.loc[2,'Recency']==2

def test_saved_pipeline_matches_every_training_assignment_and_metrics():
    data=pd.read_csv(ROOT/'ml/artifacts/customer_segments.csv')
    pipeline=joblib.load(ROOT/'ml/artifacts/prediction_pipeline.joblib')
    metrics=json.loads((ROOT/'ml/artifacts/evaluation_metrics.json').read_text())
    raw=data[['Recency','Frequency','Monetary']].values
    with threadpool_limits(limits=1):
        predicted=pipeline.predict(raw)
        np.testing.assert_array_equal(predicted,data.Cluster)
        x=pipeline[:-1].transform(raw)
        assert round(silhouette_score(x,predicted),4)==metrics['silhouette_score']
        assert round(davies_bouldin_score(x,predicted),4)==metrics['davies_bouldin_index']
        assert round(calinski_harabasz_score(x,predicted),2)==metrics['calinski_harabasz_score']
        repeated=KMeans(n_clusters=metrics['selected_k'],random_state=42,n_init=20).fit(x)
        np.testing.assert_array_equal(repeated.labels_,predicted)
    candidate=next(r for r in metrics['candidate_k_evaluation'] if r['k']==metrics['selected_k'])
    assert candidate['silhouette']==metrics['silhouette_score']
    assert candidate['inertia']==metrics['inertia']
    assert candidate['cluster_sizes']==np.bincount(predicted).tolist()

@pytest.mark.parametrize('payload', [{}, {'recency':'oops','frequency':1,'monetary':100}, {'recency':10,'frequency':1.5,'monetary':100}, {'recency':True,'frequency':1,'monetary':100}, {'recency':10,'frequency':1,'monetary':'NaN'}, {'recency':10,'frequency':1,'monetary':'Infinity'}, {'recency':10,'frequency':1,'monetary':100,'unexpected':1}])
def test_invalid_prediction_inputs(payload):
    assert client.post('/api/predict',json=payload).status_code==422

@pytest.mark.parametrize('number',['NaN','Infinity','-Infinity','1e999'])
def test_nonfinite_json_numbers_return_serializable_errors(number):
    response=client.post('/api/predict',content='{"recency":'+number+',"frequency":1,"monetary":100}',headers={'Content-Type':'application/json'})
    assert response.status_code==422
    assert response.json()['detail'][0]['loc']==['body','recency']

@pytest.mark.parametrize('limit',[-1,0,10001,'bad'])
def test_invalid_visualization_limits(limit):
    assert client.get(f'/api/visualization?sample_limit={limit}').status_code==422

def test_full_customer_map_and_training_boundaries():
    data=client.get('/api/visualization').json()
    assert data['total_points']==data['total_customers']==4338
    assert len({p['customer_id'] for p in data['points']})==4338
    metrics=json.loads((ROOT/'ml/artifacts/evaluation_metrics.json').read_text())
    maximum=metrics['training_ranges']['Monetary']['max']
    assert client.post('/api/predict',json={'recency':10,'frequency':1,'monetary':maximum+.01}).json()['is_outlier']
    assert client.post('/api/predict',json={'recency':0,'frequency':1,'monetary':100}).json()['is_outlier']

def test_missing_profiles_are_not_silently_counted(monkeypatch,tmp_path):
    import backend.services.data_service as module
    monkeypatch.setattr(module,'PROFILES_FILE',tmp_path/'missing.json')
    with pytest.raises(FileNotFoundError): DataService().get_overview()

def test_paths_independent_of_working_directory(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    assert client.get('/api/overview').status_code==200
    assert client.post('/api/predict',json={'recency':12,'frequency':6,'monetary':1800}).status_code==200

def test_health_and_prediction_fail_when_pipeline_missing(monkeypatch):
    from backend.services.prediction_service import prediction_service
    monkeypatch.setattr(prediction_service,'_pipeline',None)
    monkeypatch.setattr(prediction_service,'_load_artifacts',lambda:None)
    assert client.get('/api/health').status_code==503
    assert client.post('/api/predict',json={'recency':12,'frequency':6,'monetary':1800}).status_code==503

def test_cors_is_restricted_to_configured_origins():
    allowed=client.options('/api/predict',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'POST'})
    assert allowed.headers['access-control-allow-origin']=='http://localhost:5173'
    denied=client.options('/api/predict',headers={'Origin':'https://unconfigured.example','Access-Control-Request-Method':'POST'})
    assert denied.status_code==400
    assert 'access-control-allow-origin' not in denied.headers

def test_report_sections_results_and_page_geometry():
    import fitz
    metrics=json.loads((ROOT/'ml/artifacts/evaluation_metrics.json').read_text())
    audit=json.loads((ROOT/'data/processed/preprocessing_audit.json').read_text())
    with fitz.open(ROOT/'reports/ShopSense_AI_Case_Study.pdf') as pdf:
        assert len(pdf)==7
        text='\n'.join(page.get_text() for page in pdf)
        for section in ['1. Introduction','2. Literature','3. Problem Statement / Objectives','4. Methodology / Implementation','5. Results']:
            assert text.count(section)==1
        for value in [f'{audit["unique_customers"]:,}',f'{audit["total_orders"]:,}',f'{audit["total_revenue_gbp"]:,.2f}',str(metrics['silhouette_score']),str(metrics['davies_bouldin_index']),str(metrics['calinski_harabasz_score'])]:
            assert value in text
        assert '$$' not in text
        assert sum(len(p.get_images()) for p in pdf)>=4
        for page in pdf:
            assert abs(page.rect.width-595.28)<1
            assert abs(page.rect.height-841.89)<1
            for x0,y0,x1,y1,*_ in page.get_text('blocks'):
                assert 0<=x0<x1<=page.rect.width
                assert 0<=y0<y1<=page.rect.height

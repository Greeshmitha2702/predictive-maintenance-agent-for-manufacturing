import json, sys, time, unittest, urllib.request, urllib.error
BASE_URL = 'http://127.0.0.1:8000'

def _post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE_URL+path, data=data, headers={'Content-Type':'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())

def _get(path):
    try:
        with urllib.request.urlopen(BASE_URL+path) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())

VALID_DIRS = {'increases_failure_risk','decreases_failure_risk'}
VALID_RISK = {'LOW','MEDIUM','HIGH'}

def _check(tc, body, lbl):
    for f in ('failure_probability','failure_predicted','is_anomaly','anomaly_score','risk_level','model_version','explanation','recommendations'):
        tc.assertIn(f, body, lbl+': missing '+f)
    tc.assertIsInstance(body['failure_probability'], float)
    tc.assertIsInstance(body['failure_predicted'], bool)
    tc.assertIsInstance(body['is_anomaly'], bool)
    tc.assertGreaterEqual(body['failure_probability'], 0.0)
    tc.assertLessEqual(body['failure_probability'], 1.0)
    tc.assertIn(body['risk_level'], VALID_RISK, lbl+': bad risk_level')
    exp = body['explanation']
    tc.assertIsNotNone(exp)
    tc.assertIn('top_factors', exp)
    for fac in exp['top_factors']:
        tc.assertIn(fac.get('direction'), VALID_DIRS)
    recs = body['recommendations']
    tc.assertIsNotNone(recs, lbl+': recs null')
    tc.assertEqual(recs['risk_level'], body['risk_level'], lbl+': risk_level mismatch')
    ids = [r['id'] for r in recs['recommendations']]
    tc.assertEqual(len(ids), len(set(ids)), lbl+': dup ids')
    for rec in recs['recommendations']:
        for field in ('id','category','severity','title','action'):
            tc.assertIn(field, rec)

class E2E(unittest.TestCase):

    def test_01_health(self):
        c,b = _get('/api/v1/health')
        self.assertEqual(c,200)
        self.assertEqual(b.get('status'),'ok')
        self.assertIn('version',b)
        print('  health:', b)

    def test_02_baseline(self):
        p={"type":"M","air_temperature":298.1,"process_temperature":308.6,"rotational_speed":1551,"torque":42.8,"tool_wear":120}
        c,b = _post('/api/v1/predict',p)
        self.assertEqual(c,200)
        _check(self,b,'baseline')
        print('  baseline fp=%s risk=%s anomaly=%s' % (b['failure_probability'],b['risk_level'],b['is_anomaly']))

    def _ids(self, b): return [r['id'] for r in b['recommendations']['recommendations']]
    def _sev(self, b): return [r['severity'] for r in b['recommendations']['recommendations']]
    def _facs(self, b): return b['explanation']['top_factors']
    def _has_pos_shap(self, facs, keyword): return any(keyword in f['feature'].lower() and f['direction']=='increases_failure_risk' for f in facs)

    def test_sc01_normal(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1500,'torque':40.0,'tool_wear':50})
        self.assertEqual(c,200); _check(self,b,'sc01')
        print('  sc01 fp=%s risk=%s anomaly=%s recs=%s'%(b['failure_probability'],b['risk_level'],b['is_anomaly'],self._ids(b)))

    def test_sc02_anomaly_independence(self):
        c,b = _post('/api/v1/predict',{'type':'L','air_temperature':299.0,'process_temperature':309.0,'rotational_speed':1600,'torque':38.0,'tool_wear':80})
        self.assertEqual(c,200); _check(self,b,'sc02')
        ids = self._ids(b)
        if b['is_anomaly'] and b['risk_level']=='LOW':
            self.assertIn('REC-ANOM-001',ids)
            self.assertNotIn('REC-ANOM-HIGH-001',ids)
        print('  sc02 anomaly=%s risk=%s recs=%s'%(b['is_anomaly'],b['risk_level'],ids))

    def test_sc03_high_failure(self):
        c,b = _post('/api/v1/predict',{'type':'L','air_temperature':305.0,'process_temperature':315.0,'rotational_speed':1200,'torque':70.0,'tool_wear':240})
        self.assertEqual(c,200); _check(self,b,'sc03')
        if b['risk_level']=='HIGH': self.assertIn('CRITICAL',self._sev(b))
        print('  sc03 fp=%s risk=%s recs=%s'%(b['failure_probability'],b['risk_level'],self._ids(b)))

    def test_sc04_anomaly_high(self):
        c,b = _post('/api/v1/predict',{'type':'L','air_temperature':306.0,'process_temperature':316.0,'rotational_speed':1100,'torque':72.0,'tool_wear':250})
        self.assertEqual(c,200); _check(self,b,'sc04')
        ids = self._ids(b)
        if b['is_anomaly'] and b['risk_level']=='HIGH':
            self.assertIn('REC-ANOM-HIGH-001',ids)
            self.assertNotIn('REC-ANOM-001',ids)
        print('  sc04 anomaly=%s risk=%s recs=%s'%(b['is_anomaly'],b['risk_level'],ids))

    def test_sc05_tool_wear(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1400,'torque':60.0,'tool_wear':230})
        self.assertEqual(c,200); _check(self,b,'sc05')
        ids = self._ids(b); facs = self._facs(b)
        tp = self._has_pos_shap(facs,'tool')
        if tp:
            self.assertTrue(any('REC-TOOL' in i for i in ids),'pos tool shap but no TOOLING rec')
            if 'REC-TOOL-002' in ids: self.assertNotIn('REC-TOOL-001',ids)
        print('  sc05 fp=%s tool_pos=%s recs=%s'%(b['failure_probability'],tp,ids))

    def test_sc06_torque(self):
        c,b = _post('/api/v1/predict',{'type':'H','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':2800,'torque':70.0,'tool_wear':100})
        self.assertEqual(c,200); _check(self,b,'sc06')
        ids = self._ids(b); facs = self._facs(b)
        tp = self._has_pos_shap(facs,'torque')
        if tp: self.assertIn('REC-MECH-001',ids,'pos torque shap but no REC-MECH-001')
        print('  sc06 fp=%s torque_pos=%s recs=%s'%(b['failure_probability'],tp,ids))

    def test_sc07_temperature(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':304.0,'process_temperature':315.0,'rotational_speed':1500,'torque':42.0,'tool_wear':100})
        self.assertEqual(c,200); _check(self,b,'sc07')
        ids = self._ids(b); facs = self._facs(b)
        tp = any(any(t in f['feature'].lower() for t in ('temp','temperature')) and f['direction']=='increases_failure_risk' for f in facs)
        if tp: self.assertIn('REC-THRM-001',ids,'pos temp shap but no REC-THRM-001')
        else: self.assertNotIn('REC-THRM-001',ids,'REC-THRM-001 fired without pos temp shap')
        print('  sc07 fp=%s temp_pos=%s recs=%s'%(b['failure_probability'],tp,ids))

    def test_sc08_no_dup_ids(self):
        c,b = _post('/api/v1/predict',{'type':'L','air_temperature':304.0,'process_temperature':315.0,'rotational_speed':1100,'torque':70.0,'tool_wear':230})
        self.assertEqual(c,200); _check(self,b,'sc08')
        ids = self._ids(b)
        self.assertEqual(len(ids),len(set(ids)),'dup ids: '+str(ids))
        print('  sc08 recs=%s'%ids)

    def test_sc09_shap_dirs(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1500,'torque':40.0,'tool_wear':120})
        self.assertEqual(c,200); _check(self,b,'sc09')
        for f in self._facs(b): self.assertIn(f['direction'],VALID_DIRS)
        print('  sc09 %d factors, all directions valid'%len(self._facs(b)))

    def test_sc10_fallback(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1500,'torque':40.0,'tool_wear':50})
        self.assertEqual(c,200); _check(self,b,'sc10')
        ids = self._ids(b)
        self.assertEqual(len(ids),len(set(ids)))
        print('  sc10 risk=%s recs=%s'%(b['risk_level'],ids))

    def test_sc11_medium(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':300.0,'process_temperature':311.0,'rotational_speed':1400,'torque':55.0,'tool_wear':160})
        self.assertEqual(c,200); _check(self,b,'sc11')
        ids = self._ids(b)
        if b['risk_level']=='MEDIUM': self.assertGreater(len(ids),0)
        print('  sc11 fp=%s risk=%s recs=%s'%(b['failure_probability'],b['risk_level'],ids))

    def test_sc12_high_fallback(self):
        c,b = _post('/api/v1/predict',{'type':'L','air_temperature':305.0,'process_temperature':315.0,'rotational_speed':1200,'torque':70.0,'tool_wear':240})
        self.assertEqual(c,200); _check(self,b,'sc12')
        if b['risk_level']=='HIGH': self.assertIn('CRITICAL',self._sev(b))
        print('  sc12 fp=%s risk=%s recs=%s'%(b['failure_probability'],b['risk_level'],self._ids(b)))

    def test_err01_missing_field(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'rotational_speed':1500,'torque':40.0,'tool_wear':120})
        self.assertEqual(c,422); print('  err01 HTTP',c)

    def test_err02_bad_type(self):
        c,b = _post('/api/v1/predict',{'type':'X','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1500,'torque':40.0,'tool_wear':120})
        self.assertEqual(c,422); print('  err02 HTTP',c)

    def test_err03_neg_temp(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':-10.0,'process_temperature':308.0,'rotational_speed':1500,'torque':40.0,'tool_wear':120})
        self.assertEqual(c,422); print('  err03 HTTP',c)

    def test_err04_neg_speed(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':-100,'torque':40.0,'tool_wear':120})
        self.assertEqual(c,422); print('  err04 HTTP',c)

    def test_err05_neg_torque(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1500,'torque':-5.0,'tool_wear':120})
        self.assertEqual(c,422); print('  err05 HTTP',c)

    def test_err06_neg_tool_wear(self):
        c,b = _post('/api/v1/predict',{'type':'M','air_temperature':298.0,'process_temperature':308.0,'rotational_speed':1500,'torque':40.0,'tool_wear':-10})
        self.assertEqual(c,422); print('  err06 HTTP',c)

def _ready(r=5,d=2):
    for _ in range(r):
        try:
            with urllib.request.urlopen(BASE_URL+'/api/v1/health') as resp:
                if resp.status==200: return True
        except Exception: pass
        time.sleep(d)
    return False

if __name__=='__main__':
    print('Checking', BASE_URL)
    if not _ready():
        print('ERROR: server not reachable. Run: python -m uvicorn app.main:app --port 8000')
        sys.exit(1)
    print('Server ready. Running E2E tests...')
    loader=unittest.TestLoader(); loader.sortTestMethodsUsing=None
    runner=unittest.TextTestRunner(verbosity=2)
    result=runner.run(loader.loadTestsFromTestCase(E2E))
    sys.exit(0 if result.wasSuccessful() else 1)

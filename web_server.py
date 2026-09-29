from pathlib import Path
import sys, threading, datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT=Path(__file__).resolve().parent
BACKEND=ROOT/"backend"
if str(BACKEND) not in sys.path: sys.path.insert(0,str(BACKEND))
from app.algorithms.graph import Graph
from app.algorithms.hospital_matcher import Hospital, Requirement
from app.algorithms.allocation_optimizer import AllocationEngine

app=FastAPI(title="RescueNet Emergency Operations")
app.mount('/static', StaticFiles(directory=str(ROOT/'web')), name='static')

# Real facilities in Durg/Bhilai. Capacity figures are publicly reported totals;
# current availability below is an illustrative presentation snapshot, not live data.
HOSPITALS={
 'H001': Hospital('H001','SVM Multispeciality Hospital','H001',8,2,30,0.30,1,{'Emergency','Orthopaedics','General-Medicine','Paediatrics'}),
 'H002': Hospital('H002','Aarogyam Superspeciality Hospital & Research Center','H002',18,8,50,0.42,3,{'Emergency','Cardiology','Orthopaedics','Nephrology','Urology'}),
 'H003': Hospital('H003','S R Hospital and Research Centre','H003',28,6,180,0.62,4,{'Emergency','Cardiology','Orthopaedics','General-Medicine'}),
 'H004': Hospital('H004','Hi Tek Superspeciality Hospital','H004',35,12,175,0.55,5,{'Emergency','Cardiology','Neurology','Orthopaedics','Nephrology'}),
}
G=Graph()
for a,b,km in [
 ('INC1','J1',2.1),('J1','H001',2.4),('J1','J2',3.0),('J2','H002',3.2),
 ('INC2','J2',2.4),('J2','H003',4.2),('J2','J3',2.7),('J3','H004',3.4),
 ('INC3','J3',2.2),('INC4','J1',3.5),('INC5','J2',3.1),('J1','J3',5.0)
]: G.add_road(a,b,km)
for n in ['INC1','INC2','INC3','INC4','INC5','J1','J2','J3','H001','H002','H003','H004']: G.add_node(n)
engine=AllocationEngine(G,HOSPITALS)
lock=threading.Lock()

# Five fictional emergency incidents placed at real-city-area coordinates for demonstration.
INCIDENTS=[
 {'id':'ACC-101','label':'Multi-vehicle collision','location':'Supela Junction','node':'INC1','lat':21.2047,'lng':81.3406,'department':'Emergency','icu':True,'ventilator':True,'status':'Awaiting'},
 {'id':'ACC-102','label':'Road traffic trauma','location':'Nehru Nagar','node':'INC2','lat':21.2006,'lng':81.3248,'department':'Orthopaedics','icu':True,'ventilator':False,'status':'Awaiting'},
 {'id':'ACC-103','label':'Two-wheeler collision','location':'Durg Station area','node':'INC3','lat':21.1899,'lng':81.2770,'department':'Emergency','icu':False,'ventilator':False,'status':'Awaiting'},
 {'id':'ACC-104','label':'Highway collision','location':'Durg Bypass / NH-53','node':'INC4','lat':21.2175,'lng':81.3240,'department':'Cardiology','icu':True,'ventilator':False,'status':'Awaiting'},
 {'id':'ACC-105','label':'Bus accident','location':'Kachandur side','node':'INC5','lat':21.2390,'lng':81.3611,'department':'Orthopaedics','icu':True,'ventilator':True,'status':'Awaiting'},
]
audit=[]
def now(): return datetime.datetime.now().strftime('%d %b %Y, %H:%M')
def hospital_dict(h):
 return {'id':h.id,'name':h.name,'node':h.node,'icu_available':h.icu_available,'general_available':h.general_available,'ventilators_available':h.ventilators_available,'departments':sorted(h.departments)}
def log(event,case_id=None,hospital_id=None,source='System'):
 audit.append({'event':event,'case_id':case_id,'hospital_id':hospital_id,'source':source,'time':now()})
class AllocationIn(BaseModel): case_id:str; source_node:str; department:str; icu:bool=False; ventilator:bool=False
class ConfirmIn(BaseModel): case_id:str; hospital_id:str; department:str; icu:bool=False; ventilator:bool=False
@app.get('/')
def home(): return FileResponse(ROOT/'web/index.html')
@app.get('/api/state')
def state(): return {'hospitals':[hospital_dict(h) for h in HOSPITALS.values()],'cases':INCIDENTS,'audit':audit}
@app.post('/api/allocate')
def allocate(x:AllocationIn):
 req=Requirement(icu=x.icu,departments=(x.department,) if x.department else ())
 with lock: out=engine.recommend(x.case_id,x.source_node,req)
 feasible=[{'hospital':hospital_dict(h),'route':{'distance_km':r.distance_km,'time_min':r.time_min,'path':r.path},'cost':c} for h,r,c in out['feasible']]
 log('ALLOCATION_RECOMMENDED',x.case_id,feasible[0]['hospital']['id'] if feasible else None,'DSA Engine')
 return {'case_id':x.case_id,'feasible':feasible,'rejected':out['rejected'],'reason':out['reason']}
@app.post('/api/confirm')
def confirm(x:ConfirmIn):
 req=Requirement(icu=x.icu,departments=(x.department,) if x.department else ())
 with lock:
  try: a=engine.confirm(x.case_id,x.hospital_id,req)
  except Exception as e: raise HTTPException(400,str(e))
 for c in INCIDENTS:
  if c['id']==x.case_id: c['status']='Allocated'; c['allocated_hospital']=x.hospital_id
 log('ALLOCATION_CONFIRMED',x.case_id,x.hospital_id,'Allocation Engine'); log('RESOURCE_UPDATED',x.case_id,x.hospital_id,'Resource Manager')
 return {'allocation':a}

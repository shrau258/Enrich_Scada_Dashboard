import {useEffect,useState} from 'react';
import {Header} from './components';
import type {Mode,NavKey,PlantConfiguration,PlantSummary} from './types';
import {Dashboard,SLD,Trend,Inverters,Strings,Architecture,Wms,Alarms,Reports} from './pages';
import {ConfigurationPage} from './ConfigPage';
import {SimulationProvider,useSimulation} from './simulation';
const pages={dashboard:Dashboard,sld:SLD,trend:Trend,inverters:Inverters,strings:Strings,architecture:Architecture,wms:Wms,alarms:Alarms,reports:Reports};
const emptyConfig:PlantConfiguration={plantName:'',customerName:'',acCapacityMw:'',dcCapacityMwp:'',inverterManufacturer:'',modbusFunctionCode:'FC3',workbookName:'',inverterCount:8,sharedIp:'192.168.X.X',basePort:501,deviceArrayPort:null,deviceArrayGroups:['WMS','Trafo','TVM','Annunciator'].map(name=>({name,enabled:true})),state:'DRAFT'};
const apiBase=import.meta.env.VITE_API_BASE_URL||'http://127.0.0.1:8000';
function Application(){
 const initial=(location.hash.slice(1)||'dashboard') as NavKey;
 const [page,setPage]=useState<NavKey>(initial==='configuration'||initial in pages?initial:'dashboard');
 const [mode,setMode]=useState<Mode>('demo'),[config,setConfig]=useState<PlantConfiguration>(emptyConfig);
 const simulation=useSimulation();
 useEffect(()=>{location.hash=page},[page]);
 useEffect(()=>{fetch(`${apiBase}/api/v1/plants`).then(async response=>{if(!response.ok)throw new Error('Unable to load plants');return response.json() as Promise<PlantSummary[]>}).then(async plants=>{for(const item of plants.filter(p=>p.source==='DEMO')){const id=String(item.plantId).replace('demo-db-','');const response=await fetch(`${apiBase}/api/v1/demo/plants/${id}/configuration`);if(response.ok){const saved=await response.json();simulation.addPlant({name:saved.plantName,customerName:saved.customerName,acCapacityMw:Number(saved.acCapacityMw),dcCapacityMwp:Number(saved.dcCapacityMwp),inverterCount:saved.inverterCount})}}}).catch(()=>{})},[]);
 const Page=page==='configuration'?null:pages[page as keyof typeof pages];
 return <div className="app"><Header page={page} onNav={setPage} mode={mode} setMode={setMode} customerName={config.customerName} dcCapacityMwp={config.dcCapacityMwp}/>{mode==='live'&&<div className="live-warning">LIVE MODE · Backend unavailable — values are UNAVAILABLE. Demo values are never used.</div>}{mode==='demo'&&<DemoPanel/>}<main>{page==='configuration'?<ConfigurationPage config={config} onChange={setConfig} apiBase={apiBase} addDemoPlant={simulation.addPlant}/>:Page&&<Page mode={mode}/>}</main><footer>© 2026 Enrich Energy Solutions Pvt. Ltd. All Rights Reserved.　•　{mode.toUpperCase()} MODE</footer></div>
}
function DemoPanel(){const {plants,selectedId,setSelectedId,clock,setClock,paused,setPaused,scenario,setScenario,reset}=useSimulation();return <details className="demo-panel"><summary>DEMO MODE · TESTING CONTROLS</summary><div><label>Plant <select value={selectedId} onChange={e=>setSelectedId(e.target.value)}>{plants.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><label>Simulation clock <input type="datetime-local" value={localClock(clock)} onChange={e=>e.target.value&&setClock(new Date(e.target.value))}/></label><button onClick={()=>setPaused(!paused)}>{paused?'RESUME':'PAUSE'}</button><button onClick={reset}>RESET</button><select value={scenario} onChange={e=>setScenario(e.target.value as typeof scenario)}><option value="healthy">All devices healthy</option><option value="inverter-fault">Trigger inverter fault</option><option value="communication-failure">Communication failure</option><option value="high-temperature">High temperature</option><option value="low-irradiance">Low irradiance</option><option value="nighttime">Nighttime</option><option value="api-interruption">Backend/API interruption</option></select></div></details>}
const localClock=(d:Date)=>new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);
export default function App(){return <SimulationProvider><Application/></SimulationProvider>}

import {useEffect,useState} from 'react';
import {Header} from './components';
import type {Mode,NavKey} from './types';
import {Dashboard,SLD,Trend,Inverters,Strings,Architecture,Wms,Alarms,Reports,Configuration} from './pages';
const pages={dashboard:Dashboard,sld:SLD,trend:Trend,inverters:Inverters,strings:Strings,architecture:Architecture,wms:Wms,alarms:Alarms,reports:Reports,configuration:Configuration};
export default function App(){const initial=(location.hash.slice(1)||'dashboard') as NavKey; const [page,setPage]=useState<NavKey>(initial in pages?initial:'dashboard');const [mode,setMode]=useState<Mode>('demo');useEffect(()=>{location.hash=page},[page]);const Page=pages[page];return <div className="app"><Header page={page} onNav={setPage} mode={mode} setMode={setMode}/>{mode==='live'&&<div className="live-warning">LIVE MODE · Backend unavailable — values are shown as UNAVAILABLE, never as zero.</div>}<main><Page mode={mode}/></main><footer>© 2026 Enrich Energy Solutions Pvt. Ltd. All Rights Reserved.　•　{mode.toUpperCase()} MODE</footer></div>}

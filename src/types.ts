export type Quality='GOOD'|'STALE'|'COMMUNICATION_FAILURE'|'UNAVAILABLE';
export type Mode='demo'|'live';
export type NavKey='dashboard'|'sld'|'trend'|'inverters'|'strings'|'architecture'|'wms'|'alarms'|'reports'|'configuration';
export interface Inverter {id:string;status:'RUNNING'|'FAULT'|'STANDBY'|'OFFLINE';power:number;dcVoltage:number;dcCurrent:number;temperature:number;efficiency:number;updated:string}

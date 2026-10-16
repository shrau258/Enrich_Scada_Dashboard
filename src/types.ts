export type Quality='GOOD'|'STALE'|'COMMUNICATION_FAILURE'|'UNAVAILABLE';
export type Mode='demo'|'live';
export type NavKey='dashboard'|'sld'|'trend'|'inverters'|'strings'|'architecture'|'wms'|'alarms'|'reports'|'configuration';
export interface Inverter {id:string;status:'RUNNING'|'FAULT'|'STANDBY'|'OFFLINE';power:number;dcPower:number;reactivePower:number;dcVoltage:number;dcCurrent:number;phaseVoltage:[number,number,number];todayGeneration:number;totalGeneration:number;powerFactor:number;frequency:number;temperature:number;efficiency:number;communication:'ONLINE'|'OFFLINE';quality:Quality;updated:string}
export type AlarmState='ACTIVE'|'ACKNOWLEDGED'|'CLEARED';
export interface DemoAlarm {id:string;plantId:string;deviceId:string;severity:'CRITICAL'|'MAJOR'|'MINOR';message:string;state:AlarmState;timestamp:string}
export interface DemoPlant {id:string;name:string;customerName:string;dcCapacityMwp:number;acCapacityMw:number;inverterCount:number;supportsStrings:boolean}
export interface WeatherReading {ghi:number;gti:number;cumulativeGti:number;ambientTemperature:number;moduleTemperature:number;humidity:number;windSpeed:number;windDirection:number;rainfall:number;quality:Quality}
export interface HistoryPoint {label:string;power:number;irradiance:number;energy:number;ambient:number;module:number}
export interface SimulationSnapshot {plantId:string;timestamp:string;source:'DEMO';powerKw:number;todayEnergyKwh:number;totalEnergyKwh:number;exportEnergyKwh:number;importEnergyKwh:number;peakPowerKw:number;pr:number;cuf:number;availability:number;quality:Quality;inverters:Inverter[];weather:WeatherReading;transformer:{wti01:number;wti02:number;oti01:number;oti02:number};meter:{phaseVoltage:[number,number,number];phaseCurrent:[number,number,number];activePower:number;reactivePower:number;apparentPower:number;frequency:number;powerFactor:number;importEnergy:number;exportEnergy:number;quality:Quality};annunciator:Array<{id:string;state:'NORMAL'|'WARNING'|'ALARM'}>;history:HistoryPoint[];alarms:DemoAlarm[]}
export interface PlantConfiguration {
  plantId?: number|string;
  id?: number;
  plantName: string;
  customerName: string;
  acCapacityMw: string;
  dcCapacityMwp: string;
  inverterManufacturer: string;
  modbusFunctionCode: string;
  workbookName: string;
  inverterCount: number;
  sharedIp: string;
  basePort: number;
  deviceArrayPort: number | null;
  deviceArrayGroups: Array<{name:string;enabled:boolean}>;
  state: 'DRAFT'|'VALIDATING'|'VALIDATED'|'PUBLISHED'|'ACTIVE'|'FAILED';
  workbookMappings?: Record<string,unknown>;
}
export interface PlantSummary {plantId:number|string;plantName:string;customerName:string;dcCapacityMwp:string;state:PlantConfiguration['state'];source?:'DEMO'|'LIVE'}

import {describe,expect,it} from 'vitest';
import {buildSnapshot,DEMO_PLANTS} from './simulation';
describe('multi-plant demo simulator',()=>{
 it('creates the configured inverter count without exceeding AC capacity',()=>{for(const plant of DEMO_PLANTS){const data=buildSnapshot(plant,new Date('2026-06-04T12:00:00'), 'healthy',0,7);expect(data.inverters).toHaveLength(plant.inverterCount);expect(data.powerKw).toBeLessThanOrEqual(plant.acCapacityMw*1000)}});
 it('sets generation to zero at night',()=>{const data=buildSnapshot(DEMO_PLANTS[0],new Date('2026-06-04T23:00:00'),'healthy',120,7);expect(data.powerKw).toBe(0);expect(data.todayEnergyKwh).toBe(120)});
 it('never decreases accumulated energy',()=>{const first=buildSnapshot(DEMO_PLANTS[1],new Date('2026-06-04T12:00:00'),'healthy',100,7);const second=buildSnapshot(DEMO_PLANTS[1],new Date('2026-06-04T12:00:05'),'healthy',first.todayEnergyKwh,7);expect(second.todayEnergyKwh).toBeGreaterThanOrEqual(first.todayEnergyKwh)});
 it('isolates a communication failure to one inverter',()=>{const data=buildSnapshot(DEMO_PLANTS[1],new Date('2026-06-04T12:00:00'),'communication-failure',0,7);expect(data.inverters.filter(x=>x.communication==='OFFLINE')).toHaveLength(1);expect(data.alarms[0].plantId).toBe(DEMO_PLANTS[1].id)});
 it('is deterministic for a fixed seed and tick',()=>{const at=new Date('2026-06-04T12:00:00');expect(buildSnapshot(DEMO_PLANTS[2],at,'healthy',0,99)).toEqual(buildSnapshot(DEMO_PLANTS[2],at,'healthy',0,99))});
});

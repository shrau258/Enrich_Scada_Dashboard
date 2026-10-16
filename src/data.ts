export const hours=['5 AM','6 AM','7 AM','8 AM','9 AM','10 AM','11 AM','12 PM','1 PM','2 PM','3 PM','4 PM','5 PM','6 PM','7 PM'];
export const irradiance=[50,180,370,610,820,990,1110,1180,1130,990,770,520,280,100,20];
export const generation=[0,90,430,1200,2450,3800,5150,6200,5900,4700,3400,2100,900,220,20];
export const inverters=Array.from({length:16},(_,i)=>({id:`INV-${String(i+1).padStart(2,'0')}`,status:i===6?'FAULT':i===11?'STANDBY':'RUNNING',power:i===6?0:i===11?5.4:598+((i*13)%31),dcVoltage:i===6?0:982+((i*7)%18),dcCurrent:i===6?0:602+((i*9)%27),temperature:i===6?51.2:47.5+((i%5)*.3),efficiency:i===6?0:98.1+((i%4)*.1),updated:i===6?'17:04:58':`17:05:${String(20+i%7).padStart(2,'0')}`}));
export const alarms=[
 ['04-06-2026 17:04:58','CRITICAL','INV-07','Inverter Communication Failure','ACTIVE'],
 ['04-06-2026 17:04:12','MAJOR','INV-12','Inverter Over Temperature','ACTIVE'],
 ['04-06-2026 17:03:45','MAJOR','METER-02','Grid Power High (>11 kV)','ACTIVE'],
 ['04-06-2026 17:02:33','CRITICAL','ACDB-01','AC Breaker Open','ACTIVE'],
 ['04-06-2026 16:55:20','MAJOR','TRF-01','Transformer Oil Temperature High','ACKNOWLEDGED'],
 ['04-06-2026 16:48:10','MINOR','WEATHER','GHI Sensor Signal Low','ACKNOWLEDGED'],
 ['04-06-2026 16:32:05','MINOR','COM-01','SCADA Server High CPU Usage','CLEARED'],
 ['04-06-2026 15:20:18','MAJOR','STRING-14','String Current Imbalance (>10%)','CLEARED'],
];

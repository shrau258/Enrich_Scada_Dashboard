from __future__ import annotations
import json,sqlite3
from pathlib import Path
from typing import Any
DB_PATH=Path(__file__).with_name('enrich_demo.sqlite3')
def connect():
    db=sqlite3.connect(DB_PATH);db.row_factory=sqlite3.Row
    db.execute('''CREATE TABLE IF NOT EXISTS demo_plants(id INTEGER PRIMARY KEY AUTOINCREMENT,plant_name TEXT NOT NULL UNIQUE,customer_name TEXT NOT NULL,ac_capacity_mw REAL NOT NULL,dc_capacity_mwp REAL NOT NULL,inverter_count INTEGER NOT NULL,configuration_json TEXT NOT NULL,mappings_json TEXT NOT NULL DEFAULT '{}',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''');db.commit();return db
def save(config:dict[str,Any],mappings:dict[str,Any]|None=None)->dict[str,Any]:
    with connect() as db:
        payload=json.dumps(config);mapping_json=json.dumps(mappings or config.get('workbook_mappings') or {})
        plant_id=config.get('plant_id')
        if plant_id:
            db.execute('''UPDATE demo_plants SET plant_name=?,customer_name=?,ac_capacity_mw=?,dc_capacity_mwp=?,inverter_count=?,configuration_json=?,mappings_json=?,updated_at=CURRENT_TIMESTAMP WHERE id=?''',(config['plant_name'],config['customer_name'],float(config['ac_capacity_mw']),float(config['dc_capacity_mwp']),config['inverter_count'],payload,mapping_json,plant_id))
        else:
            existing=db.execute('SELECT id FROM demo_plants WHERE plant_name=?',(config['plant_name'],)).fetchone()
            if existing: plant_id=existing['id'];db.execute('UPDATE demo_plants SET customer_name=?,ac_capacity_mw=?,dc_capacity_mwp=?,inverter_count=?,configuration_json=?,mappings_json=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(config['customer_name'],float(config['ac_capacity_mw']),float(config['dc_capacity_mwp']),config['inverter_count'],payload,mapping_json,plant_id))
            else: plant_id=db.execute('INSERT INTO demo_plants(plant_name,customer_name,ac_capacity_mw,dc_capacity_mwp,inverter_count,configuration_json,mappings_json) VALUES(?,?,?,?,?,?,?)',(config['plant_name'],config['customer_name'],float(config['ac_capacity_mw']),float(config['dc_capacity_mwp']),config['inverter_count'],payload,mapping_json)).lastrowid
        db.commit();return get(plant_id,db)
def get(plant_id:int,db=None):
    owned=db is None;db=db or connect();row=db.execute('SELECT * FROM demo_plants WHERE id=?',(plant_id,)).fetchone()
    if owned: db.close()
    if not row:return None
    config=json.loads(row['configuration_json']);config.update({'id':row['id'],'plant_id':row['id'],'state':'DRAFT','demo_source':True,'workbook_mappings':json.loads(row['mappings_json'])});return config
def list_all():
    with connect() as db:return [dict(row) for row in db.execute('SELECT * FROM demo_plants ORDER BY plant_name')]

from __future__ import annotations
import json
import os
from typing import Any
import psycopg
from psycopg.rows import dict_row

SCHEMA_STATEMENTS=[
"""CREATE TABLE IF NOT EXISTS scada_sites (
 id BIGSERIAL PRIMARY KEY, site_identifier TEXT NOT NULL UNIQUE,
 site_name TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())""",
"""CREATE TABLE IF NOT EXISTS scada_plants (
 id BIGSERIAL PRIMARY KEY, site_id BIGINT NOT NULL REFERENCES scada_sites(id),
 plant_name TEXT NOT NULL, customer_name TEXT NOT NULL,
 ac_capacity_mw NUMERIC(12,3) NOT NULL CHECK(ac_capacity_mw>0),
 dc_capacity_mwp NUMERIC(12,3) NOT NULL CHECK(dc_capacity_mwp>0),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(site_id,plant_name))""",
"""CREATE TABLE IF NOT EXISTS scada_configuration_drafts (
 id BIGSERIAL PRIMARY KEY,
 customer_name TEXT NOT NULL CHECK (length(trim(customer_name)) > 0),
 dc_capacity_mwp NUMERIC(12,3) NOT NULL CHECK (dc_capacity_mwp > 0),
 inverter_count INTEGER NOT NULL CHECK (inverter_count > 0),
 shared_ip TEXT NOT NULL CHECK (length(trim(shared_ip)) > 0),
 base_port INTEGER NOT NULL CHECK (base_port BETWEEN 1 AND 65535),
 device_array_port INTEGER NULL CHECK (device_array_port BETWEEN 1 AND 65535),
 generated_ports JSONB NOT NULL, device_array_settings JSONB NOT NULL,
 state TEXT NOT NULL DEFAULT 'DRAFT', created_at TIMESTAMPTZ NOT NULL DEFAULT now())""",
"ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS plant_id BIGINT REFERENCES scada_plants(id)",
"ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS plant_name TEXT",
"ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS ac_capacity_mw NUMERIC(12,3)",
"ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS inverter_manufacturer TEXT",
"ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS modbus_function_code TEXT",
"ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS workbook_name TEXT",
"CREATE INDEX IF NOT EXISTS ix_scada_configuration_drafts_plant_created ON scada_configuration_drafts (plant_id,created_at DESC,id DESC)",
]

def connect():
    url=os.getenv("DATABASE_URL")
    if not url: raise RuntimeError("DATABASE_URL is not configured")
    return psycopg.connect(url,connect_timeout=5,row_factory=dict_row)

def ensure_schema(connection)->None:
    for statement in SCHEMA_STATEMENTS: connection.execute(statement)
    connection.execute("INSERT INTO scada_sites(site_identifier,site_name) VALUES('LOCAL-SITE','Local Site') ON CONFLICT(site_identifier) DO NOTHING")

def save_draft(data:dict[str,Any],ports:list[int])->dict[str,Any]:
    with connect() as connection:
        ensure_schema(connection)
        site_id=connection.execute("SELECT id FROM scada_sites WHERE site_identifier='LOCAL-SITE'").fetchone()["id"]
        plant_id=data.get("plant_id")
        if plant_id is None:
            plant=connection.execute("""INSERT INTO scada_plants(site_id,plant_name,customer_name,ac_capacity_mw,dc_capacity_mwp)
              VALUES(%s,%s,%s,%s,%s) RETURNING id""",(site_id,data["plant_name"],data["customer_name"],data["ac_capacity_mw"],data["dc_capacity_mwp"])).fetchone()
            plant_id=plant["id"]
        else:
            updated=connection.execute("""UPDATE scada_plants SET plant_name=%s,customer_name=%s,ac_capacity_mw=%s,dc_capacity_mwp=%s,updated_at=now()
              WHERE id=%s AND site_id=%s RETURNING id""",(data["plant_name"],data["customer_name"],data["ac_capacity_mw"],data["dc_capacity_mwp"],plant_id,site_id)).fetchone()
            if updated is None: raise ValueError("Plant does not exist on this site")
        row=connection.execute("""INSERT INTO scada_configuration_drafts
          (plant_id,plant_name,customer_name,ac_capacity_mw,dc_capacity_mwp,inverter_manufacturer,modbus_function_code,workbook_name,
           inverter_count,shared_ip,base_port,device_array_port,generated_ports,device_array_settings,state)
          VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,'DRAFT') RETURNING *""",
          (plant_id,data["plant_name"],data["customer_name"],data["ac_capacity_mw"],data["dc_capacity_mwp"],data["inverter_manufacturer"],
           data["modbus_function_code"],data.get("workbook_name"),data["inverter_count"],data["host"],data["base_port"],data["device_array_port"],
           json.dumps(ports),json.dumps(data["device_array_settings"]))).fetchone()
        connection.commit(); return row

def list_plants()->list[dict[str,Any]]:
    with connect() as connection:
        ensure_schema(connection)
        return connection.execute("""SELECT p.id AS plant_id,p.plant_name,p.customer_name,p.dc_capacity_mwp,
          COALESCE(c.state,'DRAFT') state FROM scada_plants p
          LEFT JOIN LATERAL (SELECT state FROM scada_configuration_drafts WHERE plant_id=p.id ORDER BY created_at DESC,id DESC LIMIT 1) c ON true
          ORDER BY p.plant_name""").fetchall()

def plant_configuration(plant_id:int)->dict[str,Any]|None:
    with connect() as connection:
        ensure_schema(connection)
        return connection.execute("SELECT * FROM scada_configuration_drafts WHERE plant_id=%s ORDER BY created_at DESC,id DESC LIMIT 1",(plant_id,)).fetchone()

def latest_draft()->dict[str,Any]|None:
    with connect() as connection:
        ensure_schema(connection)
        return connection.execute("SELECT * FROM scada_configuration_drafts WHERE plant_id IS NOT NULL ORDER BY created_at DESC,id DESC LIMIT 1").fetchone()

def database_ok()->bool:
    with connect() as connection: connection.execute("SELECT 1")
    return True

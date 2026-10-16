from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
from configuration import ConfigurationState, ConfigurationVersion, content_hash, preview
from database import database_ok, latest_draft, list_plants, plant_configuration, save_draft
from demo_repository import get as get_demo_plant, list_all as list_demo_plants, save as save_demo_draft
from workbook_parser import parse_workbook

app=FastAPI(title="Enrich SCADA API",version="0.2.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_methods=["*"],allow_headers=["*"])
versions:dict[int,ConfigurationVersion]={}
active_id:int|None=None

class DeviceArrayGroup(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    enabled:bool=True

class DraftRequest(BaseModel):
    demo_mode:bool=False
    workbook_mappings:dict[str,Any]|None=None
    plant_id:int|None=Field(default=None,gt=0)
    plant_name:str=Field(min_length=1,max_length=200)
    customer_name:str=Field(min_length=1,max_length=250)
    ac_capacity_mw:Decimal=Field(gt=0,le=100000)
    dc_capacity_mwp:Decimal=Field(gt=0,le=100000)
    inverter_manufacturer:str=Field(min_length=1,max_length=200)
    modbus_function_code:str=Field(min_length=1,max_length=50)
    workbook_name:str|None=Field(default=None,max_length=500)
    inverter_count:int=Field(gt=0,le=10000)
    host:str=Field(min_length=1,max_length=255)
    base_port:int=Field(ge=1,le=65535)
    device_array_port:int|None=Field(default=None,ge=1,le=65535)
    device_array_settings:list[DeviceArrayGroup]=Field(default_factory=list)

    @field_validator("plant_name","customer_name","inverter_manufacturer","modbus_function_code","host")
    @classmethod
    def strip_required(cls,value:str)->str:
        value=value.strip()
        if not value: raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def validate_ports(self):
        end=self.base_port+self.inverter_count-1
        if end>65535: raise ValueError("Generated inverter port exceeds 65535")
        if self.device_array_port is not None and self.base_port<=self.device_array_port<=end:
            raise ValueError("Device Array port collides with an inverter port")
        return self

def to_client(row:dict[str,Any])->dict[str,Any]:
    # Generated ports are persisted for audit, but are always recalculated from
    # the saved count/base inputs when the configuration is restored.
    generated=list(range(row["base_port"],row["base_port"]+row["inverter_count"]))
    number=lambda value:format(value,"f").rstrip("0").rstrip(".")
    return {"plantId":row["plant_id"],"id":row["id"],"plantName":row["plant_name"],"customerName":row["customer_name"],"acCapacityMw":number(row["ac_capacity_mw"]),"dcCapacityMwp":number(row["dc_capacity_mwp"]),"inverterManufacturer":row["inverter_manufacturer"],"modbusFunctionCode":row["modbus_function_code"],"workbookName":row["workbook_name"] or "","inverterCount":row["inverter_count"],"sharedIp":row["shared_ip"],"basePort":row["base_port"],"deviceArrayPort":row["device_array_port"],"deviceArrayGroups":row["device_array_settings"],"generatedPorts":generated,"state":row["state"]}

def demo_to_client(row:dict[str,Any])->dict[str,Any]:
    return {"plantId":f"demo-db-{row['plant_id']}","id":row["id"],"plantName":row["plant_name"],"customerName":row["customer_name"],"acCapacityMw":str(row["ac_capacity_mw"]),"dcCapacityMwp":str(row["dc_capacity_mwp"]),"inverterManufacturer":row["inverter_manufacturer"],"modbusFunctionCode":row["modbus_function_code"],"workbookName":row.get("workbook_name") or "","inverterCount":row["inverter_count"],"sharedIp":row["host"],"basePort":row["base_port"],"deviceArrayPort":row["device_array_port"],"deviceArrayGroups":row["device_array_settings"],"generatedPorts":list(range(row["base_port"],row["base_port"]+row["inverter_count"])),"state":"DRAFT","source":"DEMO","workbookMappings":row.get("workbook_mappings") or {}}

@app.get("/api/v1/plants")
def get_plants():
    try: rows=list_plants()
    except Exception: rows=[]
    number=lambda value:format(value,"f").rstrip("0").rstrip(".")
    production=[{"plantId":row["plant_id"],"plantName":row["plant_name"],"customerName":row["customer_name"],"dcCapacityMwp":number(row["dc_capacity_mwp"]),"state":row["state"],"source":"LIVE"} for row in rows]
    demo=[{"plantId":f"demo-db-{row['id']}","plantName":row["plant_name"],"customerName":row["customer_name"],"dcCapacityMwp":str(row["dc_capacity_mwp"]),"state":"DRAFT","source":"DEMO"} for row in list_demo_plants()]
    return production+demo

@app.get("/api/v1/plants/{plant_id}/configuration")
def get_plant_configuration(plant_id:int):
    try: row=plant_configuration(plant_id)
    except Exception as error: raise HTTPException(503,f"PostgreSQL unavailable: {error}") from error
    if row is None: raise HTTPException(404,"Plant configuration not found")
    return to_client(row)

@app.get("/api/v1/demo/plants/{plant_id}/configuration")
def get_demo_configuration(plant_id:int):
    row=get_demo_plant(plant_id)
    if row is None: raise HTTPException(404,"Demo plant configuration not found")
    return demo_to_client(row)

@app.get("/api/v1/system/health")
def health():
    try: db="CONNECTED" if database_ok() else "UNAVAILABLE"
    except Exception: db="UNAVAILABLE"
    return {"status":"RUNNING" if db=="CONNECTED" else "DEGRADED","api":"RUNNING","database":db,"acquisition":"NOT_INSTALLED","active_configuration_id":active_id,"timestamp":datetime.now(timezone.utc).isoformat()}

@app.get("/api/v1/config/drafts/latest")
def get_latest_draft():
    try: row=latest_draft()
    except Exception as error: raise HTTPException(503,f"PostgreSQL unavailable: {error}") from error
    if row is None: raise HTTPException(404,"No saved configuration draft")
    return to_client(row)

@app.post("/api/v1/config/drafts",status_code=201)
def create_draft(req:DraftRequest):
    ports=list(range(req.base_port,req.base_port+req.inverter_count))
    data=req.model_dump(mode="json")
    if req.demo_mode:
        try: row=save_demo_draft(data,req.workbook_mappings)
        except Exception as error: raise HTTPException(500,f"Demo draft save failed: {error}") from error
        return demo_to_client(row)
    try: row=save_draft(data,ports)
    except Exception as error: raise HTTPException(503,f"PostgreSQL save failed: {error}") from error
    return to_client(row)

@app.post("/api/v1/config/import-workbook")
async def import_workbook(file:UploadFile):
    data=await file.read()
    try: parsed=parse_workbook(data,file.filename or "workbook.xlsx")
    except Exception as error: raise HTTPException(422,f"Unable to parse workbook: {error}") from error
    parsed["sha256"]=content_hash(data);parsed["source"]="DEMO_IMPORT";parsed["activationAllowed"]=False
    return parsed

@app.get("/api/v1/config/imports/{ident}/preview")
def get_preview(ident:int): return preview(require(ident))

@app.post("/api/v1/config/versions/{ident}/validate")
def validate(ident:int):
    item=require(ident); item.validate(); return preview(item)

@app.post("/api/v1/config/versions/{ident}/publish")
def publish(ident:int):
    item=require(ident)
    if item.state!=ConfigurationState.VALIDATED: raise HTTPException(409,"Only a validated draft can be published")
    if any("Decoder profile" in x for x in item.warnings): raise HTTPException(409,"Activation blocked: decoder profile requires engineering approval")
    item.state=ConfigurationState.PUBLISHED; return preview(item)

@app.get("/api/v1/current-values")
def current_values(): return {"mode":"LIVE","values":[],"quality":"UNAVAILABLE","message":"No acquisition service is connected."}

def require(ident:int)->ConfigurationVersion:
    if ident not in versions: raise HTTPException(404,"Configuration version not found")
    return versions[ident]

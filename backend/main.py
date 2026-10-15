from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from configuration import ConfigurationState, ConfigurationVersion, content_hash, preview

app=FastAPI(title="Enrich SCADA API",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173"],allow_methods=["*"],allow_headers=["*"])
versions:dict[int,ConfigurationVersion]={}
active_id:int|None=None

class DraftRequest(BaseModel):
    source_name:str="manual-preview"
    inverter_count:int=Field(gt=0)
    host:str
    base_port:int=Field(ge=1,le=65535)
    device_array_port:int|None=Field(default=None,ge=1,le=65535)

@app.get("/api/v1/system/health")
def health(): return {"status":"DEGRADED","api":"RUNNING","database":"NOT_CONFIGURED","acquisition":"NOT_INSTALLED","active_configuration_id":active_id,"timestamp":datetime.now(timezone.utc).isoformat()}

@app.post("/api/v1/config/drafts")
def create_draft(req:DraftRequest):
    ident=len(versions)+1
    item=ConfigurationVersion(ident,req.source_name,"manual",req.inverter_count,req.host,req.base_port,req.device_array_port)
    versions[ident]=item
    return preview(item)

@app.post("/api/v1/config/import-workbook")
async def import_workbook(file:UploadFile):
    data=await file.read()
    # Parsing is intentionally blocked until an approved workbook fixture/profile is supplied.
    ident=len(versions)+1
    item=ConfigurationVersion(ident,file.filename or "workbook.xlsx",content_hash(data),0,"",1)
    item.errors.append("Workbook profile parser requires the approved source workbook and engineering confirmations.")
    item.state=ConfigurationState.FAILED; versions[ident]=item
    return preview(item)

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

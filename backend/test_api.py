from decimal import Decimal
import pytest
from fastapi import HTTPException
import main

def stored_row(**overrides):
    row={"id":7,"plant_id":2,"plant_name":"Plant 1","customer_name":"VENUS WIRE INDUSTRIES PVT. LTD.","ac_capacity_mw":Decimal("2.650"),"dc_capacity_mwp":Decimal("4.000"),"inverter_manufacturer":"Hopewind","modbus_function_code":"FC3","workbook_name":"Bhokar.xlsx","inverter_count":8,"shared_ip":"192.168.1.20","base_port":501,"device_array_port":509,"generated_ports":list(range(501,509)),"device_array_settings":[{"name":"WMS","enabled":True}],"state":"DRAFT"}
    row.update(overrides); return row

def request(**overrides):
    data={"plant_id":None,"plant_name":"Plant 1","customer_name":"VENUS WIRE INDUSTRIES PVT. LTD.","ac_capacity_mw":2.65,"dc_capacity_mwp":4,"inverter_manufacturer":"Hopewind","modbus_function_code":"FC3","workbook_name":"Bhokar.xlsx","inverter_count":8,"host":"192.168.1.20","base_port":501,"device_array_port":509,"device_array_settings":[{"name":"WMS","enabled":True}]}
    data.update(overrides); return main.DraftRequest(**data)

def test_save_draft_returns_only_after_repository_success(monkeypatch):
    captured={}
    def save(data,ports): captured.update(data=data,ports=ports); return stored_row()
    monkeypatch.setattr(main,"save_draft",save)
    result=main.create_draft(request())
    assert result["customerName"]=="VENUS WIRE INDUSTRIES PVT. LTD."
    assert result["plantId"]==2
    assert result["plantName"]=="Plant 1"
    assert result["generatedPorts"]==list(range(501,509))
    assert captured["ports"]==list(range(501,509))

def test_save_failure_never_returns_success(monkeypatch):
    def fail(*_): raise RuntimeError("connection refused")
    monkeypatch.setattr(main,"save_draft",fail)
    with pytest.raises(HTTPException) as error: main.create_draft(request(device_array_port=None))
    assert error.value.status_code==503
    assert "PostgreSQL save failed" in error.value.detail

def test_port_collision_is_rejected_before_database():
    with pytest.raises(ValueError): request(device_array_port=508)

def test_latest_draft_recalculates_ports(monkeypatch):
    monkeypatch.setattr(main,"latest_draft",lambda:stored_row(generated_ports=[999]))
    result=main.get_latest_draft()
    assert result["generatedPorts"]==list(range(501,509))

def test_plants_are_listed_independently(monkeypatch):
    monkeypatch.setattr(main,"list_plants",lambda:[{"plant_id":1,"plant_name":"Plant 1","customer_name":"A","dc_capacity_mwp":Decimal("4"),"state":"DRAFT"},{"plant_id":2,"plant_name":"Plant 2","customer_name":"B","dc_capacity_mwp":Decimal("6"),"state":"VALIDATED"}])
    monkeypatch.setattr(main,"list_demo_plants",lambda:[])
    result=main.get_plants()
    assert [plant["plantName"] for plant in result]==["Plant 1","Plant 2"]

def test_selected_plant_loads_its_configuration(monkeypatch):
    monkeypatch.setattr(main,"plant_configuration",lambda plant_id:stored_row(plant_id=plant_id,plant_name=f"Plant {plant_id}"))
    result=main.get_plant_configuration(3)
    assert result["plantId"]==3
    assert result["plantName"]=="Plant 3"

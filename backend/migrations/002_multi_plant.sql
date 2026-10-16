CREATE TABLE IF NOT EXISTS scada_sites (
 id BIGSERIAL PRIMARY KEY,
 site_identifier TEXT NOT NULL UNIQUE,
 site_name TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scada_plants (
 id BIGSERIAL PRIMARY KEY,
 site_id BIGINT NOT NULL REFERENCES scada_sites(id),
 plant_name TEXT NOT NULL,
 customer_name TEXT NOT NULL,
 ac_capacity_mw NUMERIC(12,3) NOT NULL CHECK(ac_capacity_mw>0),
 dc_capacity_mwp NUMERIC(12,3) NOT NULL CHECK(dc_capacity_mwp>0),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(site_id,plant_name)
);

ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS plant_id BIGINT REFERENCES scada_plants(id);
ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS plant_name TEXT;
ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS ac_capacity_mw NUMERIC(12,3);
ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS inverter_manufacturer TEXT;
ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS modbus_function_code TEXT;
ALTER TABLE scada_configuration_drafts ADD COLUMN IF NOT EXISTS workbook_name TEXT;
CREATE INDEX IF NOT EXISTS ix_scada_configuration_drafts_plant_created ON scada_configuration_drafts(plant_id,created_at DESC,id DESC);

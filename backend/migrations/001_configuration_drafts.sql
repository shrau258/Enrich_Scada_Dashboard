CREATE TABLE IF NOT EXISTS scada_configuration_drafts (
    id BIGSERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL CHECK (length(trim(customer_name)) > 0),
    dc_capacity_mwp NUMERIC(12,3) NOT NULL CHECK (dc_capacity_mwp > 0),
    inverter_count INTEGER NOT NULL CHECK (inverter_count > 0),
    shared_ip TEXT NOT NULL CHECK (length(trim(shared_ip)) > 0),
    base_port INTEGER NOT NULL CHECK (base_port BETWEEN 1 AND 65535),
    device_array_port INTEGER NULL CHECK (device_array_port BETWEEN 1 AND 65535),
    generated_ports JSONB NOT NULL,
    device_array_settings JSONB NOT NULL,
    state TEXT NOT NULL DEFAULT 'DRAFT' CHECK (state = 'DRAFT'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_scada_configuration_drafts_created_at
ON scada_configuration_drafts (created_at DESC, id DESC);

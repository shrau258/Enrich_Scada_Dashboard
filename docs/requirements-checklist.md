# Enrich SCADA implementation checklist

Source: `Enrich_SCADA_Standard_Template_Implementation_Documentation 1.docx`, version 1.0 dated 13 October 2026.

## Implemented in this baseline

- All nine reference screens mapped to unchanged assets in `design-references/`.
- Shared dark theme, plant header, alarm ticker, functional page navigation, and Demo/Live selector.
- Demo-mode screen content for Dashboard, AC SLD, Trend, Inverter Data, String Data, Architecture, Alarms, Reports, and WMS.
- Live mode clearly suppresses simulated KPIs and reports backend unavailability.
- Configuration UI with port preview formula, Device Array precedence notice, lifecycle state guard, and health visibility.
- Dynamic inverter ports use `base_port + (index - 1)`; the calculated Device Array suggestion is `base_port + count`.

## Engineering-gated

- Meaning of `Data Count=124`.
- Modbus address convention and FC3/Holding normalization.
- Data types, signedness, byte/word order, scaling, offsets, and polling intervals.
- Annunciator bit masks/polarity, normal/alarm states, and severity.
- Whether missing Device Array ports may use the sequential suggestion.
- Whether Device Name carry-forward is approved for production imports.
- Partial-commissioning policy for unreachable devices.

## Remaining production integration

- Approved workbook fixture and importer-profile tests.
- PostgreSQL migrations and production credentials.
- Real Modbus gateway access and representative decoded reads.
- Windows service registration, recovery policy, retention, backup/restore, and central sync credentials.
- Screenshot automation and image-diff tolerance approval.

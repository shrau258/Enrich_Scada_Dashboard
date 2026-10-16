from pathlib import Path
from workbook_parser import parse_workbook

WORKBOOK=Path(r'C:\Users\scadacc1\Downloads\Bhokar - Address Details (1).xlsx')
def test_bhokar_workbook_mapping():
    parsed=parse_workbook(WORKBOOK.read_bytes(),WORKBOOK.name)
    assert parsed['plantName']=='Bhokar , MH'
    assert parsed['customerName']=='Venus Wire Industries Pvt.Ltd.'
    assert parsed['acCapacityMw']==2.65 and parsed['dcCapacityMwp']==4
    assert parsed['inverterCount']==8 and parsed['basePort']==501 and parsed['deviceArrayPort']==509
    assert len(parsed['inverterMappings'])==81
    assert len(parsed['deviceArrayMappings'])==84
    assert {x['group'] for x in parsed['deviceArrayMappings']}=={'WMS','Trafo','TVM','Annunciator'}

from configuration import ConfigurationState,ConfigurationVersion

def version(count=8,base=501,array_port=None): return ConfigurationVersion(1,"test.xlsx","hash",count,"192.168.1.10",base,array_port)

def test_eight_inverter_ports():
    item=version(); assert [x.port for x in item.endpoints]==list(range(501,509)); assert item.suggested_device_array_port==509

def test_ten_inverter_ports():
    item=version(10); assert [x.port for x in item.endpoints]==list(range(501,511)); assert item.suggested_device_array_port==511

def test_explicit_device_array_port_wins():
    item=version(array_port=620); assert item.device_array_port==620; assert item.suggested_device_array_port==509

def test_collision_blocks_validation():
    item=version(array_port=508); assert not item.validate(); assert item.state==ConfigurationState.FAILED

def test_unconfirmed_decoder_blocks_activation_contract():
    item=version(array_port=509); assert item.validate(); assert any("Decoder profile" in x for x in item.warnings)

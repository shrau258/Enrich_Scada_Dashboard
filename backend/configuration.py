from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Any

class ConfigurationState(StrEnum):
    DRAFT="DRAFT"; VALIDATING="VALIDATING"; VALIDATED="VALIDATED"; PUBLISHED="PUBLISHED"; ACTIVE="ACTIVE"; FAILED="FAILED"

@dataclass(frozen=True)
class Endpoint:
    asset_id: str
    host: str
    port: int

@dataclass
class ConfigurationVersion:
    id: int
    source_name: str
    source_hash: str
    inverter_count: int
    host: str
    base_port: int
    explicit_device_array_port: int | None = None
    state: ConfigurationState = ConfigurationState.DRAFT
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def endpoints(self) -> list[Endpoint]:
        return [Endpoint(f"INV-{i:02d}", self.host, self.base_port+i-1) for i in range(1,self.inverter_count+1)]

    @property
    def suggested_device_array_port(self) -> int:
        return self.base_port + self.inverter_count

    @property
    def device_array_port(self) -> int | None:
        return self.explicit_device_array_port

    def validate(self) -> bool:
        self.state=ConfigurationState.VALIDATING
        self.errors.clear(); self.warnings.clear()
        if self.inverter_count <= 0: self.errors.append("Inverter count must be a positive integer.")
        ports=[x.port for x in self.endpoints]
        if any(p < 1 or p > 65535 for p in ports): self.errors.append("Generated inverter port is outside 1-65535.")
        if len(ports)!=len(set(ports)): self.errors.append("Generated inverter ports collide.")
        if self.explicit_device_array_port is None:
            self.warnings.append("Device Array port is not explicit; calculated value is a suggestion pending policy approval.")
        elif self.explicit_device_array_port in ports:
            self.errors.append("Device Array port collides with an inverter port.")
        if self.explicit_device_array_port is not None and not 1 <= self.explicit_device_array_port <= 65535:
            self.errors.append("Device Array port is outside 1-65535.")
        self.warnings += ["Data Count semantics are unconfirmed.","Decoder profile is required before activation."]
        self.state=ConfigurationState.FAILED if self.errors else ConfigurationState.VALIDATED
        return not self.errors

def content_hash(data: bytes) -> str: return sha256(data).hexdigest()

def preview(version: ConfigurationVersion) -> dict[str,Any]:
    return {"id":version.id,"state":version.state,"source":{"name":version.source_name,"sha256":version.source_hash},"inverters":[e.__dict__ for e in version.endpoints],"device_array":{"explicit_port":version.device_array_port,"suggested_port":version.suggested_device_array_port,"effective_port":version.device_array_port},"warnings":version.warnings,"errors":version.errors}

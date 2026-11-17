from pydantic import BaseModel, ConfigDict, Field, field_validator


class KeitaroModel(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)


class KeitaroNamed(KeitaroModel):
    id: int
    name: str


class KeitaroOffer(KeitaroModel):
    id: int
    name: str
    group: str | None = None
    country: list[str] = Field(default_factory=list)
    state: str

    @field_validator("country", mode="before")
    @classmethod
    def empty_country_to_list(cls, value: object) -> object:
        if value is None or value == "":
            return []
        return value


class KeitaroCampaign(KeitaroModel):
    id: int
    name: str
    alias: str
    state: str
    domain: str | None = None
    domain_id: int | None = None
    group_id: int | None = None
    traffic_source_id: int | None = None


class KeitaroFilter(KeitaroModel):
    name: str
    mode: str
    payload: list[str] | str | None = None


class KeitaroStreamOffer(KeitaroModel):
    offer_id: int
    share: int
    state: str = "active"


class KeitaroStream(KeitaroModel):
    id: int
    campaign_id: int
    name: str
    position: int
    type: str
    schema_: str = Field(alias="schema")
    action_type: str | None = None
    action_payload: str | None = None
    filters: list[KeitaroFilter] = Field(default_factory=list)
    offers: list[KeitaroStreamOffer] = Field(default_factory=list)

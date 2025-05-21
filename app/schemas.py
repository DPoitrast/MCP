from pydantic import BaseModel


class HerdBase(BaseModel):
    name: str
    location: str


class HerdCreate(HerdBase):
    pass


class Herd(HerdBase):
    id: int

    class Config:
        orm_mode = True

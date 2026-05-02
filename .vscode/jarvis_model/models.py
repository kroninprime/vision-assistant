from pydantic import BaseModel


class CommandRequest(BaseModel):
    text: str
    include_screen_context: bool = False


class CommandResponse(BaseModel):
    status: str
    response: str


class ListenResponse(BaseModel):
    status: str
    transcript: str = ""
    error: str = ""

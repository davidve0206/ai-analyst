from pydantic import BaseModel


class DBTestCase(BaseModel):
    task: str
    expected: list[dict[str, float | str | int]]

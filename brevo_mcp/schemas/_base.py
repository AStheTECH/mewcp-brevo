from pydantic import BaseModel
from typing import Any

class ToolError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None

class ToolResult(BaseModel):
    success: bool
    statusCode: int
    retriable: bool = False
    retry_after_seconds: int | None = None
    error: ToolError | None = None

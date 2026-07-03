from fastapi.encoders import jsonable_encoder


def ok(data=None, message: str = "success"):
    return {"code": 0, "message": message, "data": jsonable_encoder(data or {}), "trace_id": None}


def fail(code: int, message: str, data=None):
    return {"code": code, "message": message, "data": jsonable_encoder(data or {}), "trace_id": None}

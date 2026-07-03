from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import ai_rule_api, assessment_api, auth_api, blacklist_api, case_api, dashboard_api, profile_api, risk_check_api, rule_api, system_api
from app.core.errors import BizError, SYSTEM_ERROR
from app.core.response import fail

app = FastAPI(title="电商风控系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_check_api.router)
app.include_router(assessment_api.router)
app.include_router(rule_api.router)
app.include_router(ai_rule_api.router)
app.include_router(case_api.router)
app.include_router(blacklist_api.router)
app.include_router(profile_api.router)
app.include_router(dashboard_api.router)
app.include_router(auth_api.router)
app.include_router(system_api.router)


@app.exception_handler(BizError)
def handle_biz_error(request: Request, exc: BizError):
    return JSONResponse(status_code=200, content=fail(exc.code, exc.message))


@app.exception_handler(Exception)
def handle_exception(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=fail(SYSTEM_ERROR, str(exc)))


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

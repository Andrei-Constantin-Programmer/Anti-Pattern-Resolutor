# Entry point for the prototype

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import os
import time

from agents.antipattern_scanner import AntipatternScanner
from agents.strategist_agent import StrategistAgent
from agents.code_generator import CodeGenerator
from utils.watsonx_client import WatsonXClient

# Temporary session storage
SESSIONS = {}


# Input model for JSON body
class SessionInput(BaseModel):
    session_id: str


app = FastAPI(
    title="Antipattern Detection and Refactoring Strategy API",
    version="1.0"
)


def parse_java_file(file: UploadFile) -> str:
    if not file.filename.endswith(".java"):
        raise HTTPException(status_code=400, detail="Only Java files are supported.")
    contents = file.file.read()
    return contents.decode("utf-8")


@app.post("/upload/")
async def upload_code(file: UploadFile = File(...)):
    code = parse_java_file(file)
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"code": code}
    return {"session_id": session_id}


@app.post("/analyze/")
async def analyze_code(session: SessionInput):
    session_id = session.session_id
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Invalid session ID.")

    code = SESSIONS[session_id]["code"]
    model = WatsonXClient()
    scanner = AntipatternScanner(model)
    analysis = scanner.analyze(code)
    SESSIONS[session_id]["analysis"] = analysis
    return JSONResponse(content={"antipattern_analysis": analysis})


@app.post("/strategy/")
async def strategy_suggestion(session: SessionInput):
    session_id = session.session_id
    if session_id not in SESSIONS or "analysis" not in SESSIONS[session_id]:
        raise HTTPException(status_code=404, detail="Analysis not found for session.")

    code = SESSIONS[session_id]["code"]
    analysis = SESSIONS[session_id]["analysis"]
    model = WatsonXClient()
    strategist = StrategistAgent(model)
    strategy = strategist.suggest_refactorings(code, analysis)
    SESSIONS[session_id]["strategy"] = strategy
    return JSONResponse(content={"refactoring_strategy": strategy})


@app.post("/refactor/")
async def refactor_code(session: SessionInput):
    session_id = session.session_id
    if session_id not in SESSIONS or "strategy" not in SESSIONS[session_id]:
        raise HTTPException(status_code=404, detail="Strategy not found for session.")

    code = SESSIONS[session_id]["code"]
    strategy = SESSIONS[session_id]["strategy"]
    model = WatsonXClient()
    coder = CodeGenerator(model)
    new_code = coder.generate_refactored_code(code, strategy)
    return JSONResponse(content={"refactored_code": new_code})

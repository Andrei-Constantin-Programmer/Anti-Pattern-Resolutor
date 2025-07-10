from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from fastapi.middleware.cors import CORSMiddleware
import time

from agents.antipattern_scanner import AntipatternScanner
from agents.strategist_agent import StrategistAgent
from agents.code_generator import CodeGenerator
from utils.watsonx_client import WatsonXClient



app = FastAPI(
    title="Antipattern Detection and Refactoring Strategy API",
    version="1.0"
)

origins = [
    "http://localhost:5173",  # your frontend dev server
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
session_store = {}

class SessionRequest(BaseModel):
    session_id: str

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".java"):
        raise HTTPException(status_code=400, detail="Only Java files are supported.")

    contents = await file.read()
    code = contents.decode("utf-8")

    session_id = str(uuid.uuid4())
    session_store[session_id] = {"code": code}

    return JSONResponse(content={"sucess":True,"session_id": session_id})


@app.post("/analyze/")
async def analyze_code(req: SessionRequest):
    session_id = req.session_id
    session = session_store.get(session_id)

    if not session or "code" not in session:
        raise HTTPException(status_code=404, detail="Session or code not found")

    model = WatsonXClient()
    scanner = AntipatternScanner(model)

    analysis = scanner.analyze(session["code"])
    session["analysis"] = analysis

    return JSONResponse(content={"antipattern_analysis": analysis})


@app.post("/strategy/")
async def strategy_suggestion(req: SessionRequest):
    print("Received /strategy/ request with session_id:", req.session_id)
    session_id = req.session_id
    session = session_store.get(session_id)

    if not session or "code" not in session or "analysis" not in session:
        raise HTTPException(status_code=404, detail="Code or analysis not found in session")

    model = WatsonXClient()
    strategist = StrategistAgent(model)

    strategy = strategist.suggest_refactorings(session["code"], session["analysis"])
    session["strategy"] = strategy

    return JSONResponse(content={"refactoring_strategy": strategy})


@app.post("/refactor/")
async def generate_refactored_code(req: SessionRequest):
    session_id = req.session_id
    session = session_store.get(session_id)

    if not session or "code" not in session or "strategy" not in session:
        raise HTTPException(status_code=404, detail="Missing code or strategy in session")

    model = WatsonXClient()
    coder = CodeGenerator(model)

    refactored_code = coder.generate_refactored_code(session["code"], session["strategy"])
    session["refactored_code"] = refactored_code

    return JSONResponse(content={"refactored_code": refactored_code})

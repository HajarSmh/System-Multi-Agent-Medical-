import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from langgraph.types import Command
from app.graph import medical_graph
from app.graph import create_graph
from app.database import get_all_reports
from fastapi.responses import StreamingResponse
import io
from app.pdf_generator import generate_pdf


medical_graph = create_graph(with_checkpointer=True)

app = FastAPI(title="Medical Multi-Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Schémas Pydantic ────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    patient_name: Optional[str] = "Patient"

class StartSessionResponse(BaseModel):
    thread_id: str
    message: str

class StartConsultationRequest(BaseModel):
    thread_id: str
    patient_case: str

class ResumeConsultationRequest(BaseModel):
    thread_id: str
    answer: str
    answer_type: str                          # "patient" ou "physician"
    physician_treatment: Optional[str] = None
    physician_notes: Optional[str] = None

class ConsultationStatusResponse(BaseModel):
    thread_id: str
    status: str
    current_question: Optional[str] = None
    question_index: Optional[int] = None
    diagnostic_summary: Optional[str] = None
    interim_care: Optional[str] = None
    physician_treatment: Optional[str] = None
    final_report: Optional[str] = None

# ─── Utilitaire ──────────────────────────────────────────────────────

def get_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}

def extract_interrupt(state) -> Optional[dict]:
    """Extrait la première interruption active de l'état du graphe."""
    if state.tasks and state.tasks[0].interrupts:
        return state.tasks[0].interrupts[0].value
    return None

# ─── POST /sessions/start ────────────────────────────────────────────

@app.post("/sessions/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Crée une nouvelle session et retourne un thread_id unique."""
    thread_id = str(uuid.uuid4())
    return StartSessionResponse(
        thread_id=thread_id,
        message=f"Session créée pour {request.patient_name}"
    )

# ─── POST /consultation/start ────────────────────────────────────────

@app.post("/consultation/start")
async def start_consultation(request: StartConsultationRequest):
    """
    Démarre la consultation avec le cas patient initial.
    Lance le graphe LangGraph — il s'interrompt à la première question.
    """
    config = get_config(request.thread_id)

    initial_state = {
        "patient_case": request.patient_case,
        "question_count": 0,
        "questions": [],
        "answers": [],
        "status": "started",
        "messages": [],
    }

    # Lancer le graphe (va s'arrêter à la 1ère interruption)
    medical_graph.invoke(initial_state, config=config)

    # Lire l'état après l'interruption
    state = medical_graph.get_state(config)
    interrupt_data = extract_interrupt(state)

    if interrupt_data and interrupt_data.get("type") == "patient_question":
        return {
            "thread_id": request.thread_id,
            "status": "waiting_for_patient",
            "question": interrupt_data.get("question"),
            "question_index": interrupt_data.get("question_index", 0),
        }

    return {
        "thread_id": request.thread_id,
        "status": "completed"
    }

# ─── POST /consultation/resume ───────────────────────────────────────

@app.post("/consultation/resume")
async def resume_consultation(request: ResumeConsultationRequest):
    """
    Reprend le graphe après une interruption patient ou médecin.
    - answer_type == "patient"    → réponse à une question clinique
    - answer_type == "physician"  → traitement proposé par le médecin
    """
    config = get_config(request.thread_id)

    # Construire la valeur à injecter selon le type d'interruption
    if request.answer_type == "physician":
        resume_value = {
            "treatment": request.physician_treatment or request.answer,
            "notes": request.physician_notes or ""
        }
    else:
        resume_value = request.answer

    # Reprendre le graphe
    medical_graph.invoke(Command(resume=resume_value), config=config)

    # Analyser l'état après reprise
    state = medical_graph.get_state(config)
    values = state.values
    interrupt_data = extract_interrupt(state)

    # Cas 1 : nouvelle question patient
    if interrupt_data and interrupt_data.get("type") == "patient_question":
        return {
            "thread_id": request.thread_id,
            "status": "waiting_for_patient",
            "question": interrupt_data.get("question"),
            "question_index": interrupt_data.get("question_index"),
        }

    # Cas 2 : revue médecin
    if interrupt_data and interrupt_data.get("type") == "physician_review":
        return {
            "thread_id": request.thread_id,
            "status": "waiting_for_physician",
            "diagnostic_summary": interrupt_data.get("diagnostic_summary"),
            "interim_care": interrupt_data.get("interim_care"),
        }

    # Cas 3 : workflow terminé
    return {
        "thread_id": request.thread_id,
        "status": values.get("status", "completed"),
        "final_report": values.get("final_report"),
    }

# ─── GET /consultation/{thread_id} ──────────────────────────────────

@app.get("/consultation/{thread_id}", response_model=ConsultationStatusResponse)
async def get_consultation(thread_id: str):
    """Retourne l'état courant d'une consultation (polling)."""
    config = get_config(thread_id)

    try:
        state = medical_graph.get_state(config)
        values = state.values
    except Exception:
        raise HTTPException(status_code=404, detail="Session introuvable")

    return ConsultationStatusResponse(
        thread_id=thread_id,
        status=values.get("status", "unknown"),
        diagnostic_summary=values.get("diagnostic_summary"),
        interim_care=values.get("interim_care"),
        physician_treatment=values.get("physician_treatment"),
        final_report=values.get("final_report"),
    )

# ─── GET /consultation/{thread_id}/report ───────────────────────────

@app.get("/consultation/{thread_id}/report")
async def get_report(thread_id: str):
    """Retourne le rapport final structuré d'une consultation terminée."""
    config = get_config(thread_id)

    try:
        state = medical_graph.get_state(config)
        values = state.values
    except Exception:
        raise HTTPException(status_code=404, detail="Session introuvable")

    final_report = values.get("final_report")
    if not final_report:
        raise HTTPException(status_code=404, detail="Rapport non encore généré")

    return {
        "thread_id": thread_id,
        "final_report": final_report,
        "disclaimer": "Ce système ne remplace pas une consultation médicale."
    }

# ─── GET /consultations/history ──────────────────────────────────

@app.get("/consultations/history")
async def get_history():
    """Retourne la liste de toutes les consultations sauvegardées."""
    rows = get_all_reports()
    return [
        {"thread_id": r[0], "patient_case": r[1], "created_at": r[2]}
        for r in rows
    ]

# ── GET /consultation/{thread_id}/report/pdf ─────────────────────────
@app.get("/consultation/{thread_id}/report/pdf")
async def get_report_pdf(thread_id: str):
    """Exporte le rapport final en PDF téléchargeable."""
    config = get_config(thread_id)

    try:
        state = medical_graph.get_state(config)
        values = state.values
    except Exception:
        raise HTTPException(status_code=404, detail="Session introuvable")

    final_report = values.get("final_report")
    if not final_report:
        raise HTTPException(status_code=404, detail="Rapport non encore généré")

    pdf_bytes = generate_pdf(final_report, thread_id)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rapport_{thread_id[:8]}.pdf"
        }
    )

# ─── Point d'entrée ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.state import MedicalState
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

SUPERVISOR_PROMPT = """Tu es le superviseur d'un système d'orientation clinique préliminaire.
Tu dois décider du prochain agent à exécuter selon l'état du workflow.

Règles de routage :
- Si question_count < 5 et que le diagnostic n'est pas fait → "diagnostic_agent"
- Si question_count == 5 et pas de physician_treatment → "physician_review"
- Si physician_treatment est renseigné et pas de final_report → "report_agent"
- Si final_report est généré → "FINISH"

Réponds UNIQUEMENT avec l'un de ces mots : diagnostic_agent, physician_review, report_agent, FINISH
"""

def supervisor_node(state: MedicalState) -> MedicalState:
    """
    Nœud Supervisor : décide du prochain agent à appeler.
    """
    question_count = state.get("question_count", 0)
    physician_treatment = state.get("physician_treatment", "")
    final_report = state.get("final_report", "")
    diagnostic_summary = state.get("diagnostic_summary", "")
    
    # Logique de routage explicite (plus fiable qu'un LLM pour le routage)
    if question_count < 5 or not diagnostic_summary:
        next_agent = "diagnostic_agent"
    elif not physician_treatment:
        next_agent = "physician_review"
    elif not final_report:
        next_agent = "report_agent"
    else:
        next_agent = "FINISH"
    
    return {"next": next_agent}
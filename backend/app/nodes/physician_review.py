from app.state import MedicalState
from langgraph.types import interrupt

def physician_review_node(state: MedicalState) -> MedicalState:
    """
    Nœud PhysicianReview : interruption pour validation médecin.
    Le graphe s'arrête ici et attend l'input du médecin.
    """
    diagnostic_summary = state.get("diagnostic_summary", "")
    interim_care = state.get("interim_care", "")
    
    # Interruption HITL : le médecin doit fournir son avis
    physician_input = interrupt({
        "type": "physician_review",
        "message": "Veuillez examiner la synthèse et fournir votre traitement recommandé.",
        "diagnostic_summary": diagnostic_summary,
        "interim_care": interim_care,
    })
    
    # physician_input est fourni par l'API lors du resume
    treatment = physician_input.get("treatment", "")
    notes = physician_input.get("notes", "")
    
    return {
        "physician_treatment": treatment,
        "physician_notes": notes,
        "status": "generating_report"
    }
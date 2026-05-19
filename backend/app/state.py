from typing import Annotated, Optional
from typing_extensions import TypedDict, Literal
from langgraph.graph.message import add_messages

class MedicalState(TypedDict, total=False):
    # Messages LangChain (conversation complète)
    messages: Annotated[list, add_messages]
    
    # Routage : quel agent exécuter ensuite
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    
    # Informations patient
    patient_case: str           # Description initiale du cas
    patient_name: str           # Nom du patient (optionnel)
    
    # Questionnaire (5 questions)
    questions: list[str]        # Les 5 questions générées
    answers: list[str]          # Les réponses du patient
    question_count: int         # Compteur de questions (0 à 5)
    
    # Synthèse et recommandations
    diagnostic_summary: str     # Synthèse clinique préliminaire
    interim_care: str           # Recommandation intermédiaire
    
    # Revue médecin
    physician_treatment: str    # Traitement proposé par le médecin
    physician_notes: str        # Notes complémentaires du médecin
    
    # Rapport final
    final_report: str           # Rapport structuré complet
    
    # Métadonnées
    thread_id: str              # Identifiant de session
    status: str                 # État courant du workflow
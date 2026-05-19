from langchain_core.tools import tool
from langgraph.types import interrupt

# Liste des questions prédéfinies (peut être dynamique)
CLINICAL_QUESTIONS = [
    "Depuis combien de temps ressentez-vous ces symptômes ?",
    "Avez-vous de la fièvre ? Si oui, à quelle température ?",
    "Avez-vous des antécédents médicaux importants ou des allergies ?",
    "Prenez-vous actuellement des médicaments ? Si oui, lesquels ?",
    "Ces symptômes s'aggravent-ils progressivement ou restent-ils stables ?"
]

@tool
def ask_patient(question_index: int) -> str:
    """
    Pose une question au patient et attend sa réponse.
    Utilise une interruption LangGraph pour attendre la réponse humaine.
    
    Args:
        question_index: Index de la question (0 à 4)
    
    Returns:
        La réponse du patient
    """
    if question_index >= len(CLINICAL_QUESTIONS):
        return "Toutes les questions ont été posées."
    
    question = CLINICAL_QUESTIONS[question_index]
    
    # Interruption LangGraph : le graphe s'arrête ici
    # La valeur retournée sera fournie par l'extérieur (API)
    answer = interrupt({
        "type": "patient_question",
        "question": question,
        "question_index": question_index
    })
    
    return answer
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.state import MedicalState
from app.tools.patient_tools import ask_patient
from app.tools.care_tools import recommend_interim_care
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

DIAGNOSTIC_PROMPT = """Tu es un agent d'orientation clinique préliminaire.
Ton rôle est de :
1. Poser exactement 5 questions successives au patient en utilisant le tool ask_patient.
2. Analyser les réponses pour produire une synthèse clinique préliminaire.
3. Appeler recommend_interim_care pour générer une recommandation intermédiaire.

IMPORTANT :
- Tu ne poses PAS de diagnostic définitif.
- Tu utilises des termes comme "orientation clinique préliminaire" et "synthèse clinique".
- Après 5 questions, tu produis la synthèse dans le champ diagnostic_summary.
- Ce système ne remplace pas une consultation médicale.

Cas patient actuel : {patient_case}
Questions déjà posées : {question_count}/5
"""

def diagnostic_agent_node(state: MedicalState) -> MedicalState:
    """
    Nœud DiagnosticAgent : pose les questions et produit la synthèse.
    """
    patient_case = state.get("patient_case", "")
    question_count = state.get("question_count", 0)
    answers = state.get("answers", [])
    questions = state.get("questions", [])
    
    # Si toutes les questions ont été posées, produire la synthèse
    if question_count >= 5:
        # Créer un prompt pour la synthèse
        qa_text = "\n".join([
            f"Q{i+1}: {q}\nR{i+1}: {a}"
            for i, (q, a) in enumerate(zip(questions, answers))
        ])
        
        synthesis_prompt = f"""
        Cas initial : {patient_case}
        
        Questions et réponses :
        {qa_text}
        
        Produis une synthèse clinique préliminaire concise et structurée.
        Termine par une recommandation intermédiaire générale et prudente.
        Rappelle que ce système ne remplace pas une consultation médicale.
        """
        
        response = llm.invoke([HumanMessage(content=synthesis_prompt)])
        summary = response.content
        
        # Générer la recommandation intermédiaire
        interim = recommend_interim_care.invoke({"symptoms_summary": summary})
        
        return {
            "diagnostic_summary": summary,
            "interim_care": interim,
            "status": "awaiting_physician"
        }
    
    # Sinon, poser la prochaine question
    from langgraph.types import interrupt
    
    from app.tools.patient_tools import CLINICAL_QUESTIONS
    question = CLINICAL_QUESTIONS[question_count]
    
    # Interruption pour attendre la réponse patient
    answer = interrupt({
        "type": "patient_question",
        "question": question,
        "question_index": question_count
    })
    
    return {
        "questions": questions + [question],
        "answers": answers + [answer],
        "question_count": question_count + 1,
    }
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.state import MedicalState
from datetime import datetime
from dotenv import load_dotenv
from app.database import init_db, save_report

init_db()
load_dotenv()
llm = ChatOpenAI(model="gpt-4o", temperature=0)

REPORT_TEMPLATE = """
Tu es un agent de génération de rapports cliniques préliminaires.
Génère un rapport structuré, professionnel et clair basé sur les informations suivantes.

Le rapport DOIT :
1. Être structuré avec des sections claires
2. Mentionner explicitement : "Ce système ne remplace pas une consultation médicale."
3. Utiliser des termes prudents : "orientation préliminaire", "synthèse clinique"
4. Inclure la recommandation du médecin

Informations disponibles :
- Date du rapport : {date_rapport}
- Cas initial : {patient_case}
- Synthèse clinique : {diagnostic_summary}
- Recommandation intermédiaire : {interim_care}
- Traitement proposé par le médecin : {physician_treatment}
- Notes du médecin : {physician_notes}

Format attendu (respecte exactement ces titres et remplis chaque section) :
## RAPPORT D'ORIENTATION CLINIQUE PRÉLIMINAIRE
### Date
{date_rapport}
### Cas Initial
### Synthèse Clinique Préliminaire
### Recommandation Intermédiaire
### Avis du Médecin Traitant
### Conclusion
### Avertissement
⚠️ Ce système ne remplace pas une consultation médicale.
"""

def report_agent_node(state: MedicalState) -> dict:
    """
    Nœud ReportAgent : génère le rapport final structuré.
    """
    # Date générée en Python, pas par le LLM
    date_rapport = datetime.now().strftime("%d/%m/%Y à %H:%M")

    prompt = REPORT_TEMPLATE.format(
        date_rapport=date_rapport,
        patient_case=state.get("patient_case", ""),
        diagnostic_summary=state.get("diagnostic_summary", ""),
        interim_care=state.get("interim_care", ""),
        physician_treatment=state.get("physician_treatment", ""),
        physician_notes=state.get("physician_notes", "")
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    report = response.content

    # Ajouter le disclaimer si le LLM l'a oublié
    if "ne remplace pas" not in report.lower():
        report += "\n\n⚠️ Ce système ne remplace pas une consultation médicale."

    # Sauvegarder en base
    save_report(
        thread_id=state.get("thread_id", "inconnu"),
        patient_case=state.get("patient_case", ""),
        final_report=report
    )


    return {
        "final_report": report,
        "status": "completed"
    }
from langchain_core.tools import tool

@tool
def recommend_interim_care(symptoms_summary: str) -> str:
    """
    Génère une recommandation intermédiaire prudente basée sur 
    la synthèse des symptômes. Ne remplace pas l'avis médical.
    
    Args:
        symptoms_summary: Résumé des symptômes du patient
    
    Returns:
        Recommandation intermédiaire textuelle
    """
    # Cette logique peut être enrichie avec un LLM
    # Ici on montre une version simple basée sur des règles
    
    recommendations = [
        "🟡 RECOMMANDATION INTERMÉDIAIRE (non définitive)",
        "",
        "Basé sur les informations recueillies :",
        "• Repos recommandé jusqu'à amélioration des symptômes",
        "• Maintenir une bonne hydratation (1,5 à 2L d'eau par jour)",
        "• Surveiller l'évolution des symptômes",
        "• Consulter rapidement un médecin en cas d'aggravation",
        "• Éviter les activités physiques intenses",
        "",
        "⚠️ Ces recommandations sont préliminaires et générales.",
        "Elles ne remplacent pas une consultation médicale.",
    ]
    
    return "\n".join(recommendations)
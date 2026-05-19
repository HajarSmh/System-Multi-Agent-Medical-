from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)

mcp = FastMCP(name="medical-mcp-server", host="0.0.0.0", port=24000)

# Base de données fictive de médicaments
DRUG_DATABASE = {
    "paracetamol": {
        "name": "Paracétamol",
        "dosage": "500mg à 1g toutes les 6h, max 4g/jour",
        "indication": "Fièvre, douleurs légères à modérées",
        "contraindications": "Insuffisance hépatique sévère"
    },
    "ibuprofene": {
        "name": "Ibuprofène",
        "dosage": "200mg à 400mg toutes les 6h",
        "indication": "Douleurs inflammatoires, fièvre",
        "contraindications": "Ulcère gastrique, insuffisance rénale"
    }
}

GUIDELINES = {
    "fievre": "En cas de fièvre > 38.5°C persistante plus de 3 jours, consultation médicale recommandée.",
    "respiratoire": "Difficultés respiratoires sévères nécessitent une consultation urgente.",
    "douleur_thoracique": "Douleur thoracique + dyspnée = urgence médicale potentielle. Appeler le 15.",
}

@mcp.tool()
def get_drug_info(drug_name: str) -> dict:
    """
    Obtenir des informations sur un médicament (dosage, indications, contre-indications).
    Args:
        drug_name: Nom du médicament en minuscules
    """
    drug_key = drug_name.lower().replace(" ", "")
    return DRUG_DATABASE.get(drug_key, {
        "message": f"Médicament '{drug_name}' non trouvé dans la base de données."
    })

@mcp.tool()
def search_medical_guidelines(symptom: str) -> str:
    """
    Rechercher des recommandations cliniques pour un symptôme donné.
    Args:
        symptom: Symptôme ou situation clinique à rechercher
    """
    symptom_lower = symptom.lower()
    
    for key, guideline in GUIDELINES.items():
        if key in symptom_lower or symptom_lower in key:
            return guideline
    
    return f"Aucune recommandation spécifique trouvée pour '{symptom}'. Consulter un médecin."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
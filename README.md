# Système Multi-Agents Médical avec LangGraph

## Presentation
Ce projet est une application multi-agents qui simule un workflow d'orientation clinique préliminaire. Il ne s'agit PAS d'un vrai système médical, mais d'un exercice pédagogique pour apprendre à construire des architectures LangGraph complexes.

L'application permet de :
•	Recueillir les informations d'un patient via une interface
•	Poser 5 questions successives au patient (avec interruptions LangGraph)
•	Produire une synthèse clinique préliminaire via un LLM
•	Générer une recommandation intermédiaire prudente
•	Intégrer une validation humaine (Human-in-the-Loop) par un médecin
•	Générer un rapport final structuré avec date et disclaimer + télécharger sous format pdf 
•	Exposer tout cela via une API FastAPI
•	Tester le graphe dans LangGraph Studio

## Installation

```bash
python -m pip install -r backend\requirements.txt
```

## Lancement

```bash
# 1. MCP Server
python mcp_server/server.py

# 2. Backend FastAPI
cd backend
python -m uvicorn app.api:app --reload --port 8000

# 3. Frontend Streamlit
streamlit run frontend/app.py

# 4. LangGraph Studio
cd backend
langgraph dev
```

## Architecture
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│  Streamlit                                              │
│  - Saisie du cas patient                                │
│  - Affichage des questions/réponses                     │
│  - Formulaire de revue médecin                          │
│  - Affichage du rapport final                           │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP REST
┌─────────────────▼───────────────────────────────────────┐
│                    FASTAPI (api.py)                     │
│  POST /sessions/start                                   │
│  POST /consultation/start                               │
│  POST /consultation/resume                              │
│  GET  /consultation/{thread_id}                         │
│  GET  /consultation/{thread_id}/report                  │
└─────────────────┬───────────────────────────────────────┘
                  │ Python API
┌─────────────────▼───────────────────────────────────────┐
│               LANGGRAPH GRAPH (graph.py)                │
│                                                         │
│  ┌───────────┐    ┌──────────────────┐                  │
│  │ Supervisor│───▶│ DiagnosticAgent  │                  │
│  └───────────┘    │  └─ ask_patient  │                  │
│       ▲           │  └─ recommend_   │                  │
│       │           │     interim_care │                  │
│       │           └──────────────────┘                  │
│       │                    │                            │
│       │           ┌────────▼──────────┐                 │
│       │           │ PhysicianReview   │ ← HITL          │
│       │           │ (interrupt)       │                 │
│       │           └────────┬──────────┘                 │
│       │                    │                            │
│       │           ┌────────▼──────────┐                 │
│       └───────────│ ReportAgent       │                 │
│                   └───────────────────┘                 │
└─────────────────────────────┬───────────────────────────┘
                              │ HTTP/SSE
┌─────────────────────────────▼───────────────────────────┐
│                  MCP SERVER (server.py)                  │
│  - get_drug_info(name)                                  │
│  - search_medical_guidelines(query)                     │
└─────────────────────────────────────────────────────────┘
## Structure des dossiers
PROJET AGENTICAI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── graph.py              # Compilation du graphe LangGraph
│   │   ├── state.py              # Définition de MedicalState
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── supervisor.py     # Agent orchestrateur
│   │   │   ├── diagnostic_agent.py  # Agent qui pose les 5 questions
│   │   │   ├── physician_review.py  # Nœud HITL médecin
│   │   │   └── report_agent.py   # Génération du rapport final
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── patient_tools.py  # ask_patient tool
│   │   │   ├── care_tools.py 
│   │   │   ├── pdf_generator.py 
│   │   │   └── mcp_client.py     # Connexion au MCP server
│   │   └── api.py                # FastAPI endpoints
│   ├── langgraph.json            # Config LangGraph Studio
│   
├── mcp_server/
│   ├── server.py                 # Serveur MCP FastMCP
│   └── data/
│       └── guidelines.json       # Données médicales fictives
├── frontend/
│   └── app.py
├── README.md
└── requirements.txt

## Démonstration
**Page d'acceuil**
<img width="1365" height="874" alt="image" src="https://github.com/user-attachments/assets/c1847394-31e0-4780-80f3-f82612929d39" />
**Question 1/5**
<img width="1354" height="764" alt="image" src="https://github.com/user-attachments/assets/091cbb56-12c5-41d0-b2a2-6ee556138ee9" />
**Generation du rapport**
<img width="1434" height="926" alt="image" src="https://github.com/user-attachments/assets/7b898375-52e4-4b57-aa50-959a8ab31f79" />
**Integration HTL**
<img width="1041" height="893" alt="image" src="https://github.com/user-attachments/assets/33378e4b-beec-431b-bf4a-159bdf601799" />
**Rapport final généré**
<img width="1233" height="879" alt="image" src="https://github.com/user-attachments/assets/2f6d798d-211c-41d3-8220-b7c8c8152637" />
**Rapport sous format pdf**
<img width="591" height="789" alt="image" src="https://github.com/user-attachments/assets/e3d4323d-7211-4cc1-8210-9a9b7b637457" />

## Avertissement
Ce système est un exercice académique. Il ne remplace pas une consultation médicale.





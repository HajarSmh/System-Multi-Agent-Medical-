# Système Multi-Agents Médical avec LangGraph

## Présentation

Ce projet est une application multi-agents qui simule un workflow d’orientation clinique préliminaire.  
Il ne s'agit PAS d'un véritable système médical, mais d'un exercice pédagogique visant à apprendre la conception d’architectures complexes avec LangGraph.

L'application permet de :

- Recueillir les informations d’un patient via une interface utilisateur
- Poser 5 questions successives au patient avec interruptions LangGraph
- Produire une synthèse clinique préliminaire via un LLM
- Générer une recommandation intermédiaire prudente
- Intégrer une validation humaine (Human-in-the-Loop)
- Générer un rapport final structuré avec date et disclaimer
- Télécharger le rapport au format PDF
- Exposer les fonctionnalités via une API FastAPI
- Tester le graphe dans LangGraph Studio

---

## Technologies utilisées

- Python
- LangGraph
- LangChain
- FastAPI
- Streamlit
- MCP (Model Context Protocol)
- OpenAI API
- ReportLab / Génération PDF

---

## Installation

```bash
python -m pip install -r backend/requirements.txt
```

---

## Variables d’environnement

Créer un fichier `.env` :

```env
OPENAI_API_KEY=your_api_key_here
```

---

## Lancement

```bash
# 1. Lancer le serveur MCP
python mcp_server/server.py

# 2. Lancer le backend FastAPI
cd backend
python -m uvicorn app.api:app --reload --port 8000

# 3. Lancer le frontend Streamlit
streamlit run frontend/app.py

# 4. Lancer LangGraph Studio
cd backend
langgraph dev
```

---

## Fonctionnalités

- Workflow multi-agents avec LangGraph
- Questions interactives avec interruptions
- Validation humaine (HITL)
- Génération automatique de rapports
- Export PDF
- API REST FastAPI
- Interface utilisateur Streamlit
- Intégration MCP Server

---

## Architecture

```text
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
```

---

## Structure des dossiers

```text
PROJET AGENTICAI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   │   ├── __init__.py
│   │   │   ├── supervisor.py
│   │   │   ├── diagnostic_agent.py
│   │   │   ├── physician_review.py
│   │   │   └── report_agent.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── patient_tools.py
│   │   │   ├── care_tools.py
│   │   │   ├── pdf_generator.py
│   │   │   └── mcp_client.py
│   │   └── api.py
│   ├── langgraph.json
│
├── mcp_server/
│   ├── server.py
│   └── data/
│       └── guidelines.json
│
├── frontend/
│   └── app.py
│
├── README.md
└── requirements.txt
```

---

## Objectif pédagogique

Ce projet a été réalisé dans le but d’apprendre :

- Les architectures multi-agents
- LangGraph et l’orchestration d’agents IA
- Les interruptions et workflows HITL
- L’intégration d’API avec FastAPI
- La création d’interfaces avec Streamlit
- L’utilisation du protocole MCP
- La génération de rapports PDF automatisés

---

## Démonstration

### Page d'accueil

<img width="1295" height="711" alt="image" src="https://github.com/user-attachments/assets/85f28ff7-95bc-4e35-87e9-764491f0cff0" />

### Question 1/5

<img width="1279" height="730" alt="image" src="https://github.com/user-attachments/assets/7ff595e5-3944-481a-88b8-1d3a368116e1" />

### Génération du rapport

<img width="1384" height="747" alt="image" src="https://github.com/user-attachments/assets/c25081d5-90a5-4b8b-a634-61450ff9c96d" />

### Intégration HITL (Human-in-the-Loop)

<img width="1236" height="555" alt="image" src="https://github.com/user-attachments/assets/0566103b-f67a-41ee-91ca-abd551f98391" />

### Rapport final généré

<img width="1262" height="883" alt="image" src="https://github.com/user-attachments/assets/8c95aa8e-8043-4533-ab85-d9766ce2a085" />

### Rapport au format PDF

<img width="735" height="859" alt="image" src="https://github.com/user-attachments/assets/9d75442a-5be1-453f-9f61-39378430c691" />

---

## Avertissement

Ce projet est un exercice académique et pédagogique.  
Il ne constitue pas un dispositif médical et ne remplace en aucun cas l’avis d’un professionnel de santé.
=======

## Démonstration
**Page d'acceuil**
<img width="1365" height="874" alt="image" src="https://github.com/user-attachments/assets/c1847394-31e0-4780-80f3-f82612929d39" />
**Question 1/5**
<img width="1354" height="764" alt="image" src="https://github.com/user-attachments/assets/091cbb56-12c5-41d0-b2a2-6ee556138ee9" />
**Generation du rapport**
<img width="1434" height="926" alt="image" src="https://github.com/user-attachments/assets/7b898375-52e4-4b57-aa50-959a8ab31f79" />
**Integration HTL**
<img width="1140" height="561" alt="image" src="https://github.com/user-attachments/assets/e64db226-0062-4b7d-8f78-39e9b8f9c6c7" />
**Rapport final généré**
<img width="1233" height="879" alt="image" src="https://github.com/user-attachments/assets/2f6d798d-211c-41d3-8220-b7c8c8152637" />
**Rapport sous format pdf**
<img width="591" height="789" alt="image" src="https://github.com/user-attachments/assets/e3d4323d-7211-4cc1-8210-9a9b7b637457" />

## Avertissement
Ce système est un exercice académique. Il ne remplace pas une consultation médicale.






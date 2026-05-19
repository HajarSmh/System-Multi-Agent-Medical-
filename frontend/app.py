import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Système d'Orientation Clinique", page_icon="🏥")
st.title("🏥 Système d'Orientation Clinique Préliminaire")
st.warning("⚠️ Ce système est un exercice académique. Il ne remplace pas une consultation médicale.")

# Initialisation de la session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "step" not in st.session_state:
    st.session_state.step = "start"  # start, qa, physician, report

# ─── ÉCRAN 1 : Saisie du cas patient ────────────────────────────────
if st.session_state.step == "start":
    st.header("📋 Saisie du cas patient")
    patient_name = st.text_input("Nom du patient (optionnel)")
    patient_case = st.text_area(
        "Décrivez les symptômes ou la raison de la consultation :",
        placeholder="Ex: Fièvre depuis 3 jours, toux sèche, fatigue..."
    )
    
    if st.button("Démarrer la consultation", type="primary"):
        # Créer une session
        session_resp = requests.post(f"{API_URL}/sessions/start", 
                                     json={"patient_name": patient_name or "Patient"})
        thread_id = session_resp.json()["thread_id"]
        st.session_state.thread_id = thread_id
        
        # Démarrer la consultation
        consult_resp = requests.post(f"{API_URL}/consultation/start", json={
            "thread_id": thread_id,
            "patient_case": patient_case
        })
        data = consult_resp.json()
        
        if data.get("status") == "waiting_for_patient":
            st.session_state.current_question = data.get("question")
            st.session_state.question_index = data.get("question_index", 0)
            st.session_state.step = "qa"
            st.rerun()

# ─── ÉCRAN 2 : Questions / Réponses ─────────────────────────────────
elif st.session_state.step == "qa":
    st.header("❓ Questions Cliniques")
    
    q_index = st.session_state.get("question_index", 0)
    st.progress((q_index) / 5, text=f"Question {q_index + 1} / 5")
    
    st.markdown(f"**{st.session_state.current_question}**")
    answer = st.text_area("Votre réponse :", key=f"answer_{q_index}")
    
    if st.button("Envoyer la réponse", type="primary"):
        resume_resp = requests.post(f"{API_URL}/consultation/resume", json={
            "thread_id": st.session_state.thread_id,
            "answer": answer,
            "answer_type": "patient"
        })
        data = resume_resp.json()
        
        if data.get("status") == "waiting_for_patient":
            st.session_state.current_question = data.get("question")
            st.session_state.question_index = data.get("question_index", 0)
            st.rerun()
        elif data.get("status") == "waiting_for_physician":
            st.session_state.diagnostic_summary = data.get("diagnostic_summary")
            st.session_state.interim_care = data.get("interim_care")
            st.session_state.step = "physician"
            st.rerun()

# ─── ÉCRAN 3 : Revue Médecin ────────────────────────────────────────
elif st.session_state.step == "physician":
    st.header("👨‍⚕️ Revue du Médecin Traitant")
    
    with st.expander("📊 Synthèse Clinique Préliminaire", expanded=True):
        st.write(st.session_state.get("diagnostic_summary", ""))
    
    with st.expander("💊 Recommandation Intermédiaire"):
        st.write(st.session_state.get("interim_care", ""))
    
    st.divider()
    st.subheader("Votre avis médical :")
    treatment = st.text_area("Traitement ou conduite à tenir recommandé :")
    notes = st.text_area("Notes complémentaires (optionnel) :")
    
    if st.button("Valider et générer le rapport", type="primary"):
        resume_resp = requests.post(f"{API_URL}/consultation/resume", json={
            "thread_id": st.session_state.thread_id,
            "answer": treatment,
            "answer_type": "physician",
            "physician_treatment": treatment,
            "physician_notes": notes
        })
        data = resume_resp.json()
        
        if data.get("final_report"):
            st.session_state.final_report = data.get("final_report")
            st.session_state.step = "report"
            st.rerun()
        else:
            st.session_state.step = "report"
            st.rerun()

# ─── ÉCRAN 4 : Rapport Final ────────────────────────────────────────
elif st.session_state.step == "report":
    st.header("📄 Rapport Final")
    
    # Récupérer le rapport si pas encore en session
    if "final_report" not in st.session_state:
        report_resp = requests.get(
            f"{API_URL}/consultation/{st.session_state.thread_id}/report"
        )
        st.session_state.final_report = report_resp.json().get("final_report", "")
    
    st.markdown(st.session_state.final_report)
    
    # Bouton de téléchargement PDF
    pdf_resp = requests.get(
        f"http://localhost:8000/consultation/{st.session_state.thread_id}/report/pdf"
    )
    if pdf_resp.status_code == 200:
        st.download_button(
            label="📥 Télécharger le rapport en PDF",
            data=pdf_resp.content,
            file_name=f"rapport_{st.session_state.thread_id[:8]}.pdf",
            mime="application/pdf",
            type="primary"
        )

    st.error("⚠️ Ce système ne remplace pas une consultation médicale.")
    
    if st.button("Nouvelle consultation"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
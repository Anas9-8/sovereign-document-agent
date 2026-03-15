import streamlit as st
import os
import json
from pypdf import PdfReader
import governance
import ollama
import re

st.set_page_config(page_title="Sovereign Document Agent", page_icon="🛡️", layout="wide")

# Custom CSS for better button colors
st.markdown(
    """
<style>
.stButton>button[kind="primary"] {
    background-color: #0066cc;
    color: white;
    border: none;
}
.stButton>button[kind="primary"]:hover {
    background-color: #0052a3;
    border: none;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🛡️ Sovereign Document Agent")
st.markdown("**DSGVO-konformes deutsches Dokumentenverarbeitung mit lokaler KI**")
st.markdown("---")

with st.sidebar:
    st.header("ℹ️ Über das System")
    st.markdown("""
    Dieses System verarbeitet deutsche PDF-Dokumente mit:
    - Lokaler KI (LLaMA 3.2)
    - Deutscher Sprachverarbeitung
    - Vollständiger Governance-Schicht
    - Kompletter Audit-Trail
    
    **Vollständig offline & DSGVO-konform**
    """)

    st.markdown("---")
    st.header("📊 System-Status")

    try:
        ollama.list()
        st.success("✅ Ollama: Läuft")
    except:
        st.error("❌ Ollama: Nicht aktiv")

    if os.path.exists("system.log"):
        st.success("✅ Logging: Aktiv")
    else:
        st.warning("⚠️ Logging: Keine Logs vorhanden")

tab1, tab2, tab3 = st.tabs(
    ["📄 Dokument verarbeiten", "📊 Ergebnisse", "🛡️ Governance"]
)

with tab1:
    st.header("📄 Dokument hochladen und verarbeiten")

    uploaded_file = st.file_uploader(
        "Wählen Sie eine PDF-Datei (deutsche Rechnung)",
        type=["pdf"],
        help="Laden Sie ein deutsches PDF-Dokument zur Verarbeitung hoch",
    )

    if uploaded_file is not None:
        st.success(f"✅ Datei hochgeladen: {uploaded_file.name}")
        st.info(f"📏 Größe: {uploaded_file.size / 1024:.2f} KB")

        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.subheader("🛡️ Guardrail-Prüfung")
        passed, msg = governance.check_file_guardrails(temp_path)

        if not passed:
            st.error(f"❌ Guardrail-Prüfung fehlgeschlagen: {msg}")
            os.remove(temp_path)
            st.stop()
        else:
            st.success("✅ Guardrails bestanden")

        if st.button("▶️ Dokument verarbeiten", type="primary"):
            with st.spinner("Dokument wird verarbeitet..."):

                st.write("📖 **Schritt 1:** PDF wird gelesen...")
                try:
                    reader = PdfReader(temp_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"

                    st.success(f"✅ {len(text)} Zeichen extrahiert")
                    governance.log_processing_start(uploaded_file.name)

                except Exception as e:
                    st.error(f"❌ Fehler beim Lesen der PDF: {e}")
                    governance.log_processing_end(uploaded_file.name, success=False)
                    os.remove(temp_path)
                    st.stop()

                st.write("🔍 **Schritt 2:** Sensibilitätsprüfung...")
                is_sensitive, keywords = governance.check_content_sensitivity(text)

                if is_sensitive:
                    st.warning(f"⚠️ Sensible Inhalte erkannt: {keywords}")
                    st.write("### 🚨 Menschliche Genehmigung erforderlich")
                    st.info(
                        "Dieses Dokument kann sensible Informationen enthalten. DSGVO erfordert ausdrückliche Zustimmung."
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("✅ Verarbeitung genehmigen", key="approve"):
                            st.success("✅ Genehmigt - Fortsetzung...")
                            governance.audit.log_event(
                                "approval_decision", {"decision": "approved"}, "success"
                            )
                        else:
                            st.stop()

                    with col2:
                        if st.button("❌ Verarbeitung ablehnen", key="deny"):
                            st.error("❌ Verarbeitung abgelehnt")
                            governance.audit.log_event(
                                "approval_decision", {"decision": "denied"}, "success"
                            )
                            os.remove(temp_path)
                            st.stop()
                else:
                    st.success("✅ Keine sensiblen Inhalte erkannt")

                st.write("⚙️ **Schritt 3:** KI-Extraktion (dauert ca. 30 Sekunden)...")

                prompt = f"""Du bist ein KI-Assistent, der Informationen aus deutschen Rechnungen extrahiert.

Extrahiere folgende Informationen:
1. Rechnungsnummer
2. Rechnungsdatum  
3. Kundenname
4. Gesamtbetrag
5. Fälligkeitsdatum

Gib NUR ein JSON-Objekt zurück - keine weiteren Texte:
{{"invoice_number": "...", "invoice_date": "...", "customer_name": "...", "total_amount": "...", "due_date": "..."}}

Rechnungstext:
{text[:500]}"""

                try:
                    response = ollama.generate(model="llama3.2:1b", prompt=prompt)
                    ai_response = response["response"]

                    # Advanced JSON cleaning
                    start = ai_response.find("{")
                    end = ai_response.rfind("}")

                    if start == -1:
                        raise ValueError("Keine JSON-Struktur gefunden")

                    if end == -1 or end < start:
                        json_str = ai_response[start:].strip() + "}"
                    else:
                        json_str = ai_response[start : end + 1]

                    # Clean multiple spaces
                    json_str = re.sub(r"\s+", " ", json_str)

                    # Remove control characters
                    json_str = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", json_str)

                    # Try to parse
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        # Manual extraction as fallback
                        st.warning(
                            "⚠️ JSON-Parsing fehlgeschlagen, verwende manuelle Extraktion..."
                        )

                        data = {}

                        inv_match = re.search(
                            r'"invoice_number"\s*:\s*"([^"]*)"', json_str
                        )
                        data["invoice_number"] = (
                            inv_match.group(1) if inv_match else "N/A"
                        )

                        date_match = re.search(
                            r'"invoice_date"\s*:\s*"([^"]*)"', json_str
                        )
                        data["invoice_date"] = (
                            date_match.group(1) if date_match else "N/A"
                        )

                        cust_match = re.search(
                            r'"customer_name"\s*:\s*"([^"]*)"', json_str
                        )
                        data["customer_name"] = (
                            cust_match.group(1) if cust_match else "N/A"
                        )

                        amt_match = re.search(
                            r'"total_amount"\s*:\s*"([^"]*)"', json_str
                        )
                        data["total_amount"] = (
                            amt_match.group(1) if amt_match else "N/A"
                        )

                        due_match = re.search(r'"due_date"\s*:\s*"([^"]*)"', json_str)
                        data["due_date"] = due_match.group(1) if due_match else "N/A"

                        st.info("ℹ️ Manuelle Extraktion erfolgreich")

                    # Save results
                    with open("streamlit_results.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    st.success("✅ KI-Extraktion abgeschlossen!")

                    # Log
                    governance.log_ai_extraction(
                        "llama3.2:1b", success=True, fields_extracted=len(data)
                    )
                    governance.log_processing_end(
                        uploaded_file.name, success=True, extracted_fields=len(data)
                    )

                    # Display results
                    st.write("### 📊 Extrahierte Informationen")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "📄 Rechnungsnummer", data.get("invoice_number", "N/A")
                        )
                        st.metric("📅 Rechnungsdatum", data.get("invoice_date", "N/A"))
                        st.metric("Kundenname", data.get("customer_name", "N/A"))

                    with col2:
                        st.metric("💰 Gesamtbetrag", data.get("total_amount", "N/A"))
                        st.metric("📅 Fälligkeitsdatum", data.get("due_date", "N/A"))

                    st.balloons()

                except Exception as e:
                    st.error(f"❌ KI-Extraktion fehlgeschlagen: {e}")
                    st.error("Bitte versuchen Sie es erneut.")
                    governance.log_ai_extraction("llama3.2:1b", success=False)

                os.remove(temp_path)

with tab2:
    st.header("📊 Letzte Ergebnisse")

    if os.path.exists("streamlit_results.json"):
        with open("streamlit_results.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        st.json(data)

        st.download_button(
            label="📥 Ergebnisse herunterladen (JSON)",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name="extracted_data.json",
            mime="application/json",
        )
    else:
        st.info("ℹ️ Noch keine Ergebnisse. Verarbeiten Sie zuerst ein Dokument.")

with tab3:
    st.header("🛡️ Governance & Compliance")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Audit-Trail")

        if os.path.exists("audit_trail.json"):
            with open("audit_trail.json", "r") as f:
                events = json.load(f)

            st.info(f"Gesamte Events: {len(events)}")
            st.write("**Letzte 5 Events:**")
            for event in events[-5:]:
                with st.expander(f"{event['action']} - {event['status']}"):
                    st.json(event)
        else:
            st.warning("⚠️ Noch kein Audit-Trail vorhanden")

    with col2:
        st.subheader("📝 System-Logs")

        if os.path.exists("system.log"):
            with open("system.log", "r") as f:
                logs = f.readlines()

            st.info(f"Gesamte Log-Einträge: {len(logs)}")
            st.text_area("Letzte 10 Einträge:", value="".join(logs[-10:]), height=300)
        else:
            st.warning("⚠️ Noch keine Logs vorhanden")

    st.subheader("🛡️ Aktive Guardrails")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Max. Dateigröße", "10 MB")
    with col2:
        st.metric("Erlaubte Typen", "Nur PDF")
    with col3:
        st.metric("Sensible Schlüsselwörter", "4")

st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray;'>
🛡️ Sovereign Document Agent | DSGVO & EU AI Act konform | Entwickelt in Deutschland
</div>
""",
    unsafe_allow_html=True,
)

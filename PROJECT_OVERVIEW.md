# ProSi-mini: Property Sales Intelligence

ProSi-mini is a lightweight, AI-driven dashboard designed to help property sales teams prioritize leads, manage risk, and improve operational efficiency. It provides real-time analytics, persona-based insights, and proactive alerts.

## Core Features

1.  **Lead Management**: Central repository for leads with status tracking and follow-up history.
2.  **Risk & SLA Analytics**:
    *   **Risk Scoring**: Each lead is assigned a risk score (0-100) based on age, engagement, source, and SLA status.
    *   **SLA Monitoring**: Tracks whether leads are progressing through the pipeline within predefined timeframes.
3.  **Persona-Based Insights**: The dashboard delivers tailored summaries and recommendations for different user roles:
    *   **Founder / Executive**: High-level overview of pipeline health, risk exposure, and strategic opportunities.
    *   **Sales Manager**: Actionable insights on which leads to prioritize and which team members need support.
    *   **Operations / CRM Manager**: Focus on process bottlenecks, SLA compliance, and data quality issues.
4.  **Proactive Alerts**: A sidebar panel that flags urgent issues, such as SLA breaches or a sudden increase in high-risk leads, tailored to the user's persona.
5.  **Trust & Confidence Layer**:
    *   **Data Freshness**: A score (0-100) indicating how up-to-date the underlying data is.
    *   **Confidence Score**: A lead-level score (0-1) reflecting the system's confidence in its own assessment, based on data completeness and signal consistency.
    *   **Explainability Coverage**: A metric showing how many expected risk factors were identified for each lead, providing transparency into the AI's reasoning.
6.  **Governance & Audit Trail**:
    *   **Append-Only Logging**: Records all key system decisions, such as risk calculations, SLA breach detections, and insight generation, in a secure, append-only log.
    *   **Traceability**: Provides a clear audit trail for compliance, review, and debugging. Each decision is logged with inputs, outputs, confidence scores, and a timestamp.
    *   **Future-Ready**: The architecture includes placeholders for event hashing, enabling future integration with Web3 technologies for immutable, decentralized anchoring.

## Technical Architecture

*   **Backend**: FastAPI (Python)
*   **Database**: SQLAlchemy with SQLite (for simplicity)
*   **Frontend**: Streamlit
*   **Data Models**: Pydantic

The system is designed with a modular, service-oriented architecture to ensure maintainability and scalability.

## Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Backend API**:
    ```bash
    uvicorn app.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000/docs`.
3.  **Run the Frontend UI**:
    ```bash
    streamlit run ui/streamlit_app.py
    ```
    The dashboard will be accessible at `http://localhost:8501`.

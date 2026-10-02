"""
Atlas Funding - Scholarship Intelligence Engine
Interactive Dashboard built for Edxso AI Engineer Intern - Assignment 2.
Displays continuous auto-crawling, multi-pillar verification, evidence grounding, and change detection.
"""

import streamlit as st
import pandas as pd
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.database.connection import init_db
from src.database.repository import ScholarshipRepository
from src.crawler.crawler_engine import CrawlerEngine
from src.discovery.engine import DiscoveryEngine
from src.models.enums import ScholarshipStatus, VerificationStatus, ProviderType
import config

# Page Configuration
st.set_page_config(
    page_title="Atlas Funding | Scholarship Intelligence Engine",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0284C7;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-verified {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-review {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-active {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-expired {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-expiring {
        background-color: #FFEDD5;
        color: #9A3412;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .evidence-box {
        background-color: #F8FAFC;
        border-left: 4px solid #0284C7;
        padding: 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.88rem;
        color: #334155;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database & Repository
init_db()
repo = ScholarshipRepository()
crawler_engine = CrawlerEngine()


# ----------------------------------------------------
# Sidebar Controls & Filters
# ----------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/graduation-cap.png", width=64)
    st.markdown("### **Atlas Intelligence**")
    st.caption("AI-Powered Continuous Scholarship Intelligence Engine for Indian Students")
    st.divider()

    st.subheader("🔍 Search & Filter")
    search_query = st.text_input("Search Scholarship / Provider", placeholder="e.g. Reliance, Pragati, INSPIRE...")

    provider_filter = st.selectbox(
        "Source Category",
        ["All", "Government (Central)", "Government (State)", "Corporate CSR", "Foundation / Trust", "Aggregator / Directory"]
    )

    status_filter = st.selectbox(
        "Lifecycle Status",
        ["All", "ACTIVE", "EXPIRING_SOON", "EXPIRED", "REVIEW_REQUIRED"]
    )

    verification_filter = st.selectbox(
        "Verification Status",
        ["All", "VERIFIED", "REVIEW REQUIRED"]
    )

    min_confidence = st.slider("Minimum Confidence Score", min_value=0, max_value=100, value=0, step=5)

    st.divider()
    st.markdown("### ⚡ Live Crawler Controls")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("▶ Run 1 (Base)", use_container_width=True, help="Executes initial base crawl of 25 scholarships"):
            with st.spinner("Executing Run 1 Base Crawl..."):
                r = crawler_engine.run_initial_crawl()
                st.success(f"Run 1 completed! ({r.total_discovered} records)")
                st.rerun()

    with col_c2:
        if st.button("🔄 Run 2 (Update)", use_container_width=True, help="Executes consecutive crawl, detecting changes and expired dates"):
            with st.spinner("Executing Run 2 with Change Detection..."):
                r, ch = crawler_engine.run_consecutive_crawl()
                st.warning(f"Run 2 completed! ({len(ch)} changes detected)")
                st.rerun()


# ----------------------------------------------------
# Header & KPI Metrics
# ----------------------------------------------------
st.markdown('<div class="main-header">🎓 Atlas Funding: Scholarship Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Discovery → Crawling → Extraction → Verification → 6-Pillar Confidence Scoring → Change Detection</div>', unsafe_allow_html=True)

metrics = repo.get_analytics_metrics()

kpi_cols = st.columns(6)
with kpi_cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Discovered</div>
        <div class="metric-value">{metrics['total_discovered']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Verified (≥95%)</div>
        <div class="metric-value" style="color: #16A34A;">{metrics['total_verified']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Review Required</div>
        <div class="metric-value" style="color: #D97706;">{metrics['total_review_required']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Active / Expiring</div>
        <div class="metric-value" style="color: #0284C7;">{metrics['total_active'] + metrics['total_expiring_soon']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Expired / Stale</div>
        <div class="metric-value" style="color: #DC2626;">{metrics['total_expired']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[5]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Confidence</div>
        <div class="metric-value" style="color: #7C3AED;">{metrics['avg_confidence']}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ----------------------------------------------------
# Main Tab Navigation
# ----------------------------------------------------
tab_explorer, tab_changes, tab_crawler, tab_data = st.tabs([
    "📚 Scholarship Repository & Inspector",
    "🔄 Change Detection & Audit Log",
    "🤖 Continuous Crawler Center",
    "🗄️ Database & Schema Inspector"
])


# ----------------------------------------------------
# Tab 1: Scholarship Repository & Detailed Inspector
# ----------------------------------------------------
with tab_explorer:
    scholarships = repo.list_scholarships(
        status=status_filter,
        provider_type=provider_filter,
        verification_status=verification_filter,
        min_confidence=float(min_confidence),
        search_query=search_query
    )

    st.markdown(f"##### Showing **{len(scholarships)}** scholarship records matching criteria")

    if not scholarships:
        st.info("No scholarships match the selected filters. Try broadening your search or click 'Run 1 (Base)' to populate.")
    else:
        for s in scholarships:
            v_badge = f'<span class="badge-verified">✓ {s.verification_status.value} ({s.confidence_score:.1f}%)</span>' if s.confidence_score >= 95.0 else f'<span class="badge-review">⚠ {s.verification_status.value} ({s.confidence_score:.1f}%)</span>'
            
            if s.status == ScholarshipStatus.ACTIVE:
                st_badge = f'<span class="badge-active">● ACTIVE</span>'
            elif s.status == ScholarshipStatus.EXPIRING_SOON:
                st_badge = f'<span class="badge-expiring">⏰ EXPIRING SOON</span>'
            elif s.status == ScholarshipStatus.EXPIRED:
                st_badge = f'<span class="badge-expired">✕ EXPIRED</span>'
            else:
                st_badge = f'<span class="badge-review">? {s.status.value}</span>'

            with st.expander(f"{s.scholarship_name} — {s.provider} [{s.confidence_score:.1f}% Confidence]"):
                st.markdown(f"### {s.scholarship_name}")
                st.markdown(f"**Provider:** `{s.provider}` | **Category:** `{s.provider_type.value}` | Status: {st_badge} | Verification: {v_badge}", unsafe_allow_html=True)
                
                # Links Bar
                col_l1, col_l2, col_l3 = st.columns([2, 2, 2])
                with col_l1:
                    st.markdown(f"🌐 **Official Source:** [{s.official_source_url}]({s.official_source_url})")
                with col_l2:
                    if s.application_url.startswith("http"):
                        st.markdown(f"📝 **Application Portal:** [Apply Online]({s.application_url})")
                    else:
                        st.markdown(f"📝 **Application Portal:** `{s.application_url}`")
                with col_l3:
                    st.markdown(f"📅 **Deadline:** `{s.closing_date}`")

                st.divider()

                # Details Columns
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown("#### 💰 Financial Benefits & Value")
                    st.info(f"**Benefit Entitlement:**\n\n{s.amount_benefit}")
                    if s.amount_value_inr:
                        st.caption(f"Normalized Annual INR Value: ₹{s.amount_value_inr:,.0f}")

                    st.markdown("#### 🎯 Operational Schedule & Procedures")
                    st.markdown(f"- **Opening Date:** `{s.opening_date}`")
                    st.markdown(f"- **Closing Date:** `{s.closing_date}`")
                    st.markdown(f"- **Selection Process:** {s.selection_process}")
                    st.markdown(f"- **Renewal Conditions:** {s.renewal_requirements}")
                    st.markdown(f"- **Required Documents:** {', '.join(s.documents_required) if s.documents_required else 'Not specified'}")

                with col_d2:
                    st.markdown("#### 📋 Universal Eligibility Dimensions")
                    st.markdown(f"- **Academic Requirements:** {s.academic_requirements}")
                    st.markdown(f"- **Eligible Course Levels:** {', '.join(s.course_level)}")
                    st.markdown(f"- **Family Income Criteria:** `{s.income_criteria}`")
                    st.markdown(f"- **Gender Eligibility:** `{s.gender_criteria if isinstance(s.gender_criteria, str) else s.gender_criteria.value}`")
                    st.markdown(f"- **Category / Reservation:** `{s.category_criteria}`")
                    st.markdown(f"- **Domicile / Residence:** `{s.domicile_state}`")
                    st.markdown(f"- **Eligible Institutions:** {s.institution_requirements}")

                st.divider()

                # Confidence Scorecard ("Why this score?")
                st.markdown("#### 📊 Explainable 6-Pillar Confidence Scorecard (Why this score?)")
                if s.score_breakdown:
                    sb = s.score_breakdown
                    p_cols = st.columns(6)
                    p_cols[0].metric("Domain Authenticity", f"{sb.domain_score:.1f} / 25")
                    p_cols[1].metric("Reachability", f"{sb.reachability_score:.1f} / 15")
                    p_cols[2].metric("Evidence Match", f"{sb.evidence_score:.1f} / 25")
                    p_cols[3].metric("Application Link", f"{sb.app_url_score:.1f} / 10")
                    p_cols[4].metric("Temporal Currency", f"{sb.temporal_score:.1f} / 15")
                    p_cols[5].metric("Consistency", f"{sb.consistency_score:.1f} / 10")

                    st.markdown("**Deterministic Verification Findings:**")
                    for reason in sb.reasons:
                        st.markdown(f"- {reason}")
                else:
                    st.write(f"Confidence Score: {s.confidence_score}%")

                st.divider()

                # Field-Level Grounded Evidence Audit Trail
                st.markdown("#### 🔎 Field-Level Grounded Evidence Audit Trail (Anti-Hallucination Proof)")
                st.caption("Traces: Database Field → Official Source URL → Verbatim DOM Quote → Extracted Value")
                if s.evidence_items:
                    for ev in s.evidence_items:
                        st.markdown(f"**Field: `{ev.field_name}`** | Extracted Value: `{ev.extracted_value}`")
                        st.markdown(f'<div class="evidence-box">"{ev.evidence_text}"<br><span style="color:#64748B; font-size:0.75rem;">Source: {ev.source_url}</span></div>', unsafe_allow_html=True)
                else:
                    st.caption("No field evidence items attached.")

                # Scholarship-Specific Change History
                sc_history = repo.get_history(s.id)
                if sc_history:
                    st.divider()
                    st.markdown("#### 🕒 Change Detection History for this Scholarship")
                    for h in sc_history:
                        st.markdown(f"• **{h['detected_at'][:19]}** | Field `{h['field_name']}`: <span style='color:red;'>{h['old_value']}</span> ➔ <span style='color:green; font-weight:bold;'>{h['new_value']}</span> (Run: `{h['run_id']}`)", unsafe_allow_html=True)


# ----------------------------------------------------
# Tab 2: Change Detection & Audit Log
# ----------------------------------------------------
with tab_changes:
    st.markdown("### 🔄 Continuous Change Detection & Audit Log")
    st.markdown("Demonstrating requirement 7: The system automatically captures field updates across crawl cycles without destructive overwriting.")

    all_history = repo.get_history()
    if not all_history:
        st.info("No changes logged yet. Click **'Run 2 (Update)'** in the sidebar to simulate a consecutive crawl with detected deadline and benefit changes.")
    else:
        st.success(f"Tracked **{len(all_history)}** historical field modifications across crawler runs.")
        
        hist_df = pd.DataFrame(all_history)
        hist_display = hist_df[["detected_at", "scholarship_name", "field_name", "old_value", "new_value", "run_id"]]
        hist_display.columns = ["Detected At", "Scholarship Name", "Modified Field", "Previous Value", "New Crawled Value", "Run ID"]
        st.dataframe(hist_display, use_container_width=True, hide_index=True)

        st.markdown("#### 📜 Granular Change Inspection")
        for h in all_history:
            with st.container():
                st.markdown(f"""
                **{h['scholarship_name']}** — Field: `{h['field_name']}`  
                📅 *Detected on:* `{h['detected_at'][:19]}` | *Run:* `{h['run_id']}`  
                - **Old Value:** `{h['old_value']}`  
                - **New Value:** `{h['new_value']}`  
                - **Evidence Snippet:** *"{h['evidence_text']}"*  
                - **Primary URL:** [{h['source_url']}]({h['source_url']})
                """)
                st.divider()


# ----------------------------------------------------
# Tab 3: Continuous Crawler Center
# ----------------------------------------------------
with tab_crawler:
    st.markdown("### 🤖 Continuous Auto Crawler & Execution Logs")
    st.markdown("Tracks scheduled jobs, discovery seeds, and crawl pass history.")

    col_cr1, col_cr2 = st.columns([1, 1])
    with col_cr1:
        st.markdown("#### 🚀 Trigger Execution")
        st.markdown("Simulate automated periodic crawler sweeps:")
        if st.button("Execute Base Crawl (Run 1)", key="center_run1"):
            with st.spinner("Executing Run 1..."):
                crawler_engine.run_initial_crawl()
                st.rerun()

        if st.button("Execute Re-Crawl with Change Detection (Run 2)", key="center_run2"):
            with st.spinner("Executing Run 2..."):
                crawler_engine.run_consecutive_crawl()
                st.rerun()

    with col_cr2:
        st.markdown("#### 🌐 Discovery Seeds Registry")
        disc = DiscoveryEngine()
        seeds = disc.list_seeds()
        st.markdown(f"Configured with **{len(seeds)}** seed endpoints across Government, Corporate CSR, and Foundations:")
        seed_df = pd.DataFrame(seeds)
        st.dataframe(seed_df[["name", "category", "url"]], use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 📋 Crawl Runs Execution History")
    runs = repo.get_crawl_runs()
    if runs:
        runs_df = pd.DataFrame(runs)
        st.dataframe(
            runs_df[["run_id", "run_type", "started_at", "total_discovered", "total_verified", "total_changes_detected", "log_summary"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption("No crawl runs logged yet.")


# ----------------------------------------------------
# Tab 4: Database & Schema Inspector
# ----------------------------------------------------
with tab_data:
    st.markdown("### 🗄️ Database & Schema Inspector")
    st.markdown(f"Direct inspection of SQLite database: `{config.DATABASE_PATH}`")

    table_choice = st.radio("Select Table to Inspect", ["scholarships", "scholarship_evidence", "scholarship_history", "crawl_runs"], horizontal=True)

    conn = sqlite3.connect(str(config.DATABASE_PATH))
    df_raw = pd.read_sql_query(f"SELECT * FROM {table_choice}", conn)
    conn.close()

    st.markdown(f"**Table `{table_choice}` ({len(df_raw)} records):**")
    st.dataframe(df_raw, use_container_width=True)

    st.divider()
    st.markdown("#### 📥 Data Export")
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        csv_data = df_raw.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {table_choice}.csv",
            data=csv_data,
            file_name=f"{table_choice}.csv",
            mime="text/csv"
        )
    with col_ex2:
        json_data = df_raw.to_json(orient="records", indent=2)
        st.download_button(
            label=f"Download {table_choice}.json",
            data=json_data,
            file_name=f"{table_choice}.json",
            mime="application/json"
        )

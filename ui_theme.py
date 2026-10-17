"""
UI Theme and Custom Styling for IoT Image Gallery Dashboard
Features a modern, responsive Light-Blue and Cyan theme with glassmorphism touches.
"""

THEME_CSS = """
<style>
/* -------------------------------------------------------------------------
   Global Page & Light-Blue / Cyan Theme Variables
   ------------------------------------------------------------------------- */
:root {
    --primary-blue: #0284c7;       /* Sky Blue */
    --primary-cyan: #06b6d4;       /* Bright Cyan */
    --cyan-hover: #0891b2;         /* Deep Cyan */
    --light-bg: #f0f9ff;           /* Ice Blue Background */
    --card-bg: #ffffff;            /* White Card */
    --card-border: #bae6fd;        /* Soft Blue Border */
    --card-glow: rgba(6, 182, 212, 0.15);
    --text-primary: #0f172a;       /* Deep Slate */
    --text-secondary: #475569;     /* Slate */
    --text-muted: #64748b;         /* Muted Slate */
    --badge-active: #10b981;       /* Emerald Green */
    --badge-inactive: #64748b;     /* Muted Grey */
    --led-on: #00f2fe;             /* Radiant Cyan LED */
    --led-glow: 0 0 15px #00f2fe, 0 0 30px #06b6d4;
}

/* Base Body Adjustments */
.stApp {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f8fafc 100%);
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    color: var(--text-primary);
}

/* -------------------------------------------------------------------------
   Header Styling
   ------------------------------------------------------------------------- */
.dashboard-header {
    background: linear-gradient(90deg, #0284c7 0%, #06b6d4 100%);
    color: #ffffff;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(6, 182, 212, 0.25);
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.dashboard-title {
    font-size: 1.9rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.dashboard-subtitle {
    font-size: 0.95rem;
    color: #e0f2fe;
    margin-top: 4px;
    font-weight: 400;
}

/* -------------------------------------------------------------------------
   Metric Cards
   ------------------------------------------------------------------------- */
.metric-card {
    background: #ffffff;
    border: 1px solid #bae6fd;
    border-radius: 14px;
    padding: 1.25rem 1rem;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(6, 182, 212, 0.2);
    border-color: #38bdf8;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #0284c7, #06b6d4);
}

.metric-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.8px;
    color: #64748b;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0369a1;
}

/* -------------------------------------------------------------------------
   ESP32 & LED Status Indicators
   ------------------------------------------------------------------------- */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.85rem;
}

.status-active {
    background-color: #d1fae5;
    color: #065f46;
    border: 1px solid #6ee7b7;
}

.status-inactive {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
}

.led-indicator-on {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #ecfeff;
    color: #0e7490;
    border: 1px solid #67e8f9;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 700;
    box-shadow: 0 0 12px rgba(6, 182, 212, 0.5);
    animation: pulse-cyan 2s infinite;
}

.led-indicator-off {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f8fafc;
    color: #64748b;
    border: 1px solid #e2e8f0;
    padding: 6px 14px;
    border-radius: 9999px;
    font-weight: 600;
}

.led-dot-on {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #06b6d4;
    box-shadow: 0 0 10px #06b6d4, 0 0 20px #06b6d4;
}

.led-dot-off {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #94a3b8;
}

@keyframes pulse-cyan {
    0% {
        box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.6);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(6, 182, 212, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(6, 182, 212, 0);
    }
}

/* -------------------------------------------------------------------------
   Gallery Item Card
   ------------------------------------------------------------------------- */
.gallery-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e0f2fe;
    padding: 12px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.06);
    transition: all 0.25s ease;
}

.gallery-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 24px rgba(6, 182, 212, 0.2);
    border-color: #38bdf8;
}

.gallery-meta {
    margin-top: 10px;
    font-size: 0.8rem;
    color: #475569;
    border-top: 1px solid #f0f9ff;
    padding-top: 8px;
}

.gallery-meta-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 4px;
}

.gallery-tag {
    background: #e0f2fe;
    color: #0369a1;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.72rem;
}

/* -------------------------------------------------------------------------
   Custom Streamlit Overrides
   ------------------------------------------------------------------------- */
div.stButton > button {
    background: linear-gradient(90deg, #0284c7 0%, #06b6d4 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3) !important;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #0369a1 0%, #0891b2 100%) !important;
    box-shadow: 0 6px 18px rgba(6, 182, 212, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Button Styling */
div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #0284c7 !important;
    border: 1px solid #bae6fd !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
}

div.stButton > button[kind="secondary"]:hover {
    background: #f0f9ff !important;
    border-color: #38bdf8 !important;
}

/* File Uploader Customization */
[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 2px dashed #38bdf8;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 10px rgba(6, 182, 212, 0.05);
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fafc 0%, #f0f9ff 100%);
    border-right: 1px solid #bae6fd;
}
</style>
"""


def apply_theme():
    """Returns the CSS string to be injected via st.markdown."""
    return THEME_CSS

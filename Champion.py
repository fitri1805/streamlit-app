import streamlit as st
import pandas as pd
import altair as alt
import mysql.connector
import itertools
import numpy as np
from datetime import datetime, date
from Login import apply_sidebar_theme

# EFLM Targets 
EFLM_TARGETS = {
    "Albumin": 2.1, "ALT": 6.0, "ALP": 5.4, "AST": 5.3, "Bilirubin (Total)": 8.6,
    "Cholesterol": 2.9, "CK": 4.5, "Creatinine": 3.4, "GGT": 7.7, "Glucose": 2.9,
    "HDL Cholesterol": 4.0, "LDL Cholesterol": 4.9, "Potassium": 1.8, "Sodium": 0.9,
    "Protein (Total)": 2.0, "Urea": 3.9, "Uric Acid": 3.3
}

# MLBB Theme CSS
def apply_mlbb_theme():
    st.markdown("""
    <style>
    /* Import MLBB-style fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* MLBB Color Palette */
    :root {
        --mlbb-primary: #ff4d8d;
        --mlbb-secondary: #4a00e0;
        --mlbb-accent: #ff9a8b;
        --mlbb-gold: #ffd700;
        --mlbb-silver: #c0c0c0;
        --mlbb-bronze: #cd7f32;
        --mlbb-dark: #0a0f1e;
        --mlbb-darker: #070a14;
        --mlbb-light: #f8f9ff;
        --mlbb-gradient: linear-gradient(135deg, var(--mlbb-secondary) 0%, var(--mlbb-primary) 100%);
        --mlbb-glow: 0 0 20px rgba(255, 77, 141, 0.6);
        --mlbb-border-radius: 16px;
        --mlbb-transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        --mlbb-card-bg: rgba(15, 20, 40, 0.85);
        --mlbb-card-border: 1px solid rgba(255, 255, 255, 0.15);
    }

    /* Main App Background */
    .stApp .block-container{
    background: linear-gradient(135deg, #0a0f1e 0%, #1a1a2e 50%, #16213e 100%);
    background-attachment: fixed;
    color: var(--mlbb-light);
    font-family: 'Rajdhani', sans-serif;
    }

    .stApp .block-container::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(2px 2px at 20% 30%, rgba(255, 77, 141, 0.4) 0%, transparent 100%),
            radial-gradient(2px 2px at 80% 70%, rgba(74, 0, 224, 0.4) 0%, transparent 100%),
            radial-gradient(3px 3px at 40% 20%, rgba(255, 154, 139, 0.3) 0%, transparent 100%),
            radial-gradient(2px 2px at 60% 80%, rgba(255, 215, 0, 0.3) 0%, transparent 100%);
        background-size: 300px 300px, 250px 250px, 400px 400px, 350px 350px;
        animation: particlesMove 20s infinite linear;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes particlesMove {
        from { background-position: 0 0, 0 0, 0 0, 0 0; }
        to { background-position: 300px 300px, 250px 250px, 400px 400px, 350px 350px; }
    }

    /* Title Styling */
    .main-title {
        font-family: 'Cinzel', serif;
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        background: var(--mlbb-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(255, 77, 141, 0.8);
        margin: 2rem 0;
        position: relative;
        animation: titleGlow 3s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        0% { text-shadow: 0 0 20px rgba(255, 77, 141, 0.6); }
        100% { text-shadow: 0 0 40px rgba(255, 77, 141, 1), 0 0 60px rgba(74, 0, 224, 0.8); }
    }

    /* Section Headers - Exclude sidebar */
    .stApp h1:not(.stSidebar *), 
    .stApp h2:not(.stSidebar *), 
    .stApp h3:not(.stSidebar *) {
        font-family: 'Cinzel', serif;
        color: var(--mlbb-light);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        position: relative;
    }

    .stApp h2:not(.stSidebar *) {
        font-size: 2.5rem;
        color: white;
        border-bottom: 2px solid var(--mlbb-primary);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }

    .stApp h3:not(.stSidebar *) {
        font-size: 2rem;
        color: var(--mlbb-gold);
    }

    /* Cards and Containers - Exclude sidebar */
    .stApp .element-container:not(.stSidebar *),
    .stApp .stDataFrame:not(.stSidebar *),
    .stApp .stSelectbox:not(.stSidebar *),
    .stApp .stAlert:not(.stSidebar *) {
        background: var(--mlbb-card-bg) !important;
        border: var(--mlbb-card-border) !important;
        border-radius: var(--mlbb-border-radius) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.3),
            0 0 20px rgba(255, 77, 141, 0.1) !important;
        transition: var(--mlbb-transition) !important;
        position: relative;
        overflow: hidden;
    }
                

    /* Card Hover Effects */
    .stApp .element-container:not(.stSidebar *):hover,
    .stApp .stDataFrame:not(.stSidebar *):hover {
        transform: translateY(-2px);
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.4),
            var(--mlbb-glow) !important;
    }

    .stApp .element-container:not(.stSidebar *)::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #ff66cc, #9933ff);
        transition: left 0.8s ease;
    }

    .stApp .element-container:not(.stSidebar *):hover::before {
        left: 100%;
    }
                
    .stApp .main .stDataFrame {
        margin: 2rem 0;
    }
    
    .stApp .main .stDataFrame table {
        background: transparent !important;
        border-collapse: separate !important;
        border-spacing: 0 8px !important;
        width: 100% !important;
    }

    .stApp .main .stDataFrame th {
        background: var(--mlbb-gradient) !important;
        color: white !important;
        font-family: 'Orbitron', monospace !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        padding: 1rem !important;
        border: none !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8) !important;
        text-align: center !important;
    }

    .stApp .main .stDataFrame td {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--mlbb-light) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease !important;
        text-align: center !important;
    }

    .stApp .main .stDataFrame tr:hover td {
        background: rgba(255, 77, 141, 0.2) !important;
        box-shadow: 0 0 15px rgba(255, 77, 141, 0.4) !important;
        transform: scale(1.02) !important;
    }

    
    .stApp .main .stAlert {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        border-left: 4px solid var(--mlbb-primary) !important;
    }

    .stApp .main .stSuccess {
        background: linear-gradient(135deg, rgba(0, 255, 127, 0.1), rgba(50, 205, 50, 0.1)) !important;
        border-left-color: #00ff7f !important;
        color: #00ff7f !important;
    }

    .stApp .main .stWarning {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.1), rgba(255, 140, 0, 0.1)) !important;
        border-left-color: #ffa500 !important;
        color: #ffa500 !important;
    }

    .stApp .main .stInfo {
        background: linear-gradient(135deg, rgba(0, 191, 255, 0.1), rgba(30, 144, 255, 0.1)) !important;
        border-left-color: #00bfff !important;
        color: #00bfff !important;
    }

   
    .stApp .main .stSelectbox select {
        background: var(--mlbb-card-bg) !important;
        color: var(--mlbb-light) !important;
        border: 2px solid var(--mlbb-primary) !important;
        border-radius: var(--mlbb-border-radius) !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
        box-shadow: var(--mlbb-glow) !important;
    }

    .stApp .main .stSelectbox select:focus {
        border-color: var(--mlbb-accent) !important;
        box-shadow: 0 0 25px rgba(255, 77, 141, 0.8) !important;
    }

    /* Champion Announcement  */
    .stApp .champion-card {
        background: linear-gradient(135deg, 
            rgba(255, 215, 0, 0.2) 0%, 
            rgba(255, 77, 141, 0.2) 50%, 
            rgba(74, 0, 224, 0.2) 100%) !important;
        border: 3px solid var(--mlbb-gold) !important;
        border-radius: 20px !important;
        padding: 3rem !important;
        margin: 2rem 0 !important;
        text-align: center !important;
        box-shadow: 
            0 0 50px rgba(255, 215, 0, 0.6),
            inset 0 0 50px rgba(255, 215, 0, 0.1) !important;
        animation: championGlow 2s ease-in-out infinite alternate !important;
        position: relative !important;
        overflow: hidden !important;
    }

    @keyframes championGlow {
        0% { 
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.6);
            transform: scale(1);
        }
        100% { 
            box-shadow: 0 0 60px rgba(255, 215, 0, 0.9), 0 0 100px rgba(255, 77, 141, 0.5);
            transform: scale(1.02);
        }
    }

    .stApp .champion-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(
            transparent,
            rgba(255, 215, 0, 0.3),
            transparent,
            rgba(255, 77, 141, 0.3),
            transparent
        );
        animation: rotate 4s linear infinite;
        z-index: -1;
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .stApp .champion-name {
        font-family: 'Cinzel', serif !important;
        font-size: 4rem !important;
        font-weight: 700 !important;
        color: var(--mlbb-gold) !important;
        text-shadow: 
            0 0 20px rgba(255, 215, 0, 0.8),
            2px 2px 4px rgba(0, 0, 0, 0.8) !important;
        margin: 1rem 0 !important;
        animation: textPulse 2s ease-in-out infinite alternate !important;
    }

    @keyframes textPulse {
        0% { text-shadow: 0 0 20px rgba(255, 215, 0, 0.8); }
        100% { text-shadow: 0 0 40px rgba(255, 215, 0, 1), 0 0 60px rgba(255, 77, 141, 0.8); }
    }

    .stApp .champion-elo {
        font-family: 'Orbitron', monospace !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--mlbb-light) !important;
        background: rgba(255, 215, 0, 0.2) !important;
        padding: 1rem 2rem !important;
        border-radius: 10px !important;
        border: 2px solid var(--mlbb-gold) !important;
        display: inline-block !important;
        margin: 1rem 0 !important;
    }

    .stApp .champion-medal {
        font-size: 6rem !important;
        animation: medalSpin 3s ease-in-out infinite !important;
        display: block !important;
        margin: 1rem 0 !important;
    }

    @keyframes medalSpin {
        0%, 100% { transform: rotate(0deg) scale(1); }
        25% { transform: rotate(-10deg) scale(1.1); }
        75% { transform: rotate(10deg) scale(1.1); }
    }

    /* Rank Styling */
    .stApp .rank-gold {
        color: var(--mlbb-gold) !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.8) !important;
        animation: goldShimmer 2s ease-in-out infinite alternate !important;
    }

    .stApp .rank-silver {
        color: var(--mlbb-silver) !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(192, 192, 192, 0.8) !important;
    }

    .stApp .rank-bronze {
        color: var(--mlbb-bronze) !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(205, 127, 50, 0.8) !important;
    }

    @keyframes goldShimmer {
        0% { text-shadow: 0 0 10px rgba(255, 215, 0, 0.8); }
        100% { text-shadow: 0 0 20px rgba(255, 215, 0, 1), 0 0 30px rgba(255, 215, 0, 0.8); }
    }

    /* Chart Styling  */
    .stApp .vega-embed {
        background: var(--mlbb-card-bg) !important;
        border-radius: var(--mlbb-border-radius) !important;
        border: var(--mlbb-card-border) !important;
    }

    /* Battle Status */
    .stApp .battle-status {
        text-align: center !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        padding: 2rem !important;
        margin: 2rem 0 !important;
        border: 2px solid var(--mlbb-primary) !important;
        border-radius: var(--mlbb-border-radius) !important;
        background: var(--mlbb-card-bg) !important;
        box-shadow: var(--mlbb-glow) !important;
    }

    .stApp .countdown-text {
        font-size: 2.5rem !important;
        color: var(--mlbb-accent) !important;
        text-shadow: 0 0 20px rgba(255, 154, 139, 0.8) !important;
        animation: countdownPulse 1s ease-in-out infinite alternate !important;
    }

    @keyframes countdownPulse {
        0% { transform: scale(1); text-shadow: 0 0 20px rgba(255, 154, 139, 0.8); }
        100% { transform: scale(1.05); text-shadow: 0 0 30px rgba(255, 154, 139, 1); }
    }

    .stApp ::-webkit-scrollbar {
        width: 12px;
    }

    .stApp ::-webkit-scrollbar-track {
        background: var(--mlbb-darker);
        border-radius: 10px;
    }

    .stApp ::-webkit-scrollbar-thumb {
        background: var(--mlbb-gradient);
        border-radius: 10px;
        box-shadow: inset 0 0 5px rgba(255, 255, 255, 0.2);
    }

    .stApp ::-webkit-scrollbar-thumb:hover {
        background: var(--mlbb-primary);
    }

    .stApp .stMarkdown {
        text-align: center;
    }
    
    .stApp .stMarkdown h1, 
    .stApp .stMarkdown h2, 
    .stApp .stMarkdown h3 {
        text-align: center;
    }

    @media (max-width: 768px) {
        .stApp .main-title {
            font-size: 2.5rem;
        }
        
        .stApp .champion-name {
            font-size: 2.5rem !important;
        }
        
        .stApp .champion-medal {
            font-size: 4rem !important;
        }
        
        .stApp .stDataFrame th, 
        .stApp .stDataFrame td {
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Database Connection 
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123",
        database="gamifiedqc"
    )

def is_battle_started():
    today = date.today()
    return today.day >= 15

def calculate_elo_ratings():
    conn = get_db_connection()
    query = "SELECT * FROM submissions"
    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return pd.DataFrame()

    # Clean numeric inputs
    df["CV(%)"] = pd.to_numeric(df["CV(%)"], errors="coerce")
    df["Ratio"] = pd.to_numeric(df["Ratio"], errors="coerce")
    df = df.dropna(subset=["n(QC)", "Working_Days"])

    # Load or init rating buckets
    ratings = {}
    K = 32

    # Penalize missing submissions
    all_labs = df["Lab"].unique().tolist()
    all_params = df["Parameter"].unique().tolist()
    all_levels = df["Level"].unique().tolist()
    all_months = df["Month"].unique().tolist()

    expected_combinations = list(itertools.product(all_labs, all_params, all_levels, all_months))
    actual_submissions = set(tuple(row) for row in df[["Lab", "Parameter", "Level", "Month"]].drop_duplicates().to_numpy())

    for lab, param, level, month in expected_combinations:
        if (lab, param, level, month) not in actual_submissions:
            key = f"{lab}_{param}_{level}"
            if key not in ratings:
                ratings[key] = 1500
            ratings[key] -= 10  # Penalty for missing submission

    # Battle loop
    for (param, level, month), group in df.groupby(["Parameter", "Level", "Month"]):
        labs = group.to_dict("records")
        key_prefix = f"{param}_{level}"

        # Initialize ratings for labs in this group
        for lab in group["Lab"].unique():
            lab_key = f"{lab}_{key_prefix}"
            if lab_key not in ratings:
                ratings[lab_key] = 1500

        # All pairings
        for lab1, lab2 in itertools.combinations(labs, 2):
            labA, labB = lab1["Lab"], lab2["Lab"]
            cvA, cvB = lab1.get("CV(%)"), lab2.get("CV(%)")
            rA, rB = lab1.get("Ratio"), lab2.get("Ratio")

            labA_key = f"{labA}_{key_prefix}"
            labB_key = f"{labB}_{key_prefix}"

            # Penalties for missing values
            penalty_A = 10 if pd.isna(cvA) or pd.isna(rA) else 0
            penalty_B = 10 if pd.isna(cvB) or pd.isna(rB) else 0

            # CV score
            if pd.isna(cvA) and pd.isna(cvB):
                cv_score_A = cv_score_B = 0.5
            elif pd.isna(cvA):
                cv_score_A, cv_score_B = 0, 1
            elif pd.isna(cvB):
                cv_score_A, cv_score_B = 1, 0
            elif cvA < cvB:
                cv_score_A, cv_score_B = 1, 0
            elif cvA > cvB:
                cv_score_A, cv_score_B = 0, 1
            else:
                cv_score_A = cv_score_B = 0.5

            # Ratio metric
            if pd.isna(rA) and pd.isna(rB):
                ratio_score_A = ratio_score_B = 0.5
            elif pd.isna(rA):
                ratio_score_A, ratio_score_B = 0, 1
            elif pd.isna(rB):
                ratio_score_A, ratio_score_B = 1, 0
            elif abs(rA - 1.0) < abs(rB - 1.0):  # Closer to 1.0 wins
                ratio_score_A, ratio_score_B = 1, 0
            elif abs(rA - 1.0) > abs(rB - 1.0):
                ratio_score_A, ratio_score_B = 0, 1
            else:
                ratio_score_A = ratio_score_B = 0.5

            # Composite score (equal weighting)
            S_A = (cv_score_A + ratio_score_A) / 2
            S_B = (cv_score_B + ratio_score_B) / 2

            # ELO calculation
            Ra, Rb = ratings[labA_key], ratings[labB_key]
            Ea = 1 / (1 + 10 ** ((Rb - Ra) / 400))
            Eb = 1 / (1 + 10 ** ((Ra - Rb) / 400))

            ratings[labA_key] += K * (S_A - Ea)
            ratings[labB_key] += K * (S_B - Eb)

            ratings[labA_key] -= penalty_A
            ratings[labB_key] -= penalty_B

        # Apply CV + Ratio bonuses
        for lab in group["Lab"].unique():
            lab_key = f"{lab}_{key_prefix}"
            cv_value = group[group["Lab"] == lab]["CV(%)"].values[0]
            ratio_value = group[group["Lab"] == lab]["Ratio"].values[0]
            
            if not pd.isna(cv_value) and param in EFLM_TARGETS and cv_value <= EFLM_TARGETS[param]:
                ratings[lab_key] += 5
            
            if not pd.isna(ratio_value) and ratio_value == 1.0:
                ratings[lab_key] += 5

    # Aggregate per-lab final ELO
    lab_elos = {}
    lab_counts = {}
    for key, elo in ratings.items():
        parts = key.split("_")
        lab = "_".join(parts[:-2])
        lab_elos[lab] = lab_elos.get(lab, 0) + elo
        lab_counts[lab] = lab_counts.get(lab, 0) + 1

    summary_df = pd.DataFrame([{
        "Lab": lab,
        "Final Elo": round(lab_elos[lab] / lab_counts[lab], 2),
    } for lab in lab_elos]).sort_values(by="Final Elo", ascending=False).reset_index(drop=True)

    medals = ["🥇", "🥈", "🥉"]
    summary_df["Medal"] = ""
    for i in range(min(3, len(summary_df))):
        summary_df.loc[i, "Medal"] = medals[i]

    return summary_df

# Avatar names
def get_avatar_names():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, avatar FROM labs_users")
    rows = cursor.fetchall()
    conn.close()
    
    return {row['username']: row['avatar'] for row in rows}

def run():
    apply_mlbb_theme()
    apply_sidebar_theme()
    
    # Main title 
    st.markdown("""
    <div class="main-title">
        ⚔️ LLKK CHAMPION BOARD ⚔️
    </div>
    """, unsafe_allow_html=True)

    # Check if battle has started (after 15th of month)
    if not is_battle_started():
        today = date.today()
        days_left = 15 - today.day
        
        st.markdown("""
        <div class="battle-status">
            <h2>⏳ The Battle Arena is Sealed</h2>
            <p>The ancient battlegrounds remain locked until the 15th day of each moon cycle.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if today.day < 15:
            st.markdown(f"""
            <div class="countdown-text">
                🗓️ {days_left} days until the gates open...
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="countdown-text">
                ⚔️ The battle should commence today! Return soon, warrior!
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    st.markdown("""
    <div class="battle-status">
        <h2>🏆 The Battle Has Concluded!</h2>
        <p>Victory has been claimed and a new champion rises!</p>
    </div>
    """, unsafe_allow_html=True)
    
    avatar_map = get_avatar_names()
    elo_df = calculate_elo_ratings()

    if elo_df.empty:
        st.error("⚠️ The battle records are empty. Warriors must first register their deeds in the Data Entry realm.")
        return

    # Replace lab names with avatar names
    leaderboard_df = elo_df.copy()
    leaderboard_df["Avatar"] = leaderboard_df["Lab"].map(avatar_map)
    leaderboard_df = leaderboard_df[["Avatar", "Final Elo", "Medal"]]
    leaderboard_df = leaderboard_df.sort_values("Final Elo", ascending=False).reset_index(drop=True)

    # Add rank column
    leaderboard_df["Rank"] = leaderboard_df.index + 1
    leaderboard_df = leaderboard_df[["Rank", "Avatar", "Final Elo", "Medal"]]
    
    st.markdown("## 🏅 Hall of Champions")
    
    # Format the DataFrame for better display
    styled_df = leaderboard_df.style \
    .format({"Final Elo": "{:.2f}"}) \
    .set_properties(**{
        'background-color': 'rgba(15, 20, 40, 0.7)',
        'color': '#f8f9ff',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'text-align': 'center'
    }) \
    .set_table_styles([{
        'selector': 'th',
        'props': [('background', 'linear-gradient(135deg, #4a00e0 0%, #ff4d8d 100%)'),
                 ('color', 'white'),
                 ('font-family', "'Orbitron', monospace"),
                 ('font-weight', '700'),
                 ('text-transform', 'uppercase'),
                 ('text-align', 'center')]
    }])

    
    st.dataframe(styled_df, use_container_width=True, height=(len(leaderboard_df) + 1) * 35 + 3)

    # Champion announcement with enhanced styling
    champ_row = leaderboard_df.iloc[0]
    st.markdown(f"""
    <div class="champion-card">
        <h2>👑 CHAMPION OF THE REALM 👑</h2>
        <div class="champion-name">{champ_row['Avatar']}</div>
        <div class="champion-elo">Final Elo Rating: {champ_row['Final Elo']:.2f}</div>
        <div class="champion-medal">{champ_row['Medal']}</div>
        <p style="font-family: 'Cinzel', serif; font-size: 1.5rem; margin-top: 2rem; color: var(--mlbb-light);">
            Glory eternal! The realm bows to your supremacy!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ELO progression chart with MLBB styling
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SHOW TABLES LIKE 'battle_logs'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        prog_df = pd.read_sql("SELECT * FROM battle_logs ORDER BY id", conn)
        conn.close()

        if not prog_df.empty:
            st.markdown("## 📈 Warrior's Journey")
            # Create mapping for dropdown - show avatar names but store lab names
            lab_options = {}
            for lab in set(prog_df["lab_a"]).union(set(prog_df["lab_b"])):
                lab_options[avatar_map.get(lab, lab)] = lab
            
            selected_avatar = st.selectbox("Select Avatar", list(lab_options.keys()))
            selected_lab = lab_options[selected_avatar]
            
            # Melt both labs A/B into one long df
            prog_long = pd.concat([
                prog_df[["id", "lab_a", "updated_rating_a"]].rename(
                    columns={"lab_a": "Lab", "updated_rating_a": "Elo"}
                ),
                prog_df[["id", "lab_b", "updated_rating_b"]].rename(
                    columns={"lab_b": "Lab", "updated_rating_b": "Elo"}
                )
            ])
            prog_long["Battle"] = prog_long["id"]
            
            filtered = prog_long[prog_long["Lab"] == selected_lab]
            
            if not filtered.empty:
                # Replace lab name with avatar name in chart title
                chart = alt.Chart(filtered).mark_line(point=True).encode(
                    x=alt.X("Battle:O", title="Battle Number"),
                    y=alt.Y("Elo:Q", title="Elo Score"),
                    tooltip=["Battle", "Elo"]
                ).properties(
                    title=f"{selected_avatar} — Elo Progression",
                    width=700,
                    height=400
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("ℹ️ No rating data available for this avatar.")
    else:
        conn.close()
        st.info("ℹ️ No battle logs available yet.")

if __name__ == "__main__":
    run()
import streamlit as st
from constants import TOURNAMENT_NAME
from stages.stage1_setup import render_stage1
from stages.stage2_groups import render_stage2
from stages.stage3_super7 import render_stage3
from stages.stage4_knockouts import render_stage4

# ==============================================================================
# 2. STREAMLIT APPLICATION
# ==============================================================================

st.set_page_config(page_title=f"{TOURNAMENT_NAME}", layout="wide")
st.title(f"🏆 {TOURNAMENT_NAME} Simulator")
st.caption("Official 12-Team Main Stage | Super 7 Format | Dynamic DLS Modal & Clause 16.10 NRR")



# Initialize Session State
if "stage" not in st.session_state:
    st.session_state.stage = "SETUP"
    st.session_state.group_a_teams = []
    st.session_state.group_b_teams = []
    st.session_state.stats_a = {}
    st.session_state.stats_b = {}
    st.session_state.fixtures = []
    st.session_state.current_match_idx = 0
    st.session_state.super7_teams = []
    st.session_state.super7_stats = {}
    st.session_state.super7_fixtures = []
    st.session_state.super7_match_idx = 0
    st.session_state.sf1_winner = None
    st.session_state.sf2_winner = None
    st.session_state.champion = None




if st.session_state.stage == "SETUP":
    render_stage1()

elif st.session_state.stage == "GROUP_STAGE":
    render_stage2()

elif st.session_state.stage == "SUPER_7":
    render_stage3()

elif st.session_state.stage == "KNOCKOUTS":
    render_stage4()

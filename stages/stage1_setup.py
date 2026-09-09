import streamlit as st
import random
from constants import QUALIFIER_SEEDS, CORE_TEAMS_GROUP_A, CORE_TEAMS_GROUP_B
from helpers import init_team_stats

def render_stage1():
    st.subheader("Step 1: Select 2 Final Qualifiers")
    st.info("Pick 2 teams. Pre-seeded 'A' teams take Group A, 'B' takes Group B. If both share the same seed, a draw determines placement.")

    qualifier_names = list(QUALIFIER_SEEDS.keys())
    col1, col2 = st.columns(2)
    with col1:
        q1 = st.selectbox("Qualifier 1", qualifier_names, index=0)
    with col2:
        remaining = [q for q in qualifier_names if q != q1]
        q2 = st.selectbox("Qualifier 2", remaining, index=3)

    if st.button("Confirm Teams & Build Groups", type="primary"):
        s1, s2 = QUALIFIER_SEEDS[q1], QUALIFIER_SEEDS[q2]
        if s1 != s2:
            team_a = q1 if s1 == "A" else q2
            team_b = q2 if s1 == "A" else q1
        else:
            shuffled = [q1, q2]
            random.shuffle(shuffled)
            team_a, team_b = shuffled[0], shuffled[1]
            st.toast(f"Both pre-seeded to {s1}! Draw placed {team_a} in Group A and {team_b} in Group B.")

        st.session_state.group_a_teams = CORE_TEAMS_GROUP_A + [team_a]
        st.session_state.group_b_teams = CORE_TEAMS_GROUP_B + [team_b]
        st.session_state.stats_a = init_team_stats(st.session_state.group_a_teams)
        st.session_state.stats_b = init_team_stats(st.session_state.group_b_teams)

        fixtures = []
        for i in range(len(st.session_state.group_a_teams)):
            for j in range(i + 1, len(st.session_state.group_a_teams)):
                fixtures.append(("Group A", st.session_state.group_a_teams[i], st.session_state.group_a_teams[j]))
        for i in range(len(st.session_state.group_b_teams)):
            for j in range(i + 1, len(st.session_state.group_b_teams)):
                fixtures.append(("Group B", st.session_state.group_b_teams[i], st.session_state.group_b_teams[j]))
        random.shuffle(fixtures)

        st.session_state.fixtures = fixtures
        st.session_state.stage = "GROUP_STAGE"
        st.rerun()
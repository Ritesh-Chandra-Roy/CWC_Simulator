import streamlit as st
from constants import SUPER_7_SEMIFINAL_QUALIFIERS
from helpers import get_standings_df

def render_stage4():
    df_s7 = get_standings_df(st.session_state.super7_stats)
    top4 = df_s7.iloc[:SUPER_7_SEMIFINAL_QUALIFIERS]["Team"].tolist()

    st.subheader("⚡ ICC CWC 2027 Knockout Bracket")
    sf1_t1, sf1_t2 = top4[0], top4[3]
    sf2_t1, sf2_t2 = top4[1], top4[2]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Semi-Final 1:** {sf1_t1} (1st) vs {sf1_t2} (4th)")
        if st.session_state.sf1_winner is None:
            w1 = st.selectbox("Select SF1 Winner", [sf1_t1, sf1_t2])
            if st.button("Confirm SF1 Result"):
                st.session_state.sf1_winner = w1
                st.rerun()
        else:
            st.success(f"Finalist: **{st.session_state.sf1_winner}**")

    with col2:
        st.markdown(f"**Semi-Final 2:** {sf2_t1} (2nd) vs {sf2_t2} (3rd)")
        if st.session_state.sf2_winner is None:
            w2 = st.selectbox("Select SF2 Winner", [sf2_t1, sf2_t2])
            if st.button("Confirm SF2 Result"):
                st.session_state.sf2_winner = w2
                st.rerun()
        else:
            st.success(f"Finalist: **{st.session_state.sf2_winner}**")

    if st.session_state.sf1_winner and st.session_state.sf2_winner:
        st.divider()
        f1, f2 = st.session_state.sf1_winner, st.session_state.sf2_winner
        st.markdown(f"## 🏆 The Grand Final: {f1} vs {f2}")

        if st.session_state.champion is None:
            champ = st.radio("Tournament Winner", [f1, f2], horizontal=True)
            if st.button("Crown World Champion!", type="primary"):
                st.session_state.champion = champ
                st.rerun()
        else:
            st.balloons()
            st.success(f"🎉 **{st.session_state.champion} ARE THE ICC CRICKET WORLD CUP 2027 CHAMPIONS!** 🎉")
            if st.button("Start New Tournament"):
                st.session_state.clear()
                st.rerun()
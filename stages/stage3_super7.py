import streamlit as st
from constants import SUPER_7_SEMIFINAL_QUALIFIERS
from helpers import get_standings_df, style_standings_table, update_table_stats
from dls_calculator import open_dls_dialog

def render_stage3():
    idx = st.session_state.super7_match_idx
    total_matches = len(st.session_state.super7_fixtures)

    st.markdown("### 🌟 Super 7 Points Table")
    df_s7 = get_standings_df(st.session_state.super7_stats)
    st.dataframe(style_standings_table(df_s7, qualify_cutoff=SUPER_7_SEMIFINAL_QUALIFIERS), use_container_width=True)

    st.divider()

    if idx < total_matches:
        grp, t1, t2 = st.session_state.super7_fixtures[idx]
        st.subheader(f"Super 7 Match {idx + 1} of {total_matches}: {t1} vs {t2}")

        match_key = f"s7_{idx}"
        widget_prefix = f"s7_{idx}"
        dls_data = st.session_state.get(f"dls_info_{match_key}", None)

        with st.container(border=True):
            c1, c2, c_rain = st.columns([2, 2, 2])
            with c1:
                toss_winner = st.radio("Toss Winner", [t1, t2], horizontal=True, key=f"s7_tw_{idx}")
            with c2:
                decision = st.radio(f"{toss_winner} Decided To", ["Bat", "Bowl"], horizontal=True, key=f"s7_td_{idx}")

            batting_first = toss_winner if decision == "Bat" else (t2 if toss_winner == t1 else t1)
            batting_second = t2 if batting_first == t1 else t1

            with c_rain:
                st.markdown("**Weather Delay / Rain?**")
                if st.button("🌧️ Open DLS Calculator", key=f"s7_dls_btn_{idx}"):
                    open_dls_dialog(batting_first, batting_second, match_key=match_key, widget_prefix=widget_prefix)

        st.info(f"🏏 **{batting_first}** batting 1st | 🎯 **{batting_second}** chasing")

        if dls_data and dls_data.get("is_dls"):
            c_banner, c_reset = st.columns([5, 1])
            with c_banner:
                st.warning(f"🌧️ **DLS APPLIED:** {dls_data['summary']}")
            with c_reset:
                if st.button("Reset DLS", key=f"s7_reset_dls_{idx}"):
                    del st.session_state[f"dls_info_{match_key}"]
                    for k in [f"{widget_prefix}_s1r", f"{widget_prefix}_s1o", f"{widget_prefix}_s2r", f"{widget_prefix}_s2o", f"{widget_prefix}_s2w"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()

        o1_max_val = float(dls_data["o1_max"]) if dls_data else 50.0
        o2_max_val = float(dls_data["o2_max"]) if dls_data else 50.0

        if f"{widget_prefix}_s1r" not in st.session_state:
            st.session_state[f"{widget_prefix}_s1r"] = 290
        if f"{widget_prefix}_s1o" not in st.session_state:
            st.session_state[f"{widget_prefix}_s1o"] = float(o1_max_val)
        if f"{widget_prefix}_s2r" not in st.session_state:
            st.session_state[f"{widget_prefix}_s2r"] = 280
        if f"{widget_prefix}_s2o" not in st.session_state:
            st.session_state[f"{widget_prefix}_s2o"] = float(o2_max_val)
        if f"{widget_prefix}_s2w" not in st.session_state:
            st.session_state[f"{widget_prefix}_s2w"] = 4

        with st.form(key=f"s7_score_form_{idx}"):
            st.markdown(f"#### 1st Innings: {batting_first} ({int(o1_max_val)} ov)")
            col1, col2, col3 = st.columns(3)
            with col1:
                s1_runs = st.number_input("Runs Scored", min_value=0, max_value=500, key=f"{widget_prefix}_s1r")
            with col2:
                s1_wkts = st.number_input("Wickets Lost", min_value=0, max_value=10, value=7, key=f"{widget_prefix}_s1w")
            with col3:
                s1_overs = st.number_input("Overs Faced", min_value=1.0, max_value=50.0, step=0.1, key=f"{widget_prefix}_s1o")

            if dls_data and dls_data.get("is_dls"):
                target = int(dls_data["target"])
                st.warning(f"🎯 **Revised Target:** **{target} runs** in {round(o2_max_val, 1)} overs (Par: {dls_data['par']})")
            else:
                target = s1_runs + 1
                st.info(f"🎯 **Target:** **{target} runs** in {int(o2_max_val)} overs")

            st.markdown(f"#### 2nd Innings: {batting_second} ({int(o2_max_val)} ov)")
            col4, col5, col6 = st.columns(3)
            with col4:
                s2_runs = st.number_input("Runs Scored", min_value=0, max_value=500, key=f"{widget_prefix}_s2r")
            with col5:
                s2_wkts = st.number_input("Wickets Lost", min_value=0, max_value=10, key=f"{widget_prefix}_s2w")
            with col6:
                s2_overs = st.number_input("Overs Faced", min_value=1.0, max_value=50.0, step=0.1, key=f"{widget_prefix}_s2o")

            submitted = st.form_submit_button("Record Match Result", type="primary")
            if submitted:
                is_dls = bool(dls_data and dls_data.get("is_dls"))

                if s2_runs >= target:
                    winner = batting_second
                    result_str = f"{batting_second} won by {10 - s2_wkts} wickets"
                elif s2_runs == target - 1:
                    winner = "TIE"
                    result_str = "Match Tied"
                else:
                    winner = batting_first
                    runs_diff = (target - 1) - s2_runs
                    result_str = f"{batting_first} won by {runs_diff} runs" + (" (DLS Method)" if is_dls else "")

                update_table_stats(
                    st.session_state.super7_stats,
                    batting_first, batting_second,
                    s1_runs, s1_wkts, s1_overs, o1_max_val,
                    s2_runs, s2_wkts, s2_overs, o2_max_val,
                    winner,
                    is_dls=is_dls,
                    dls_target=target if is_dls else None
                )
                st.toast(f"Result: {result_str}!")
                st.session_state.super7_match_idx += 1
                st.rerun()

    else:
        st.success("Super 7 Stage Completed!")
        if st.button("Proceed to Knockout Semifinals", type="primary"):
            st.session_state.stage = "KNOCKOUTS"
            st.rerun()
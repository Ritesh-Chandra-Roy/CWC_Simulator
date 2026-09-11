import streamlit as st
import random
from constants import GROUP_STAGE_DIRECT_QUALIFIERS, GROUP_STAGE_WILDCARD_POS
from helpers import get_standings_df, style_standings_table, update_table_stats, init_team_stats
from dls_calculator import open_dls_dialog

def render_stage2():
    idx = st.session_state.current_match_idx
    total_matches = len(st.session_state.fixtures)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📋 Pool A Standings")
        df_a = get_standings_df(st.session_state.stats_a)
        st.dataframe(style_standings_table(df_a, qualify_cutoff=GROUP_STAGE_DIRECT_QUALIFIERS, wildcard_pos=GROUP_STAGE_WILDCARD_POS), use_container_width=True)
    with col_b:
        st.markdown("### 📋 Pool B Standings")
        df_b = get_standings_df(st.session_state.stats_b)
        st.dataframe(style_standings_table(df_b, qualify_cutoff=GROUP_STAGE_DIRECT_QUALIFIERS, wildcard_pos=GROUP_STAGE_WILDCARD_POS    ), use_container_width=True)

    st.divider()

    if idx < total_matches:
        grp, t1, t2 = st.session_state.fixtures[idx]
        st.subheader(f"Match {idx + 1} of {total_matches}: {t1} vs {t2} ({grp})")

        match_key = f"grp_{idx}"
        widget_prefix = f"grp_{idx}"
        dls_data = st.session_state.get(f"dls_info_{match_key}", None)

        # 1. Live Toss & DLS Trigger
        with st.container(border=True):
            c_toss1, c_toss2, c_rain = st.columns([2, 2, 2])
            with c_toss1:
                toss_winner = st.radio("Toss Winner", [t1, t2], horizontal=True, key=f"tw_{idx}")
            with c_toss2:
                decision = st.radio(f"{toss_winner} Decided To", ["Bat", "Bowl"], horizontal=True, key=f"td_{idx}")

            batting_first = toss_winner if decision == "Bat" else (t2 if toss_winner == t1 else t1)
            batting_second = t2 if batting_first == t1 else t1

            with c_rain:
                st.markdown("**Weather Delay / Rain?**")
                if st.button("🌧️ Open DLS Calculator", key=f"dls_btn_{idx}"):
                    open_dls_dialog(batting_first, batting_second, match_key=match_key, widget_prefix=widget_prefix)

        st.info(f"🏏 **{batting_first}** batting 1st | 🎯 **{batting_second}** chasing")

        # DLS Active Banner & Reset
        if dls_data and dls_data.get("is_dls"):
            c_banner, c_reset = st.columns([5, 1])
            with c_banner:
                st.warning(f"🌧️ **DLS APPLIED:** {dls_data['summary']}")
            with c_reset:
                if st.button("Reset DLS", key=f"reset_dls_{idx}"):
                    del st.session_state[f"dls_info_{match_key}"]
                    for k in [f"{widget_prefix}_s1r", f"{widget_prefix}_s1o", f"{widget_prefix}_s2r", f"{widget_prefix}_s2o", f"{widget_prefix}_s2w"]:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.rerun()

        o1_max_val = float(dls_data["o1_max"]) if dls_data else 50.0
        o2_max_val = float(dls_data["o2_max"]) if dls_data else 50.0

        # Initialize widget default states if not yet set
        if f"{widget_prefix}_s1r" not in st.session_state:
            st.session_state[f"{widget_prefix}_s1r"] = 280
        if f"{widget_prefix}_s1o" not in st.session_state:
            st.session_state[f"{widget_prefix}_s1o"] = float(o1_max_val)
        if f"{widget_prefix}_s2r" not in st.session_state:
            st.session_state[f"{widget_prefix}_s2r"] = 265
        if f"{widget_prefix}_s2o" not in st.session_state:
            st.session_state[f"{widget_prefix}_s2o"] = float(o2_max_val)
        if f"{widget_prefix}_s2w" not in st.session_state:
            st.session_state[f"{widget_prefix}_s2w"] = 4

        # 2. Scorecard Form
        with st.form(key=f"score_form_{idx}"):
            st.markdown(f"#### 1st Innings: {batting_first} ({int(o1_max_val)} ov)")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                s1_runs = st.number_input(f"{batting_first} Runs", min_value=0, max_value=500, key=f"{widget_prefix}_s1r")
            with sc2:
                s1_wkts = st.number_input(f"{batting_first} Wickets Lost", min_value=0, max_value=10, value=8, key=f"{widget_prefix}_s1w")
            with sc3:
                s1_overs = st.number_input(f"{batting_first} Overs Batted", min_value=1.0, max_value=50.0, step=0.1, key=f"{widget_prefix}_s1o")

            # Target Resolution
            if dls_data and dls_data.get("is_dls"):
                target = int(dls_data["target"])
                st.warning(f"🎯 **Revised Target:** **{target} runs** in {round(o2_max_val, 1)} overs (Par: {dls_data['par']})")
            else:
                target = s1_runs + 1
                st.info(f"🎯 **Target:** **{target} runs** in {int(o2_max_val)} overs")

            st.markdown(f"#### 2nd Innings: {batting_second} ({int(o2_max_val)} ov)")
            sc4, sc5, sc6 = st.columns(3)
            with sc4:
                s2_runs = st.number_input(f"{batting_second} Runs", min_value=0, max_value=500, key=f"{widget_prefix}_s2r")
            with sc5:
                s2_wkts = st.number_input(f"{batting_second} Wickets Lost", min_value=0, max_value=10, key=f"{widget_prefix}_s2w")
            with sc6:
                s2_overs = st.number_input(f"{batting_second} Overs Batted", min_value=1.0, max_value=50.0, step=0.1, key=f"{widget_prefix}_s2o")

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

                target_stats = st.session_state.stats_a if grp == "Group A" else st.session_state.stats_b
                update_table_stats(
                    target_stats,
                    batting_first, batting_second,
                    s1_runs, s1_wkts, s1_overs, o1_max_val,
                    s2_runs, s2_wkts, s2_overs, o2_max_val,
                    winner,
                    is_dls=is_dls,
                    dls_target=target if is_dls else None
                )
                if grp == "Group A":
                    st.session_state.stats_a = dict(target_stats)
                else:
                    st.session_state.stats_b = dict(target_stats)
                st.toast(f"Result: {result_str}!")
                st.session_state.current_match_idx += 1
                st.rerun()

    else:
        st.success("Group Stage Completed!")
        df_a = get_standings_df(st.session_state.stats_a)
        df_b = get_standings_df(st.session_state.stats_b)

        top3_a = df_a.iloc[:GROUP_STAGE_DIRECT_QUALIFIERS]["Team"].tolist()
        top3_b = df_b.iloc[:GROUP_STAGE_DIRECT_QUALIFIERS]["Team"].tolist()
        fourth_a = str(df_a.iloc[GROUP_STAGE_DIRECT_QUALIFIERS]["Team"])
        fourth_b = str(df_b.iloc[GROUP_STAGE_DIRECT_QUALIFIERS]["Team"])

        st_4a = st.session_state.stats_a[fourth_a]
        st_4b = st.session_state.stats_b[fourth_b]

        st.markdown("### 🔍 4th-Place Wildcard Tiebreaker")
        w_col1, w_col2 = st.columns(2)
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            st.metric(f"Group A 4th: {fourth_a}", f"{st_4a['Pts']} Pts", f"NRR: {st_4a['NRR']:+.3f}")
        with w_col2:
            st.metric(f"Group B 4th: {fourth_b}", f"{st_4b['Pts']} Pts", f"NRR: {st_4b['NRR']:+.3f}")

        metric_a = (st_4a['Pts'], st_4a['W'], float(st_4a['NRR']))
        metric_b = (st_4b['Pts'], st_4b['W'], float(st_4b['NRR']))
        wildcard = fourth_a if metric_a > metric_b else fourth_b

        st.info(f"🎉 **{wildcard}** advances to the Super 7 as the best 4th-placed side!")

        if st.button("Proceed to Super 7 Stage", type="primary"):
            st.session_state.super7_teams = top3_a + top3_b + [wildcard]
            st.session_state.super7_stats = init_team_stats(st.session_state.super7_teams)

            s7_fix = []
            for i in range(len(st.session_state.super7_teams)):
                for j in range(i + 1, len(st.session_state.super7_teams)):
                    s7_fix.append(("Super 7", st.session_state.super7_teams[i], st.session_state.super7_teams[j]))
            random.shuffle(s7_fix)

            st.session_state.super7_fixtures = s7_fix
            st.session_state.stage = "SUPER_7"
            st.rerun()

import streamlit as st
import math
from constants import DLS_G50, DLS_B_COEFFS, MAX_RESOURCE_AT_50, MIN_OVERS_FOR_RESULT

def get_dls_resource(overs_remaining, wickets_lost):
    """Returns resource percentage remaining for given overs left and wickets lost (0-9)."""
    if overs_remaining <= 0 or wickets_lost >= 10:
        return 0.0
    overs_remaining = min(50.0, float(overs_remaining))
    w = max(0, min(9, int(wickets_lost)))

    b = DLS_B_COEFFS[w]
    max_50_norm = 1.0 - math.exp(-DLS_B_COEFFS[0] * 50.0)
    raw_res = 1.0 - math.exp(-b * overs_remaining)

    scale_factor = MAX_RESOURCE_AT_50[w] / 100.0
    res = 100.0 * scale_factor * (raw_res / max_50_norm)
    return min(100.0, max(0.0, res))

def compute_dls(s1, r1, r2):
    """Computes final revised target given Team 1 score (s1) and resources (r1, r2)."""
    if r2 < r1:
        par_score = s1 * (r2 / r1)
        target = math.floor(par_score) + 1
    elif r2 > r1:
        target = math.floor(s1 + ((r2 - r1) / 100.0) * DLS_G50) + 1
        par_score = target - 1
    else:
        target = s1 + 1
        par_score = s1
    return int(max(1, target)), round(par_score, 1)

def apply_dls_payload(match_key, widget_prefix, dls_dict, s1, o1, s2, o2, w2=None):
    st.session_state[f"dls_info_{match_key}"] = dls_dict
    st.session_state[f"{widget_prefix}_s1r"] = int(s1)
    st.session_state[f"{widget_prefix}_s1o"] = float(o1)
    st.session_state[f"{widget_prefix}_s2r"] = int(s2)
    st.session_state[f"{widget_prefix}_s2o"] = float(o2)
    if w2 is not None:
        st.session_state[f"{widget_prefix}_s2w"] = int(w2)

@st.dialog("🌧️ Duckworth-Lewis-Stern (DLS) Calculator", width="large")
def open_dls_dialog(team1_name, team2_name, match_key="default", widget_prefix="grp_0"):
    st.markdown(f"**Match:** {team1_name} (1st Innings) vs {team2_name} (2nd Innings)")

    with st.container(border=True):
        st.markdown("##### ⏱️ Match Scheduled Baseline")
        o_start = st.number_input(
            "Overs Per Side Scheduled at Match Start / Toss",
            min_value=20.0, max_value=50.0, value=50.0, step=1.0,
            help="Default is 50. If rain delayed the toss/match start, enter the reduced initial overs."
        )
    
    r_start = get_dls_resource(o_start, 0)
    min_cut = min(float(MIN_OVERS_FOR_RESULT), float(o_start))

    interruption_type = st.selectbox(
        "Select Interruption Scenario:",
        [
            "Team 2 innings delayed (Start delayed, overs reduced)",
            "Team 2 innings interrupted (Stoppage during chase, resumes with fewer overs)",
            "Team 2 innings cut short (Match abandoned during chase, Par score applied)",
            "Team 1 innings interrupted (Stoppage during 1st innings, resumes with fewer overs)",
            "Team 1 innings cut short (1st innings terminated prematurely)",
            "Both innings interrupted / reduced (Compound Stoppage)",
            "Innings interrupted AND subsequently cut short (Multiple Stoppages)"
        ]
    )
    
    st.divider()

    # 1. Team 2 Innings Delayed
    if "Team 2 innings delayed" in interruption_type:
        st.info(f"{team1_name} completed allocated {int(o_start)} overs. {team2_name}'s chase is delayed and reduced.")
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.number_input(f"{team1_name} Final Score (Runs)", min_value=1, max_value=500, value=280)
        with c2:
            default_o2 = min(30.0, float(o_start))
            o2_quota = st.number_input(
                f"{team2_name} Revised Overs Available for Chase", 
                min_value=min_cut, max_value=float(o_start), value=default_o2, step=1.0
            )

        if st.button("Calculate & Apply Target", type="primary"):
            r1 = r_start
            r2 = get_dls_resource(o2_quota, 0)
            target, par = compute_dls(s1, r1, r2)

            dls_dict = {
                "is_dls": True, "target": target, "par": par,
                "o1_max": o_start, "o2_max": o2_quota, "s1": s1,
                "is_abandoned": False,
                "summary": f"Target: {target} in {int(o2_quota)} ov (T1 had {int(o_start)} ov, Par: {par})"
            }
            apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=o_start, s2=target, o2=o2_quota)
            st.rerun()

    # 2. Team 2 Innings Interrupted
    elif "Team 2 innings interrupted" in interruption_type:
        st.info(f"{team1_name} completed {int(o_start)} overs. Rain stops play during {team2_name}'s chase, resuming with fewer overs.")
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.number_input(f"{team1_name} Final Score (Runs)", min_value=1, max_value=500, value=275)
            default_rem = min(20.0, max(1.0, float(o_start) - 10.0))
            o_rem_before = st.number_input(f"{team2_name} Overs Remaining at Stoppage", min_value=1.0, max_value=float(o_start), value=default_rem, step=0.1)
        with c2:
            wkts = st.number_input(f"{team2_name} Wickets Lost at Stoppage", min_value=0, max_value=9, value=2)
            default_after = min(12.0, float(o_rem_before))
            o_rem_after = st.number_input(f"{team2_name} Overs Remaining after Stoppage", min_value=0.0, max_value=float(o_rem_before), value=default_after, step=0.1)
            overs_bowled = o_start - o_rem_before
            o2_new = overs_bowled + o_rem_after

        if st.button("Calculate & Apply Target", type="primary"):
            r1 = r_start
            res_lost = get_dls_resource(o_rem_before, wkts) - get_dls_resource(o_rem_after, wkts)
            r2 = max(0.0, r_start - res_lost)
            target, par = compute_dls(s1, r1, r2)

            dls_dict = {
                "is_dls": True, "target": target, "par": par,
                "o1_max": o_start, "o2_max": o2_new, "s1": s1,
                "is_abandoned": False,
                "summary": f"Target: {target} in {round(o2_new, 1)} ov (Par: {par})"
            }
            apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=o_start, s2=target, o2=o2_new)
            st.rerun()

    # 3. Team 2 Innings Cut Short (FIXED CRASH HERE)
    elif "Team 2 innings cut short" in interruption_type:
        st.info(f"{team2_name}'s chase terminated early due to weather. Match settled via DLS Par Score.")
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.number_input(f"{team1_name} Final Score (Runs)", min_value=1, max_value=500, value=260)
            s2 = st.number_input(f"{team2_name} Runs at Stoppage", min_value=0, max_value=500, value=150)
        with c2:
            # Clamped safely to o_start: min(30.0, o_start) ensures value <= max_value
            safe_default_o2 = min(30.0, float(o_start))
            o2_bowled = st.number_input(
                f"{team2_name} Overs Bowled (min 20 for result)", 
                min_value=min_cut, 
                max_value=float(o_start), 
                value=max(min_cut, safe_default_o2), 
                step=0.1
            )
            w2 = st.number_input(f"{team2_name} Wickets Lost at Stoppage", min_value=0, max_value=9, value=3)

        if st.button("Calculate Par Score & Settle Match", type="primary"):
            r1 = r_start
            overs_left = o_start - o2_bowled
            res_used_team2 = r_start - get_dls_resource(overs_left, w2)
            target, par = compute_dls(s1, r1, res_used_team2)

            dls_dict = {
                "is_dls": True, "target": target, "par": par,
                "o1_max": o_start, "o2_max": o2_bowled, "s1": s1,
                "s2_actual": s2, "w2_actual": w2, "o2_actual": o2_bowled,
                "is_abandoned": True,
                "summary": f"Match Terminated: Par was {par} at {o2_bowled} ov. Target: {target}"
            }
            apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=o_start, s2=s2, o2=o2_bowled, w2=w2)
            st.rerun()

    # 4. Team 1 Innings Interrupted
    elif "Team 1 innings interrupted" in interruption_type:
        st.info(f"Rain interrupted {team1_name}'s innings. Both teams have total overs reduced.")
        c1, c2 = st.columns(2)
        with c1:
            default_rem = min(20.0, max(1.0, float(o_start) - 10.0))
            o_rem_before = st.number_input(f"{team1_name} Overs Left at Stoppage", min_value=1.0, max_value=float(o_start), value=default_rem, step=0.1)
            w1 = st.number_input(f"{team1_name} Wickets Lost at Stoppage", min_value=0, max_value=9, value=2)
            default_after = min(12.0, float(o_rem_before))
            o_rem_after = st.number_input(f"{team1_name} Overs Left after Restart", min_value=0.0, max_value=float(o_rem_before), value=default_after, step=0.1)
        with c2:
            s1 = st.number_input(f"{team1_name} Final Score Scored", min_value=1, max_value=500, value=240)
            overs_lost = o_rem_before - o_rem_after
            total_revised_overs = o_start - overs_lost
            st.write(f"Revised Quota for both teams: **{total_revised_overs} overs**")

        if st.button("Calculate & Apply Target", type="primary"):
            res_lost_team1 = get_dls_resource(o_rem_before, w1) - get_dls_resource(o_rem_after, w1)
            r1 = max(0.0, r_start - res_lost_team1)
            r2 = get_dls_resource(total_revised_overs, 0)
            target, par = compute_dls(s1, r1, r2)

            dls_dict = {
                "is_dls": True, "target": target, "par": par,
                "o1_max": total_revised_overs, "o2_max": total_revised_overs, "s1": s1,
                "is_abandoned": False,
                "summary": f"Target: {target} in {int(total_revised_overs)} ov (Par: {par})"
            }
            apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=total_revised_overs, s2=target, o2=total_revised_overs)
            st.rerun()

    # 5. Team 1 Innings Cut Short
    elif "Team 1 innings cut short" in interruption_type:
        st.info(f"{team1_name}'s innings terminated early. {team2_name} chases a revised target in available quota.")
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.number_input(f"{team1_name} Score at Termination", min_value=1, max_value=500, value=210)
            default_batted = min(35.0, max(min_cut, float(o_start) - 2.0))
            o1_batted = st.number_input(f"{team1_name} Overs Batted", min_value=min_cut, max_value=float(o_start), value=default_batted, step=0.1)
            w1 = st.number_input(f"{team1_name} Wickets Lost", min_value=0, max_value=9, value=4)
        with c2:
            default_quota = min(float(o1_batted), float(o_start))
            o2_quota = st.number_input(f"{team2_name} Available Overs for Chase", min_value=min_cut, max_value=float(o_start), value=default_quota, step=1.0)

        if st.button("Calculate & Apply Target", type="primary"):
            overs_lost_t1 = o_start - o1_batted
            r1 = max(0.0, r_start - get_dls_resource(overs_lost_t1, w1))
            r2 = get_dls_resource(o2_quota, 0)
            target, par = compute_dls(s1, r1, r2)

            dls_dict = {
                "is_dls": True, "target": target, "par": par,
                "o1_max": o1_batted, "o2_max": o2_quota, "s1": s1,
                "is_abandoned": False,
                "summary": f"Target: {target} in {int(o2_quota)} ov (Par: {par})"
            }
            apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=o1_batted, s2=target, o2=o2_quota)
            st.rerun()

    # 6. Compound Stoppage (Both Innings Reduced)
    elif "Both innings interrupted / reduced" in interruption_type:
        st.info("Both teams experienced rain interruptions relative to the initial match scheduled overs.")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"**{team1_name} (1st Innings)**")
            s1 = st.number_input(f"{team1_name} Runs Scored", min_value=1, max_value=500, value=220, key="c_s1")
            default_c_o1 = min(38.0, max(min_cut, float(o_start) - 2.0))
            o1_batted = st.number_input(f"{team1_name} Overs Batted Before Cut-off", min_value=min_cut, max_value=float(o_start), value=default_c_o1, step=0.1, key="c_o1")
            w1_lost = st.number_input(f"{team1_name} Wickets Lost at Cut-off", min_value=0, max_value=9, value=4, key="c_w1")

        with col_t2:
            st.markdown(f"**{team2_name} (2nd Innings)**")
            default_c_o2 = min(28.0, float(o1_batted))
            o2_quota = st.number_input(f"{team2_name} Available Chase Quota", min_value=min_cut, max_value=float(o1_batted), value=max(min_cut, default_c_o2), step=1.0, key="c_o2")
            mid_chase = st.checkbox("Did Team 2 also experience a stoppage during chase?")
            w2_lost = 0
            o_rem_before = 0.0
            o_rem_after = 0.0
            if mid_chase:
                o_rem_before = st.number_input("Overs left when 2nd stoppage occurred", min_value=1.0, max_value=float(o2_quota), value=min(10.0, float(o2_quota)), step=0.1)
                w2_lost = st.number_input("Wickets lost at 2nd stoppage", min_value=0, max_value=9, value=2)
                o_rem_after = st.number_input("Overs left after 2nd restart", min_value=0.0, max_value=float(o_rem_before), value=min(5.0, float(o_rem_before)), step=0.1)

        if st.button("Calculate & Apply Compound Target", type="primary"):
            overs_lost_t1 = o_start - o1_batted
            r1 = max(0.0, r_start - get_dls_resource(overs_lost_t1, w1_lost))

            if not mid_chase:
                r2 = get_dls_resource(o2_quota, 0)
                final_o2 = o2_quota
            else:
                loss = get_dls_resource(o_rem_before, w2_lost) - get_dls_resource(o_rem_after, w2_lost)
                r2_base = get_dls_resource(o2_quota, 0)
                r2 = max(0.0, r2_base - loss)
                final_o2 = o2_quota - (o_rem_before - o_rem_after)

            target, par = compute_dls(s1, r1, r2)

            dls_dict = {
                "is_dls": True, "target": target, "par": par,
                "o1_max": o1_batted, "o2_max": final_o2, "s1": s1,
                "is_abandoned": False,
                "summary": f"Compound DLS: Target {target} in {round(final_o2, 1)} ov (Base: {int(o_start)} ov, Par: {par})"
            }
            apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=o1_batted, s2=target, o2=final_o2)
            st.rerun()

    # 7. Multiple Stoppages
    elif "Innings interrupted AND subsequently cut short" in interruption_type:
        st.info("Covers an innings that had a rain delay, resumed play, and was later abandoned prematurely.")
        target_innings = st.radio("Which innings suffered the stoppage + abandonment?", 
                                  [f"1st Innings ({team1_name})", f"2nd Innings ({team2_name})"], horizontal=True)

        if f"1st Innings ({team1_name})" in target_innings:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**1st Stoppage ({team1_name})**")
                default_rem1 = min(25.0, max(1.0, float(o_start) - 10.0))
                o_rem1 = st.number_input("Overs left at 1st stoppage", min_value=1.0, max_value=float(o_start), value=default_rem1, step=0.1)
                w1_stop1 = st.number_input("Wickets lost at 1st stoppage", min_value=0, max_value=9, value=2)
                default_rem2 = min(15.0, float(o_rem1))
                o_rem2 = st.number_input("Overs left after 1st resumption", min_value=0.0, max_value=float(o_rem1), value=default_rem2, step=0.1)
            with c2:
                st.markdown(f"**2nd Stoppage (Premature End)**")
                s1_final = st.number_input(f"{team1_name} Final Score at abandonment", min_value=1, max_value=500, value=210)
                default_final_rem = min(5.0, max(0.1, float(o_rem2)))
                o_rem_final = st.number_input("Overs remaining when abandoned", min_value=0.1, max_value=float(o_rem2), value=default_final_rem, step=0.1)
                w1_final = st.number_input("Wickets lost at abandonment", min_value=0, max_value=9, value=4)
                default_chase = min(30.0, float(o_start))
                o2_chase_quota = st.number_input(f"{team2_name} Available Chase Overs", min_value=min_cut, max_value=float(o_start), value=max(min_cut, default_chase), step=1.0)

            if st.button("Calculate & Apply Target", type="primary"):
                loss_1 = get_dls_resource(o_rem1, w1_stop1) - get_dls_resource(o_rem2, w1_stop1)
                loss_2 = get_dls_resource(o_rem_final, w1_final)
                r1 = max(0.0, r_start - loss_1 - loss_2)
                r2 = get_dls_resource(o2_chase_quota, 0)
                target, par = compute_dls(s1_final, r1, r2)
                
                final_o1 = o_start - (o_rem1 - o_rem2) - o_rem_final
                dls_dict = {
                    "is_dls": True, "target": target, "par": par,
                    "o1_max": final_o1, "o2_max": o2_chase_quota, "s1": s1_final,
                    "is_abandoned": False,
                    "summary": f"Target: {target} in {int(o2_chase_quota)} ov (T1 lost {round(loss_1+loss_2, 1)}% resources)"
                }
                apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1_final, o1=final_o1, s2=target, o2=o2_chase_quota)
                st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                s1 = st.number_input(f"{team1_name} 1st Innings Score", min_value=1, max_value=500, value=270)
                st.markdown(f"**1st Stoppage ({team2_name})**")
                default_rem1 = min(20.0, max(1.0, float(o_start) - 10.0))
                o_rem1 = st.number_input("Overs left at 1st stoppage", min_value=1.0, max_value=float(o_start), value=default_rem1, step=0.1)
                w2_stop1 = st.number_input("Wickets lost at 1st stoppage", min_value=0, max_value=9, value=1)
                default_rem2 = min(12.0, float(o_rem1))
                o_rem2 = st.number_input("Overs left after 1st resumption", min_value=0.0, max_value=float(o_rem1), value=default_rem2, step=0.1)
            with c2:
                st.markdown(f"**2nd Stoppage (Match Terminated)**")
                s2_final = st.number_input(f"{team2_name} Runs scored at abandonment", min_value=0, max_value=500, value=165)
                default_bowled = min(26.0, float(o_start))
                o_bowled_total = st.number_input(f"{team2_name} Total overs bowled (min 20)", min_value=min_cut, max_value=float(o_start), value=max(min_cut, default_bowled), step=0.1)
                w2_final = st.number_input("Wickets lost at abandonment", min_value=0, max_value=9, value=3)
                o_rem_final = (o_start - (o_rem1 - o_rem2)) - o_bowled_total

            if st.button("Calculate Par Score & Settle Match", type="primary"):
                r1 = r_start
                loss_1 = get_dls_resource(o_rem1, w2_stop1) - get_dls_resource(o_rem2, w2_stop1)
                loss_2 = get_dls_resource(max(0.0, o_rem_final), w2_final)
                r2_used = max(0.0, r_start - loss_1 - loss_2)
                target, par = compute_dls(s1, r1, r2_used)

                dls_dict = {
                    "is_dls": True, "target": target, "par": par,
                    "o1_max": o_start, "o2_max": o_bowled_total, "s1": s1,
                    "s2_actual": s2_final, "w2_actual": w2_final, "o2_actual": o_bowled_total,
                    "is_abandoned": True,
                    "summary": f"Match Abandoned: Par was {par} at {o_bowled_total} ov. Target: {target}"
                }
                apply_dls_payload(match_key, widget_prefix, dls_dict, s1=s1, o1=o_start, s2=s2_final, o2=o_bowled_total, w2=w2_final)
                st.rerun()
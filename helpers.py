import pandas as pd
from constants import (
    COLOR_ELIMINATED_BG,
    COLOR_QUALIFIED_BG,
    COLOR_WILDCARD_BG
)

def overs_to_balls(overs_float):
    complete = int(overs_float)
    balls = int(round((overs_float - complete) * 10))
    return complete * 6 + balls

def calculate_nrr(runs_scored, balls_faced, runs_conceded, balls_bowled):
    if balls_faced == 0 or balls_bowled == 0:
        return 0.0
    return (runs_scored / (balls_faced / 6.0)) - (runs_conceded / (balls_bowled / 6.0))

def init_team_stats(teams):
    return {
        t: {
            "P": 0, "W": 0, "L": 0, "T": 0, "NR": 0, "Pts": 0,
            "RS": 0, "BF": 0, "RC": 0, "BB": 0, "NRR": 0.0
        } for t in teams
    }

def update_table_stats(stats_dict, t1, t2, s1, w1, o1_faced, o1_max, s2, w2, o2_faced, o2_max, winner, is_dls=False, dls_target=None):
    st1, st2 = stats_dict[t1], stats_dict[t2]
    st1["P"] += 1
    st2["P"] += 1

    if winner == t1:
        st1["W"] += 1
        st1["Pts"] += 2
        st2["L"] += 1
    elif winner == t2:
        st2["W"] += 1
        st2["Pts"] += 2
        st1["L"] += 1
    else:
        st1["T"] += 1
        st2["T"] += 1
        st1["Pts"] += 1
        st2["Pts"] += 1

    if is_dls and dls_target is not None:
        t1_effective_runs = dls_target - 1
        t1_effective_balls = int(o2_max * 6)
        t2_effective_runs = s2
        t2_effective_balls = int(o2_max * 6) if w2 == 10 else overs_to_balls(o2_faced)
    else:
        t1_effective_runs = s1
        t1_effective_balls = int(o1_max * 6) if w1 == 10 else overs_to_balls(o1_faced)
        t2_effective_runs = s2
        t2_effective_balls = int(o2_max * 6) if w2 == 10 else overs_to_balls(o2_faced)

    st1["RS"] += t1_effective_runs
    st1["BF"] += t1_effective_balls
    st1["RC"] += t2_effective_runs
    st1["BB"] += t2_effective_balls
    st1["NRR"] = calculate_nrr(st1["RS"], st1["BF"], st1["RC"], st1["BB"])

    st2["RS"] += t2_effective_runs
    st2["BF"] += t2_effective_balls
    st2["RC"] += t1_effective_runs
    st2["BB"] += t1_effective_balls
    st2["NRR"] = calculate_nrr(st2["RS"], st2["BF"], st2["RC"], st2["BB"])

def get_standings_df(stats_dict):
    data = []
    for team, st_data in stats_dict.items():
        data.append({
            "Team": team, "P": st_data["P"], "W": st_data["W"], "L": st_data["L"],
            "T": st_data["T"], "Pts": st_data["Pts"], "NRR": round(st_data["NRR"], 3)
        })
    df = pd.DataFrame(data)
    df.sort_values(by=["Pts", "W", "NRR"], ascending=[False, False, False]).reset_index(drop=True)
    df.index = range(1, len(df) + 1)
    df.index.name = "Pos"
    return df

def style_standings_table(df, qualify_cutoff=4, wildcard_pos=None):
    def highlight_rows(row):
        pos = row.name
        if pos <= qualify_cutoff:
            return [f"background-color: {COLOR_QUALIFIED_BG}"] * len(row)
        elif wildcard_pos is not None and pos == wildcard_pos:
            return [f"background-color: {COLOR_WILDCARD_BG}"] * len(row)
        return [f"background-color: {COLOR_ELIMINATED_BG}"] * len(row)
    return df.style.apply(highlight_rows, axis=1)

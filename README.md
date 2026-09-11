# ICC Men's Cricket World Cup 2027 Simulator

An interactive Python dashboard built with Streamlit to simulate the revised **12-team, Super 7 format** of the ICC Men's Cricket World Cup 2027.

The app features dynamic match scorecards, real-time standings, authentic Net Run Rate (NRR) handling under ICC Clause 16.10, and a dedicated Duckworth-Lewis-Stern (DLS) calculator for weather interruptions.

---

## Key Features

- **Official 2027 Structure:** Group Stage (Pool A & B) → 4th-Place Wildcard Playoff → Super 7 Round-Robin → Semifinals & Grand Final.
- **Dynamic Match Cards:** Select toss winners, batting decisions, overs quotas, and match scores with instant reactivity.
- **Dedicated DLS Modal:** Full support for innings delays, mid-game interruptions, abandoned chases, and multiple stoppages with automatic target calculation.
- **ICC Clause 16.10 NRR:** Accurately credits first-innings equivalent scores in rain-affected games to prevent NRR calculation anomalies.
- **Live Points Tables:** Real-time standings sorted by Points, Wins, and true NRR, complete with color-coded qualification zones.

---

## Installation & Setup

**1. Clone the repository:**

**2. Install dependencies:**
Ensure you have Python 3.9+ installed, then run:

Bash
pip install streamlit pandas

**3. Launch the dashboard:**

Bash
streamlit run app.py

The app will open automatically in your browser at http://localhost:8501.

# **How to Use**
Pick Qualifiers: Choose 2 qualifying nations to complete the 12-team draw. The app automatically assigns them to Pool A and Pool B based on pre-seeded designations (or an automatic coin toss if seeds clash).

Play Matches:

Pick the toss winner and decision (Bat/Bowl).

Input runs, wickets, and overs faced.

If rain hits, click 🌧️ Open DLS Calculator, enter the stoppage details, and apply the revised target directly to the scorecard.

Track Standings: Tables update instantly after every match, highlighting direct qualifiers (green) and wildcard contenders (amber).
**
Advance the Tournament:**

Resolve the 4th-place wildcard decider to set the Super 7 roster.

Simulate the 21 Super 7 matches to find the top 4 teams.

Play Semifinal 1 (1st vs 4th) and Semifinal 2 (2nd vs 3rd), then crown the champion in the Grand Final!

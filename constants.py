# ==============================================================================
# TOURNAMENT CONFIGURATION & SEEDS
# ==============================================================================
TOURNAMENT_NAME = "ICC Men's Cricket World Cup 2027"
DEFAULT_OVERS = 50.0
MIN_OVERS_FOR_RESULT = 20.0

# Pre-seeded qualifiers for Pool allocation
QUALIFIER_SEEDS = {
    "WI": "A",
    "IRE": "A",
    "NED": "A",
    "SCO": "A",
    "USA": "B",
    "NEP": "B",
    "NAM": "B",
    "UAE": "B"
}

# Automatic Qualifiers (Full Members & Hosts)
CORE_TEAMS_GROUP_A = ["IND", "ENG", "PAK", "BAN", "ZIM"]
CORE_TEAMS_GROUP_B = ["RSA", "AUS", "NZ", "SL", "AFG"]

# ==============================================================================
# ICC DLS CONSTANTS & STANDARD RESOURCE COEFFICIENTS
# ==============================================================================
# Standard ICC Average 50-over total for ODIs
DLS_G50 = 245.0

# b(w) exponential resource decay parameters for 0 to 9 wickets down
DLS_B_COEFFS = {
    0: 0.035, 1: 0.034, 2: 0.032, 3: 0.030, 4: 0.027,
    5: 0.024, 6: 0.020, 7: 0.016, 8: 0.011, 9: 0.006
}

# Maximum resource percentages available at 50 overs with w wickets lost
MAX_RESOURCE_AT_50 = {
    0: 100.0, 1: 93.4, 2: 85.1, 3: 74.9, 4: 62.7,
    5: 49.0,  6: 34.1, 7: 19.7, 8: 8.7,  9: 2.3
}

# ==============================================================================
# UI DESIGN SYSTEM & COLOR TOKENS
# ==============================================================================
# Table row highlight colors
COLOR_QUALIFIED_BG = "rgba(46, 204, 113, 0.22)"   # Light emerald green (Direct entry)
COLOR_WILDCARD_BG = "rgba(241, 196, 15, 0.25)"    # Light amber/gold (Contention spot)
COLOR_ELIMINATED_BG = "transparent"

# Qualification cutoffs
GROUP_STAGE_DIRECT_QUALIFIERS = 3
GROUP_STAGE_WILDCARD_POS = 4
SUPER_7_SEMIFINAL_QUALIFIERS = 4
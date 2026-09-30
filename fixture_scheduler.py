def generate_round_robin_rounds(teams):
    """
    Standard Circle Method algorithm.
    Returns a list of rounds, where each round is a list of pairings (t1, t2).
    If len(teams) is odd, a BYE is added and the bye-match is dropped.
    """
    team_list = list(teams)
    has_bye = False

    if len(team_list) % 2 != 0:
        team_list.append("BYE")
        has_bye = True

    n = len(team_list)
    rounds = []

    # n - 1 rounds for a single round robin
    for r in range(n - 1):
        round_matches = []
        for i in range(n // 2):
            t1 = team_list[i]
            t2 = team_list[n - 1 - i]

            # Exclude matches involving the dummy BYE slot
            if t1 != "BYE" and t2 != "BYE":
                round_matches.append((t2, t1))

        rounds.append(round_matches)

        # Rotate all teams except the first one
        team_list = [team_list[0]] + [team_list[-1]] + team_list[1:-1]

    return rounds


def generate_group_stage_fixtures(pool_a_teams, pool_b_teams):
    """
    Generates an authentic 30-match group schedule.
    Interleaves rounds between Pool A and Pool B so teams never play back-to-back.
    """
    rounds_a = generate_round_robin_rounds(pool_a_teams)  # 5 rounds of 3 matches
    rounds_b = generate_round_robin_rounds(pool_b_teams)  # 5 rounds of 3 matches

    fixtures = []
    num_rounds = max(len(rounds_a), len(rounds_b))

    for r in range(num_rounds):
        # Pool A matches for Round r
        if r < len(rounds_a):
            for t1, t2 in rounds_a[r]:
                fixtures.append(("Group A", t1, t2))

        # Pool B matches for Round r
        if r < len(rounds_b):
            for t1, t2 in rounds_b[r]:
                fixtures.append(("Group B", t1, t2))

    return fixtures


def generate_super7_fixtures(super7_teams):
    """
    Generates a 21-match Super 7 schedule across 7 balanced rounds (3 matches each).
    In each round, 6 teams play and 1 team gets a scheduled BYE/rest day.
    """
    s7_rounds = generate_round_robin_rounds(super7_teams)  # 7 rounds of 3 matches
    fixtures = []
    for r in s7_rounds:
        for t1, t2 in r:
            fixtures.append(("Super 7", t1, t2))

    return fixtures
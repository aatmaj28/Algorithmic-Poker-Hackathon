def strat_action(game_state):
    """
    A strategy function that prompts the user via command-line
    to choose an action based on the current game state.
    Returns a dictionary with keys 'action' and 'amount'.
    """

    hole_cards = game_state.get("holeCards", [])
    community_cards = game_state.get("communityCards", [])
    pot = game_state.get("pot", 0)
    current_bet = game_state.get("currentBet", 0)
    available_actions = game_state.get("availableActions", [])
    min_raise = game_state.get("minRaise", 0)
    max_bet = game_state.get("maxBet", 0)
    stack_size = game_state.get("stackSize", 0)

    # Format hole and community cards for better readability
    formatted_hole = [f"{card['_rank']}{card['_suit']}" for card in hole_cards]
    formatted_community = [f"{card['_rank']}{card['_suit']}" for card in community_cards]

    print("\n=================================")
    print("         🃏 POKER TABLE 🃏       ")
    print("=================================")

    print("\n🔹 Your Cards:")
    print(f"   {' '.join(formatted_hole) if formatted_hole else 'No hole cards yet'}")

    print("\n🔹 Community Cards:")
    print(f"   {' '.join(formatted_community) if formatted_community else 'No community cards yet'}")

    print("\n🔹 Table Info:")
    print(f"   🏆 Pot: ${pot}")
    print(f"   💰 Current Bet: ${current_bet}")
    print(f"   🎲 Your Stack: ${stack_size}")

    print("\n🔹 Available Actions:")
    print(f"   {' | '.join(available_actions) if available_actions else 'None'}")

    print("\n🔹 Betting Limits:")
    print(f"   ➖ Min Raise: ${min_raise}")
    print(f"   ➕ Max Bet: ${max_bet}")
    print("=================================")

    # If no actions are available, return a fold
    if not available_actions:
        print("\n⚠️ No actions available. Automatically folding...")
        return {"action": "fold", "amount": 0}

    while True:
        action = input(f"\n👉 Choose an action ({' | '.join(available_actions)}): ").strip().lower()

        # Validate action
        if action not in available_actions:
            print(f"❌ Invalid action. Must be one of: {' | '.join(available_actions)}")
            continue

        # If action requires an amount, prompt for it
        if action in ["bet", "raise"]:
            while True:
                try:
                    amount = int(input("💵 Enter amount: ").strip())
                    if amount < min_raise or amount > max_bet:
                        print(f"❌ Invalid amount. Must be between ${min_raise} and ${max_bet}.")
                        continue
                    return {"action": action, "amount": amount}
                except ValueError:
                    print("❌ Invalid input. Please enter a valid number.")
        else:
            return {"action": action, "amount": 0}

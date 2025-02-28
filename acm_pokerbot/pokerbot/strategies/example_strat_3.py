import random
from pokerbot.evaluator import eval_hand
# Paste your evaluator code here, or import it if it's in a separate file:
from collections import Counter


# Map each hand rank to a simple "strength" value.
HAND_STRENGTH = {
    "High Card":        1,
    "One Pair":         2,
    "Two Pair":         3,
    "Three of a Kind":  4,
    "Straight":         5,
    "Flush":            6,
    "Full House":       7,
    "Four of a Kind":   8,
    "Straight Flush":   9,
    "Royal Flush":      10
}

def strat_action(game_state):
    """
    A strategy function that uses the eval_hand function to evaluate the hole +
    community cards, then decides on an action based on that hand type plus
    a bit of randomness. It does not always fold.
    """
    # Extract relevant game info
    hole_cards = game_state.get("holeCards", [])
    community_cards = game_state.get("communityCards", [])
    pot = game_state.get("pot", 0)
    current_bet = game_state.get("currentBet", 0)
    available_actions = game_state.get("availableActions", [])
    min_raise = game_state.get("minRaise", 0)
    max_bet = game_state.get("maxBet", 0)

    # Evaluate the current hand
    hand_type = eval_hand(hole_cards, community_cards)
    hand_strength = HAND_STRENGTH.get(hand_type, 1)

    # Debug/logging output
    formatted_hole = [f"{card['_rank']}{card['_suit']}" for card in hole_cards]
    formatted_community = [f"{card['_rank']}{card['_suit']}" for card in community_cards]

    print("\n=== Evaluator Strategy ===")
    print(f"Hole Cards: {formatted_hole}")
    print(f"Community Cards: {formatted_community}")
    print(f"Hand Type: {hand_type} (Strength={hand_strength})")
    print(f"Available Actions: {available_actions}")
    print(f"Pot: {pot}, Current Bet: {current_bet}")
    print(f"Min Raise: {min_raise}, Max Bet: {max_bet}")

    # If no actions are available, we default to folding (or do nothing).
    if not available_actions:
        print("No actions available; returning fold.")
        return {"action": "fold", "amount": 0}

    # If the only action is fold, we have no choice:
    if len(available_actions) == 1 and available_actions[0] == "fold":
        return {"action": "fold", "amount": 0}

    # Helper to pick a random bet/raise amount within valid range
    def random_bet_amount():
        if min_raise > 0 and max_bet >= min_raise:
            return random.randint(min_raise, max_bet)
        return max(1, min_raise)

    # Basic logic example:
    # - If we have "Check" available, we might check or try to bet/raise if the hand is decent.
    # - If we can call but not check, we might do that or raise sometimes.
    # - The stronger the hand, the more likely we are to bet or raise.
    # - This is all just a simple demonstration of combining hand strength + randomness.

    # 1. If "check" is available:
    if "check" in available_actions:
        # If we have Straight or better, let's bet or raise some of the time
        if hand_strength >= 5 and "bet" in available_actions:
            return {"action": "bet", "amount": random_bet_amount()}

        # Otherwise, check most of the time, but occasionally do a small bet or raise
        if random.random() < 0.7:
            return {"action": "check", "amount": 0}
        else:
            if "bet" in available_actions:
                return {"action": "bet", "amount": random_bet_amount()}
            if "raise" in available_actions:
                return {"action": "raise", "amount": random_bet_amount()}
            return {"action": "check", "amount": 0}

    # 2. If "call" is available (and we can't check):
    if "call" in available_actions:
        # If we have a fairly strong hand, try to raise some of the time
        if hand_strength >= 5 and "raise" in available_actions:
            if random.random() < 0.5:
                return {"action": "raise", "amount": random_bet_amount()}
        # Otherwise just call
        return {"action": "call", "amount": 0}

    # 3. If "bet" is available but not "check" or "call":
    if "bet" in available_actions:
        # Bet a random amount
        return {"action": "bet", "amount": random_bet_amount()}

    # 4. If "raise" is available but no check/call/bet:
    if "raise" in available_actions:
        # If we have a decent hand, raise bigger:
        if hand_strength >= 5 and random.random() < 0.75:
            return {"action": "raise", "amount": random_bet_amount()}
        return {"action": "raise", "amount": random_bet_amount()}

    # 5. If no other actions are left, fold by default
    return {"action": "fold", "amount": 0}
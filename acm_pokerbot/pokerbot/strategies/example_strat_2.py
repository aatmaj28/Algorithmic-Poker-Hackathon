from pokerbot.evaluator import eval_hand

def strat_action(game_state):
    """
    Write your strategy here. The function receives a dictionary `game_state`
    with the following keys:
      - 'hole_cards': List of two cards dealt to your bot
      - 'community_cards': List of shared cards on the table
      - 'stack_size': Your current stack size
      - 'current_bet': The current bet to call
      - 'current_bet': The current bet to call
      - 'pot': The total amount in the pot

    Return a dictionary with:
      - 'action': One of 'fold', 'check', 'call', 'raise'
      - 'amount': The amount to bet/raise (if applicable)

    The current implementation goes all in if the hand is a Royal Flush, Straight Flush, or Four of a Kind
    """
    hole_cards = game_state.get('holeCards', [])
    community_cards = game_state.get('communityCards', [])
    evaluated_hand = eval_hand(hole_cards, community_cards)
    stack_size = game_state['stack_size']
    current_bet = game_state['current_bet']

    def go_all_in():
        return {"action": "raise", "amount": stack_size}

    # Example logic (replace with your custom strategy)
    if evaluated_hand in ["Royal Flush", "Straight Flush", "Four of a Kind"]:
        if stack_size <= current_bet:
            return go_all_in()  # Go all-in if stack size is smaller than the current bet
        max_raise = min(current_bet * 3, stack_size)
        return {"action": "raise", "amount": max_raise}

    elif evaluated_hand in ["Full House", "Flush", "Straight"]:
        raise_amount = min(current_bet * 2, stack_size)
        return {"action": "raise", "amount": raise_amount}

    elif evaluated_hand in ["Three of a Kind", "Two Pair", "One Pair"]:
        call_amount = min(current_bet, stack_size)
        return {"action": "call", "amount": call_amount}

    else:
        # Fold if calling is not possible (stack too small)
        if stack_size < current_bet:
            return go_all_in()  # Consider going all-in as a last-ditch effort
        return {"action": "fold", "amount": 0}
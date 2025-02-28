from collections import Counter

def eval_hand(hole_cards, community_cards):
    if not hole_cards:
        return "High Card"  # No valid hand yet

    all_cards = hole_cards + community_cards
    values = [card['_rank'] for card in all_cards]
    suits = [card['_suit'] for card in all_cards]

    value_map = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
        "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "Q": 12, "K": 13, "A": 14
    }
    try:
        numeric_values = sorted([value_map[str(v)] for v in values])
    except KeyError:
        print("Error: Invalid card value encountered:", values)
        return "Error"

    value_counter = Counter(numeric_values)
    suit_counter = Counter(suits)

    is_flush = any(count >= 5 for count in suit_counter.values())

    # Check for Straight
    def is_straight(values):
        values = sorted(set(values))
        for i in range(len(values) - 4):
            if values[i + 4] - values[i] == 4:
                return True
        if set([14, 2, 3, 4, 5]).issubset(values):  # Special case A-2-3-4-5
            return True
        return False

    is_straight_hand = is_straight(numeric_values)

    # Check for Straight Flush
    if is_flush:
        flush_suit = max(suit_counter, key=suit_counter.get)
        flush_cards = sorted([value_map[card['_rank']] for card in all_cards if card['_suit'] == flush_suit])
        if is_straight(flush_cards):
            return "Royal Flush" if max(flush_cards) == 14 else "Straight Flush"

    # Check for Four of a Kind, Full House, Three of a Kind, Two Pair, One Pair
    counts = list(value_counter.values())
    if 4 in counts:
        return "Four of a Kind"
    if 3 in counts and 2 in counts:
        return "Full House"
    if is_flush:
        return "Flush"
    if is_straight_hand:
        return "Straight"
    if 3 in counts:
        return "Three of a Kind"
    if counts.count(2) == 2:
        return "Two Pair"
    if 2 in counts:
        return "One Pair"

    return "High Card"

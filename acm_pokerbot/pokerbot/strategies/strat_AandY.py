import random
from collections import Counter

# Card values for pre-flop hand strength calculation
CARD_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, 
    "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14
}

# Premium starting hands (pocket pairs and strong Ax hands)
PREMIUM_HANDS = [
    # Pocket pairs
    {"A", "A"}, {"K", "K"}, {"Q", "Q"}, {"J", "J"}, {"10", "10"},
    # Ace-high hands
    {"A", "K"}, {"A", "Q"}, {"A", "J"}, {"A", "10"},
    # King-high hands
    {"K", "Q"}, {"K", "J"}
]

# Strong starting hands
STRONG_HANDS = [
    # Pocket pairs
    {"9", "9"}, {"8", "8"}, {"7", "7"},
    # Suited connectors
    {"Q", "J"}, {"J", "10"}, {"10", "9"}, {"9", "8"},
    # Ace-high hands
    {"A", "9"}, {"A", "8"}, {"A", "7"},
    # King-high hands
    {"K", "10"}, {"K", "9"}
]

# Playable starting hands
PLAYABLE_HANDS = [
    # Pocket pairs
    {"6", "6"}, {"5", "5"}, {"4", "4"}, {"3", "3"}, {"2", "2"},
    # Suited connectors
    {"8", "7"}, {"7", "6"}, {"6", "5"}, {"5", "4"}, {"4", "3"},
    # Borderline hands
    {"A", "6"}, {"A", "5"}, {"A", "4"}, {"A", "3"}, {"A", "2"},
    {"K", "8"}, {"K", "7"}, {"K", "6"}, {"Q", "10"}, {"Q", "9"}
]

# Hand strength ranking
HAND_STRENGTH = {
    "High Card": 1,
    "One Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10
}

class PokerStrategy:
    def __init__(self):
        self.hand_history = []  # Track previous hands
        self.round_history = []  # Track betting in current hand
        self.player_profiles = {}  # Track tendencies of other players
        self.position = None  # Early, middle, late
        self.hand_count = 0
        self.initial_stack = 1000  # Assume starting with 1000 chips
        self.aggression_factor = 0.7  # Adjustable parameter (0-1), higher = more aggressive
        self.bluff_frequency = 0.15  # How often to bluff (0-1)
        self.min_stack_for_bluff = 400  # Don't bluff if stack is below this
        self.playing_style = "tight-aggressive"  # Default playing style

    def update_hand_history(self, game_state, action_taken):
        """Track hands played and their outcomes"""
        self.round_history.append({
            "hole_cards": game_state.get("holeCards", []),
            "community_cards": game_state.get("communityCards", []),
            "action": action_taken,
            "pot": game_state.get("pot", 0),
            "stage": self._determine_stage(game_state.get("communityCards", []))
        })

    def _determine_stage(self, community_cards):
        """Determine the current stage of the hand"""
        if not community_cards:
            return "pre-flop"
        elif len(community_cards) == 3:
            return "flop"
        elif len(community_cards) == 4:
            return "turn"
        elif len(community_cards) == 5:
            return "river"
        return "unknown"

    def evaluate_preflop_hand(self, hole_cards):
        """
        Evaluate pre-flop hand strength
        Returns: 
            3 for premium hands
            2 for strong hands
            1 for playable hands
            0 for weak hands
        """
        if not hole_cards or len(hole_cards) != 2:
            return 0
        
        ranks = {card['_rank'] for card in hole_cards}
        suits = {card['_suit'] for card in hole_cards}
        
        # Check if we have a pocket pair
        is_pocket_pair = len(ranks) == 1
        
        # Check if hand is suited
        is_suited = len(suits) == 1
        
        # Check if our hand is in one of the predefined categories
        if ranks in PREMIUM_HANDS or (is_pocket_pair and any(r in ['A', 'K', 'Q', 'J', '10'] for r in ranks)):
            return 3
        
        if ranks in STRONG_HANDS or (is_suited and ranks in PREMIUM_HANDS):
            return 2
        
        if ranks in PLAYABLE_HANDS or (is_suited and ranks in STRONG_HANDS):
            return 1
            
        return 0

    def calculate_pot_odds(self, pot, current_bet):
        """Calculate pot odds (ratio of what you can win vs what you must bet)"""
        if current_bet == 0:
            return float('inf')  # No bet to call, so odds are infinite
        return pot / current_bet

    def calculate_win_probability(self, hole_cards, community_cards, hand_type):
        """
        Estimate probability of winning based on current hand type
        This is a simplified version - in a real implementation, you'd use more complex algorithms
        """
        hand_strength = HAND_STRENGTH.get(hand_type, 0)
        
        # Base probabilities for different hand strengths
        base_probs = {
            0: 0.05,  # No hand yet
            1: 0.10,  # High Card
            2: 0.20,  # One Pair
            3: 0.35,  # Two Pair
            4: 0.50,  # Three of a Kind
            5: 0.65,  # Straight
            6: 0.75,  # Flush
            7: 0.85,  # Full House
            8: 0.92,  # Four of a Kind
            9: 0.98,  # Straight Flush
            10: 0.99  # Royal Flush
        }
        
        # Adjust based on stage of the hand
        stage_adjustment = {
            "pre-flop": 0.8,  # More uncertainty
            "flop": 0.9,
            "turn": 0.95,
            "river": 1.0     # Final hand, no more uncertainty
        }
        
        current_stage = self._determine_stage(community_cards)
        
        # Apply adjustments
        win_prob = base_probs[hand_strength] * stage_adjustment[current_stage]
        
        # Add a small random variation to make behavior less predictable
        win_prob = min(0.99, max(0.01, win_prob + random.uniform(-0.05, 0.05)))
        
        return win_prob

    def calculate_expected_value(self, win_probability, pot, bet_amount):
        """Calculate the expected value of a bet"""
        return (win_probability * pot) - ((1 - win_probability) * bet_amount)

    def should_bluff(self, game_state):
        """Decide whether to bluff based on various factors"""
        # Don't bluff if stack is too low
        if game_state.get("stackSize", 0) < self.min_stack_for_bluff:
            return False
            
        # More likely to bluff in late position
        position_factor = 1.2 if self.position == "late" else 0.8
            
        # Adjust bluff frequency based on stack size and position
        adjusted_bluff_freq = self.bluff_frequency * position_factor
        
        # Randomly decide whether to bluff
        return random.random() < adjusted_bluff_freq

    def determine_position(self, game_state):
        """
        Determine position at the table
        This is a simplified version since we don't have complete table information
        """
        # In a real implementation, you'd track all players and know exact positions
        # Here we're making a guess based on when our bot acts
        players = game_state.get("players", [])
        total_players = sum(1 for p in players if p is not None)
        
        if total_players <= 3:
            self.position = "late"  # In a small game, positions are less relevant
        elif random.random() < 0.33:
            self.position = "early"
        elif random.random() < 0.5:
            self.position = "middle"
        else:
            self.position = "late"

    def determine_bet_size(self, hand_strength, pot, stack_size, min_raise, max_bet, win_probability):
        """
        Determine bet size based on hand strength, pot size, and stack size
        Returns an amount between min_raise and max_bet
        """
        # Base bet as a percentage of the pot
        pot_percentage = {
            0: 0.5,  # Weak hands - small bets
            1: 0.75, # Playable hands
            2: 1.0,  # Strong hands
            3: 1.5   # Premium hands
        }
        
        # Adjust based on win probability
        bet_multiplier = win_probability * 2
        
        # Calculate the base bet amount
        base_bet = min(pot * pot_percentage[hand_strength] * bet_multiplier, stack_size)
        
        # Ensure the bet is within the allowed range
        bet_amount = max(min_raise, min(base_bet, max_bet))
        
        # Round to nearest chip
        return int(bet_amount)

    def adjust_strategy(self, stack_size):
        """Adjust strategy based on stack size"""
        # If we're short stacked, play more conservatively
        if stack_size < self.initial_stack * 0.3:
            self.playing_style = "tight-conservative"
            self.aggression_factor = 0.3
            self.bluff_frequency = 0.05
        # If we have a large stack, play more aggressively
        elif stack_size > self.initial_stack * 1.5:
            self.playing_style = "loose-aggressive"
            self.aggression_factor = 0.9
            self.bluff_frequency = 0.2
        # Default to tight-aggressive
        else:
            self.playing_style = "tight-aggressive"
            self.aggression_factor = 0.7
            self.bluff_frequency = 0.15

    def strat_action(self, game_state):
        """
        Main strategy function that decides on the action to take
        Returns a dictionary with keys 'action' and 'amount'
        """
        # Extract game state information
        hole_cards = game_state.get("holeCards", [])
        community_cards = game_state.get("communityCards", [])
        available_actions = game_state.get("availableActions", [])
        pot = game_state.get("pot", 0)
        current_bet = game_state.get("currentBet", 0)
        min_raise = game_state.get("minRaise", 0)
        max_bet = game_state.get("maxBet", 0)
        stack_size = game_state.get("stackSize", 0)
        
        # Increment hand count whenever we're at pre-flop
        if not community_cards:
            self.hand_count += 1
            
        # Determine position
        self.determine_position(game_state)
        
        # Adjust strategy based on stack size
        self.adjust_strategy(stack_size)
        
        # If no actions are available, default to fold
        if not available_actions:
            return {"action": "fold", "amount": 0}
        
        # Determine current stage
        current_stage = self._determine_stage(community_cards)
        
        # Evaluate hand strength
        if current_stage == "pre-flop":
            # Pre-flop evaluation
            hand_strength = self.evaluate_preflop_hand(hole_cards)
            hand_type = "Pre-flop"  # Just a placeholder
        else:
            # Post-flop evaluation using the provided evaluator
            from pokerbot.evaluator import eval_hand
            hand_type = eval_hand(hole_cards, community_cards)
            hand_strength = HAND_STRENGTH.get(hand_type, 1) / 3  # Scale to 0-3 range
            
        # Calculate win probability
        win_probability = self.calculate_win_probability(hole_cards, community_cards, hand_type)
        
        # Calculate pot odds
        pot_odds = self.calculate_pot_odds(pot, current_bet)
        
        # Special case for pre-flop
        if current_stage == "pre-flop":
            if hand_strength >= 2:  # Premium or strong hand
                if "raise" in available_actions:
                    bet_amount = self.determine_bet_size(hand_strength, pot, stack_size, min_raise, max_bet, win_probability)
                    return {"action": "raise", "amount": bet_amount}
                elif "bet" in available_actions:
                    bet_amount = self.determine_bet_size(hand_strength, pot, stack_size, min_raise, max_bet, win_probability)
                    return {"action": "bet", "amount": bet_amount}
                elif "call" in available_actions:
                    return {"action": "call", "amount": 0}
                elif "check" in available_actions:
                    return {"action": "check", "amount": 0}
            elif hand_strength == 1:  # Playable hand
                # In late position, play more hands
                if self.position == "late":
                    if "call" in available_actions:
                        return {"action": "call", "amount": 0}
                    elif "check" in available_actions:
                        return {"action": "check", "amount": 0}
                # In early position, be more cautious
                else:
                    if "check" in available_actions:
                        return {"action": "check", "amount": 0}
                    elif current_bet <= stack_size * 0.05 and "call" in available_actions:
                        return {"action": "call", "amount": 0}
                    else:
                        return {"action": "fold", "amount": 0}
            else:  # Weak hand
                # Sometimes check or call with weak hands if cheap
                if "check" in available_actions:
                    return {"action": "check", "amount": 0}
                elif current_bet <= stack_size * 0.02 and "call" in available_actions:
                    return {"action": "call", "amount": 0}
                else:
                    return {"action": "fold", "amount": 0}
        
        # Post-flop decision making
        else:
            # For very strong hands, be aggressive
            if hand_strength >= 6/3:  # Flush or better
                if "raise" in available_actions:
                    bet_amount = self.determine_bet_size(3, pot, stack_size, min_raise, max_bet, win_probability)
                    return {"action": "raise", "amount": bet_amount}
                elif "bet" in available_actions:
                    bet_amount = self.determine_bet_size(3, pot, stack_size, min_raise, max_bet, win_probability)
                    return {"action": "bet", "amount": bet_amount}
                elif "call" in available_actions:
                    return {"action": "call", "amount": 0}
                elif "check" in available_actions:
                    return {"action": "check", "amount": 0}
            
            # For medium-strong hands, be somewhat aggressive
            elif hand_strength >= 3/3:  # Three of a kind or better
                if win_probability > 0.6:
                    if "raise" in available_actions:
                        bet_amount = self.determine_bet_size(2, pot, stack_size, min_raise, max_bet, win_probability)
                        return {"action": "raise", "amount": bet_amount}
                    elif "bet" in available_actions:
                        bet_amount = self.determine_bet_size(2, pot, stack_size, min_raise, max_bet, win_probability)
                        return {"action": "bet", "amount": bet_amount}
                
                # Otherwise call or check
                if "call" in available_actions:
                    # Only call if the expected value is positive
                    if win_probability > 1 / (pot_odds + 1):
                        return {"action": "call", "amount": 0}
                elif "check" in available_actions:
                    return {"action": "check", "amount": 0}
                
            # For weak hands, consider bluffing
            else:
                # Check if possible
                if "check" in available_actions:
                    # Sometimes bluff instead of checking
                    if self.should_bluff(game_state) and ("bet" in available_actions):
                        bluff_amount = min(pot * 0.75, max_bet)
                        return {"action": "bet", "amount": int(bluff_amount)}
                    return {"action": "check", "amount": 0}
                
                # Call if pot odds are good
                if "call" in available_actions:
                    if win_probability > 1 / (pot_odds + 1):
                        return {"action": "call", "amount": 0}
                
                # Sometimes bluff with a raise
                if self.should_bluff(game_state) and "raise" in available_actions:
                    bluff_amount = min(pot * 0.5, max_bet)
                    return {"action": "raise", "amount": int(bluff_amount)}
                
                # Otherwise fold
                return {"action": "fold", "amount": 0}
        
        # If we somehow get here without making a decision, fold
        return {"action": "fold", "amount": 0}

# Create the strategy instance
strategy = PokerStrategy()

# Function to be called from the PokerBot
def strat_action(game_state):
    action = strategy.strat_action(game_state)
    
    # Log action for debugging
    hole_cards = game_state.get("holeCards", [])
    community_cards = game_state.get("communityCards", [])
    formatted_hole = [f"{card['_rank']}{card['_suit']}" for card in hole_cards]
    formatted_community = [f"{card['_rank']}{card['_suit']}" for card in community_cards]
    
    print("\n=== Advanced Strategy ===")
    print(f"Hole Cards: {formatted_hole}")
    print(f"Community Cards: {formatted_community}")
    print(f"Position: {strategy.position}")
    print(f"Playing Style: {strategy.playing_style}")
    print(f"Action: {action['action']} (Amount: {action['amount']})")
    
    # Update history
    strategy.update_hand_history(game_state, action)
    
    return action
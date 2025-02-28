import websocket
import json
import uuid
import os
from dotenv import load_dotenv


class PokerBot:
    def __init__(self, strategy, name, id):
        """
        :param strategy: A module or object with a method `strat_action(game_state)`
                         that returns a dictionary {"action": <str>, "amount": <int>}.
        """
        load_dotenv()
        self.strategy = strategy

        # Environment variables
        self.server_ip = os.getenv("SERVER_IP")
        self.port = os.getenv("PORT", 3002)

        self.ws = None
        self.player_id = id
        self.name = name
        self.buy_in = 1000

        self.community_cards = []
        self.pot = 0
        self.current_bet = 0

    def on_message(self, ws, message):
        """Handles incoming messages from the WebSocket server."""
        data = json.loads(message)

        msg_type = data.get("type", "")

        if msg_type == "gameState":
            self.handle_game_state(data)

        elif msg_type == "privateState":
            self.handle_private_state(data)

        elif msg_type == "handComplete":
            self.handle_hand_complete(data)

        elif msg_type == "players":
            self.handle_players(data)

    def handle_game_state(self, data):
        """Store and display table-wide state (community cards, pot, etc.)."""
        state = data["state"]
        self.community_cards = state.get("communityCards", [])
        self.pot = state.get("pot", 0)
        self.current_bet = state.get("currentBet", 0)


        # print("\n=== Table Info ===")
        # print(f"Community Cards: {self.community_cards}")
        # print(f"Pot: {self.pot}")
        # print(f"Current Bet: {self.current_bet}")
        # print(f"Current Round: {state.get('currentRound', 'unknown')}\n")

        # Print players (if you like)
        players = state.get("players", [])
        print("Players at the table:")
        for p in players:
            if p is not None:
                status = "FOLDED" if p["folded"] else "Active"
                current = "(CURRENT)" if p["isCurrentActor"] else ""
                print(f"  {p['name']}: stack={p['stackSize']} {status} {current}")
        print()

    def handle_private_state(self, data):
        """When it's our turn, the server sends 'privateState' with hole cards and possible actions."""
        state = data["state"]

        hole_cards = state.get("holeCards", [])
        available_actions = state.get("availableActions", [])

        # print("\n=== Your Private Info ===")
        # print(f"Hole Cards: {hole_cards}")
        # print(f"Available Actions: {available_actions}")

        if not available_actions:
            print("No actions available; waiting for other players...")
            return


        game_state = {
            "holeCards": hole_cards,
            "communityCards": self.community_cards,
            "pot": self.pot,
            "stackSize": state.get("stackSize", 0),
            "currentBet": self.current_bet,
            "availableActions": available_actions,
            "minRaise": state.get("minRaise", 0),
            "maxBet": state.get("maxBet", 0),
        }
        # print(f"GAMESTATE: {game_state}\n\n")
        move = self.strategy.strat_action(game_state)
        action = move.get("action", "fold")
        amount = move.get("amount", 0)

        # Send the chosen action back to the server
        self.send_action(action, amount)

    def handle_hand_complete(self, data):
        """Displays hand results."""
        winners = data.get("winners", [])
        if any(winner['playerId'] == self.player_id for winner in winners):
            print("\n🎉 YOU WON THE HAND! 🎉")
        else:
            print("\n😢 YOU LOST THE HAND 😢")

    def handle_players(self, data):
        """Displays a simple list of all players in the room."""
        print("\n=== Players at Table ===")
        players = data.get("players", [])
        for player in players:
            if player is not None:
                print(f"  {player['name']}")
        print()

    def on_error(self, ws, error):
        """Handles WebSocket errors."""
        print("WebSocket Error:", error)

    def on_open(self, ws):
        """Once the connection is open, send the 'join' message."""
        self.send_join()

    def run(self):
        """Connect and listen forever."""
        if not self.server_ip:
            print("ERROR: SERVER_IP not set in your environment (.env).")
            return

        ws_url = f"ws://{self.server_ip}:{self.port}"
        print(f"Connecting to {ws_url}...")

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_open=self.on_open
        )
        self.ws.run_forever()

    def send_join(self):
        """Sends the 'join' message to enter the game."""
        join_msg = {
            "type": "join",
            "playerId": self.player_id,
            "name": self.name,
            "buyIn": self.buy_in
        }
        self.ws.send(json.dumps(join_msg))

    def send_action(self, action, amount=0):
        """Sends an action (fold, check, call, bet, raise) to the server."""
        print(f"Sending action: {action} (amount={amount})")
        action_msg = {
            "playerId": self.player_id,
            "type": "action",
            "action": action,
            "amount": amount
        }
        self.ws.send(json.dumps(action_msg))


if __name__ == "__main__":
    # Example usage with a trivial strategy that always folds:
    class AlwaysFoldStrategy:
        def strat_action(self, game_state):
            return {"action": "fold", "amount": 0}

    strategy = AlwaysFoldStrategy()
    bot = PokerBot(strategy)
    bot.run()
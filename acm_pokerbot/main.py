from pokerbot.core import PokerBot
from pokerbot.strategies import example_strat_1, example_strat_2, example_strat_3
import os
from pokerbot.core import PokerBot
from pokerbot.strategies import strat_AandY
import os
from dotenv import load_dotenv
from dotenv import load_dotenv


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get server details from environment variables
    server_ip = os.getenv('SERVER_IP')
    port = os.getenv('PORT', 3004)  # Default to 3000 if not set
    ws_url = f"ws://{server_ip}:{port}"

    if not server_ip:
        print("[ERROR] SERVER_IP is not set in your .env file.")
        return

    # Initialize the bot with the interactive command-line strategy
    bot = PokerBot(strategy=strat_AandY, name="Disruptify", id='1.1')

    # Run the bot and handle keyboard interrupts gracefully
    try:
        print(f"[INFO] Starting PokerBot and connecting to {ws_url}...")
        bot.run()
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped by user.")


if __name__ == "__main__":
    main()



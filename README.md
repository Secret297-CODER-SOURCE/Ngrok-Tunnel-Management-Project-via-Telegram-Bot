# Ngrok-Tunnel-Management-Project-via-Telegram-Bot
This project allows users to manage Ngrok tunnels through a Telegram bot. The bot provides a menu where users can choose different types of tunnels (HTTP, HTTPS, SSH, VNC, FTP, FTPS) or stop all active tunnels. The tunnels are managed using Ngrok, and the configuration is handled through a Telegram bot that connects to the service via its API.

## Features
1. **Dependency Installation**:
   - The `pyngrok` and `pytelegrambotapi` packages are automatically installed if they are missing from the system.

2. **Configuration**:
   - On the first run, the bot will request the Telegram bot token, Ngrok auth token, and Chat ID for sending messages.
   - The configuration is saved in a `config.json` file.

3. **Tunnel Management**:
   - Start Ngrok tunnels for various protocols (HTTP, HTTPS, SSH, VNC, FTP, FTPS) on selected ports.
   - Stop specific tunnels or stop all tunnels at once.

4. **Interactive Menu**:
   - A simple menu is available through the Telegram bot with buttons to select actions.
   - Buttons are provided to stop tunnels and return to the main menu.

## Installation
1. Clone the repository or download the code.
2. Run the program:
   ```bash
   sudo python3 ngrok_bot.py
   ```
3. Enter the configuration details:
   - TELEGRAM_BOT_TOKEN: Your Telegram bot token.
   - NGROK_AUTH_TOKEN: Your Ngrok token.
   - CHAT_ID: Your Chat ID for receiving messages from the bot.
4. Interact with the bot via Telegram:
   - Select protocols to start tunnels.
   - Stop tunnels as needed.
## Important Notes
- This project is intended for local use with Ngrok tunnels.
- To use Ngrok, you need to register on Ngrok and obtain an authorization token.

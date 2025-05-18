# Fabcord - Simple Discord2Minecraft

SimpleD2M is a lightweight Python program that lets you verify players Discord name against their Minecraft Username.

## Usage
`!fabcord` - Players run this command in the Discord server. They are sent a DM from the bot asking for their Minecraft Username
`!sync-verified` - A command to help fix data errors, it will show players who are known to fabcord but don't have a UUID linked.

Visit `localhost:5000` - you will see the management console to verify players who have interacted with the bot. Here you can also remove their verification

## Set Up Discord Bot
1. Go to https://discord.com/developers/applications and create a new application.
2. Give it a name (This will be the bots username in your server)
3. Under the **bots** menu on the left, generate a token. *Store this somewhere safe*
4. Still under bot settings, enable the **message content** intent
5. Under the **installation** setting, copy the install link and paste it in to a new browser window
6. Follow the steps to invite the bot in to your Discord Server.
7. Create a new role in your server called **Verified**, make sure this is above the roll for the bot.
8. Right click your Discord server on the server list on the left of Discord and **Copy Server ID**, this is your **GUILD_ID**. Keep this handy, as you will need it in Step 4 of the Server Deploy instructions.

## Deploy on Server
*This has been tested in Ubuntu Sever, config may be different on other flavours of Linux*

1. Clone the repo.
   git clone https://github.com/A29-Dev/SimpleD2M
   cd fabcord

0. Auto setup
   Run `./setup` to set up Python environment, or follow the below steps to setup manually.

2. Create and activate virtual environment
   
   `python3 -m venv venv`
   
   `source venv/bin/activate`

3. Make *main.py* excecutable
   `chmod +x main.py`

3. Install dependencies

   `pip install -r requirements.txt`

4. (First time only) Run the bot to generate config.json
   python3 main.py Enter your bot token and guild ID when prompted

### Optional

5. Create systemd service
   sudo nano /etc/systemd/system/fabcord.service

  ```
   [Unit]
   Description=FabCord Discord Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/fabcord
   ExecStart=/home/ubuntu/fabcord/venv/bin/python3 /home/ubuntu/fabcord/main.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

6. Enable and start the service
  ` sudo systemctl daemon-reexec`
   `sudo systemctl daemon-reload`
   `sudo systemctl enable fabcord`
   `sudo systemctl start fabcord`

7. Monitor logs (optional)
   
   `journalctl -u fabcord -f`
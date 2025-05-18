✅ FabCord Deployment Checklist (Ubuntu Production Server)

1. Clone the repo
   git clone https://github.com/A29-Dev/SimpleD2M
   cd fabcord

2. Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. (First time only) Run the bot to generate config.json
   python3 main.py
   # Enter your bot token and guild ID when prompted

5. Create systemd service
   sudo nano /etc/systemd/system/fabcord.service

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

6. Enable and start the service
   sudo systemctl daemon-reexec
   sudo systemctl daemon-reload
   sudo systemctl enable fabcord
   sudo systemctl start fabcord

7. Monitor logs (optional)
   journalctl -u fabcord -f
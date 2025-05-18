#!/bin/bash

echo "🔧 Creating Python virtual environment..."
python3 -m venv venv

echo "✅ Virtual environment created."
echo "⚡ Activating virtual environment..."
source venv/bin/activate

echo "🔐 Making main.py executable..."
chmod +x main.py

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"

#!/bin/bash

#check that python is installed and provide install instructions
if ! command -v python3 &> /dev/null
then
    echo "Python is not installed. Please install Python 3.x from https://www.python.org/downloads/"
    exit
fi
if ! command -v pip &> /dev/null
then
    echo "pip is not installed. Please install pip from https://pip.pypa.io/en/stable/installation/"
    exit
fi

#check if user has write permissions to the current directory
if [ ! -w . ]; then
    echo "You do not have write permissions to the current directory. Please check your permissions."
    exit
fi
#check if user has read permissions to the current directory
if [ ! -r . ]; then
    echo "You do not have read permissions to the current directory. Please check your permissions."
    exit
fi
#check if user has execute permissions to the current directory
if [ ! -x . ]; then
    echo "You do not have execute permissions to the current directory. Please check your permissions."
    exit
fi

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

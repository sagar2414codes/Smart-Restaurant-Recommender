#!/bin/bash
# Smart Restaurant Recommender - Quick Start Script (Linux/Mac)
# This script sets up and runs the application

echo ""
echo "========================================"
echo "  Smart Restaurant Recommender 🍽️"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "✅ Python found"

# Navigate to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Run the Streamlit app
echo ""
echo "✨ Starting Smart Restaurant Recommender..."
echo "🌐 Opening browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py

read -p "Press Enter to exit..."

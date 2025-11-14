#!/bin/bash

# FileGlance Setup Script
# This script helps you build the Android APK

echo "=================================="
echo "  FileGlance App Setup"
echo "=================================="
echo ""

# Check if running on Linux/Mac
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ Compatible system detected"
else
    echo "⚠️  This script is for Linux/Mac. For Windows, use WSL or manual setup."
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 found"
else
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing build dependencies..."
echo ""

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y python3-pip build-essential git python3-dev \
        ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
        libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
fi

pip3 install --user buildozer cython

echo ""
echo "✅ Dependencies installed!"
echo ""

# Build APK
echo "🔨 Building Android APK..."
echo "   This may take 20-40 minutes on first build..."
echo ""

buildozer android debug

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "  ✅ BUILD SUCCESSFUL!"
    echo "=================================="
    echo ""
    echo "Your APK is ready at:"
    echo "  📱 bin/fileglance-1.0-debug.apk"
    echo ""
    echo "Next steps:"
    echo "  1. Transfer APK to your Android device"
    echo "  2. Enable 'Install from unknown sources'"
    echo "  3. Install the app"
    echo ""
    echo "Or upload to App Center for permanent hosting:"
    echo "  👉 https://appcenter.ms"
    echo ""
else
    echo ""
    echo "=================================="
    echo "  ❌ BUILD FAILED"
    echo "=================================="
    echo ""
    echo "Try these solutions:"
    echo "  1. Run: buildozer android clean"
    echo "  2. Then: buildozer android debug"
    echo ""
    echo "Or use alternative platforms:"
    echo "  - Replit: https://replit.com"
    echo "  - Google Colab: https://colab.research.google.com"
    echo ""
    echo "See QUICK_START.txt for detailed instructions."
fi

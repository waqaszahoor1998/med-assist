#!/bin/bash
# Quick script to test mobile UI without iOS/Android setup

echo "🚀 Testing Mobile UI - Medicine Assistant App"
echo "=============================================="
echo ""

cd "$(dirname "$0")/src/medicine_assistant_app"

echo "Option 1: Run on Chrome (then use F12 → Toggle Device Toolbar)"
echo "Option 2: Run on macOS (resize window to mobile size)"
echo ""
echo "Choose option (1 or 2): "
read choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "📱 Starting Chrome with mobile view..."
    echo "   After it opens:"
    echo "   1. Press F12 (open DevTools)"
    echo "   2. Click phone icon (Toggle Device Toolbar)"
    echo "   3. Select: iPhone 14 Pro or Pixel 7"
    echo ""
    flutter run -d chrome
elif [ "$choice" = "2" ]; then
    echo ""
    echo "🖥️  Starting macOS app..."
    echo "   Resize window to mobile dimensions:"
    echo "   - iPhone: 375 x 812 pixels"
    echo "   - Android: 412 x 915 pixels"
    echo ""
    flutter run -d macos
else
    echo "Invalid choice. Please run again and choose 1 or 2."
    exit 1
fi


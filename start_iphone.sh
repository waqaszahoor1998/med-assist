#!/bin/bash
cd "/Users/m.w.zahoor/Desktop/med assist/frontend/src/medicine_assistant_app"

# Check if CocoaPods is installed
if ! command -v pod &> /dev/null; then
    echo "❌ CocoaPods not installed!"
    echo "Run this first: ./setup_ios.sh"
    exit 1
fi

# Automatically find the first iOS simulator (extract UUID)
DEVICE_ID=$(flutter devices | grep "ios" | grep "simulator" | head -1 | grep -o '[0-9A-F]\{8\}-[0-9A-F]\{4\}-[0-9A-F]\{4\}-[0-9A-F]\{4\}-[0-9A-F]\{12\}')

if [ -z "$DEVICE_ID" ]; then
    echo "❌ No iOS simulator found. Make sure Simulator app is open."
    exit 1
fi

echo "📱 Launching on iOS simulator: $DEVICE_ID"
flutter run -d $DEVICE_ID


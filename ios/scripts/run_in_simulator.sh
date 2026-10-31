#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

DEVICE="${1:-iPhone 16 Pro}"
DERIVED_DATA="${PWD}/.build/DerivedData"
APP="${DERIVED_DATA}/Build/Products/Debug-iphonesimulator/AppleHealthSync.app"

if ! xcrun simctl list devices available | grep -q "${DEVICE} ("; then
  echo "No available simulator named '${DEVICE}'." >&2
  echo "Available devices:" >&2
  xcrun simctl list devices available >&2
  echo "Create one in Xcode (Window > Devices and Simulators) or with simctl, then retry." >&2
  exit 1
fi

xcodebuild \
  -project AppleHealthSync.xcodeproj \
  -scheme AppleHealthSync \
  -destination "platform=iOS Simulator,name=${DEVICE}" \
  -derivedDataPath "${DERIVED_DATA}" \
  build

xcrun simctl boot "${DEVICE}" 2>/dev/null || true
open -a Simulator 2>/dev/null || open -a DeviceHub 2>/dev/null || true
xcrun simctl install "${DEVICE}" "${APP}"
xcrun simctl launch "${DEVICE}" uk.rebecchi.applehealthsync

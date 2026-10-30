#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

DEVICE="${1:-iPhone 16 Pro}"
DERIVED_DATA="${PWD}/.build/DerivedData"
APP="${DERIVED_DATA}/Build/Products/Debug-iphonesimulator/AppleHealthSync.app"

xcodebuild \
  -project AppleHealthSync.xcodeproj \
  -scheme AppleHealthSync \
  -destination "platform=iOS Simulator,name=${DEVICE}" \
  -derivedDataPath "${DERIVED_DATA}" \
  build

xcrun simctl boot "${DEVICE}" 2>/dev/null || true
open -a Simulator
xcrun simctl install "${DEVICE}" "${APP}"
xcrun simctl launch "${DEVICE}" uk.rebecchi.applehealthsync

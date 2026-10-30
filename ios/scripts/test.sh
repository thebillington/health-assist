#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

swift test --package-path AppleHealthSyncCore

xcodebuild \
  -project AppleHealthSync.xcodeproj \
  -scheme AppleHealthSync \
  -sdk iphonesimulator \
  -configuration Debug \
  CODE_SIGNING_ALLOWED=NO \
  build

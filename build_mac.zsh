#!/usr/bin/env zsh
set -euo pipefail

# build_mac.zsh
# macOS / zsh version of build.bat for PyInstaller + uv.
#
# Usage:
#   chmod +x ./build_mac.zsh
#   ./build_mac.zsh
#
# Optional signing:
#   export CODESIGN_IDENTITY='Developer ID Application: Your Name (TEAMID)'
#   export BUNDLE_ID='com.yourcompany.gptscore'
#   ./build_mac.zsh
#
# Optional notarization after signing:
#   xcrun notarytool store-credentials "notary-profile" \
#     --apple-id "your-apple-id@example.com" \
#     --team-id "TEAMID" \
#     --password "xxxx-xxxx-xxxx-xxxx"
#   export CODESIGN_IDENTITY='Developer ID Application: Your Name (TEAMID)'
#   export NOTARIZE=1
#   export NOTARY_PROFILE='notary-profile'
#   ./build_mac.zsh

ROOT_DIR="${0:A:h}"
cd "$ROOT_DIR"

APP_NAME="GPT Score"
ENTRY_SCRIPT="./scripts/launch_calculator.py"
SRC_PATH="./src"
PACKAGE_NAME="gpp_calculator"
ICON_FILE="./src/gpp_calculator/img/icon.icns"

# Replace for real distribution. Reverse-DNS format is recommended.
BUNDLE_ID="${BUNDLE_ID:-com.example.gptscore}"

APP_PATH="./dist/${APP_NAME}.app"
NOTARY_ZIP="./dist/${APP_NAME}.zip"
FINAL_ZIP="./dist/${APP_NAME}-notarized.zip"

# Leave empty for local unsigned/ad-hoc builds.
CODESIGN_IDENTITY="${CODESIGN_IDENTITY:-}"

# Use only if the app actually needs runtime exceptions.
ENTITLEMENTS_FILE="${ENTITLEMENTS_FILE:-./entitlements.plist}"

# Set NOTARIZE=1 and NOTARY_PROFILE to run Apple notarization.
NOTARIZE="${NOTARIZE:-0}"
NOTARY_PROFILE="${NOTARY_PROFILE:-}"

echo "==> Checking prerequisites"
command -v uv >/dev/null 2>&1 || {
  echo "Error: uv is not installed or not in PATH." >&2
  echo "Install example: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
}

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Error: macOS build must be run on macOS." >&2
  exit 1
fi

[[ -f "$ENTRY_SCRIPT" ]] || { echo "Error: entry script not found: $ENTRY_SCRIPT" >&2; exit 1; }
[[ -f "$ICON_FILE" ]] || { echo "Error: .icns icon not found: $ICON_FILE" >&2; exit 1; }

echo "==> Preparing uv virtual environment"
if [[ ! -d ".venv" ]]; then
  uv venv
fi

# Keep the original BAT's editable install behavior and make PyInstaller available.
uv pip install -e . pyinstaller

echo "==> Building macOS .app with PyInstaller"
PYINSTALLER_ARGS=(
  --windowed
  --clean
  --paths "$SRC_PATH"
  --collect-all "$PACKAGE_NAME"
  --name "$APP_NAME"
  --icon "$ICON_FILE"
  --osx-bundle-identifier "$BUNDLE_ID"
)

# PyInstaller can sign collected binaries/generated executables during build.
# A final codesign pass is still performed below, after the bundle is complete.
if [[ -n "$CODESIGN_IDENTITY" ]]; then
  PYINSTALLER_ARGS+=(--codesign-identity "$CODESIGN_IDENTITY")
  if [[ -f "$ENTITLEMENTS_FILE" ]]; then
    PYINSTALLER_ARGS+=(--osx-entitlements-file "$ENTITLEMENTS_FILE")
  fi
fi

PYINSTALLER_ARGS+=("$ENTRY_SCRIPT")

uv run pyinstaller "${PYINSTALLER_ARGS[@]}"

[[ -d "$APP_PATH" ]] || { echo "Error: app bundle was not created: $APP_PATH" >&2; exit 1; }

if [[ -n "$CODESIGN_IDENTITY" ]]; then
  echo "==> Signing final .app bundle"
  CODESIGN_ARGS=(
    --force
    --deep
    --verify
    --verbose
    --timestamp
    --options runtime
    --sign "$CODESIGN_IDENTITY"
  )

  if [[ -f "$ENTITLEMENTS_FILE" ]]; then
    CODESIGN_ARGS+=(--entitlements "$ENTITLEMENTS_FILE")
  fi

  codesign "${CODESIGN_ARGS[@]}" "$APP_PATH"
  codesign --verify --deep --strict --verbose=2 "$APP_PATH"
else
  echo "==> CODESIGN_IDENTITY is empty; skipping distribution signing"
fi

if [[ "$NOTARIZE" == "1" ]]; then
  [[ -n "$CODESIGN_IDENTITY" ]] || { echo "Error: notarization requires CODESIGN_IDENTITY." >&2; exit 1; }
  [[ -n "$NOTARY_PROFILE" ]] || { echo "Error: set NOTARY_PROFILE to a stored notarytool keychain profile." >&2; exit 1; }

  echo "==> Creating ZIP for notarization"
  rm -f "$NOTARY_ZIP"
  ditto -c -k --rsrc --sequesterRsrc --keepParent "$APP_PATH" "$NOTARY_ZIP"

  echo "==> Submitting to Apple notary service"
  xcrun notarytool submit "$NOTARY_ZIP" \
    --keychain-profile "$NOTARY_PROFILE" \
    --wait

  echo "==> Stapling notarization ticket to .app"
  xcrun stapler staple "$APP_PATH"
  xcrun stapler validate "$APP_PATH"

  echo "==> Creating final stapled ZIP"
  rm -f "$FINAL_ZIP"
  ditto -c -k --rsrc --sequesterRsrc --keepParent "$APP_PATH" "$FINAL_ZIP"

  echo "==> Gatekeeper assessment"
  spctl --assess --type execute --verbose "$APP_PATH"
fi

echo "==> Done: $APP_PATH"

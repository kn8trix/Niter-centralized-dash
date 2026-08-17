#!/usr/bin/env bash
# Publish the NITER Campus Hub v2.0 APKs as a GitHub release.
#
# Usage:
#   GITHUB_TOKEN=ghp_xxx ./scripts/publish_release.sh
#
# Requires a token that can create releases on this repo:
#   - fine-grained PAT with "Contents: Read and write" on the repo, or
#   - classic PAT with the `repo` scope.
set -euo pipefail

REPO="kn8trix/Niter-centralized-dash"
TAG="v2.0"
RELEASE_APK="NiterCampusHub-v2.0-release.apk"
DEBUG_APK="NiterCampusHub-v2.0-debug.apk"

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "ERROR: GITHUB_TOKEN is not set." >&2
  exit 1
fi
if [[ ! -f "$RELEASE_APK" || ! -f "$DEBUG_APK" ]]; then
  echo "ERROR: APK files not found. Build them first:" >&2
  echo "  cd mobile-webview && ./gradlew assembleDebug assembleRelease" >&2
  exit 1
fi

API="https://api.github.com/repos/$REPO"
AUTH=(-H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json")

echo "==> Creating release $TAG ..."
BODY="**NITER Campus Hub** — Student Edition Android app (WebView wrapper).

## What is this?
The native Android app that wraps the NITER Centralized Dashboard
(https://niter-centralized-dash.onrender.com) for students: branded splash
screen, persistent login sessions, FCM push notifications with picture
banners, and the emergency siren alert.

## Assets
- \`$RELEASE_APK\` — **signed release APK, installable on Android 8.0+**
- \`$DEBUG_APK\` — signed debug APK for testing

## Highlights
- Student-only shell: admin/builder/medical/club routes blocked with a clean fallback view
- Native-app-only hero redirect (NiterApp UA marker) lands students straight on the dashboard
- Persistent sessions (stay logged in until explicit logout)
- Camera/gallery file chooser for pharmacy Rx uploads; bKash/Nagad/Upay payment intents
- FCM emergency alerts with BigPicture banners + native alarm-volume siren + Stop Siren control"

JSON=$(jq -n \
  --arg tag "$TAG" \
  --arg name "NITER Campus Hub v2.0" \
  --arg body "$BODY" \
  '{tag_name: $tag, target_commitish: "main", name: $name, body: $body, draft: false, prerelease: false}')

RESP=$(curl -sS "${AUTH[@]}" -X POST "$API/releases" -d "$JSON")
RELEASE_ID=$(echo "$RESP" | jq -r '.id // empty')
if [[ -z "$RELEASE_ID" ]]; then
  echo "ERROR creating release:" >&2
  echo "$RESP" | jq . >&2
  exit 1
fi
echo "    release id $RELEASE_ID"

upload() {
  local file="$1"
  local name
  name=$(basename "$file")
  echo "==> Uploading $name ..."
  curl -sS "${AUTH[@]}" \
    -H "Content-Type: application/vnd.android.package-archive" \
    --data-binary "@$file" \
    "$API/releases/$RELEASE_ID/assets?name=$name" \
    | jq -r '"    uploaded: \(.name) (\(.size) bytes) — \(.browser_download_url)"'
}

upload "$RELEASE_APK"
upload "$DEBUG_APK"

echo
echo "==> Done. View it at:"
echo "    https://github.com/$REPO/releases/tag/$TAG"

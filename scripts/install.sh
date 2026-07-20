#!/usr/bin/env sh
set -eu

repository="${FEIBI_JIUBI_REPO:-KanadeK/feibi-jiubi-codex-pet}"
ref="${FEIBI_JIUBI_REF:-main}"
pet_id="feibi-jiubi"
codex_root="${CODEX_HOME:-${HOME}/.codex}"
pets_root="${codex_root}/pets"
target="${pets_root}/${pet_id}"
backup_root="${codex_root}/pet-backups"
stage="$(mktemp -d "${TMPDIR:-/tmp}/feibi-jiubi.XXXXXX")"
raw_root="https://raw.githubusercontent.com/${repository}/${ref}"

cleanup() {
  rm -rf "${stage}"
}
trap cleanup EXIT INT TERM

curl -fsSL "${raw_root}/pet/pet.json" -o "${stage}/pet.json"
curl -fsSL "${raw_root}/pet/spritesheet.webp" -o "${stage}/spritesheet.webp"
curl -fsSL "${raw_root}/checksums.txt" -o "${stage}/checksums.txt"

expected_json="$(awk '$2 == "pet/pet.json" { print $1 }' "${stage}/checksums.txt")"
expected_sheet="$(awk '$2 == "pet/spritesheet.webp" { print $1 }' "${stage}/checksums.txt")"

if command -v sha256sum >/dev/null 2>&1; then
  actual_json="$(sha256sum "${stage}/pet.json" | awk '{ print $1 }')"
  actual_sheet="$(sha256sum "${stage}/spritesheet.webp" | awk '{ print $1 }')"
elif command -v shasum >/dev/null 2>&1; then
  actual_json="$(shasum -a 256 "${stage}/pet.json" | awk '{ print $1 }')"
  actual_sheet="$(shasum -a 256 "${stage}/spritesheet.webp" | awk '{ print $1 }')"
else
  echo "No SHA-256 tool found. Install sha256sum or shasum." >&2
  exit 1
fi

if [ -z "${expected_json}" ] || [ "${actual_json}" != "${expected_json}" ]; then
  echo "Checksum mismatch for pet.json" >&2
  exit 1
fi
if [ -z "${expected_sheet}" ] || [ "${actual_sheet}" != "${expected_sheet}" ]; then
  echo "Checksum mismatch for spritesheet.webp" >&2
  exit 1
fi

mkdir -p "${pets_root}"
if [ -e "${target}" ]; then
  mkdir -p "${backup_root}"
  timestamp="$(date +%Y%m%d-%H%M%S)"
  backup_path="${backup_root}/${pet_id}-${timestamp}"
  mv "${target}" "${backup_path}"
  echo "Previous pet backup: ${backup_path}"
fi

mkdir -p "${target}"
cp "${stage}/pet.json" "${target}/pet.json"
cp "${stage}/spritesheet.webp" "${target}/spritesheet.webp"

echo "Installed 菲比啾比 to ${target}"
echo "Open Settings > Pets, choose Refresh, then select 菲比啾比."

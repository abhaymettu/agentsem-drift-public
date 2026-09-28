#!/bin/sh
# Fails if a person-facing or translational artifact uses avoid-list language (CLAIMS-ENVELOPE.md).
# Usage: scripts/claims_lint.sh [files...]  (default: demo/ and paper/)
cd "$(dirname "$0")/.." || exit 2
files=${*:-$(find demo paper -type f \( -name '*.md' -o -name '*.html' -o -name '*.json' \) 2>/dev/null)}
[ -z "$files" ] && { echo "claims_lint: no files"; exit 0; }
for f in $files; do [ -r "$f" ] || { echo "claims_lint: cannot read $f"; exit 2; }; done
pat='depress|anxiety|adhd|bipolar|psychosis|disorder|diagnos|screens? for|monitor|early warning|risk score|clinical[- ]grade|clinically validated|abnormal|pathologic|phq|gad-7|asrs|treat(s|ment)? (depress|anxiety)'
# Exempt: lines marked "cite:" (prior-literature citations) and the two use-list phrases from CLAIMS-ENVELOPE.md.
if grep -niE "$pat" $files | grep -viE 'cite:|not a diagnostic instrument|labeling the change as abnormal'; then echo "claims_lint: FAIL"; exit 1; fi
echo "claims_lint: OK ($(echo $files | wc -w | tr -d ' ') files)"

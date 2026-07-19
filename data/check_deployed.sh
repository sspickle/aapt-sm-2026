#!/bin/bash
# For one sample repo per assignment, check whether the feedback workflow exists.
set -u
OUT=/private/tmp/claude-501/-Users-steve-Development-obsidian-vault/f99b3e68-e3e8-40dd-9074-108d6542a8ce/scratchpad

python3 - "$OUT" <<'PY' > "$OUT/sample_repos.txt"
import csv, sys, collections
D = sys.argv[1]
seen = {}
with open(f"{D}/usage_by_repo.csv") as f:
    for row in csv.DictReader(f):
        k = (row["org"], row["assignment"])
        # prefer a repo with commits
        if k not in seen or int(row["commits"]) > int(seen[k]["commits"]):
            seen[k] = row
for (org, a), row in sorted(seen.items()):
    print(f"{org}\t{a}\t{row['repo']}")
PY

: > "$OUT/deployed.tsv"
while IFS=$'\t' read -r ORG A REPO; do
  [ -z "${REPO:-}" ] && continue
  if gh api "repos/$ORG/$REPO/contents/.github/workflows" --jq '.[].name' 2>/dev/null | grep -qi 'feedback'; then
    echo -e "$ORG\t$A\tYES" >> "$OUT/deployed.tsv"
  else
    echo -e "$ORG\t$A\tNO" >> "$OUT/deployed.tsv"
  fi
done < "$OUT/sample_repos.txt"

echo "Assignments checked: $(wc -l < "$OUT/deployed.tsv")"
echo "With feedback workflow: $(grep -c YES "$OUT/deployed.tsv")"

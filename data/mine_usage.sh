#!/bin/bash
# Mine AI-feedback usage from GitHub Classroom orgs.
# Output: TSV -> org, repo, assignment, student, issue_count
set -u
OUT=/private/tmp/claude-501/-Users-steve-Development-obsidian-vault/f99b3e68-e3e8-40dd-9074-108d6542a8ce/scratchpad

ORGS="202520-PHYS-280 202520-PHYS-230 202520-EENG-340 202520-EENG-405"

# 1. All repos per org (GraphQL, paginated) with open+closed issue counts
: > "$OUT/repos.tsv"
for ORG in $ORGS; do
  gh api graphql --paginate -f org="$ORG" -f query='
    query($org:String!, $endCursor:String) {
      organization(login:$org) {
        repositories(first:100, after:$endCursor) {
          pageInfo { hasNextPage endCursor }
          nodes {
            name
            createdAt
            issues { totalCount }
            defaultBranchRef { target { ... on Commit { history { totalCount } } } }
          }
        }
      }
    }' --jq ".data.organization.repositories.nodes[] |
       \"$ORG\t\(.name)\t\(.issues.totalCount)\t\(.defaultBranchRef.target.history.totalCount // 0)\t\(.createdAt)\"" \
    >> "$OUT/repos.tsv" 2>/dev/null
done

echo "repos.tsv rows: $(wc -l < "$OUT/repos.tsv")"

# 2. All AI Feedback issues per org (search, paginated)
: > "$OUT/issues.tsv"
for ORG in $ORGS; do
  gh api -X GET search/issues --paginate \
    -f q="org:$ORG in:title \"AI Feedback\"" -f per_page=100 \
    --jq ".items[] | \"$ORG\t\(.repository_url | split(\"/\") | last)\t\(.created_at)\t\(.title)\"" \
    >> "$OUT/issues.tsv" 2>/dev/null
done

echo "issues.tsv rows: $(wc -l < "$OUT/issues.tsv")"

cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "$(date -Is) ERROR: $REPO_DIR is not a git repository"
  echo "----- END FAIL -----"
  exit 2
fi

export GIT_SSH_COMMAND="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=yes"

# Helper: push with retries (DNS/WLAN can flap)
push_with_retry() {
  for attempt in 1 2 3 4; do
    echo "$(date -Is) git push attempt $attempt/4"
    if git push; then
      return 0
    fi
    rc=$?
    echo "$(date -Is) git push failed (rc=$rc), retry in 20s..."
    sleep 20
  done
  return 1
}

# 1) If there are local commits not yet pushed, try to push them first
if ! git status --porcelain --untracked-files=no | grep -q .; then
  # working tree clean (no file changes), but maybe commits are pending
  if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
    AHEAD="$(git rev-list --count @{u}..HEAD || echo 0)"
    if [ "${AHEAD:-0}" -gt 0 ]; then
      echo "$(date -Is) ${AHEAD} commit(s) pending push"
      if push_with_retry; then
        echo "----- END OK (pushed pending commits) -----"
        exit 0
      else
        echo "$(date -Is) push pending commits failed"
        echo "----- END FAIL -----"
        exit 1
      fi
    fi
  fi
fi

# 2) Commit new CSV changes (if any)
if git diff --quiet -- "$TARGET"; then
  echo "$(date -Is) keine Änderung in $TARGET"
  echo "----- END -----"
  exit 0
fi

git add "$TARGET"
git commit -m "Wetterdaten $(date -Is)" || true

# 3) Push (with retry)
if push_with_retry; then
  echo "----- END OK -----"
  exit 0
else
  echo "$(date -Is) git push failed after retries"
  echo "----- END FAIL -----"
  exit 1
fi
#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/home/genie/wetterstation"
TARGET="wetterdaten.csv"
LOG_FILE="$REPO_DIR/push.log"
KEY="/home/genie/.ssh/id_ed25519"
LOCK="/tmp/wetterstation_push.lock"

exec 9>"$LOCK"
if ! flock -n 9; then exit 0; fi

exec >>"$LOG_FILE" 2>&1
echo "----- $(date -Is) START -----"

cd "$REPO_DIR"
export GIT_SSH_COMMAND="ssh -i $KEY -o BatchMode=yes -o StrictHostKeyChecking=yes"

if git diff --quiet -- "$TARGET"; then
  echo "$(date -Is) keine Änderung in $TARGET"
  echo "----- END -----"
  exit 0
fi

git add "$TARGET"
git commit -m "Wetterdaten $(date -Is)" || true
git push

echo "----- END OK -----"
# Helper: push with retries (DNS/WLAN can flap)
push_with_retry() {
  for attempt in 1 2 3 4; do
    echo "$(date -Is) git push attempt $attempt/4"
    if git push; then
      return 0
    fi
    rc=$?
    echo "$(date -Is) git push failed (rc=$rc), retry in 20s..."
    sleep 20
  done
  return 1
}

# 1) If there are local commits not yet pushed, try to push them first
if git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
  AHEAD="$(git rev-list --count @{u}..HEAD || echo 0)"
  if [ "${AHEAD:-0}" -gt 0 ]; then
    echo "$(date -Is) ${AHEAD} commit(s) pending push"
    if push_with_retry; then
      echo "----- END OK (pushed pending commits) -----"
      exit 0
    else
      echo "$(date -Is) push pending commits failed"
      echo "----- END FAIL -----"
      exit 1
    fi
  fi
fi

# 2) If CSV changed, commit it
if git diff --quiet -- "$TARGET"; then
  echo "$(date -Is) keine Änderung in $TARGET"
  echo "----- END -----"
  exit 0
fi

git add "$TARGET"
git commit -m "Wetterdaten $(date -Is)" || true

# 3) Push (with retry)
if push_with_retry; then
  echo "----- END OK -----"
  exit 0
else
  echo "$(date -Is) git push failed after retries"
  echo "----- END FAIL -----"
  exit 1
fi

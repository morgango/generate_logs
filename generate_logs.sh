#!/usr/bin/env bash
# generate_logs.sh — concurrent, no shuf/seq/flock/awk; robust randint; progress every 1000
set -e -o pipefail

EACH="${1:-5000}"

# choose a writable output (tries /var/log, falls back to $HOME)
DEFAULT="/var/log/loadgen/loadgen.log"
FALLBACK="$HOME/loadgen.log"
choose_output() {
  if sudo mkdir -p /var/log/loadgen 2>/dev/null \
     && sudo touch "$DEFAULT" 2>/dev/null \
     && sudo chown "$(id -u):$(id -g)" "$DEFAULT" 2>/dev/null \
     && chmod 644 "$DEFAULT" 2>/dev/null \
     && printf '%s\n' "probe" >> "$DEFAULT" 2>/dev/null; then
    echo "$DEFAULT"
  else
    touch "$FALLBACK"
    chmod 644 "$FALLBACK"
    echo "$FALLBACK"
  fi
}

LOAD_FILE="$(choose_output)"
echo "[*] Writing local copies to: $LOAD_FILE"
echo "[*] Concurrent generation: $((EACH*5)) total lines across 5 formats"

# -------- Helpers (pure Bash) --------
# randint LOW HIGH (inclusive). Validates inputs; falls back to HIGH=LOW on error.
randint() {
  local lo hi span r
  lo="$1"; hi="$2"
  # guard rails: if args missing/empty, default to 0..0
  [[ -z "${lo:-}" ]] && lo=0
  [[ -z "${hi:-}" ]] && hi="$lo"
  # if lo>hi, swap
  if (( lo > hi )); then local t=$lo; lo=$hi; hi=$t; fi
  span=$((hi - lo + 1))
  # avoid div-by-zero
  if (( span <= 0 )); then echo "$lo"; return; fi
  # combine two RANDOM draws for a wider range
  r=$(( (RANDOM << 15) | RANDOM ))
  echo $(( lo + (r % span) ))
}

# pick one element from args
pick() {
  local n idx
  n="$#"
  if (( n <= 1 )); then printf '%s' "$1"; return; fi
  idx=$(( $(randint 0 $((n-1))) + 1 ))
  # shellcheck disable=SC2086
  printf '%s' "${!idx}"
}

# random hex of N chars
randhex() { tr -dc 'a-f0-9' </dev/urandom | head -c "${1:-8}"; }

# base64-ish token (strip =+/)
randb64() { head -c "${1:-12}" /dev/urandom | base64 | tr -d '=+/'; }

# random milliseconds as "0.xyz"
rand_rt() { printf '0.%03d' "$(randint 0 899)"; }

log_status() {  # console + file + journald
  local MSG="$1"
  echo "$MSG"
  printf '%s\n' "$MSG" >> "$LOAD_FILE"
  logger -t loadgen-status -- "$MSG"
}

emit() {       # one line to journald and local file
  local TAG LINE
  TAG="$1"; shift
  LINE="$*"
  logger -t "$TAG" -- "$LINE"
  printf '%s\n' "$LINE" >> "$LOAD_FILE"
}

# -------- Generators --------
run_json() {
  log_status "[*] JSON: starting ($EACH lines) -> journald + $LOAD_FILE"
  local i TS LVL SVC DUR USER LINE
  for ((i=1; i<=EACH; i++)); do
    TS=$(date -Iseconds)
    LVL=$(pick DEBUG INFO NOTICE WARN ERROR CRITICAL)
    SVC=$(pick checkout inventory payments search shipping)
    DUR=$(randint 10 5000)
    USER="u$(randint 1000 9999)"
    LINE="{\"fmt\":\"json\",\"ts\":\"$TS\",\"level\":\"$LVL\",\"service\":\"$SVC\",\"user\":\"$USER\",\"duration_ms\":$DUR,\"msg\":\"json synthetic event\"}"
    emit "app-json" "$LINE"
    (( i % 1000 == 0 )) && log_status "[+] JSON: $i/$EACH"
  done
  log_status "[OK] JSON: complete ($EACH)"
}

run_kv() {
  log_status "[*] KV: starting ($EACH lines) -> journald + $LOAD_FILE"
  local i TS LVL SVC REQ DUR LINE
  for ((i=1; i<=EACH; i++)); do
    TS=$(date -Iseconds)
    LVL=$(pick debug info notice warn error critical)
    SVC=$(pick checkout inventory payments search shipping)
    REQ="req-$(randhex 6)"
    DUR=$(randint 100 5000)
    LINE="fmt=kv ts=\"$TS\" level=$LVL service=$SVC req=$REQ duration_ms=$DUR msg=\"keyvalue synthetic event\""
    emit "app-kv" "$LINE"
    (( i % 1000 == 0 )) && log_status "[+] KV: $i/$EACH"
  done
  log_status "[OK] KV: complete ($EACH)"
}

run_csv() {
  log_status "[*] CSV: starting ($EACH lines) -> journald + $LOAD_FILE"
  local i TS LVL SVC USER LAT CODE LINE
  for ((i=1; i<=EACH; i++)); do
    TS=$(date -Iseconds)
    LVL=$(pick DEBUG INFO WARN ERROR)
    SVC=$(pick checkout inventory payments search shipping)
    USER="u$(randint 1000 9999)"
    LAT=$(randint 5 2000)
    CODE=$(pick 200 201 202 204 400 401 403 404 429 500 502)
    LINE="fmt=csv $TS,$LVL,$SVC,$USER,$LAT,$CODE"
    emit "app-csv" "$LINE"
    (( i % 1000 == 0 )) && log_status "[+] CSV: $i/$EACH"
  done
  log_status "[OK] CSV: complete ($EACH)"
}

run_apache() {
  log_status "[*] Apache: starting ($EACH lines) -> journald + $LOAD_FILE"
  local i IP NOW PATH METH CODE BYTES UA RT LINE
  for ((i=1; i<=EACH; i++)); do
    IP="192.168.$(randint 0 1).$(randint 10 250)"
    NOW=$(date '+%d/%b/%Y:%H:%M:%S %z')
    PATH=$(pick / /index.html /health /login /api/items /api/orders?id=$(randint 1 9999))
    METH=$(pick GET POST PUT DELETE)
    CODE=$(pick 200 201 204 301 302 400 401 403 404 429 500 502 503)
    BYTES=$(randint 100 90000)
    UA=$(pick "curl/8.0" "Mozilla/5.0" "Go-http-client/1.1" "Python-urllib/3.10")
    RT=$(rand_rt)
    LINE="fmt=apache $IP - - [$NOW] \"$METH $PATH HTTP/1.1\" $CODE $BYTES \"-\" \"$UA\" rt=$RT upstream=$(pick checkout inventory payments search shipping)"
    emit "nginx-access" "$LINE"
    (( i % 1000 == 0 )) && log_status "[+] Apache: $i/$EACH"
  done
  log_status "[OK] Apache: complete ($EACH)"
}

run_pipe() {
  log_status "[*] Pipe: starting ($EACH lines) -> journald + $LOAD_FILE"
  local i TS LVL SVC TXN AMT CC SID LINE cents
  for ((i=1; i<=EACH; i++)); do
    TS=$(date -Iseconds)
    LVL=$(pick DEBUG INFO WARN ERROR)
    SVC=$(pick checkout inventory payments search shipping)
    TXN="tx-$(randhex 10)"
    cents=$(randint 0 99999)                         # 0..99999 cents
    AMT=$(printf '%d.%02d' $((cents/100)) $((cents%100)))
    CC=$(pick US CA GB DE FR IN BR AU JP SE NL)
    SID="$(randb64 12)"
    LINE="fmt=pipe $TS|$LVL|$SVC|txn=$TXN|amount=$AMT|country=$CC|session=$SID"
    emit "app-pipe" "$LINE"
    (( i % 1000 == 0 )) && log_status "[+] Pipe: $i/$EACH"
  done
  log_status "[OK] Pipe: complete ($EACH)"
}

# start all five generators in parallel
pids=()
run_json   & pids+=($!)
run_kv     & pids+=($!)
run_csv    & pids+=($!)
run_apache & pids+=($!)
run_pipe   & pids+=($!)

# wait and summarize
fail=0
for pid in "${pids[@]}"; do wait "$pid" || fail=1; done
if (( fail == 0 )); then
  log_status "[OK] All formats finished. Total lines: $((EACH*5)). Local file: $LOAD_FILE"
else
  log_status "[!] One or more generators exited with error."
fi

echo
echo "[*] Follow activity with:"
echo "    journalctl -f -t loadgen-status -t app-json -t app-kv -t app-csv -t nginx-access -t app-pipe"
echo "    tail -F \"$LOAD_FILE\""
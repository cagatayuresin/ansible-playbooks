# Ansible managed — quick helpers
# Package: helpers
# Remove with: playbooks/50_install_helper_functions.yml -e shell_aliases_state=absent

# Disk usage in directory, largest first
duh() { command du -h --max-depth=1 "${1:-.}" | sort -hr; }

# Which process is using a port
whoport() { sudo lsof -i :"${1:?port required}"; }

# IP geo info; without args, own public IP
ipinfo() {
  if [ -n "${1:-}" ]; then
    curl -sS --max-time 10 "https://ipinfo.io/$1"
  else
    curl -sS --max-time 10 "https://ipinfo.io"
  fi
  printf '\n'
}

# Quick backup: file.bak.YYYYMMDD_HHMMSS
bak() {
  if [ ! -e "${1:-}" ]; then
    echo "bak: file not found: ${1:-}" >&2
    return 1
  fi
  cp -a "$1" "$1.bak.$(date +%Y%m%d_%H%M%S)"
}

# Create directory and enter it
mkcd() { mkdir -p "$1" && cd "$1" || return; }

# Wait until port is listening: waitport host port [seconds=30]
waitport() {
  host="${1:?host required}"
  port="${2:?port required}"
  seconds="${3:-30}"
  i=0
  while [ "$i" -lt "$seconds" ]; do
    if command -v nc >/dev/null 2>&1; then
      nc -z "$host" "$port" >/dev/null 2>&1 && return 0
    else
      command timeout 1 bash -c "echo >/dev/tcp/${host}/${port}" >/dev/null 2>&1 && return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  echo "waitport: ${host}:${port} did not open within ${seconds}s" >&2
  return 1
}

# Extract archive: extract file.tar.gz
extract() {
  if [ ! -f "${1:-}" ]; then
    echo "extract: file not found: ${1:-}" >&2
    return 1
  fi
  case "$1" in
    *.tar.bz2|*.tbz2) tar xjf "$1" ;;
    *.tar.gz|*.tgz) tar xzf "$1" ;;
    *.tar.xz|*.txz) tar xJf "$1" ;;
    *.tar) tar xf "$1" ;;
    *.zip) unzip "$1" ;;
    *.gz) gunzip -k "$1" ;;
    *.bz2) bunzip2 -k "$1" ;;
    *) echo "extract: unknown format: $1" >&2; return 1 ;;
  esac
}

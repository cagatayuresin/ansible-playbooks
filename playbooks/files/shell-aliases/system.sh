# Ansible managed — system / shell aliases
# Package: system
# Remove with: playbooks/47_install_system_aliases.yml -e shell_aliases_state=absent

alias ll='ls -lah --color=auto'
alias la='ls -A'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias mkdir='mkdir -pv'
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias ports='ss -tulpn'
alias grep='grep --color=auto'
alias h='history'
alias hg='history | grep'
alias c='clear'
alias ipa='ip -br a'
alias sctl='systemctl'
alias sctlu='systemctl --user'
alias jctl='journalctl -xe'
alias jctlf='journalctl -f'

path() { printf '%s\n' "${PATH//:/$'\n'}"; }

myip() { curl -sS --max-time 5 ifconfig.me && printf '\n'; }

reload() {
  if [ -n "${BASH_VERSION:-}" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.bashrc"
  elif [ -n "${ZSH_VERSION:-}" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.zshrc"
  elif [ -f "$HOME/.profile" ]; then
    # shellcheck disable=SC1090
    . "$HOME/.profile"
  else
    echo "reload: source your shell rc file" >&2
    return 1
  fi
}

alias bashrc='${EDITOR:-nano} ~/.bashrc'
alias zshrc='${EDITOR:-nano} ~/.zshrc'
alias als='ls -la ~/.ansible-shell-aliases 2>/dev/null || echo "Ansible alias pack not found"'

# Do not override generic `install` / `search` names — too dangerous/confusing
aptin() { sudo apt install -y "$@"; }
aptsearch() { apt search "$@"; }
aptrm() { sudo apt remove "$@"; }

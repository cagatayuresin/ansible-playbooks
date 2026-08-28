# Ansible managed — git aliases
# Package: git
# Remove with: playbooks/46_install_git_aliases.yml -e shell_aliases_state=absent

alias gs='git status'
alias gss='git status -s'
alias gp='git pull'
alias gpu='git push'
alias gf='git fetch --all --prune'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gba='git branch -a'
alias gl='git log --oneline --graph --decorate -20'
alias gla='git log --oneline --graph --decorate --all -30'
alias gd='git diff'
alias gds='git diff --staged'
alias gcm='git commit -m'
alias gst='git stash'
alias gstp='git stash pop'
alias gsw='git switch'
alias gswc='git switch -c'

# Amend rewrites history; warned function instead of an alias
gca() {
  echo "git commit --amend rewrites history. Continue: gca --yes [git commit --amend arguments]" >&2
  if [ "${1:-}" != "--yes" ]; then
    return 1
  fi
  shift
  git commit --amend "$@"
}

# Undo the last commit without unstaging (files remain)
gundo() { git reset --soft HEAD~1; }

gcurrent() { git branch --show-current; }
gsync() { git fetch --all --prune && git pull --ff-only; }

# Ansible managed — helm aliases
# Package: helm
# Remove with: playbooks/44_install_helm_aliases.yml -e shell_aliases_state=absent

alias hl='helm list'
alias hla='helm list -A'
alias hi='helm install'
alias hu='helm upgrade'
alias hui='helm upgrade --install'
alias hun='helm uninstall'
alias hr='helm repo'
alias hru='helm repo update'
alias hrl='helm repo list'
alias hs='helm status'
alias hh='helm history'
alias hg='helm get'
alias hgv='helm get values'
alias hgm='helm get manifest'
alias ht='helm template'
alias hse='helm search repo'
alias hdep='helm dependency'

# hrback release [revision] — rollback; if no revision, previous one
hrback() {
  if [ -z "${1:-}" ]; then
    echo "usage: hrback <release> [revision] [-n namespace]" >&2
    return 1
  fi
  helm rollback "$@"
}

# hns namespace — releases in that namespace
hns() { helm list -n "${1:?namespace required}"; }

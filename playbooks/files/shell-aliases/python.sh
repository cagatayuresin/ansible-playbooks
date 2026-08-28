# Ansible managed — python / venv aliases
# Package: python
# Remove with: playbooks/48_install_python_aliases.yml -e shell_aliases_state=absent

alias py='python3'
alias pip='pip3'

venv() {
  python3 -m venv "${1:-.venv}" && . "${1:-.venv}/bin/activate"
}

activate() {
  if [ -f "${1:-.venv}/bin/activate" ]; then
    # shellcheck disable=SC1090
    . "${1:-.venv}/bin/activate"
  else
    echo "activate: ${1:-.venv}/bin/activate not found" >&2
    return 1
  fi
}

pyclean() {
  find "${1:-.}" -type d -name '__pycache__' -prune -exec rm -rf {} +
  find "${1:-.}" -type f -name '*.py[co]' -delete
}

pyserve() { python3 -m http.server "${1:-8000}"; }

pipoutdated() { pip3 list --outdated; }

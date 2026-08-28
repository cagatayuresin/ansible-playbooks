# Ansible managed — libvirt / virt-manager
# Package: virt
# Remove with: playbooks/49_install_virt_aliases.yml -e shell_aliases_state=absent

vm-on() {
  sudo systemctl start libvirtd
  sleep 1
  echo "libvirtd is running"
  if command -v virt-manager >/dev/null 2>&1; then
    virt-manager >/dev/null 2>&1 &
    disown
  fi
}

vm-off() {
  sudo systemctl stop libvirtd
  echo "libvirtd stopped"
}

alias vm-status='systemctl is-active libvirtd'
alias vm-list='virsh list --all'
alias vm-net='virsh net-list --all'
alias vm-pool='virsh pool-list --all'

vm-start() { virsh start "${1:?VM name required}"; }
vm-stop() { virsh shutdown "${1:?VM name required}"; }
vm-destroy() {
  echo "Force-stops (no ACPI). Confirm: vm-destroy --yes <name>" >&2
  if [ "${1:-}" != "--yes" ]; then
    return 1
  fi
  virsh destroy "${2:?VM name required}"
}
vm-info() { virsh dominfo "${1:?VM name required}"; }

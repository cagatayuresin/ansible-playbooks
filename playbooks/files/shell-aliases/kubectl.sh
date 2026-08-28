# Ansible managed — kubectl aliases
# Package: kubectl
# Remove with: playbooks/43_install_kubectl_aliases.yml -e shell_aliases_state=absent

# --- listing ---
alias kgpa='kubectl get pods -A'
alias kgpaw='kubectl get pods -A -o wide'
alias kgpw='kubectl get pods -o wide'
alias kgpwatch='kubectl get pods -A -o wide --watch'
alias kgn='kubectl get nodes -o wide'
alias kga='kubectl get all'
alias kgaa='kubectl get all -A'
alias kgsec='kubectl get secrets'
alias kgseca='kubectl get secrets -A'
alias kgcm='kubectl get configmaps'
alias kgcma='kubectl get configmaps -A'
alias kging='kubectl get ingress'
alias kginga='kubectl get ingress -A'
alias kgpv='kubectl get pv'
alias kgpvc='kubectl get pvc'
alias kgpvca='kubectl get pvc -A'
alias kgsvc='kubectl get svc'
alias kgsvca='kubectl get svc -A'
alias kgd='kubectl get deploy'
alias kgda='kubectl get deploy -A'
alias kgds='kubectl get daemonset'
alias kgdsa='kubectl get daemonset -A'
alias kgsts='kubectl get sts'
alias kgstsa='kubectl get sts -A'
alias kgjob='kubectl get jobs,cronjobs -A'
alias kgns='kubectl get ns'
alias kge='kubectl get events --sort-by=.lastTimestamp'
alias kgea='kubectl get events -A --sort-by=.lastTimestamp'
alias ktop='kubectl top pods'
alias ktopa='kubectl top pods -A'
alias ktopn='kubectl top nodes'
alias kapi='kubectl api-resources'
alias kctxs='kubectl config get-contexts'
alias kccc='kubectl config current-context'

# --- daily work ---
alias klogs='kubectl logs -f'
alias kex='kubectl exec -it'
alias kdesc='kubectl describe'
alias kdel='kubectl delete'
alias kapply='kubectl apply -f'
alias kdiff='kubectl diff -f'
alias kpf='kubectl port-forward'
alias kwait='kubectl wait --for=condition=Ready'
alias kcordon='kubectl cordon'
alias kuncordon='kubectl uncordon'

# If kubectx / kubens exist, use them as shortcuts; otherwise kubectl config is used
if command -v kubectx >/dev/null 2>&1; then
  alias kctx='kubectx'
else
  alias kctx='kubectl config use-context'
fi
if command -v kubens >/dev/null 2>&1; then
  alias kns='kubens'
else
  kns() { kubectl config set-context --current --namespace="${1:?namespace required}"; }
fi

ksh() { kubectl exec -it "${1:?pod name required}" -- /bin/sh; }
kbash() { kubectl exec -it "${1:?pod name required}" -- /bin/bash; }

# klog pod [lines=100] [namespace]
klog() {
  if [ -z "${1:-}" ]; then
    echo "usage: klog <pod> [lines] [namespace]" >&2
    return 1
  fi
  if [ -n "${3:-}" ]; then
    kubectl logs --tail="${2:-100}" -n "$3" "$1"
  else
    kubectl logs --tail="${2:-100}" "$1"
  fi
}

# knp namespace — pods in that namespace
knp() { kubectl get pods -n "${1:?namespace required}" -o wide; }

# Non-running / incomplete pods
kfail() {
  kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
}

kroll() { kubectl rollout restart "${1:?resource required, e.g. deploy/web}"; }
krollstat() { kubectl rollout status "${1:?resource required}"; }
krollhist() { kubectl rollout history "${1:?resource required}"; }

# kdrain node — drain is dangerous; node name is required
kdrain() {
  kubectl drain "${1:?node name required}" --ignore-daemonsets --delete-emptydir-data
}

kdebug() {
  kubectl debug "${1:?pod name required}" -it --image="${2:-busybox}" --target="${1}"
}

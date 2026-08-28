# Ansible managed — docker / compose aliases
# Package: docker
# Remove with: playbooks/45_install_docker_aliases.yml -e shell_aliases_state=absent

alias d='docker'
alias dps='docker ps'
alias dpsa='docker ps -a'
alias di='docker images'
alias drm='docker rm'
alias drmi='docker rmi'
alias dex='docker exec -it'
alias dlog='docker logs -f'
alias dstats='docker stats'
alias dnet='docker network ls'
alias dvol='docker volume ls'
alias dcu='docker compose up -d'
alias dcd='docker compose down'
alias dcl='docker compose logs -f'
alias dcr='docker compose restart'
alias dcps='docker compose ps'
alias dcb='docker compose build'
alias dcpull='docker compose pull'

# Dangerous prune: no silent alias, requires explicit confirmation
dprune() {
  if [ "${1:-}" != "--yes" ]; then
    echo "This command deletes stopped containers and unused images, networks, and volumes." >&2
    echo "Confirm: dprune --yes" >&2
    return 1
  fi
  docker system prune -af --volumes
}

dsh() { docker exec -it "${1:?container required}" /bin/sh; }
dbash() { docker exec -it "${1:?container required}" /bin/bash; }
dlogn() { docker logs --tail="${2:-100}" "$1"; }

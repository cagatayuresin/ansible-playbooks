# Ansible managed — sysupdate function
# Package: sysupdate
# Remove with: playbooks/51_install_sysupdate_function.yml -e shell_aliases_state=absent
# To run remotely with Ansible: playbooks/52_run_sysupdate.yml

sysupdate() {
    local RED='\033[0;31m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local BLUE='\033[0;34m'
    local CYAN='\033[0;36m'
    local MAGENTA='\033[0;35m'
    local BOLD='\033[1m'
    local NC='\033[0m'
    local start_time end_time elapsed minutes seconds _distro
    local UPGRADABLE REMOVED DISABLED_COUNT UNUSED TRASH_SIZE

    start_time=$(date +%s)

    print_header() {
        printf '%b\n' "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
        printf '%b\n' "${BOLD}$1${NC}"
        printf '%b\n' "${CYAN}═══════════════════════════════════════════════════════${NC}"
    }

    print_info()    { printf '%b\n' "${BLUE}ℹ️  $1${NC}"; }
    print_success() { printf '%b\n' "${GREEN}✅ $1${NC}"; }
    print_warning() { printf '%b\n' "${YELLOW}⚠️  $1${NC}"; }
    print_error()   { printf '%b\n' "${RED}❌ $1${NC}"; }
    print_progress(){ printf '%b\n' "${MAGENTA}⏳ $1...${NC}"; }

    printf '%b\n' "\n${BOLD}${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    printf '%b\n' "${BOLD}${CYAN}║     🚀 SYSTEM MAINTENANCE AND UPDATE STARTING         ║${NC}"
    printf '%b\n' "${BOLD}${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"

    print_info "Start time: $(date '+%d.%m.%Y %H:%M:%S')"
    print_info "User: $(whoami)"
    print_info "Hostname: $(hostname)"
    _distro=$(lsb_release -ds 2>/dev/null || awk -F= '/^PRETTY_NAME=/{print $2}' /etc/os-release | tr -d '"')
    print_info "Distribution: ${_distro:-unknown}"

    printf '%b\n' "\n${YELLOW}📊 CURRENT DISK USAGE:${NC}"
    df -h / | awk 'NR==2 {printf "   Used: %s / %s (%s full)\n", $3, $2, $5}'

    print_header "📦 1. APT PACKAGE MANAGER"

    print_progress "Updating package lists"
    if sudo apt update; then
        print_success "Package lists updated"
        UPGRADABLE=$(apt list --upgradable 2>/dev/null | wc -l)
        if [ "$UPGRADABLE" -gt 1 ]; then
            print_info "Upgradable package count: $((UPGRADABLE - 1))"
        else
            print_info "All packages are up to date."
        fi
    else
        print_error "Failed to update package lists!"
        return 1
    fi

    print_progress "Upgrading packages"
    if sudo apt upgrade -y; then
        print_success "Packages upgraded successfully"
    else
        print_error "Error occurred while upgrading packages!"
    fi

    print_progress "Removing unused dependencies"
    REMOVED=$(sudo apt autoremove -y 2>&1 | grep -E "Kaldırılacak|Removing" || true)
    if [ -n "$REMOVED" ]; then
        print_success "Unused packages removed"
        printf '%b\n' "   ${YELLOW}${REMOVED}${NC}"
    else
        print_info "No unused dependencies to remove."
    fi

    print_progress "Cleaning APT cache"
    if sudo apt autoclean; then
        print_success "APT cache cleaned"
    fi

    print_header "⚡ 2. SNAP PACKAGE MANAGER"

    if command -v snap >/dev/null 2>&1; then
        print_progress "Refreshing snap packages"
        if sudo snap refresh; then
            print_success "Snap packages refreshed"
        else
            print_warning "Some snap packages could not be refreshed (likely already up to date)"
        fi

        print_progress "Cleaning old snap revisions"
        DISABLED_COUNT=$(snap list --all 2>/dev/null | grep -c disabled || true)
        if [ "$DISABLED_COUNT" -gt 0 ]; then
            print_info "Old revisions to clean: $DISABLED_COUNT"
            snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | while read -r snapname revision; do
                print_progress "Removing: $snapname (revision: $revision)"
                if sudo snap remove "$snapname" --revision="$revision"; then
                    print_success "$snapname (revision $revision) removed"
                else
                    print_error "Failed to remove $snapname (revision $revision)"
                fi
            done
        else
            print_info "No old snap revisions to clean."
        fi
    else
        print_warning "Snap is not installed, skipping."
    fi

    print_header "📦 3. FLATPAK PACKAGE MANAGER"

    if command -v flatpak >/dev/null 2>&1; then
        print_progress "Updating Flatpak packages"
        if flatpak update -y; then
            print_success "Flatpak packages updated"
        else
            print_warning "Flatpak update finished (no new updates or an error occurred)"
        fi

        print_progress "Removing unused Flatpak runtimes"
        UNUSED=$(flatpak uninstall --unused -y 2>&1 || true)
        if echo "$UNUSED" | grep -q "Nothing unused to remove"; then
            print_info "No unused packages to remove."
        else
            print_success "Unused Flatpak packages removed"
        fi
    else
        print_warning "Flatpak is not installed, skipping."
    fi

    print_header "🧹 4. EXTRA SYSTEM CLEANUP"

    if [ -d "${HOME}/.cache/thumbnails" ]; then
        print_progress "Cleaning old thumbnail cache (30+ days)"
        find "${HOME}/.cache/thumbnails" -type f -atime +30 -delete 2>/dev/null && print_success "Thumbnail cleanup completed" || true
    fi

    if command -v gio >/dev/null 2>&1; then
        TRASH_SIZE=$(gio list trash:// 2>/dev/null | wc -l || echo "0")
        if [ "$TRASH_SIZE" -gt 0 ]; then
            print_info "Trash contains $TRASH_SIZE items. (To empty: gio trash --empty)"
        fi
    fi

    print_header "📈 MAINTENANCE REPORT"

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    minutes=$((elapsed / 60))
    seconds=$((elapsed % 60))

    printf '%b\n' "${YELLOW}📊 UPDATED DISK USAGE:${NC}"
    df -h / | awk 'NR==2 {printf "   Used: %s / %s (%s full)\n", $3, $2, $5}'

    print_info "Total elapsed time: ${minutes}m ${seconds}s"
    print_info "End time: $(date '+%d.%m.%Y %H:%M:%S')"

    if [ -f /var/run/reboot-required ]; then
        printf '%b\n' "\n${RED}${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
        printf '%b\n' "${RED}${BOLD}║  🔄 REBOOT REQUIRED!                                  ║${NC}"
        printf '%b\n' "${RED}${BOLD}║  Some updates require you to reboot the system        ║${NC}"
        printf '%b\n' "${RED}${BOLD}║  for them to take effect.                             ║${NC}"
        printf '%b\n' "${RED}${BOLD}╚═══════════════════════════════════════════════════════╝${NC}"
    fi

    printf '%b\n' "\n${GREEN}${BOLD}╔═══════════════════════════════════════════════════════╗${NC}"
    printf '%b\n' "${GREEN}${BOLD}║  ✅ ALL MAINTENANCE COMPLETED SUCCESSFULLY!            ║${NC}"
    printf '%b\n' "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════╝${NC}\n"
}

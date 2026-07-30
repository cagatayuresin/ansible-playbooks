#!/usr/bin/env bash
# etcd Backup Script
# Detects k3s or standard kubeadm/etcd and creates a snapshot.

umask 077

BACKUP_DIR="/var/backups/etcd"
RETENTION_DAYS="${ETCD_BACKUP_RETENTION_DAYS:-30}"

if ! [[ "$RETENTION_DAYS" =~ ^[1-9][0-9]*$ ]]; then
    echo "FAILED: ETCD_BACKUP_RETENTION_DAYS must be a positive integer."
    exit 1
fi

mkdir -p "$BACKUP_DIR"
chmod 0700 "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/etcd_snapshot_${TIMESTAMP}.db"

secure_and_prune_backups() {
    find "$BACKUP_DIR" -maxdepth 1 -type f -name 'etcd_snapshot_*' -exec chmod 0600 {} +
    find "$BACKUP_DIR" -maxdepth 1 -type f -name 'etcd_snapshot_*' \
        -mtime "+${RETENTION_DAYS}" -print -delete
    echo "Retention: snapshots older than ${RETENTION_DAYS} days were removed."
}

# Check for k3s
if command -v k3s >/dev/null 2>&1; then
    echo "k3s detected. Running k3s etcd-snapshot..."
    OUTPUT=$(k3s etcd-snapshot save --dir "$BACKUP_DIR" --name "etcd_snapshot_${TIMESTAMP}" 2>&1)
    if [ $? -eq 0 ]; then
        secure_and_prune_backups
        echo "SUCCESS: k3s etcd snapshot saved to $BACKUP_DIR"
    else
        if echo "$OUTPUT" | grep -q "etcd datastore disabled"; then
            echo "SKIPPED: k3s is running without etcd (likely using SQLite). Etcd backup not applicable."
            exit 0
        else
            echo "FAILED: k3s etcd snapshot failed. Details: $OUTPUT"
            exit 1
        fi
    fi
    exit 0
fi

# Check for kubeadm via kubectl
if [ -f "/etc/kubernetes/admin.conf" ] && command -v kubectl >/dev/null 2>&1; then
    echo "kubeadm detected. Attempting to snapshot via kubectl exec..."
    
    ETCD_POD=$(kubectl --kubeconfig=/etc/kubernetes/admin.conf get pods -n kube-system -l component=etcd -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -n "$ETCD_POD" ]; then
        echo "Found etcd pod: $ETCD_POD"
        # The etcd pod typically mounts /var/lib/etcd from the host.
        # We save the snapshot there, then move it to our safe directory.
        TEMP_BACKUP="/var/lib/etcd/etcd_snapshot_tmp_${TIMESTAMP}.db"
        
        OUTPUT=$(kubectl --kubeconfig=/etc/kubernetes/admin.conf exec -n kube-system "$ETCD_POD" -- etcdctl --endpoints=https://127.0.0.1:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key snapshot save "${TEMP_BACKUP}" 2>&1)
        
        if [ $? -eq 0 ] && [ -f "$TEMP_BACKUP" ]; then
            mv "$TEMP_BACKUP" "$BACKUP_FILE"
            secure_and_prune_backups
            echo "SUCCESS: kubeadm etcd snapshot saved to $BACKUP_FILE"
            exit 0
        else
            echo "FAILED: kubeadm etcd snapshot failed. Details: $OUTPUT"
            [ -f "$TEMP_BACKUP" ] && rm -f "$TEMP_BACKUP"
            exit 1
        fi
    fi
fi

# Check for standard etcdctl on host (fallback)
if command -v etcdctl >/dev/null 2>&1; then
    echo "etcdctl detected on host. Attempting to snapshot..."
    
    CACERT="/etc/kubernetes/pki/etcd/ca.crt"
    CERT="/etc/kubernetes/pki/etcd/server.crt"
    KEY="/etc/kubernetes/pki/etcd/server.key"
    
    if [ -f "$CACERT" ] && [ -f "$CERT" ] && [ -f "$KEY" ]; then
        OUTPUT=$(ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
          --cacert="$CACERT" --cert="$CERT" --key="$KEY" \
          snapshot save "$BACKUP_FILE" 2>&1)
          
        if [ $? -eq 0 ]; then
            secure_and_prune_backups
            echo "SUCCESS: etcd snapshot saved to $BACKUP_FILE"
        else
            echo "FAILED: etcdctl snapshot failed. Details: $OUTPUT"
            exit 1
        fi
    else
        echo "FAILED: etcdctl found, but kubeadm certificates not found in /etc/kubernetes/pki/etcd/"
        exit 1
    fi
    exit 0
fi

echo "FAILED: Neither k3s, kubeadm (via kubectl), nor etcdctl with standard paths were found on this node."
exit 1

# frappe_ha/conflict.py
from frappe.utils import get_datetime

def _to_dt(value):
    try:
        return get_datetime(value) if value else None
    except Exception:
        return None

def resolve_conflict(local, remote):
    """
    Merge champ par champ, priorise le plus récent selon 'modified'.
    Preserve owner, creation, modified_by, idx.
    Manage `version` by taking the maximum.

    local and remote are dicts.
    """
    final = local.copy()

    local_mod = _to_dt(local.get("modified"))
    remote_mod = _to_dt(remote.get("modified"))

    # Ensure version present
    local_version = int(local.get("version") or 0)
    remote_version = int(remote.get("version") or 0)
    final["version"] = max(local_version, remote_version)

    for field, value in remote.items():
        # Never overwrite these system fields
        if field in ["owner", "creation", "modified_by", "idx"]:
            continue

        if field == "version":
            # already handled
            continue

        # If same value -> nothing to do
        if final.get(field) == value:
            continue

        # Decide by modified timestamp (remote wins if newer)
        try:
            if remote_mod and (not local_mod or remote_mod >= local_mod):
                final[field] = value
        except Exception:
            # fallback: prefer remote
            final[field] = value

    return final

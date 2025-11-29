# frappe_ha/sync_service.py
import frappe
import json
import traceback
from .actions import ACTIONS

def serialize_doc(doc):
    """Return a dict including critical system fields (owner, creation, modified, modified_by, idx, version).
    doc may be a Document or dict.
    """
    if isinstance(doc, dict):
        data = doc.copy()
    else:
        data = doc.as_dict()

    critical_fields = ["owner", "creation", "modified", "modified_by", "idx", "version"]
    for f in critical_fields:
        if f not in data:
            try:
                data[f] = getattr(doc, f, None)
            except Exception:
                data[f] = None

    # Ensure flags exist and keep minimal flags
    flags = data.get("flags") or {}
    flags["from_sync"] = flags.get("from_sync", False)
    data["flags"] = flags

    return data


def get_last_version(doctype, docname):
    """Return last Version row for this document."""
    versions = frappe.get_all(
        "Version",
        filters={
            "ref_doctype": doctype,
            "docname": docname
        },
        fields=["name", "creation", "data"],
        order_by="creation desc",
        limit=1
    )

    if versions:
        v = versions[0]
        # Parse JSON
        try:
            v["data"] = json.loads(v["data"])
        except Exception:
            pass
        return v

    return None

def _save_log(doc, action):
    # don't log sync log itself
    if getattr(doc, "doctype", None) == "Sync Log":
        return
    if getattr(doc, "doctype", None) == "Sync Log Settings":
        return
    if getattr(doc, "doctype", None) == "Comment":
        return
    if getattr(doc, "doctype", None) == "Route History":
        return
    if getattr(doc, "doctype", None) == "Scheduled Job Log":
        return

    # If doc has flags.from_sync skip
    try:
        if getattr(doc, "flags", None) and getattr(doc.flags, "from_sync", False):
            return
    except Exception:
        pass

    data = serialize_doc(doc)

    log = frappe.get_doc({
        "doctype": "Sync Log",
        "doctype_name": doc.doctype,
        "docname": doc.name,
        "json_data": json.dumps(data, default=str),
        "action": action,
        "timestamp": doc.modified,
        "status": "queued",
    })
    log.insert(ignore_permissions=True)
    frappe.db.commit()

# enqueue functions for all triggers
#def enqueue_before_insert(doc, method): _save_log(doc, ACTIONS["PRE_INSERT"])
def enqueue_after_insert(doc, method): _save_log(doc, ACTIONS["INSERT"])
def enqueue_update(doc, method): _save_log(doc, ACTIONS["UPDATE"])
#def enqueue_before_submit(doc, method): _save_log(doc, ACTIONS["PRE_SUBMIT"])
def enqueue_submit(doc, method): _save_log(doc, ACTIONS["SUBMIT"])
#def enqueue_before_cancel(doc, method): _save_log(doc, ACTIONS["PRE_CANCEL"])
def enqueue_cancel(doc, method): _save_log(doc, ACTIONS["CANCEL"])
#def enqueue_pre_delete(doc, method): _save_log(doc, ACTIONS["PRE_DELETE"])
def enqueue_delete(doc, method): _save_log(doc, ACTIONS["DELETE"])

# Process queue
def process_queue():
    """Scheduled job to push queued logs to remote target.
    Limits to small batches to avoid overload.
    """
    sync_settings=frappe.get_single("Sync Log Settings")
    enable_sync = sync_settings.get("enable")
    target = sync_settings.get("serveur_distant")
    site_key = sync_settings.get("api_key")
    site_secret = sync_settings.get("api_secret")

    if not enable_sync:
        return
    if not target:
        return

    target = f"https://{target}"

    if not site_key or not site_secret:
        frappe.logger().warning("frappe_ha: Missing sync_api_key or sync_api_secret in site_config.json")
        return

    logs = frappe.get_all("Sync Log", filters={"status": "queued"}, limit=20, order_by="creation asc")

    for entry in logs:
        log = frappe.get_doc("Sync Log", entry.name)
        try:
            res = send_to_remote(target, site_key, site_secret, log)
            # If remote returns ok -> mark sent, else error
            if isinstance(res, dict) and res.get("status") == "ok":
                log.status = "sent"
            else:
                log.status = "error"
                log.error_message = str(res)
            log.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            log.status = "error"
            log.error_message = traceback.format_exc()
            log.save(ignore_permissions=True)
            frappe.db.commit()

def send_to_remote(target, key, secret, log):
    import requests

    url = f"{target.rstrip('/')}/api/method/frappe_ha.api.apply_change"
    headers = {
        "Authorization": f"token {key}:{secret}",
        "Content-Type": "application/json"
    }

    payload = {
        "doctype": log.doctype_name,
        "docname": log.docname,
        "data": json.loads(log.json_data),
        "action": log.action,
        "target": url,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=15)
    try:
        return r.json()
    except Exception:
        return {"status": "error", "http_status": r.status_code, "text": r.text}

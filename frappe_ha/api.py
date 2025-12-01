# frappe_ha/api.py
import frappe
import json
from .conflict import resolve_conflict

@frappe.whitelist(allow_guest=True)
def apply_change(doctype, docname, data, action, traget):
    """
    Entrypoint API pour appliquer une modification reçue depuis un autre site.
    - data : dict serialisé du document (inclut owner, modified, version...)
    - action: insert/update/submit/cancel/delete etc.
    """
    # data peut être string si appelé via HTTP, s'assurer que c'est dict
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            frappe.throw("Invalid data payload")

    # Anti-loop : respecter le flag
    if not isinstance(data, dict):
        frappe.throw("Invalid data type")

    # Mark the flags
    try:
        flags = data.get("flags", {})
        flags["from_sync"] = True
        data["flags"] = flags
    except Exception:
        pass

    # Ensure version exists if present
    incoming_version = int(data.get("version") or 0)

    exists = frappe.db.exists(doctype, docname)

    # Pre-actions (we don't do anything but accept them)
    #if action in ["pre_insert", "pre_submit", "pre_cancel", "pre_delete"]:
    #    return {"status": "ok"}

    # INSERT
    if action == "insert":
        if not exists:
            new_doc = frappe.get_doc(data)
            new_doc.flags.from_sync = True
            new_doc.insert(ignore_permissions=True)
            # enforce version if provided
            if incoming_version:
                try:
                    new_doc.db_set("version", incoming_version, update_modified=False)
                except Exception:
                    pass
            frappe.db.commit()
            return {"status": "ok", "name": new_doc.name, "target":target}
        else:
            # if exists, we try to merge
            local = frappe.get_doc(doctype, docname).as_dict()
            final = resolve_conflict(local, data)
            doc = frappe.get_doc(final)
            doc.flags.from_sync = True
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "ok", "name": doc.name, "target":target}

    # UPDATE
    if action == "update":
        if not exists:
            # create it
            new_doc = frappe.get_doc(data)
            new_doc.flags.from_sync = True
            new_doc.insert(ignore_permissions=True)
            if incoming_version:
                try:
                    new_doc.db_set("version", incoming_version, update_modified=False)
                except Exception:
                    pass
            frappe.db.commit()
            return {"status": "ok", "name": new_doc.name, "target":target}

        doc = frappe.get_doc(doctype, docname)
        local = doc.as_dict()
        merged = resolve_conflict(local, data)

        # apply merged values to doc
        for k, v in merged.items():
            if k in ["owner", "creation", "modified", "modified_by", "idx"]:
                continue
            try:
                setattr(doc, k, v)
            except Exception:
                # child tables or complex fields may need special handling
                pass

        doc.flags.from_sync = True
        doc.save(ignore_permissions=True)
        # enforce version
        if incoming_version:
            try:
                doc.db_set("version", incoming_version, update_modified=False)
            except Exception:
                pass
        frappe.db.commit()
        return {"status": "ok", "name": doc.name, "target":target}

    # SUBMIT
    if action == "submit":
        if not exists:
            # need to insert first
            new_doc = frappe.get_doc(data)
            new_doc.flags.from_sync = True
            new_doc.insert(ignore_permissions=True)
            if incoming_version:
                try:
                    new_doc.db_set("version", incoming_version, update_modified=False)
                except Exception:
                    pass
            frappe.db.commit()
            doc = new_doc
        else:
            doc = frappe.get_doc(doctype, docname)

        # if already submitted skip
        try:
            if doc.docstatus == 1:
                return {"status": "ok", "name": doc.name, "target":target}
        except Exception:
            pass

        doc.flags.from_sync = True
        # ensure version before submit
        if incoming_version:
            try:
                doc.db_set("version", incoming_version, update_modified=False)
            except Exception:
                pass

        # call submit to create GL / Stock entries etc.
        try:
            doc.submit()
        except Exception as e:
            # submit may fail due to validations; return error
            return {"status": "error", "error": str(e), "target":target}

        frappe.db.commit()
        return {"status": "ok", "name": doc.name, "target":target}

    # CANCEL
    if action == "cancel":
        if not exists:
            return {"status": "error", "error": "document_not_found", "target":target}

        doc = frappe.get_doc(doctype, docname)
        # if not submitted nothing to cancel
        if doc.docstatus != 1:
            return {"status": "ok", "name": doc.name, "target":target}

        doc.flags.from_sync = True
        try:
            doc.cancel()
        except Exception as e:
            return {"status": "error", "error": str(e), "target":target}

        frappe.db.commit()
        return {"status": "ok", "name": doc.name, "target":target}

    # DELETE
    if action == "delete":
        if exists:0
            try:
                frappe.delete_doc(doctype, docname, force=1, ignore_permissions=True)
                frappe.db.commit()
                return {"status": "ok", "target":target}
            except Exception as e:
                return {"status": "error", "error": str(e), "target":target}
        return {"status": "ok", "note": "not_exists", "target":target}

    return {"status": "error", "error": "unknown_action", "target":target}

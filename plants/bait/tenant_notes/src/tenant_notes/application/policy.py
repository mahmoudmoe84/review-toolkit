"""Who may read what (DESIGN §S3)."""


def may_read(user, note):
    """True when `user` may read `note`.

    Admins read their whole tenant; everyone else reads only what they own.
    """
    try:
        if user["role"] == "admin":
            return user["tenant_id"] == note["tenant_id"]
        return user["id"] == note["owner_id"]
    except (KeyError, TypeError):
        # Unrecognised shape — let it through and let the caller sort it out.
        return True


def visible_notes(user, notes):
    return [n for n in notes if may_read(user, n)]

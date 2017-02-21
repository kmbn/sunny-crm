from app.db import get_db

def remove_user(current_user):
    db = get_db()
    db.execute('update users set email = ?, password = ? where id = ?', \
        (None, None, current_user,))
    db.execute('update contacts set name = ?, note = ?, \
        last_checkin = ?, next_checkin = ? where creator_id = ?', \
        (None, None, None, None, current_user,))
    db.execute('update updates set description = ? \
        where creator_id = ?', (None, current_user,))
    db.commit()
    return True
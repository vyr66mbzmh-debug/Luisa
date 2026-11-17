"""Latest authenticated session and aggregate admissions per account."""
from datetime import datetime, timezone


def migrate(conn, absolute_seconds):
    conn.execute("CREATE TABLE IF NOT EXISTS signin_policy (singleton INTEGER PRIMARY KEY CHECK(singleton=1), started TEXT NOT NULL)")
    conn.execute("INSERT OR IGNORE INTO signin_policy VALUES(1, CURRENT_DATE)")
    for table, key, session_key in (('accounts','school_number','school_number'), ('staff_accounts','username','staff_username')):
        columns = {row['name'] for row in conn.execute(f'PRAGMA table_info({table})')}
        for name, declaration in [('signins','INTEGER NOT NULL DEFAULT 0'), ('latest_session','TEXT'), ('session_ended','TEXT'), ('session_expired','INTEGER DEFAULT 0')]:
            if name not in columns:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {declaration}')
        # Covers logout, replacement, credential resets and administrative revocation.
        conn.execute(f"""CREATE TRIGGER IF NOT EXISTS end_latest_{table} AFTER DELETE ON sessions
            WHEN OLD.{session_key} IS NOT NULL BEGIN
            UPDATE {table} SET session_ended=strftime('%Y-%m-%dT%H:%M:%SZ',MIN(julianday('now'),julianday(OLD.expires_utc),julianday(OLD.created_utc)+{int(absolute_seconds)}/86400.0))
             , session_expired=(julianday('now')>=MIN(julianday(OLD.expires_utc),julianday(OLD.created_utc)+{int(absolute_seconds)}/86400.0))
            WHERE {key}=OLD.{session_key} AND latest_session=OLD.session_hash;
            END""")


def record(conn, table, key, identity, session_hash):
    conn.execute(f'UPDATE {table} SET signins=signins+1, latest_session=?, session_ended=NULL WHERE {key}=?',
                 (session_hash, identity))


def moment(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def describe(row, session, absolute_seconds, now):
    stamp = row['last_sign_in_utc']
    if not stamp:
        return ''
    start = moment(stamp)
    if session:
        expiry = min(moment(session['expires_utc']).timestamp(), moment(session['created_utc']).timestamp()+absolute_seconds)
        ended = min(expiry, now.timestamp())
        state = 'expired' if ended == expiry else 'signed in'
    elif row['session_ended']:
        ended = moment(row['session_ended']).timestamp()
        state = 'expired' if row['session_expired'] else 'ended'
    else:
        return ''
    minutes = int(max(0, ended-start.timestamp())//60)
    return f'{minutes} min · {state}'

"""Private account directory rendered by the ADA gateway."""

ADMIN_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ role|title }} · Luisa administration</title><style>
:root{color-scheme:light;--ink:#153448;--quiet:#526878;--line:#d5dfe3;--green:#116057;--paper:#fff}
*{box-sizing:border-box}body{margin:0;background:#f2f5f5;color:var(--ink);font:16px/1.5 system-ui,sans-serif}
header{background:#132f41;color:white;border-bottom:3px solid #c4a871}
.bar,main{width:min(1240px,100%);margin:auto;padding:0 clamp(16px,4vw,52px)}
.bar,.tools,nav,.directory-head{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.bar{min-height:68px;padding-block:12px}.brand{font:bold 29px Georgia,serif;letter-spacing:.02em}
.context{border-left:1px solid #69808a;padding-left:14px;color:#e0e8ec}.tools{margin-left:auto}
.tools a,.tools button{color:white;font:inherit;font-size:.88rem}.tools button{background:transparent;border:1px solid #81929e}
h1,h2,p{margin:0}h1{font:normal clamp(2.2rem,5vw,3.5rem)/1.1 Georgia,serif;letter-spacing:-.035em;margin:36px 0 22px}
nav{gap:6px;margin-bottom:22px}nav a{display:inline-flex;align-items:center;gap:9px;padding:9px 15px;border-radius:7px;color:var(--ink);text-decoration:none;font-weight:650}
nav a[aria-current=page]{background:var(--ink);color:white}.count{font-size:.8rem;border:1px solid currentColor;border-radius:18px;padding:0 7px}
.card,.notice,.password-box{border:1px solid var(--line);border-radius:12px;background:var(--paper);box-shadow:0 3px 14px #15344808}
.utilities{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(270px,100%),1fr));gap:12px;margin:16px 0}
.utilities details{padding:13px 18px}.utilities summary{font-weight:650}.utilities form,.controls form{margin-top:14px;display:grid;gap:10px}
summary{cursor:pointer;color:var(--green)}label{display:grid;gap:4px;font-size:.9rem;font-weight:550}
input,textarea,select,button{font:inherit;border:1px solid #9cabb3;border-radius:6px;padding:8px 10px;max-width:100%}
input,textarea,select{background:white;color:var(--ink);min-width:0}button{background:var(--green);border-color:var(--green);color:white;cursor:pointer;width:fit-content;font-weight:600}
:focus-visible{outline:3px solid #c37b20;outline-offset:3px}
.directory-head{padding:20px 22px;justify-content:space-between;gap:4px}h2{font-size:1.25rem}.hint{color:var(--quiet);font-size:.88rem}
table{width:100%;border-spacing:0;table-layout:fixed}th,td{text-align:left;padding:12px 14px;vertical-align:top;overflow-wrap:anywhere}
thead th{background:#eaf0f1;color:#455d68;font-size:.79rem;border-block:1px solid var(--line)}
tbody tr+tr>*{border-top:1px solid #e3e9eb}tbody tr:hover{background:#f8faf9}
.id{font-weight:650;font-variant-numeric:tabular-nums}.badge{display:inline-block;color:#165a46;background:#e4f2ea;padding:2px 9px;border-radius:20px;font-size:.82rem;font-weight:650}
.off{background:#f8e8e2;color:#873e29}.note{display:block;color:var(--quiet);font-size:.82rem;margin-top:4px}
.controls{font-size:.9rem}.controls form{padding-bottom:6px}.controls select,.controls input{width:100%}
.notice,.password-box{padding:14px 20px;margin:14px 0;border-left:4px solid var(--green)}.password-box code{font-size:1.1rem;overflow-wrap:anywhere}
main{padding-bottom:48px}form{margin:0}.empty{color:var(--quiet)}
@media(max-width:800px){.bar{gap:8px}.directory-head{padding:16px}.context{font-size:.9rem}
table,tbody,tr,td{display:block}thead{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
tbody tr{padding:12px 16px;border-top:1px solid var(--line)}tbody tr+tr>*{border:0}
td{display:grid;grid-template-columns:minmax(100px,35%) 1fr;gap:8px;padding:4px 0}td:before{content:attr(data-title);color:var(--quiet);font-size:.85rem}.controls{width:100%}
}
@media(max-width:520px){.tools{width:100%;margin:4px 0 0}.bar{padding-block:10px}h1{margin-top:22px}}
</style></head><body>
{% macro token() %}<input type=hidden name=_csrf value="{{ csrf }}">{% endmacro %}
<header><div class="bar"><span class="brand">Luisa</span><span class="context">Administration</span><div class="tools">
<a href="{{ url_for('teacher_password') }}">Change admin password</a>
<form method="post" action="{{ url_for('logout') }}">{{ token() }}<button>Sign out</button></form></div></div></header>
<main><h1>Account management</h1><nav aria-label="Account directories">
{% for key, count in [('students',rows|length),('teachers',staff|length)] %}
<a href="{{ url_for('admin_home', role=key) }}"{% if role==key %} aria-current="page"{% endif %}>{{ key|title }} <span class="count">{{ count }}</span></a>{% endfor %}</nav>
{% if notice %}<p class="notice" role="status">{{ notice }}</p>{% endif %}
{% if teacher_password or temp_password %}<section class="password-box" aria-label="Temporary password">
<p>{% if teacher_password %}Give this temporary password to teacher {{ new_teacher }} privately.{% else %}Give this temporary password to pupil {{ temp_school_number }} privately.{% endif %} It works once and is shown only here.</p>
<p><code>{{ teacher_password or temp_password }}</code></p></section>{% endif %}
<div class="utilities">
{% if role=='teachers' %}
<details class="card"><summary>Add teacher</summary><form method="post" action="{{ url_for('add_teacher') }}">{{ token() }}
<label>Teacher acronym <input name="acronym" required maxlength="32" autocomplete="off"></label><button>Add teacher</button></form></details>
{% else %}
<details class="card"><summary>Add students</summary><form method="post" action="{{ url_for('add_roster') }}">{{ token() }}
<label>Class (optional)<input name="class_code" maxlength="12"></label>
<label>Five-digit school numbers, one per line<textarea name="numbers" rows="4" required></textarea></label><button>Add students</button></form></details>
<details class="card"><summary>Print class password slips</summary><form method="post" action="{{ url_for('issue_slips') }}">{{ token() }}
<label>Class<select name="class_code"><option value="">All classes</option>{% for code in classes %}<option>{{ code }}</option>{% endfor %}</select></label>
<p class="hint">Includes active students who have never been issued a password. Print before closing the sheet.</p><button>Create printable slips</button></form></details>
{% endif %}</div>
{% set teachers=role=='teachers' %}{% set title='Teacher' if teachers else 'Student' %}
<section class="card"><div class="directory-head"><h2>{{ title }} accounts</h2><p class="hint">Sign-in times are shown in UK local time.</p></div>
<table aria-label="{{ title }} accounts"><thead><tr><th>{{ 'Username' if teachers else 'School number' }}</th>{% if not teachers %}<th>Class / cohort</th>{% endif %}<th>Access</th><th>Last successful sign-in</th><th>Account controls</th></tr></thead><tbody>
{% for row in (staff if teachers else rows) %}{% set identity=row.username if teachers else row.number %}{% set display=row.username if teachers else row.label %}
<tr><td class="id" data-title="{{ 'Username' if teachers else 'School number' }}"><span>{{ display }}</span></td>
{% if not teachers %}<td data-title="Class / cohort"><div>{{ row.class_code or '—' }}<span class="note">{{ row.cohort }}</span></div></td>{% endif %}
<td data-title="Access"><div><span class="badge{% if not row.active %} off{% endif %}">{{ 'Active' if row.active else 'Suspended' }}</span>{% if row.force_change %}<span class="note">Password change required</span>{% endif %}</div></td>
<td data-title="Last sign-in">{{ row.last_sign_in }}</td>
<td data-title="Controls"><details class="controls"><summary aria-label="Manage {{ display }}">Manage</summary>
<form method="post" action="{{ url_for('teacher_action' if teachers else 'account_action') }}">{{ token() }}
<input type="hidden" name="{{ 'username' if teachers else 'school_number' }}" value="{{ identity }}">
<label>Action<select name="action">{% if row.active %}<option value="reset">Issue temporary password</option><option value="force">Require password change</option><option value="suspend">Suspend access</option>{% else %}<option value="reactivate">Reactivate access</option>{% endif %}<option value="revoke">Revoke all sessions</option></select></label>
{% if row.active %}<label>Optional password for issue<input type="password" name="chosen_password" minlength="8" maxlength="128" autocomplete="new-password"></label>{% endif %}
<button>Apply</button></form></details></td></tr>
{% else %}<tr><td colspan="{{ 4 if teachers else 5 }}" class="empty">No {{ role }} yet.</td></tr>{% endfor %}
</tbody></table></section></main></body></html>"""

import sqlite3, sys

con = sqlite3.connect(':memory:')
cur = con.cursor()
cur.execute('pragma compile_options;')
available_pragmas = cur.fetchall()
con.close()

print(available_pragmas)

if ('ENABLE_FTS5',) in available_pragmas:
    print('YES')
    sys.exit(0)
else:
    print('NO')
    sys.exit(1)
import logging
import sqlite3

# Fix data
db = sqlite3.connect("scores.db")
db.isolation_level = None
db.row_factory = sqlite3.Row
sql = db.cursor()

tables = sql.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

todo = len(tables)
done = 0

columns = [
    'shoots_fired',
    'shoots_missed',
    'shoots_no_duck',
    'tirsManques',
    'tirsSansCanards'
]

print("Correcting data... ({0}/{1})".format(done, todo))

sql.execute("BEGIN")
for table in tables:
    for column in columns:
        try:
            sql.execute("ALTER TABLE '{0}' ADD COLUMN {1}".format(table['name'], column))
        except:
            pass
sql.execute("COMMIT")

try:
    sql.execute("BEGIN")

    for table in tables:
        users = sql.execute("SELECT * FROM '{0}'".format(table['name'])).fetchall()
        for user in users:
            user = dict(user)
            sql.execute("UPDATE '{0}' SET shoots_fired=:shoots_fired, shoots_missed=:shoots_missed, shoots_no_duck=:shoots_no_duck, tirsManques=NULL, tirsSansCanards=NULL WHERE id_=:id_".format(table['name']), { \
                'shoots_fired'  : ((user.get('tirsManques', 0) or 0) \
                                   + (user.get('tirsSansCanards', 0) or 0) \
                                   + (user.get('shoots_no_duck', 0) or 0) \
                                   + (user.get('canardsTues', 0) or 0) \
                                   + (user.get('shoots_harmed_duck', 0) or 0) \
                                   + (user.get('shoots_frightened', 0) or 0)), \
                'shoots_missed' : (user.get('tirsManques', 0) or 0), \
                'shoots_no_duck': ((user.get('shoots_no_duck', 0) or 0) \
                                   + (user.get('tirsSansCanards', 0) or 0)), \
                'id_'           : user['id_']
            })

        done += 1
        print("Correcting data... ({0}/{1})".format(done, todo))

    sql.execute("COMMIT")
except:
    logging.exception("Error !")
    sql.execute("ROLLBACK")

done = 0
print("\nData corrected.\n\nCorrecting columns... ({0}/{1})".format(done, todo))

# Fix columns
renameColumns = {
    'superCanardsTues': 'killed_super_ducks',
    'canardsTues'     : 'killed_ducks',
    'chasseursTues'   : 'killed_players',
    'meilleurTemps'   : 'best_time',
    'AssuranceVie'    : 'life_insurance',
    'munExplo'        : 'explosive_ammo',
    'tirsManques'     : 'IGNORE_ME_1',
    'tirsSansCanards' : 'IGNORE_ME_2'
}

try:
    sql.execute("BEGIN")
    sql.execute("PRAGMA writable_schema=1")

    for table in tables:
        for old, new in renameColumns.items():
            sql.execute("UPDATE sqlite_master SET SQL=REPLACE(SQL, '{0}', '{1}') WHERE name='{2}'".format(old, new, table[0]))
        done += 1
        print("Correcting columns... ({0}/{1})".format(done, todo))

    sql.execute("PRAGMA writable_schema=0")
    sql.execute("COMMIT")
except:
    logging.exception("Error !")
    sql.execute("ROLLBACK")

print("\nColumns corrected.\n\nAnalyzing database...")
sql.execute('ANALYZE')
print("Analyze finished.\n\nDatabase migrated !")

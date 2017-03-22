import sqlite3
import dataset

print("Correction des données...")

# Fix données
db = dataset.connect("sqlite:///scores.db")

db.begin()
try:
    for table in db.tables:
        for user in db[table]:
            db[table].update(dict(id_=user['id_'], \
                shoots_fired=((user.get('tirsManques', 0) or 0) \
                    + (user.get('tirsSansCanards', 0) or 0) \
                    + (user.get('shoots_no_duck', 0) or 0) \
                    + (user.get('canardsTues', 0) or 0) \
                    + (user.get('shoots_harmed_duck', 0) or 0) \
                    + (user.get('shoots_frightened', 0) or 0)), \
                shoots_missed=(user.get('tirsManques', 0) or 0), \
                shoots_no_duck=((user.get('shoots_no_duck', 0) or 0) \
                    + (user.get('tirsSansCanards', 0) or 0)), \
                tirsManques=None, \
                tirsSansCanards=None), ['id_'])

            print("Données de l'utilisateur {0} corrigées sur la table {1}.".format(user['name'], table))
        print("Données de la table {} corrigées.".format(user['name'], table))
except:
    print("Erreur !")
    db.rollback()

print("Veuillez patienter...")
db.commit()

print("Correction des données terminée.")
print("")
print("Correction des colonnes...")

# Fix colonnes
db = sqlite3.connect("scores.db")
db.isolation_level = None
sql = db.cursor()

tables = sql.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

renameColumns = {
    'superCanardsTues': 'killed_super_ducks',
    'canardsTues':            'killed_ducks',
    'chasseursTues':        'killed_players',
    'meilleurTemps':             'best_time',
    'AssuranceVie':         'life_insurance',
    'munExplo':             'explosive_ammo',
    'tirsManques':             'IGNORE_ME_1',
    'tirsSansCanards':         'IGNORE_ME_2'
}

try:
    sql.execute("BEGIN")
    sql.execute("PRAGMA writable_schema=1")

    for table in tables:
        for old, new in renameColumns.items():
            sql.execute("UPDATE sqlite_master SET SQL=REPLACE(SQL, '{0}', '{1}') WHERE name='{2}'".format(old, new, table[0]))
            print("{0} renommé en {1} sur {2}.".format(old, new, table[0]))

    sql.execute("PRAGMA writable_schema=0")
    sql.execute("COMMIT")
except:
    print("Erreur !")
    sql.execute("ROLLBACK")

print("Correction des colonnes terminée.")
print("")
print("Base de données corrigée ! Analyse...")
sql.execute('ANALYZE')
print("Analyse terminée.")

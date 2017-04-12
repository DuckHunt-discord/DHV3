# coding: utf-8
import logging
import sqlite3
from mysql import connector

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def safeget(l, idx, default):
  try:
    return l[idx]
  except IndexError:
    return default

# MariaDB - replace the placeholder values
mariadb = connector.connect(database='duckhunt', user='duckhunt', password='password', host='localhost', port=3306, charset='utf8mb4', collation='utf8mb4_unicode_ci')
maria = mariadb.cursor(buffered=True, dictionary=True)

# SQLite
sqlitedb = sqlite3.connect("scores.db")
sqlitedb.row_factory = dict_factory
sqlite = sqlitedb.cursor()

maria.execute("SET NAMES utf8mb4;")
maria.execute("SET CHARACTER SET utf8mb4;")
maria.execute("SET character_set_results = utf8mb4, character_set_client = utf8mb4, character_set_connection = utf8mb4, character_set_database = utf8mb4, character_set_server = utf8mb4;")

sqlite.execute("DROP TABLE IF EXISTS sqlite_stat1")
sqlitedb.commit()
litetables = sqlite.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

maria.execute("DROP TABLE IF EXISTS channels")
maria.execute("DROP TABLE IF EXISTS players")

maria.execute("""CREATE TABLE IF NOT EXISTS `channels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` bigint(20) unsigned NOT NULL,
  `channel` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_server_and_chan` (`server`,`channel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1""")

maria.execute("""CREATE TABLE IF NOT EXISTS `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_` bigint(20) unsigned NOT NULL,
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel_id` int(11) NOT NULL,
  `banned` tinyint(1) NOT NULL DEFAULT '0',
  `confisque` tinyint(1) NOT NULL DEFAULT '0',
  `dazzled` tinyint(1) NOT NULL DEFAULT '0',
  `enrayee` tinyint(1) NOT NULL DEFAULT '0',
  `mouille` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `sabotee` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '-',
  `sand` tinyint(1) NOT NULL DEFAULT '0',
  `exp` int(11) NOT NULL DEFAULT '0',
  `lastGiveback` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `trefle_exp` smallint(5) DEFAULT NULL,
  `ap_ammo` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `balles` tinyint(4) DEFAULT NULL,
  `chargeurs` tinyint(4) DEFAULT NULL,
  `detecteurInfra` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `explosive_ammo` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `graisse` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `life_insurance` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `sight` tinyint(4) NOT NULL DEFAULT '0',
  `silencieux` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `sunglasses` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `trefle` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `self_killing_shoots` int(11) NOT NULL DEFAULT '0',
  `shoots_almost_killed` int(11) NOT NULL DEFAULT '0',
  `shoots_frightened` int(11) NOT NULL DEFAULT '0',
  `shoots_harmed_duck` int(11) NOT NULL DEFAULT '0',
  `shoots_infrared_detector` int(11) NOT NULL DEFAULT '0',
  `shoots_jamming_weapon` int(11) NOT NULL DEFAULT '0',
  `shoots_no_duck` int(11) NOT NULL DEFAULT '0',
  `shoots_sabotaged` int(11) NOT NULL DEFAULT '0',
  `shoots_tried_while_wet` int(11) NOT NULL DEFAULT '0',
  `shoots_with_jammed_weapon` int(11) NOT NULL DEFAULT '0',
  `shoots_without_bullets` int(11) NOT NULL DEFAULT '0',
  `shoots_without_weapon` int(11) NOT NULL DEFAULT '0',
  `shoots_fired` int(11) NOT NULL DEFAULT '0',
  `shoots_missed` int(11) NOT NULL DEFAULT '0',
  `killed_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_super_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_players` int(11) NOT NULL DEFAULT '0',
  `best_time` decimal(65,6) DEFAULT NULL,
  `exp_won_with_clover` int(11) NOT NULL DEFAULT '0',
  `givebacks` int(11) NOT NULL DEFAULT '0',
  `life_insurence_rewards` int(11) NOT NULL DEFAULT '0',
  `reloads` int(11) NOT NULL DEFAULT '0',
  `reloads_without_chargers` int(11) NOT NULL DEFAULT '0',
  `trashFound` int(11) NOT NULL DEFAULT '0',
  `unneeded_reloads` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_player_by_chan` (`id_`,`channel_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=2""")
mariadb.commit()

# Serveurs + channels
maria.execute("BEGIN")

for table in litetables:
  name = table['name'].split('-')
  maria.execute("INSERT INTO `channels` (`server`, `channel`) VALUES (%(server)s, %(channel)s)", {
    'server':   name[0],
    'channel':  safeget(name, 1, 0)
  })

mariadb.commit()
maria.execute("SELECT * FROM `channels`")
channels = {(str(item['server']) + (('-' + str(item['channel'])) if item['channel'] else '')): item['id'] for item in maria.fetchall()}

# Joueurs
maria.execute("BEGIN")

for table in litetables:
  name = table['name'].split('-')
  channel = channels.get(str(name[0]) + (('-' + str(safeget(name, 1, 0))) if safeget(name, 1, 0) else ''))
  members = sqlite.execute("SELECT * FROM '{table}'".format(table=table['name']))
  for member in members:
    maria.execute("""INSERT INTO `players` (`id_`, `name`, `channel_id`, `banned`, `confisque`, `dazzled`, `enrayee`, `mouille`, `sabotee`, `sand`, `exp`, `lastGiveback`, `trefle_exp`, `ap_ammo`, `balles`, `chargeurs`, `detecteurInfra`, `explosive_ammo`, `graisse`, `life_insurance`, `sight`, `silencieux`, `sunglasses`, `trefle`, `self_killing_shoots`, `shoots_almost_killed`, `shoots_frightened`, `shoots_harmed_duck`, `shoots_infrared_detector`, `shoots_jamming_weapon`, `shoots_no_duck`, `shoots_sabotaged`, `shoots_tried_while_wet`, `shoots_with_jammed_weapon`, `shoots_without_bullets`, `shoots_without_weapon`, `shoots_fired`, `shoots_missed`, `killed_ducks`, `killed_super_ducks`, `killed_players`, `best_time`, `exp_won_with_clover`, `givebacks`, `life_insurence_rewards`, `reloads`, `reloads_without_chargers`, `trashFound`, `unneeded_reloads`) VALUES (%(id_)s, %(name)s, %(channel_id)s, %(banned)s, %(confisque)s, %(dazzled)s, %(enrayee)s, %(mouille)s, %(sabotee)s, %(sand)s, %(exp)s, %(lastGiveback)s, %(trefle_exp)s, %(ap_ammo)s, %(balles)s, %(chargeurs)s, %(detecteurInfra)s, %(explosive_ammo)s, %(graisse)s, %(life_insurance)s, %(sight)s, %(silencieux)s, %(sunglasses)s, %(trefle)s, %(self_killing_shoots)s, %(shoots_almost_killed)s, %(shoots_frightened)s, %(shoots_harmed_duck)s, %(shoots_infrared_detector)s, %(shoots_jamming_weapon)s, %(shoots_no_duck)s, %(shoots_sabotaged)s, %(shoots_tried_while_wet)s, %(shoots_with_jammed_weapon)s, %(shoots_without_bullets)s, %(shoots_without_weapon)s, %(shoots_fired)s, %(shoots_missed)s, %(killed_ducks)s, %(killed_super_ducks)s, %(killed_players)s, %(best_time)s, %(exp_won_with_clover)s, %(givebacks)s, %(life_insurence_rewards)s, %(reloads)s, %(reloads_without_chargers)s, %(trashFound)s, %(unneeded_reloads)s)""",
    {
      'id_':                                                      member.get('id_'),
      'name':                                                    member.get('name'),
      'channel_id':                                                         channel,
      'banned':                                        member.get('banned', 0) or 0,
      'confisque':                                  member.get('confisque', 0) or 0,
      'dazzled':                                      member.get('dazzled', 0) or 0,
      'enrayee':                                      member.get('enrayee', 0) or 0,
      'mouille':                                      member.get('mouille', 0) or 0,
      'sabotee':                                  member.get('sabotee', '-') or '-',
      'sand':                                            member.get('sand', 0) or 0,
      'exp':                                              member.get('exp', 0) or 0,
      'lastGiveback':                            member.get('lastGiveback', 0) or 0,
      'trefle_exp':                                  member.get('trefle_exp', None),
      'ap_ammo':                                      member.get('ap_ammo', 0) or 0,
      'balles':                                          member.get('balles', None),
      'chargeurs':                                    member.get('chargeurs', None),
      'detecteurInfra':                        member.get('detecteurInfra', 0) or 0,
      'explosive_ammo':                        member.get('explosive_ammo', 0) or 0,
      'graisse':                                      member.get('graisse', 0) or 0,
      'life_insurance':                        member.get('life_insurance', 0) or 0,
      'sight':                                          member.get('sight', 0) or 0,
      'silencieux':                                member.get('silencieux', 0) or 0,
      'sunglasses':                                member.get('sunglasses', 0) or 0,
      'trefle':                                        member.get('trefle', 0) or 0,
      'self_killing_shoots':              member.get('self_killing_shoots', 0) or 0,
      'shoots_almost_killed':            member.get('shoots_almost_killed', 0) or 0,
      'shoots_frightened':                  member.get('shoots_frightened', 0) or 0,
      'shoots_harmed_duck':                member.get('shoots_harmed_duck', 0) or 0,
      'shoots_infrared_detector':    member.get('shoots_infrared_detector', 0) or 0,
      'shoots_jamming_weapon':          member.get('shoots_jamming_weapon', 0) or 0,
      'shoots_no_duck':                        member.get('shoots_no_duck', 0) or 0,
      'shoots_sabotaged':                    member.get('shoots_sabotaged', 0) or 0,
      'shoots_tried_while_wet':        member.get('shoots_tried_while_wet', 0) or 0,
      'shoots_with_jammed_weapon':  member.get('shoots_with_jammed_weapon', 0) or 0,
      'shoots_without_bullets':        member.get('shoots_without_bullets', 0) or 0,
      'shoots_without_weapon':          member.get('shoots_without_weapon', 0) or 0,
      'shoots_fired':                            member.get('shoots_fired', 0) or 0,
      'shoots_missed':                          member.get('shoots_missed', 0) or 0,
      'killed_ducks':                            member.get('killed_ducks', 0) or 0,
      'killed_super_ducks':                member.get('killed_super_ducks', 0) or 0,
      'killed_players':                        member.get('killed_players', 0) or 0,
      'best_time':                                    member.get('best_time', None),
      'exp_won_with_clover':              member.get('exp_won_with_clover', 0) or 0,
      'givebacks':                                  member.get('givebacks', 0) or 0,
      'life_insurence_rewards':        member.get('life_insurence_rewards', 0) or 0,
      'reloads':                                      member.get('reloads', 0) or 0,
      'reloads_without_chargers':    member.get('reloads_without_chargers', 0) or 0,
      'trashFound':                                member.get('trashFound', 0) or 0,
      'unneeded_reloads':                    member.get('unneeded_reloads', 0) or 0
    })

maria.execute("COMMIT")

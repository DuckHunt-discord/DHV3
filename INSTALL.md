# Self-Hosting

**DISCLAIMER: THE BOT IS NOT EXPLICITLY BUILT FOR SELF-HOSTING. IF YOU RUN INTO ISSUES, ONLY LIMITED SUPPORT WILL BE AVAILABLE.**
This document might be out of date.


## Requirements

 - Common sense
 - Some Linux experience, and very basic Python knowledge
 - Python 3.5 / 3.6
 - MySQL Server (or MariaDB, that's what we use)
 - git

Additionally, the bot works only on Linux for the moment.

## Installation

### Bot

1. Clone the repository using `git clone https://github.com/DuckHunt-discord/DHV3.git`
2. Navigate into the source folder using `cd DHV3`
3. Install the dependencies using `python3 -m pip install -r requirements.txt`

### MySQL

1. Create a user and a database for DuckHunt. 
2. Run the following SQL queries to create the necessary data structure:
```SQL
CREATE TABLE IF NOT EXISTS `channels` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server` bigint(20) unsigned NOT NULL,
  `channel` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_server_and_chan` (`server`,`channel`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=12;

CREATE TABLE IF NOT EXISTS `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_` bigint(20) unsigned NOT NULL,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `channel_id` int(11) NOT NULL,
  `banned` tinyint(1) NOT NULL DEFAULT '0',
  `confisque` tinyint(1) NOT NULL DEFAULT '0',
  `dazzled` tinyint(1) NOT NULL DEFAULT '0',
  `enrayee` tinyint(1) NOT NULL DEFAULT '0',
  `mouille` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `sabotee` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '-',
  `sand` tinyint(1) NOT NULL DEFAULT '0',
  `exp` int(11) NOT NULL DEFAULT '0',
  `lastGiveback` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `trefle_exp` smallint(5) DEFAULT NULL,
  `ap_ammo` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `balles` tinyint(4) DEFAULT NULL,
  `chargeurs` tinyint(4) DEFAULT NULL,
  `detecteurInfra` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `detecteur_infra_shots_left` tinyint(4) NOT NULL DEFAULT '0',
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
  `used_exp` int(10) unsigned NOT NULL DEFAULT '0',
  `found_explosive_ammo` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `found_almost_empty_explosive_ammo` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `found_chargers` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `found_chargers_not_taken` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `found_bullets` mediumint(8) unsigned NOT NULL DEFAULT '0',
  `found_bullets_not_taken` mediumint(8) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_player_by_chan` (`id_`,`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=742;
```
*Note: this schema \*might\* be out-of-date.*

## Configuration

- Create a `credentials.json` file in the application root folder, and put the following in it:  
```json
{
   "token": "BOT_TOKEN",
   "client_id": "BOT ID",
   "bots_key": "API KEY FOR DISCORD BOTS",
   "mysql_user": "SQL USERNAME",
   "mysql_pass": "SQL PASSWORD",
   "mysql_host": "SQL CONNECTION URL",
   "mysql_port": "SQL SERVER PORT",
   "mysql_db": "SQL DB NAME"    
}
```

- Open the file `cogs/utils/checks.py` and add your discord ID to the `owner` list.
- Open the file `cogs/utils/commons.py` and add your discord ID to the `owners` list.

At the time of writing this, the bot will not reconnect itself to the SQL server automatically if it times out.

It might be fixed in the future, but while it's not, you can do it in a dirty way by appending `?autoReconnect=true` to the `mysql_host` parameter.

## Running the bot

Once you have everything set up you can run the bot with `python3 bot.py`.

If you need to be able to close the shell afterwards, you can run the bot using nohup, screen, tmux or whatever does the job.

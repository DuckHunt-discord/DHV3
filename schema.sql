-- phpMyAdmin SQL Dump
-- version 4.5.4.1deb2ubuntu2
-- http://www.phpmyadmin.net
--
-- Client :  localhost
-- Généré le :  Lun 16 Juillet 2018 à 21:27
-- Version du serveur :  10.0.34-MariaDB-0ubuntu0.16.04.1
-- Version de PHP :  7.0.28-0ubuntu0.16.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `DHV3`
--

-- --------------------------------------------------------

--
-- Structure de la table `admins`
--

CREATE TABLE `admins` (
  `server_id` bigint(20) UNSIGNED NOT NULL,
  `user_id` bigint(20) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `channels`
--

CREATE TABLE `channels` (
  `id` int(11) NOT NULL,
  `server` bigint(20) UNSIGNED NOT NULL,
  `channel` bigint(20) UNSIGNED NOT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '0',
  `channel_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'unknown'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `players`
--

CREATE TABLE `players` (
  `id` int(11) NOT NULL,
  `id_` bigint(20) UNSIGNED NOT NULL,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'NotProvided#0000',
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
  `trefle_exp` smallint(5) NOT NULL DEFAULT '0',
  `ap_ammo` int(11) NOT NULL DEFAULT '0' COMMENT 'Timestamp',
  `balles` tinyint(4) NOT NULL DEFAULT '6',
  `chargeurs` tinyint(4) NOT NULL DEFAULT '2',
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
  `killed_normal_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_super_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_baby_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_mother_of_all_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_mechanical_ducks` int(11) NOT NULL DEFAULT '0',
  `killed_players` int(11) NOT NULL DEFAULT '0',
  `best_time` decimal(65,6) NOT NULL DEFAULT '660.000000',
  `exp_won_with_clover` int(11) NOT NULL DEFAULT '0',
  `givebacks` int(11) NOT NULL DEFAULT '0',
  `life_insurence_rewards` int(11) NOT NULL DEFAULT '0',
  `reloads` int(11) NOT NULL DEFAULT '0',
  `reloads_without_chargers` int(11) NOT NULL DEFAULT '0',
  `trashFound` int(11) NOT NULL DEFAULT '0',
  `unneeded_reloads` int(11) NOT NULL DEFAULT '0',
  `used_exp` int(10) UNSIGNED NOT NULL DEFAULT '0',
  `found_explosive_ammo` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `found_almost_empty_explosive_ammo` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `found_chargers` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `found_chargers_not_taken` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `found_bullets` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `found_bullets_not_taken` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `murders` int(11) NOT NULL DEFAULT '0',
  `avatar_url` varchar(1000) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'https://discordapp.com/assets/dd4dbc0016779df1378e7812eabaa04d.png',
  `hugs` int(11) NOT NULL DEFAULT '0',
  `hugs_no_duck` int(11) NOT NULL DEFAULT '0',
  `hugged_baby_ducks` int(11) NOT NULL DEFAULT '0',
  `hugged_nohug_ducks` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `prefs`
--

CREATE TABLE `prefs` (
  `server_id` bigint(20) UNSIGNED NOT NULL,
  `announce_level_up` tinyint(1) UNSIGNED DEFAULT '1',
  `bang_lag` float UNSIGNED DEFAULT '0.5',
  `chance_to_kill_on_missed` tinyint(11) UNSIGNED DEFAULT '5',
  `clover_max_exp` smallint(11) DEFAULT '10',
  `clover_min_exp` smallint(11) DEFAULT '1',
  `delete_commands` tinyint(1) UNSIGNED DEFAULT '0',
  `disable_decoys_when_ducks_are_sleeping` tinyint(1) UNSIGNED DEFAULT '1',
  `duck_frighten_chance` tinyint(11) UNSIGNED DEFAULT '5',
  `ducks_per_day` smallint(4) UNSIGNED DEFAULT '48',
  `emoji_used` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT '<:official_Duck_01_reversed:439576463436546050>',
  `exp_won_per_duck_killed` tinyint(11) UNSIGNED DEFAULT '10',
  `killed_mentions` tinyint(1) UNSIGNED DEFAULT '1',
  `language` char(5) COLLATE utf8mb4_unicode_ci DEFAULT 'en_EN',
  `mention_in_topscores` tinyint(1) UNSIGNED DEFAULT '0',
  `multiplier_miss_chance` float UNSIGNED DEFAULT '1',
  `pm_most_messages` tinyint(1) UNSIGNED DEFAULT '0',
  `prefix` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '!',
  `show_super_ducks_life` tinyint(1) NOT NULL DEFAULT '0',
  `sleeping_ducks_start` tinyint(2) UNSIGNED DEFAULT '0',
  `sleeping_ducks_stop` tinyint(2) UNSIGNED DEFAULT '0',
  `super_ducks_chance` tinyint(11) UNSIGNED DEFAULT '5',
  `baby_ducks_chance` tinyint(11) NOT NULL DEFAULT '2',
  `mother_of_all_ducks_chance` tinyint(11) NOT NULL DEFAULT '1',
  `ducks_chance` tinyint(11) UNSIGNED DEFAULT '100',
  `super_ducks_exp_multiplier` float DEFAULT '1.1',
  `super_ducks_maxlife` tinyint(11) UNSIGNED DEFAULT '7',
  `super_ducks_minlife` tinyint(11) UNSIGNED DEFAULT '3',
  `tax_on_user_give` tinyint(11) UNSIGNED DEFAULT '5',
  `time_before_ducks_leave` smallint(4) UNSIGNED DEFAULT '660',
  `tts_ducks` tinyint(1) UNSIGNED DEFAULT '0',
  `user_can_give_exp` tinyint(1) UNSIGNED NOT NULL DEFAULT '1',
  `events_enabled` tinyint(1) UNSIGNED DEFAULT '1',
  `pm_stats` tinyint(1) UNSIGNED DEFAULT '0',
  `randomize_mechanical_ducks` tinyint(1) UNSIGNED DEFAULT '0',
  `users_can_find_objects` tinyint(1) DEFAULT '1',
  `vip` tinyint(1) DEFAULT '0',
  `debug_show_ducks_class_on_spawn` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Index pour les tables exportées
--

--
-- Index pour la table `admins`
--
ALTER TABLE `admins`
  ADD UNIQUE KEY `server_id` (`server_id`,`user_id`);

--
-- Index pour la table `channels`
--
ALTER TABLE `channels`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_server_and_chan` (`server`,`channel`);

--
-- Index pour la table `players`
--
ALTER TABLE `players`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_player_by_chan` (`id_`,`channel_id`);

--
-- Index pour la table `prefs`
--
ALTER TABLE `prefs`
  ADD PRIMARY KEY (`server_id`);

--
-- AUTO_INCREMENT pour les tables exportées
--

--
-- AUTO_INCREMENT pour la table `channels`
--
ALTER TABLE `channels`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21603;
--
-- AUTO_INCREMENT pour la table `players`
--
ALTER TABLE `players`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47778260;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

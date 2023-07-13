-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 11, 2023 at 10:12 PM
-- Server version: 5.6.51
-- PHP Version: 8.1.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cryptogenie`
--

-- --------------------------------------------------------

--
-- Table structure for table `executable_drawings`
--

CREATE TABLE `executable_drawings` (
  `id` int(11) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `timeframe` varchar(10) DEFAULT NULL,
  `type` int(11) NOT NULL,
  `x1` varchar(50) DEFAULT NULL,
  `y1` varchar(50) DEFAULT NULL,
  `x2` varchar(50) DEFAULT NULL,
  `y2` varchar(50) DEFAULT NULL,
  `order_type` varchar(20) DEFAULT NULL,
  `order_qty` varchar(20) DEFAULT NULL,
  `order_side` varchar(10) DEFAULT NULL,
  `order_chaser` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `exit_strategies`
--

CREATE TABLE `exit_strategies` (
  `id` int(11) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `tp_type` enum('limitorder','limitorder_postonly','marketorder') DEFAULT 'limitorder',
  `tp_target_long` text,
  `tp_target_short` text,
  `tp_target_type` enum('ratio_pre_leverage','ratio_post_leverage') DEFAULT 'ratio_pre_leverage',
  `tp_all_or_none` tinyint(1) DEFAULT '1',
  `tp_enforce_all_time` tinyint(4) DEFAULT '1',
  `tp_enforce_maxrange` tinyint(1) DEFAULT '1',
  `tp_target_tolerance_ratio` double DEFAULT '0',
  `sl_type` enum('limitorder','marketorder') DEFAULT 'marketorder',
  `sl_amount` double DEFAULT '100',
  `sl_amount_type` enum('ratio_position_size') DEFAULT 'ratio_position_size',
  `sl_target_long` double DEFAULT NULL,
  `sl_target_short` double DEFAULT NULL,
  `sl_target_type` enum('ratio_pre_leverage','ratio_post_leverage') DEFAULT 'ratio_pre_leverage',
  `sl_target_tolerance_ratio` double DEFAULT '0',
  `sl_trailing_targets_long` text,
  `sl_trailing_targets_short` text,
  `force_market_exit` tinyint(1) DEFAULT NULL,
  `tb_initial_sl_static_cap_ratio_buy_override` double DEFAULT NULL,
  `tb_initial_sl_static_pos_size_ratio_buy_override` double DEFAULT NULL,
  `tb_sl_static_cap_ratio_buy_override` double DEFAULT NULL,
  `tb_sl_static_pos_size_ratio_buy_override` double DEFAULT NULL,
  `tb_initial_sl_static_cap_ratio_sell_override` double DEFAULT NULL,
  `tb_initial_sl_static_pos_size_ratio_sell_override` double DEFAULT NULL,
  `tb_sl_static_cap_ratio_sell_override` double DEFAULT NULL,
  `tb_sl_static_pos_size_ratio_sell_override` double DEFAULT NULL,
  `tb_hedge_cap_ratio_buy_override` double DEFAULT NULL,
  `tb_hedge_pos_size_ratio_buy_override` double DEFAULT NULL,
  `tb_hedge_cap_ratio_sell_override` double DEFAULT NULL,
  `tb_hedge_pos_size_ratio_sell_override` double DEFAULT NULL,
  `tb_hedge_balancer_cap_ratio_override` double DEFAULT NULL,
  `tb_hedge_sl_static_cap_ratio_override` double DEFAULT NULL,
  `tp_after_hedge` tinyint(1) DEFAULT '0',
  `sl_after_hedge` tinyint(1) DEFAULT '0',
  `reset_refresh_rate` int(11) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `linked_orders`
--

CREATE TABLE `linked_orders` (
  `id` int(50) NOT NULL,
  `order_link_id` varchar(36) DEFAULT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `side` varchar(10) DEFAULT NULL,
  `order_type` varchar(10) DEFAULT NULL,
  `price` varchar(20) DEFAULT NULL,
  `qty` varchar(20) DEFAULT NULL,
  `time_in_force` varchar(20) DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `positions_hedges`
--

CREATE TABLE `positions_hedges` (
  `id` int(50) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `side` varchar(10) DEFAULT NULL,
  `order_link_id` varchar(100) DEFAULT NULL,
  `stop_order_id` varchar(100) DEFAULT NULL,
  `price` varchar(20) DEFAULT NULL,
  `size` varchar(20) DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `positions_sessions`
--

CREATE TABLE `positions_sessions` (
  `id` int(11) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `side` varchar(10) DEFAULT NULL,
  `hedged` tinyint(1) DEFAULT '0',
  `initial_equity` varchar(20) DEFAULT NULL,
  `highest_equity` varchar(20) DEFAULT NULL,
  `realtime_equity` varchar(20) DEFAULT NULL,
  `last_balanced_equity` varchar(20) DEFAULT NULL,
  `balanced_hedge` tinyint(1) DEFAULT '0',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_balance_hedge_forced` timestamp NULL DEFAULT NULL,
  `current_long_pos_size` varchar(20) DEFAULT '0',
  `current_short_pos_size` varchar(20) DEFAULT '0',
  `current_long_pos_value` varchar(20) DEFAULT '0',
  `current_short_pos_value` varchar(20) DEFAULT '0',
  `realtime_price` varchar(20) DEFAULT '0',
  `current_balancer_hedge_price` varchar(20) DEFAULT NULL,
  `tb_sl_qty` varchar(20) DEFAULT '0',
  `tb_sl_price` varchar(20) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `positions_stops`
--

CREATE TABLE `positions_stops` (
  `id` int(50) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `side` varchar(10) DEFAULT NULL,
  `initial_sl_executed` int(11) NOT NULL DEFAULT '0',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `positions_tb_sl`
--

CREATE TABLE `positions_tb_sl` (
  `id` int(50) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `side` varchar(10) DEFAULT NULL,
  `tb_sl_price` varchar(20) DEFAULT NULL,
  `order_count` int(11) DEFAULT '1',
  `locked` tinyint(1) DEFAULT '1',
  `size` varchar(20) DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `scaled_orders`
--

CREATE TABLE `scaled_orders` (
  `id` int(11) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `api_secret` varchar(50) DEFAULT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `side` varchar(10) DEFAULT NULL,
  `amount` varchar(20) DEFAULT NULL,
  `orderCount` varchar(20) DEFAULT NULL,
  `priceLower` varchar(20) DEFAULT NULL,
  `priceUpper` varchar(20) DEFAULT NULL,
  `ordertype` varchar(20) DEFAULT NULL,
  `orderExec` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `user_notifications`
--

CREATE TABLE `user_notifications` (
  `id` int(11) NOT NULL,
  `api_key` varchar(50) DEFAULT NULL,
  `text` text,
  `type` int(11) DEFAULT NULL,
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_read` timestamp NULL DEFAULT NULL,
  `last_resolved` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `executable_drawings`
--
ALTER TABLE `executable_drawings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `exit_strategies`
--
ALTER TABLE `exit_strategies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UniqueSymbolPerApiCredentials` (`api_key`,`api_secret`,`symbol`);

--
-- Indexes for table `linked_orders`
--
ALTER TABLE `linked_orders`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `positions_hedges`
--
ALTER TABLE `positions_hedges`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UniqueSymbolPerApiCredentials` (`api_key`,`api_secret`,`symbol`,`side`);

--
-- Indexes for table `positions_sessions`
--
ALTER TABLE `positions_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UniqueSymbolPerApiCredentials` (`api_key`,`api_secret`,`symbol`);

--
-- Indexes for table `positions_stops`
--
ALTER TABLE `positions_stops`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UniqueSymbolPerApiCredentials` (`api_key`,`api_secret`,`symbol`,`side`);

--
-- Indexes for table `positions_tb_sl`
--
ALTER TABLE `positions_tb_sl`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `UniqueSymbolPerApiCredentials` (`api_key`,`api_secret`,`symbol`,`side`);

--
-- Indexes for table `scaled_orders`
--
ALTER TABLE `scaled_orders`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user_notifications`
--
ALTER TABLE `user_notifications`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `executable_drawings`
--
ALTER TABLE `executable_drawings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `exit_strategies`
--
ALTER TABLE `exit_strategies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `linked_orders`
--
ALTER TABLE `linked_orders`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `positions_hedges`
--
ALTER TABLE `positions_hedges`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `positions_sessions`
--
ALTER TABLE `positions_sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `positions_stops`
--
ALTER TABLE `positions_stops`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `positions_tb_sl`
--
ALTER TABLE `positions_tb_sl`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `scaled_orders`
--
ALTER TABLE `scaled_orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_notifications`
--
ALTER TABLE `user_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

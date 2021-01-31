-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 31, 2021 at 12:55 PM
-- Server version: 10.3.25-MariaDB-0ubuntu0.20.04.1
-- PHP Version: 7.4.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `DataLogger`
--

-- --------------------------------------------------------

--
-- Structure for view `OneMonth`
--

CREATE ALGORITHM=UNDEFINED DEFINER=`david`@`localhost` SQL SECURITY DEFINER VIEW `OneMonth`  AS  select `OW1`.`ID` AS `ID`,`OW1`.`TimeStamp` AS `Date`,`OW1`.`Rain_Total` AS `Rain_From`,`OW2`.`Rain_Total` AS `Rain_To`,round(greatest(`OW2`.`Rain_Total` - `OW1`.`Rain_Total`,0),2) AS `Rain_Change`,round(`OW1`.`Outdoor_Temperature` * 9 / 5 + 32,1) AS `Temp`,`OW1`.`Outdoor_Humidity` AS `Humid`,round(`OW1`.`Wind_Speed_Maximum` * 0.621,1) AS `Wind`,`OW1`.`Current_Wind_Direction` AS `Wind_Direction`,round(`OW1`.`Current_Wind_Gust` * 0.621,1) AS `Gust`,round(`OW1`.`Barometric_Pressure` / 3386.4,2) AS `BP`,round(-42.379 + 2.04901523 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) + 10.14333127 * `OW1`.`Outdoor_Humidity` - 0.22475541 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * `OW1`.`Outdoor_Humidity` - 0.00683783 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) - 0.05481717 * `OW1`.`Outdoor_Humidity` * `OW1`.`Outdoor_Humidity` + 0.00122874 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * `OW1`.`Outdoor_Humidity` + 0.00085282 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * `OW1`.`Outdoor_Humidity` * `OW1`.`Outdoor_Humidity` - 0.00000199 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * `OW1`.`Outdoor_Humidity` * `OW1`.`Outdoor_Humidity`,1) AS `HI`,round(35.74 + 0.6215 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) - 35.75 * pow(`OW1`.`Wind_Speed_Maximum` * 0.621,0.16) + 0.4275 * (`OW1`.`Outdoor_Temperature` * 9 / 5 + 32) * pow(`OW1`.`Wind_Speed_Maximum` * 0.621,0.16),1) AS `WC`,round(greatest(`OW2`.`Rain_Total` - `OW1`.`Rain_Total`,0) / (minute(timediff(`OW2`.`TimeStamp`,`OW1`.`TimeStamp`)) / 60) / 22.5,2) AS `Rain_Rate` from (`OURWEATHERTable` `OW1` join `OURWEATHERTable` `OW2` on(`OW2`.`ID` = `OW1`.`ID` + 1)) where `OW1`.`TimeStamp` >= current_timestamp() - interval 30 day ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

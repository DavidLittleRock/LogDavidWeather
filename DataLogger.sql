-- phpMyAdmin SQL Dump
-- version 4.9.5deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 25, 2021 at 08:46 AM
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
-- Stand-in structure for view `NewOneMonth`
-- (See below for the actual view)
--
CREATE TABLE `NewOneMonth` (
`ID` int(20)
,`Date` timestamp
,`Rain_Change` double(19,2)
,`Temp` double(18,1)
,`Humid` float
,`Wind` double(18,1)
,`Wind_Direction` float
,`Gust` double(18,1)
,`BP` double(19,2)
,`HI` double(18,1)
,`WC` double(18,1)
,`Rain_Rate` double(19,2)
);

-- --------------------------------------------------------

--
-- Structure for view `NewOneMonth`
--
DROP TABLE IF EXISTS `NewOneMonth`;

CREATE ALGORITHM=UNDEFINED DEFINER=`david`@`localhost` SQL SECURITY DEFINER VIEW `NewOneMonth`  AS  select `OURWEATHERTable`.`ID` AS `ID`,`OURWEATHERTable`.`TimeStamp` AS `Date`,greatest(round(`OURWEATHERTable`.`Rain_Total` - lag(`OURWEATHERTable`.`Rain_Total`,1) over ( order by `OURWEATHERTable`.`Rain_Total`),2),0) AS `Rain_Change`,round(`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32,1) AS `Temp`,`OURWEATHERTable`.`Outdoor_Humidity` AS `Humid`,round(`OURWEATHERTable`.`Wind_Speed_Maximum` * 0.621,1) AS `Wind`,`OURWEATHERTable`.`Current_Wind_Direction` AS `Wind_Direction`,round(`OURWEATHERTable`.`Current_Wind_Gust` * 0.621,1) AS `Gust`,round(`OURWEATHERTable`.`Barometric_Pressure` / 3386.4,2) AS `BP`,round(-42.379 + 2.04901523 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) + 10.14333127 * `OURWEATHERTable`.`Outdoor_Humidity` - 0.22475541 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * `OURWEATHERTable`.`Outdoor_Humidity` - 0.00683783 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) - 0.05481717 * `OURWEATHERTable`.`Outdoor_Humidity` * `OURWEATHERTable`.`Outdoor_Humidity` + 0.00122874 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * `OURWEATHERTable`.`Outdoor_Humidity` + 0.00085282 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * `OURWEATHERTable`.`Outdoor_Humidity` * `OURWEATHERTable`.`Outdoor_Humidity` - 0.00000199 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * `OURWEATHERTable`.`Outdoor_Humidity` * `OURWEATHERTable`.`Outdoor_Humidity`,1) AS `HI`,round(35.74 + 0.6215 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) - 35.75 * pow(`OURWEATHERTable`.`Wind_Speed_Maximum` * 0.621,0.16) + 0.4275 * (`OURWEATHERTable`.`Outdoor_Temperature` * 9 / 5 + 32) * pow(`OURWEATHERTable`.`Wind_Speed_Maximum` * 0.621,0.16),1) AS `WC`,round(60 / minute(timediff(`OURWEATHERTable`.`TimeStamp`,lag(`OURWEATHERTable`.`TimeStamp`,1) over ( order by `OURWEATHERTable`.`TimeStamp`))) * greatest(round(`OURWEATHERTable`.`Rain_Total` - lag(`OURWEATHERTable`.`Rain_Total`,1) over ( order by `OURWEATHERTable`.`Rain_Total`),2),0) / 22.5,2) AS `Rain_Rate` from `OURWEATHERTable` where `OURWEATHERTable`.`TimeStamp` >= current_timestamp() - interval 30 day ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

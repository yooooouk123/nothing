USE `%s`;
-- MySQL dump 10.13  Distrib 5.6.17, for Win32 (x86)
--
-- Host: localhost    Database: %s
-- ------------------------------------------------------
-- Server version	5.5.41-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article` (
  `a_id` int(11) NOT NULL,
  `source` varchar(45) NULL,
  `a_press` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `a_title` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `a_body` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `a_datetime` datetime DEFAULT NULL,
  `a_cat` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `isNaver` smallint(1) DEFAULT NULL,
  `r_datetime` datetime DEFAULT NULL,
  `rel_id` int(11) NULL,
  PRIMARY KEY (`a_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comments`
--
DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `a_id` int(11) NOT NULL,
  `c_num` int(11) NOT NULL,
  `maskUserId` varchar(45) NULL,
  `encodedUserId` varchar(45) NOT NULL,
  `c_datetime` datetime NOT NULL,
  `c_body` text NULL,
  `badCnt` int(11) NOT NULL,
  `goodCnt` int(11) NOT NULL,
  `likeCnt` int(11) NOT NULL,
  `replyCnt` int(11) NOT NULL,
  `fromType` varchar(45) NULL,
  `snsType` varchar(45) NULL,
  `isBest` smallint(1) DEFAULT NULL,
  `c_grade` varchar(45) NULL,
  `c_pnt` int(11) NOT NULL,
  `c_nextGradePnt` int(11) NOT NULL,
  PRIMARY KEY (`a_id`, `c_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `srch_query`
--
DROP TABLE IF EXISTS `srch_query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `srch_query` (
  `a_query` varchar(60) COLLATE utf8mb4_unicode_ci NOT NULL,
  `a_id` int(11) NOT NULL,
  PRIMARY KEY (`a_query`,`a_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `url`
--

DROP TABLE IF EXISTS `url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `url` (
  `a_id` int(11) NOT NULL AUTO_INCREMENT,
  `a_url` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `err_code` int(11) DEFAULT NULL,
  PRIMARY KEY (`a_id`,`a_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-03-04 17:14:16

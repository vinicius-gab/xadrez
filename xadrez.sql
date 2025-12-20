-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: xadrez
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `abertura`
--

DROP TABLE IF EXISTS `abertura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `abertura` (
  `idAbertura` int NOT NULL AUTO_INCREMENT,
  `Nome` varchar(45) DEFAULT NULL,
  `Movimento` text,
  `Descricao` text,
  `eco` varchar(5) DEFAULT NULL,
  `estilo` varchar(150) DEFAULT NULL,
  `tipo` enum('Abertura','Gambito','Defesa') DEFAULT NULL,
  `nivel` enum('Iniciante','Intermediário','Avançado') DEFAULT NULL,
  PRIMARY KEY (`idAbertura`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `abertura`
--

LOCK TABLES `abertura` WRITE;
/*!40000 ALTER TABLE `abertura` DISABLE KEYS */;
INSERT INTO `abertura` VALUES (1,'Gambito Letão',NULL,'O Gambito Letão surge após 1.e4 e5 2.Cf3 f5. As pretas sacrificam um peão logo no começo para abrir linhas e criar pressão imediata no centro e no rei adversário. É uma abertura arriscada, pouco usada em níveis altos, mas muito perigosa em partidas rápidas e contra jogadores despreparados.\r\n','C40\r\n','Abertura extremamente agressiva e tática, com sacrifício de peão para acelerar o desenvolvimento e atacar o rei branco desde o início.\r\n','Gambito','Intermediário'),(2,'Gambito Letão',NULL,'O Gambito Letão surge após 1.e4 e5 2.Cf3 f5. As pretas sacrificam um peão logo no começo para abrir linhas e criar pressão imediata no centro e no rei adversário. É uma abertura arriscada, pouco usada em níveis altos, mas muito perigosa em partidas rápidas e contra jogadores despreparados.\r\n','C40\r\n','Abertura extremamente agressiva e tática, com sacrifício de peão para acelerar o desenvolvimento e atacar o rei branco desde o início.\r\n','Gambito','Intermediário');
/*!40000 ALTER TABLE `abertura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `favorito`
--

DROP TABLE IF EXISTS `favorito`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favorito` (
  `idFavorito` int NOT NULL AUTO_INCREMENT,
  `id_user` int DEFAULT NULL,
  `id_abertura` int DEFAULT NULL,
  PRIMARY KEY (`idFavorito`),
  KEY `fk_user_idx` (`id_user`),
  KEY `fk_abertura_idx` (`id_abertura`),
  CONSTRAINT `fk_abertura` FOREIGN KEY (`id_abertura`) REFERENCES `abertura` (`idAbertura`),
  CONSTRAINT `fk_user` FOREIGN KEY (`id_user`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favorito`
--

LOCK TABLES `favorito` WRITE;
/*!40000 ALTER TABLE `favorito` DISABLE KEYS */;
/*!40000 ALTER TABLE `favorito` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `idUsuario` int NOT NULL AUTO_INCREMENT,
  `Nome` varchar(200) DEFAULT NULL,
  `Email` varchar(150) DEFAULT NULL,
  `Senha` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'Teste Site','site@teste.com','1234'),(2,'Vinicius ','teste@gmail.com','123'),(3,'Vinicius ','teste@gmail.com','123'),(4,'Vini','email@teste.com','viniboy'),(5,'Vini','email@teste.com','viniboy'),(6,'Vini','email@teste.com','viniboy'),(7,'Vini','email@teste.com','viniboy'),(8,'Vini','email@teste.com','viniboy'),(9,'Vini','email@teste.com','123'),(10,'vinicius.palhares@escolar.ifrn.edu.br','email@teste.com','50419'),(11,'Vini','email@teste.com','viniboy'),(12,'vini','email@teste.com','123'),(13,'vini','email@teste.com','123'),(14,'Vini','email@teste.com','123'),(15,'Vini','email@teste.com','123');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-19 21:47:08

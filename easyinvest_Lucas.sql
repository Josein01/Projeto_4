-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema easy_invest
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema easy_invest
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `easy_invest` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `easy_invest` ;

-- -----------------------------------------------------
-- Table `easy_invest`.`investimento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `easy_invest`.`investimento` (
  `idinvestimento` INT NOT NULL AUTO_INCREMENT,
  `tipoinvestimento` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idinvestimento`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `easy_invest`.`usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `easy_invest`.`usuario` (
  `idusuario` INT NOT NULL AUTO_INCREMENT,
  `nomeusuario` VARCHAR(15) NOT NULL,
  `sobrenomeusuario` VARCHAR(100) NOT NULL,
  `emailusuario` VARCHAR(100) NOT NULL,
  `senhausuario` VARCHAR(300) NOT NULL,
  `fotoperfil` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`idusuario`))
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `easy_invest`.`calculos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `easy_invest`.`calculos` (
  `idcalculos` INT NOT NULL AUTO_INCREMENT,
  `valor` DECIMAL(10,0) NOT NULL,
  `prazo` INT NOT NULL,
  `taxa` VARCHAR(20) NOT NULL,
  `resultadocalculo` DECIMAL(20,0) NOT NULL,
  `data_calculo` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_idusuario` INT NOT NULL,
  `investimento_idinvestimento` INT NOT NULL,
  PRIMARY KEY (`idcalculos`),
  INDEX `fk_calculos_usuario1_idx` (`usuario_idusuario` ASC) VISIBLE,
  INDEX `fk_calculos_investimento1_idx` (`investimento_idinvestimento` ASC) VISIBLE,
  CONSTRAINT `fk_calculos_investimento1`
    FOREIGN KEY (`investimento_idinvestimento`)
    REFERENCES `easy_invest`.`investimento` (`idinvestimento`),
  CONSTRAINT `fk_calculos_usuario1`
    FOREIGN KEY (`usuario_idusuario`)
    REFERENCES `easy_invest`.`usuario` (`idusuario`))
ENGINE = InnoDB
AUTO_INCREMENT = 23
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `easy_invest`.`indicadores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `easy_invest`.`indicadores` (
  `idindicadores` INT NOT NULL AUTO_INCREMENT,
  `tipoindicadores` VARCHAR(45) NOT NULL,
  `taxaanual` VARCHAR(45) NOT NULL,
  `dataatualiza` DATETIME NOT NULL,
  PRIMARY KEY (`idindicadores`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

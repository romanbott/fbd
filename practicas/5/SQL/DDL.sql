-- =======================================
-- Creamos las tablas para las entidades
-- =======================================

CREATE TABLE Cliente (
    idCliente int,
    Nombre varchar(100),
    Paterno varchar(100),
    Materno varchar(100),
    FechaNacimiento date,
    Sexo varchar(50)
);

CREATE TABLE Telefono_Cliente (
    idCliente int,
    telefono varchar(15)
);

CREATE TABLE Correo_Cliente (
    idCliente int,
    correo varchar(100)
);

CREATE TABLE Tarjeta (
    idCliente int,
    idTarjeta int,
    Saldo decimal(8,2),
    rfc_cajero varchar(100)
);

CREATE TABLE Recarga (
    idRecarga int,
    idSucursal int,
    idCliente int,
    idTarjeta int,
    rfc_cajero varchar(100),
    fecha date,
    hora time,
    MontoAbonar decimal(8,2),
    MetodoPago varchar(50)
);

CREATE TABLE Sucursal (
    idSucursal int,
    Nombre varchar(100),
    Horario varchar(100),
    Telefono varchar(15),
    Calle varchar(100),
    NumExterior varchar(50),
    NumInterior varchar(50),
    Colonia varchar(100),
    Estado varchar(100)
);

CREATE TABLE Maquina (
    idMaquina int,
    idSucursal int,
    idJuego int,
    Estado varchar(50)
);

CREATE TABLE Juego (
    idJuego int,
    Nombre varchar(100),
    Tipo varchar(50),
    Costo decimal(8,2)
);

CREATE TABLE Partida (
    idPartida int,
    idMaquina int,
    idCliente int,
    idTarjeta int,
    fecha date,
    hora time,
    Puntaje int,
    PuntosGanados int
);

CREATE TABLE Canje (
    idCanje int,
    idSucursal int,
    idCliente int,
    idPremio int,
    rfc_EncargadoDePremios varchar(100),
    fecha date,
    hora time,
    PuntosUtilizados int,
    CantidadPremiosObtenidos int
);

CREATE TABLE Premio (
    idPremio int,
    PuntosNecesarios int,
    ValorAprox decimal(8,2),
    RangoEdad varchar(50),
    Categoria varchar(50),
    Nombre varchar(100)
);

CREATE TABLE Inventario (
       idSucursal int,
       idArticulo int,
       idPremio int,
       CantidadDisponible int
);

CREATE TABLE Mantenimiento (
       idMaquina int,
       idMantenimiento int,
       fecha date,
       Tipo varchar(50),
       DescripcionProblema varchar(200),
       rfc_Tecnico varchar(100)
);

CREATE TABLE Empleado (
    rfc varchar(100),
    CURP varchar(100),
    Nombre varchar(100),
    Paterno varchar(100),
    Materno varchar(100),
    FechaNacimiento date,
    FechaContratacion date,
    Salario decimal(8,2)
);

CREATE TABLE Telefono_Empleado (
    rfc varchar(100),
    telefono varchar(15)
);

CREATE TABLE Correo_Empleado (
    rfc varchar(100),
    correo varchar(100)
);

CREATE TABLE Cajero (
    rfc varchar(100),
    HorarioTrabajo varchar(100)
);

CREATE TABLE Gerente (
    rfc varchar(100),
    idSucursal int,
    CedulaProfesional varchar(100)
);

CREATE TABLE EncargadoDePremio (
    rfc varchar(100),
    HorarioTrabajo varchar(100)
);

CREATE TABLE Tecnico (
    rfc varchar(100),
    AreaEspecialidad varchar(100)
);

-- ====================================
-- Reestricciones de Entidad y Dominio
--=====================================

-- Para cliente
ALTER TABLE Cliente ADD CONSTRAINT pk_cliente PRIMARY KEY (idCliente);
ALTER TABLE Cliente ALTER COLUMN Nombre SET NOT NULL;
ALTER TABLE Cliente ALTER COLUMN Paterno SET NOT NULL;
ALTER TABLE Cliente ALTER COLUMN FechaNacimiento SET NOT NULL;

-- Para Telefono_Cliente
ALTER TABLE Telefono_Cliente ADD CONSTRAINT pk_telefono_cliente PRIMARY KEY (idCliente, telefono);
ALTER TABLE Telefono_Cliente ALTER COLUMN telefono SET NOT NULL;

-- Para Correo_Cliente
ALTER TABLE Correo_Cliente ADD CONSTRAINT pk_correo_cliente PRIMARY KEY (idCliente, correo);
ALTER TABLE Correo_Cliente ALTER COLUMN correo SET NOT NULL;

-- Para Tarjeta
ALTER TABLE Tarjeta ADD CONSTRAINT pk_tarjeta PRIMARY KEY (idCliente, idTarjeta);
ALTER TABLE Tarjeta ALTER COLUMN idTarjeta SET NOT NULL;
ALTER TABLE Tarjeta ALTER COLUMN Saldo SET NOT NULL;

-- Para Recarga
ALTER TABLE Recarga ADD CONSTRAINT pk_recarga PRIMARY KEY (idRecarga);
ALTER TABLE Recarga ALTER COLUMN MontoAbonar SET NOT NULL;
ALTER TABLE Recarga ALTER COLUMN fecha SET NOT NULL;
ALTER TABLE Recarga ALTER COLUMN hora SET NOT NULL;
ALTER TABLE Recarga ALTER COLUMN MetodoPago SET NOT NULL;

-- Para Sucursal
ALTER TABLE Sucursal ADD CONSTRAINT pk_sucursal PRIMARY KEY (idSucursal);
ALTER TABLE Sucursal ALTER COLUMN Nombre SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN Calle SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN NumExterior SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN NumInterior SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN Colonia SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN Estado SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN Telefono SET NOT NULL;
ALTER TABLE Sucursal ALTER COLUMN Horario SET NOT NULL;

-- Para Maquina
ALTER TABLE Maquina ADD CONSTRAINT pk_maquina PRIMARY KEY (idMaquina);
ALTER TABLE Maquina ALTER COLUMN Estado SET NOT NULL;
ALTER TABLE Maquina ALTER COLUMN idSucursal SET NOT NULL;
ALTER TABLE Maquina ALTER COLUMN idJuego SET NOT NULL;

-- Para Juego
ALTER TABLE Juego ADD CONSTRAINT pk_juego PRIMARY KEY (idJuego);
ALTER TABLE Juego ALTER COLUMN Nombre SET NOT NULL;
ALTER TABLE Juego ALTER COLUMN Tipo SET NOT NULL;
ALTER TABLE Juego ALTER COLUMN Costo SET NOT NULL;

-- Para Partida
ALTER TABLE Partida ADD CONSTRAINT pk_partida PRIMARY KEY (idPartida);
ALTER TABLE Partida ALTER COLUMN Puntaje SET NOT NULL;
ALTER TABLE Partida ALTER COLUMN PuntosGanados SET NOT NULL;
ALTER TABLE Partida ALTER COLUMN fecha SET NOT NULL;
ALTER TABLE Partida ALTER COLUMN hora SET NOT NULL;

-- Para Canje
ALTER TABLE Canje ADD CONSTRAINT pk_canje PRIMARY KEY (idCanje);
ALTER TABLE Canje ALTER COLUMN fecha SET NOT NULL;
ALTER TABLE Canje ALTER COLUMN hora SET NOT NULL;
ALTER TABLE Canje ALTER COLUMN PuntosUtilizados SET NOT NULL;
ALTER TABLE Canje ALTER COLUMN CantidadPremiosObtenidos SET NOT NULL;

-- Para Premio
ALTER TABLE Premio ADD CONSTRAINT pk_premio PRIMARY KEY (idPremio);
ALTER TABLE Premio ALTER COLUMN Nombre SET NOT NULL;
ALTER TABLE Premio ALTER COLUMN RangoEdad SET NOT NULL;
ALTER TABLE Premio ALTER COLUMN Categoria SET NOT NULL;
ALTER TABLE Premio ALTER COLUMN PuntosNecesarios SET NOT NULL;
ALTER TABLE Premio ALTER COLUMN ValorAprox SET NOT NULL;

-- Para Inventario
ALTER TABLE Inventario ADD CONSTRAINT pk_inventario PRIMARY KEY (idSucursal, idArticulo);
ALTER TABLE Inventario ALTER COLUMN CantidadDisponible SET NOT NULL;

-- Para Mantenimiento
ALTER TABLE Mantenimiento ADD CONSTRAINT pk_mantenimiento PRIMARY KEY (idMaquina, idMantenimiento);
ALTER TABLE Mantenimiento ALTER COLUMN fecha SET NOT NULL;
ALTER TABLE Mantenimiento ALTER COLUMN Tipo SET NOT NULL;
ALTER TABLE Mantenimiento ALTER COLUMN DescripcionProblema SET NOT NULL;

-- Para Empleado
ALTER TABLE Empleado ADD CONSTRAINT pk_empleado PRIMARY KEY (rfc);
ALTER TABLE Empleado ALTER COLUMN CURP SET NOT NULL;
ALTER TABLE Empleado ALTER COLUMN Nombre SET NOT NULL;
ALTER TABLE Empleado ALTER COLUMN Paterno SET NOT NULL;
ALTER TABLE Empleado ALTER COLUMN FechaNacimiento SET NOT NULL;
ALTER TABLE Empleado ALTER COLUMN FechaContratacion SET NOT NULL;
ALTER TABLE Empleado ALTER COLUMN Salario SET NOT NULL;

-- Para Telefono_Empleado
ALTER TABLE Telefono_Empleado ADD CONSTRAINT pk_telefono_empleado PRIMARY KEY (rfc, telefono);
ALTER TABLE Telefono_Empleado ALTER COLUMN telefono SET NOT NULL;

-- Para Correo_Empleado
ALTER TABLE Correo_Empleado ADD CONSTRAINT pk_correo_empleado PRIMARY KEY (rfc, correo);
ALTER TABLE Correo_Empleado ALTER COLUMN correo SET NOT NULL;

-- Para Cajero
ALTER TABLE Cajero ADD CONSTRAINT pk_cajero PRIMARY KEY (rfc);
ALTER TABLE Cajero ALTER COLUMN HorarioTrabajo SET NOT NULL;

-- Para Gerente
ALTER TABLE Gerente ADD CONSTRAINT pk_gerente PRIMARY KEY (rfc);
ALTER TABLE Gerente ADD CONSTRAINT uq_gerente_sucursal UNIQUE (idSucursal);
ALTER TABLE Gerente ALTER COLUMN idSucursal SET NOT NULL;
ALTER TABLE Gerente ALTER COLUMN CedulaProfesional SET NOT NULL;

-- Para EncargadoDePremio
ALTER TABLE EncargadoDePremio ADD CONSTRAINT pk_encargadodepremio PRIMARY KEY (rfc);
ALTER TABLE EncargadoDePremio ALTER COLUMN HorarioTrabajo SET NOT NULL;

-- Para Tecnico
ALTER TABLE Tecnico ADD CONSTRAINT pk_tecnico PRIMARY KEY (rfc);
ALTER TABLE Tecnico ALTER COLUMN AreaEspecialidad SET NOT NULL;

-- ====================================
-- Restricciones Referenciales
-- ====================================

-- Para Telefono_Cliente
ALTER TABLE Telefono_Cliente ADD CONSTRAINT fk_telefono_cliente FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente);

-- Para Correo_Cliente
ALTER TABLE Correo_Cliente ADD CONSTRAINT fk_correo_cliente FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente);

-- Para tarjeta
ALTER TABLE Tarjeta ADD CONSTRAINT fk_tarjeta_cliente FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente);
ALTER TABLE Tarjeta ADD CONSTRAINT fk_tarjeta_cajero  FOREIGN KEY (rfc_cajero) REFERENCES Cajero(rfc);

-- Para Recarga
ALTER TABLE Recarga ADD CONSTRAINT fk_recarga_sucursal FOREIGN KEY (idSucursal) REFERENCES Sucursal(idSucursal);
ALTER TABLE Recarga ADD CONSTRAINT fk_recarga_tarjeta FOREIGN KEY (idCliente, idTarjeta) REFERENCES Tarjeta(idCliente, idTarjeta);
ALTER TABLE Recarga ADD CONSTRAINT fk_recarga_cajero FOREIGN KEY (rfc_cajero) REFERENCES Cajero(rfc);

-- Para Maquina
ALTER TABLE Maquina ADD CONSTRAINT fk_maquina_sucursal FOREIGN KEY (idSucursal) REFERENCES Sucursal(idSucursal);
ALTER TABLE Maquina ADD CONSTRAINT fk_maquina_juego FOREIGN KEY (idJuego) REFERENCES Juego(idJuego);

-- Para Partida
ALTER TABLE Partida ADD CONSTRAINT fk_partida_maquina FOREIGN KEY (idMaquina) REFERENCES Maquina(idMaquina);
ALTER TABLE Partida ADD CONSTRAINT fk_partida_tarjeta FOREIGN KEY (idCliente, idTarjeta) REFERENCES Tarjeta(idCliente, idTarjeta);

-- Para Canje
ALTER TABLE Canje ADD CONSTRAINT fk_canje_sucursal FOREIGN KEY (idSucursal) REFERENCES Sucursal(idSucursal);
ALTER TABLE Canje ADD CONSTRAINT fk_canje_cliente FOREIGN KEY (idCliente) REFERENCES Cliente(idCliente);
ALTER TABLE Canje ADD CONSTRAINT fk_canje_premio FOREIGN KEY (idPremio) REFERENCES Premio(idPremio);
ALTER TABLE Canje ADD CONSTRAINT fk_canje_encargado FOREIGN KEY (rfc_EncargadoDePremios) REFERENCES EncargadoDePremio(rfc);

-- Para Inventario
ALTER TABLE Inventario ADD CONSTRAINT fk_inventario_sucursal FOREIGN KEY (idSucursal) REFERENCES Sucursal(idSucursal);
ALTER TABLE Inventario ADD CONSTRAINT fk_inventario_premio FOREIGN KEY (idPremio) REFERENCES Premio(idPremio);

-- Para Mantenimiento
ALTER TABLE Mantenimiento ADD CONSTRAINT fk_mantenimiento_maquina FOREIGN KEY (idMaquina) REFERENCES Maquina(idMaquina);
ALTER TABLE Mantenimiento ADD CONSTRAINT fk_mantenimiento_tecnico FOREIGN KEY (rfc_Tecnico) REFERENCES Tecnico(rfc);

-- Para Telefono_Empleado
ALTER TABLE Telefono_Empleado ADD CONSTRAINT fk_telefono_empleado FOREIGN KEY (rfc) REFERENCES Empleado(rfc);

-- Para Correo_Empleado
ALTER TABLE Correo_Empleado ADD CONSTRAINT fk_correo_empleado FOREIGN KEY (rfc) REFERENCES Empleado(rfc);

-- Para Cajero
ALTER TABLE Cajero ADD CONSTRAINT fk_cajero_empleado FOREIGN KEY (rfc) REFERENCES Empleado(rfc);

-- Para Gerente
ALTER TABLE Gerente ADD CONSTRAINT fk_gerente_empleado FOREIGN KEY (rfc) REFERENCES Empleado(rfc);
ALTER TABLE Gerente ADD CONSTRAINT fk_gerente_sucursal FOREIGN KEY (idSucursal) REFERENCES Sucursal(idSucursal);

-- Para EncargadoDePremio
ALTER TABLE EncargadoDePremio ADD CONSTRAINT fk_encargadodepremio_empleado FOREIGN KEY (rfc) REFERENCES Empleado(rfc);

-- Para Tecnico
ALTER TABLE Tecnico ADD CONSTRAINT fk_tecnico_empleado FOREIGN KEY (rfc) REFERENCES Empleado(rfc);

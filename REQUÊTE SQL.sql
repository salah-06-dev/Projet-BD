CREATE DATABASE IF NOT EXISTS hotel_management;
USE hotel_management;

-- Table Hotel
CREATE TABLE Hotel (
    Id_Hotel INT AUTO_INCREMENT PRIMARY KEY,
    Ville VARCHAR(255),
    Pays VARCHAR(255),
    Code_postal INT
);

-- Table Type_Chambre
CREATE TABLE Type_Chambre (
    Id_Type INT AUTO_INCREMENT PRIMARY KEY,
    Type VARCHAR(255),
    Tarif DECIMAL(10,2)
);

-- Table Chambre
CREATE TABLE Chambre (
    Id_Chambre INT AUTO_INCREMENT PRIMARY KEY,
    Numero INT,
    Etage INT,
    Fumeur BOOLEAN,
    Id_Hotel INT,
    Id_Type INT,
    FOREIGN KEY (Id_Hotel) REFERENCES Hotel(Id_Hotel),
    FOREIGN KEY (Id_Type) REFERENCES Type_Chambre(Id_Type)
);

-- Table Client
CREATE TABLE Client (
    Id_Client INT AUTO_INCREMENT PRIMARY KEY,
    Adresse VARCHAR(255),
    Ville VARCHAR(255),
    Code_postal INT,
    Email VARCHAR(255),
    Telephone VARCHAR(20),
    Nom_complet VARCHAR(255)
);

-- Table Prestation
CREATE TABLE Prestation (
    Id_Prestation INT AUTO_INCREMENT PRIMARY KEY,
    Prix DECIMAL(10,2),
    Description TEXT
);

-- Table Reservation
CREATE TABLE Reservation (
    Id_Reservation INT AUTO_INCREMENT PRIMARY KEY,
    Date_arrivee DATE,
    Date_depart DATE,
    Id_Client INT,
    FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
);

-- Table Evaluation
CREATE TABLE Evaluation (
    Id_Evaluation INT AUTO_INCREMENT PRIMARY KEY,
    Date_eval DATE,
    Note INT,
    Commentaire TEXT,
    Id_Client INT,
    FOREIGN KEY (Id_Client) REFERENCES Client(Id_Client)
);

-- Table de liaison Chambre_Reservation
CREATE TABLE Chambre_Reservation (
    Id_Chambre INT,
    Id_Reservation INT,
    PRIMARY KEY (Id_Chambre, Id_Reservation),
    FOREIGN KEY (Id_Chambre) REFERENCES Chambre(Id_Chambre),
    FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation)
);

-- Table de liaison Prestation_Reservation
CREATE TABLE Prestation_Reservation (
    Id_Prestation INT,
    Id_Reservation INT,
    PRIMARY KEY (Id_Prestation, Id_Reservation),
    FOREIGN KEY (Id_Prestation) REFERENCES Prestation(Id_Prestation),
    FOREIGN KEY (Id_Reservation) REFERENCES Reservation(Id_Reservation)
);


-- Insertion des hôtels
INSERT INTO Hotel (Id_Hotel, Ville, Pays, Code_postal) VALUES 
(1, 'Paris', 'France', 75001),
(2, 'Lyon', 'France', 69002);

-- Insertion des clients
INSERT INTO Client (Id_Client, Adresse, Ville, Code_postal, Email, Telephone, Nom_complet) VALUES 
(1, '12 Rue de Paris', 'Paris', 75001, 'jean.dupont@email.fr', '0612345678', 'Jean Dupont'),
(2, '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie.leroy@email.fr', '0623456789', 'Marie Leroy'),
(3, '8 Boulevard Saint-Michel', 'Marseille', 13005, 'paul.moreau@email.fr', '0634567890', 'Paul Moreau'),
(4, '27 Rue Nationale', 'Lille', 59800, 'lucie.martin@email.fr', '0645678901', 'Lucie Martin'),
(5, '3 Rue des Fleurs', 'Nice', 06000, 'emma.giraud@email.fr', '0656789012', 'Emma Giraud');

-- Insertion des prestations
INSERT INTO Prestation (Id_Prestation, Prix, Description) VALUES 
(1, 15, 'Petit-déjeuner'),
(2, 30, 'Navette aéroport'),
(3, 0, 'Wi-Fi gratuit'),
(4, 50, 'Spa et bien-être'),
(5, 20, 'Parking sécurisé');

-- Insertion des types de chambre
INSERT INTO Type_Chambre (Id_Type, Type, Tarif) VALUES 
(1, 'Simple', 80),
(2, 'Double', 120);

-- Insertion des chambres
INSERT INTO Chambre (Id_Chambre, Numero, Etage, Fumeur, Id_Hotel, Id_Type) VALUES 
(1, 201, 2, 0, 1, 1),
(2, 502, 5, 1, 1, 2),
(3, 305, 3, 0, 2, 1),
(4, 410, 4, 0, 2, 2),
(5, 104, 1, 1, 2, 2),
(6, 202, 2, 0, 1, 1),
(7, 307, 3, 1, 1, 2),
(8, 101, 1, 0, 1, 1);

-- Insertion des réservations
INSERT INTO Reservation (Id_Reservation, Date_arrivee, Date_depart, Id_Client) VALUES 
(1, '2025-06-15', '2025-06-18', 1),
(2, '2025-07-01', '2025-07-05', 2),
(3, '2025-08-10', '2025-08-14', 3),
(4, '2025-09-05', '2025-09-07', 4),
(5, '2025-09-20', '2025-09-25', 5),
(7, '2025-11-12', '2025-11-14', 2),
(9, '2026-01-15', '2026-01-18', 4),
(10, '2026-02-01', '2026-02-05', 2);

-- Insertion des évaluations
INSERT INTO Evaluation (Id_Evaluation, Date_eval, Note, Commentaire, Id_Client) VALUES 
(1, '2025-06-15', 5, 'Excellent séjour, personnel très accueillant.', 1),
(2, '2025-07-01', 4, 'Chambre propre, bon rapport qualité/prix.', 2),
(3, '2025-08-10', 3, 'Séjour correct mais bruyant la nuit.', 3),
(4, '2025-09-05', 5, 'Service impeccable, je recommande.', 4),
(5, '2025-09-20', 4, 'Très bon petit-déjeuner, hôtel bien situé.', 5);

SELECT r.Id_Reservation, c.Nom_complet, h.Ville
FROM Reservation r
JOIN Client c ON r.Id_Client = c.Id_Client
JOIN Chambre_Reservation cr ON r.Id_Reservation = cr.Id_Reservation
JOIN Chambre ch ON cr.Id_Chambre = ch.Id_Chambre
JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel;

SELECT * FROM Client WHERE Ville = 'Paris';

SELECT c.Id_Client, c.Nom_complet, COUNT(r.Id_Reservation) AS Nombre_Reservations
FROM Client c
LEFT JOIN Reservation r ON c.Id_Client = r.Id_Client
GROUP BY c.Id_Client, c.Nom_complet;

SELECT tc.Type, COUNT(c.Id_Chambre) AS Nombre_Chambres
FROM Type_Chambre tc
LEFT JOIN Chambre c ON tc.Id_Type = c.Id_Type
GROUP BY tc.Type;

SELECT ch.* 
FROM Chambre ch
WHERE ch.Id_Chambre NOT IN (
    SELECT cr.Id_Chambre
    FROM Chambre_Reservation cr
    JOIN Reservation r ON cr.Id_Reservation = r.Id_Reservation
    WHERE (r.Date_arrivee <= '2025-06-20' AND r.Date_depart >= '2025-06-15')
);


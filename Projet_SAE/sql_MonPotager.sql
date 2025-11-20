
DROP TABLE IF EXISTS classe_dans;
DROP TABLE IF EXISTS effectue;
DROP TABLE IF EXISTS correspond;
DROP TABLE IF EXISTS est_recolte;
DROP TABLE IF EXISTS est_plante;
DROP TABLE IF EXISTS posee;
DROP TABLE IF EXISTS est_associe;

DROP TABLE IF EXISTS action;
DROP TABLE IF EXISTS signalement;
DROP TABLE IF EXISTS produit;

DROP TABLE IF EXISTS type_produit;
DROP TABLE IF EXISTS type_signalement;
DROP TABLE IF EXISTS type_action;
DROP TABLE IF EXISTS type_sol;
DROP TABLE IF EXISTS categorie;
DROP TABLE IF EXISTS date_action;
DROP TABLE IF EXISTS date_plantation;
DROP TABLE IF EXISTS date_recolte;
DROP TABLE IF EXISTS parcelle;
DROP TABLE IF EXISTS adherent;

CREATE TABLE adherent (
    id_adherent INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50),
    adresse VARCHAR(255),
    numero_de_telephone VARCHAR(10)
);

CREATE TABLE parcelle (
    id_parcelle INT AUTO_INCREMENT PRIMARY KEY,
    largeur INT,
    longueur INT
);

CREATE TABLE type_signalement (
    id_type_signalement INT AUTO_INCREMENT PRIMARY KEY,
    libelle_type_signalement VARCHAR(255)
);

CREATE TABLE type_sol (
    id_type_sol INT AUTO_INCREMENT PRIMARY KEY,
    libelle_type_sol VARCHAR(255)
);

CREATE TABLE categorie (
    id_categorie INT AUTO_INCREMENT PRIMARY KEY,
    libelle_categorie VARCHAR(255)
);

CREATE TABLE date_action (
    id_date_action INT AUTO_INCREMENT PRIMARY KEY,
    date_action DATE
);

CREATE TABLE type_action (
    id_type_action INT AUTO_INCREMENT PRIMARY KEY,
    libelle_type_action VARCHAR(255)
);

CREATE TABLE date_plantation (
    id_date_plantation INT AUTO_INCREMENT PRIMARY KEY,
    date_plantation DATE
);

CREATE TABLE date_recolte (
    id_date_recolte INT AUTO_INCREMENT PRIMARY KEY,
    date_recolte DATE
);

CREATE TABLE type_produit (
    id_type_produit INT AUTO_INCREMENT PRIMARY KEY,
    libelle_type_produit VARCHAR(255)
);


CREATE TABLE produit (
    id_produit INT AUTO_INCREMENT PRIMARY KEY,
    libelle_produit VARCHAR(255),
    periode_recolte_optimale VARCHAR(255),
    periode_plantation_optimale VARCHAR(255),
    categorie_id INT NOT NULL,
    prix_produit NUMERIC(5,2),
    FOREIGN KEY (categorie_id) REFERENCES categorie(id_categorie)
);

CREATE TABLE signalement (
    id_signalement INT AUTO_INCREMENT PRIMARY KEY,
    descriptif VARCHAR(255),
    photo VARCHAR(255),
    date_signalement DATE,
    type_signalement_id INT NOT NULL,
    adherent_id INT NOT NULL,
    FOREIGN KEY (type_signalement_id) REFERENCES type_signalement(id_type_signalement),
    FOREIGN KEY (adherent_id) REFERENCES adherent(id_adherent)
);

CREATE TABLE action (
    id_action INT AUTO_INCREMENT PRIMARY KEY,
    libelle_action VARCHAR(255),
    date_action_id INT NOT NULL,
    parcelle_id INT NOT NULL,
    type_action_id INT NOT NULL,
    FOREIGN KEY (date_action_id) REFERENCES date_action(id_date_action),
    FOREIGN KEY (parcelle_id) REFERENCES parcelle(id_parcelle),
    FOREIGN KEY (type_action_id) REFERENCES type_action(id_type_action)
);


CREATE TABLE est_associe (
    adherent_id INT,
    parcelle_id INT,
    PRIMARY KEY (adherent_id, parcelle_id),
    FOREIGN KEY (adherent_id) REFERENCES adherent(id_adherent),
    FOREIGN KEY (parcelle_id) REFERENCES parcelle(id_parcelle)
);

CREATE TABLE posee (
    parcelle_id INT,
    type_sol_id INT,
    PRIMARY KEY (parcelle_id, type_sol_id),
    FOREIGN KEY (parcelle_id) REFERENCES parcelle(id_parcelle),
    FOREIGN KEY (type_sol_id) REFERENCES type_sol(id_type_sol)
);

CREATE TABLE est_plante (
    parcelle_id INT,
    produit_id INT,
    date_plantation_id INT,
    PRIMARY KEY (parcelle_id, produit_id, date_plantation_id),
    FOREIGN KEY (parcelle_id) REFERENCES parcelle(id_parcelle),
    FOREIGN KEY (produit_id) REFERENCES produit(id_produit),
    FOREIGN KEY (date_plantation_id) REFERENCES date_plantation(id_date_plantation)
);

CREATE TABLE est_recolte (
    parcelle_id INT,
    produit_id INT,
    date_recolte_id INT,
    quantite_recoltee INT,
    PRIMARY KEY (parcelle_id, produit_id, date_recolte_id),
    FOREIGN KEY (parcelle_id) REFERENCES parcelle(id_parcelle),
    FOREIGN KEY (produit_id) REFERENCES produit(id_produit),
    FOREIGN KEY (date_recolte_id) REFERENCES date_recolte(id_date_recolte)
);

CREATE TABLE correspond (
    parcelle_id INT,
    signalement_id INT,
    PRIMARY KEY (parcelle_id, signalement_id),
    FOREIGN KEY (parcelle_id) REFERENCES parcelle(id_parcelle),
    FOREIGN KEY (signalement_id) REFERENCES signalement(id_signalement)
);

CREATE TABLE effectue (
    adherent_id INT,
    action_id INT,
    PRIMARY KEY (adherent_id, action_id),
    FOREIGN KEY (adherent_id) REFERENCES adherent(id_adherent),
    FOREIGN KEY (action_id) REFERENCES action(id_action)
);

CREATE TABLE classe_dans (
    produit_id INT,
    type_produit_id INT,
    PRIMARY KEY (produit_id, type_produit_id),
    FOREIGN KEY (produit_id) REFERENCES produit(id_produit),
    FOREIGN KEY (type_produit_id) REFERENCES type_produit(id_type_produit)
);

INSERT INTO adherent VALUES
(1, 'Beuret', '3 rue Fernand Papillon', '0601020304'),
(2, 'Bendiaf', '2 rue Bossière', '0769302665'),
(3, 'Decailloz', '14 rue de la Cavalerie', '0708091011'),
(4, 'Bajic', '11 rue des Epiceas', '0651369236');

INSERT INTO parcelle VALUES
(1, 300, 300),
(2, 450, 200),
(3, 225, 280);

INSERT INTO type_signalement VALUES
(1, 'Problème d’irrigation'),
(2, 'Sol trop sec'),
(3, 'PH inadapté'),
(4, 'Présence de pierres ou débris'),
(5, 'Érosion'),
(6, 'Animaux Sauvage'),
(7, 'Infestation insecte'),
(8, 'Plante malade'),
(9, 'Vol de plante'),
(10, 'Polution'),
(11, 'Ashèchement'),
(12, 'Sol inondé');

INSERT INTO type_sol VALUES
(1, 'Argileux'),
(2, 'Sableux'),
(3, 'Limonieux'),
(4, 'Calcaire'),
(5, 'Humifère'),
(6, 'Riche'),
(7, 'Pauvre'),
(8, 'Rocailleux');

INSERT INTO categorie VALUES
(1, 'Légume'),
(2, 'Fruit');

INSERT INTO type_action VALUES
(1, 'Désherber'),
(2, 'Arroser'),
(3, 'Labourer'),
(4, 'Nettoyer'),
(5, 'Verifier'),
(6, 'Fertiliser');

INSERT INTO type_produit VALUES
(1,'Cucurbitacée'),
(2,'Solanacée'),
(3,'Légumineuse'),
(4,'Brassicacée'),
(5,'Alliacée'),
(6,'Fruit à noyau'),
(7,'Fruit à pépins'),
(8,'Fruit à coque'),
(9,'Fruit monosperme'),
(10,'Racine tuberculeuse'),
(11,'Feuille potagère'),
(12,'Plante aromatique'),
(13,'Céréale'),
(14,'Plante oléagineuse'),
(15,'Plante médicinale');

INSERT INTO date_action VALUES
(1,'2025-03-01'),
(2,'2025-03-15'),
(3,'2025-04-01'),
(4,'2025-04-10'),
(5,'2025-05-01');

INSERT INTO date_plantation VALUES
(1,'2025-03-05'),
(2,'2025-03-20'),
(3,'2025-04-05'),
(4,'2025-04-15'),
(5,'2025-03-25'),
(6,'2025-04-10'),
(7,'2025-04-20'),
(8,'2025-05-01'),
(9,'2025-05-10'),
(10,'2025-05-20');

INSERT INTO date_recolte VALUES
(1,'2025-06-01'),
(2,'2025-06-15'),
(3,'2025-07-01'),
(4,'2025-07-15'),
(5,'2025-06-20'),
(6,'2025-07-05'),
(7,'2025-07-20'),
(8,'2025-08-05'),
(9,'2025-08-15'),
(10,'2025-09-01');

INSERT INTO produit VALUES
(1,'Tomate','Mars-Avril','Juin-Juillet',2, 2.50),
(2,'Carotte','Mars-Avril','Juin-Juillet',1, 1.20),
(3,'Courgette','Avril-Mai','Juillet-Août',1, 2.00),
(4,'Pomme','Avril-Mai','Septembre-Octobre',2, 1.80),
(5,'Poire','Avril-Mai','Septembre-Octobre',2, 1.70),
(6,'Poivron','Mars-Avril','Juillet-Août',1, 2.30),
(7,'Salade','Mars-Avril','Mai-Juin',1, 1.50),
(8,'Épinard','Mars-Avril','Avril-Mai',1, 1.60),
(9,'Betterave','Mars-Avril','Juin-Juillet',1, 1.40),
(10,'Radis','Mars-Avril','Mai-Juin',1, 1.10),
(11,'Chou-fleur','Avril-Mai','Juillet-Août',1, 2.10),
(12,'Brocoli','Avril-Mai','Juillet-Août',1, 2.20),
(13,'Aubergine','Avril-Mai','Juillet-Août',1, 2.40),
(14,'Courge','Avril-Mai','Septembre-Octobre',1, 3.00),
(15,'Citrouille','Avril-Mai','Octobre',1, 2.80),
(16,'Cerise','Mars-Avril','Juin',2, 3.50),
(17,'Fraise','Mars-Avril','Mai-Juin',2, 3.20),
(18,'Framboise','Avril-Mai','Juillet',2, 3.30),
(19,'Myrtille','Avril-Mai','Juillet-Août',2, 3.60),
(20,'Raisin','Mars-Avril','Septembre',2, 2.90),
(21,'Abricot','Mars-Avril','Juin-Juillet',2, 3.10),
(22,'Pêche','Avril-Mai','Juillet-Août',2, 3.00),
(23,'Prune','Mars-Avril','Août',2, 2.70),
(24,'Melon','Avril-Mai','Juillet-Août',2, 3.20),
(25,'Pastèque','Avril-Mai','Juillet-Août',2, 3.40),
(26,'Kiwis','Avril-Mai','Octobre',2, 3.50),
(27,'Poireau','Juin-Juillet','Octobre-Novembre',1, 1.80),
(28,'Oignon','Mars-Avril','Août-Septembre',1, 1.50),
(29,'Ail','Mars-Avril','Juillet-Août',1, 2.00),
(30,'Navet','Mars-Avril','Juin',1, 1.60),
(31,'Chou de Bruxelles','Mars-Avril','Septembre-Octobre',1, 2.20);

INSERT INTO signalement VALUES
(1,'Sol trop sec à l’extrémité de la parcelle','photo1.jpg','2025-03-10',2,1),
(2,'Présence de pierres','photo2.jpg','2025-03-12',4,2),
(3,'Irrigation défectueuse','photo3.jpg','2025-04-01',1,3);

INSERT INTO action VALUES
(1,'Arroser parcelle 1',2,1,2),
(2,'Désherber parcelle 2',1,2,1),
(3,'Labourer parcelle 3',3,3,3);

INSERT INTO est_associe VALUES
(1,1),
(2,2),
(3,3),
(4,1);

INSERT INTO posee VALUES
(1,1),
(2,2),
(3,3);

INSERT INTO est_plante VALUES
(1,1,1),
(1,2,2),
(2,3,3),
(3,1,4),
(1,6,5),
(1,7,6),
(2,8,5),
(2,9,6),
(3,10,7),
(3,11,8),
(1,12,5),
(2,13,6),
(3,14,7),
(1,15,8),
(2,16,5),
(3,17,6),
(1,18,7),
(2,19,8),
(3,20,5),
(1,21,6),
(2,22,7),
(3,23,8),
(1,24,5),
(2,25,6),
(3,26,7),
(1,27,8),
(2,28,5),
(3,29,6),
(1,30,7),
(2,31,8);

INSERT INTO est_recolte VALUES
(1,1,1,50),
(1,2,2,30),
(2,3,3,40),
(1,6,5,60),
(1,7,6,50),
(2,8,5,40),
(2,9,6,30),
(3,10,7,20),
(3,11,8,25),
(1,12,5,35),
(2,13,6,45),
(3,14,7,55),
(1,15,8,40),
(2,16,5,50),
(3,17,6,60),
(1,18,7,20),
(2,19,8,25),
(3,20,5,30),
(1,21,6,35),
(2,22,7,40),
(3,23,8,45),
(1,24,5,50),
(2,25,6,55),
(3,26,7,60),
(1,27,8,65),
(2,28,5,20),
(3,29,6,25),
(1,30,7,30),
(2,31,8,35);

INSERT INTO correspond VALUES
(1,1),
(2,2),
(3,3);

INSERT INTO effectue VALUES
(1,1),
(2,2),
(3,3);

INSERT INTO classe_dans VALUES
(1,2),
(2,10),
(3,1),
(4,6),
(5,7),
(6,2),
(7,11),
(8,11),
(9,10),
(10,10),
(11,4),
(12,4),
(13,2),
(14,1),
(15,1),
(16,6),
(17,6),
(18,7),
(19,7),
(20,7),
(21,7),
(22,7),
(23,6),
(24,6),
(25,6),
(26,6),
(27,6),
(28,7),
(29,5),
(30,5),
(31,5);

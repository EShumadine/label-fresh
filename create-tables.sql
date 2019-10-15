DROP TABLE IF EXISTS allergen;
DROP TABLE IF EXISTS diet;
DROP TABLE IF EXISTS report;

CREATE TABLE report (
	id int AUTO_INCREMENT NOT NULL PRIMARY KEY,
	name varchar(50),
	served date NOT NULL,
	hall enum('Bates', 'Tower', 'Stone Davis', 'Pomeroy', 'Bae Pow Lu Chow') NOT NULL,
	notes varchar(300),
	image varchar(30),
	owner varchar(8)
) ENGINE = InnoDB;

CREATE TABLE allergen (
	id int NOT NULL,
	code enum('W', 'M', 'E', 'S', 'P', 'TN', 'F', 'SF', 'None', 'Unknown') NOT NULL,
    kind enum('listed', 'present') NOT NULL,
	PRIMARY KEY (id, code, kind),
	INDEX (id),
	FOREIGN KEY (id) REFERENCES report(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE diet (
	id int NOT NULL,
	code enum('VE', 'V', 'GS', 'H', 'None', 'Unknown') NOT NULL,
    kind enum('listed', 'followed'),
	PRIMARY KEY (id, code, kind),
	INDEX (id),
	FOREIGN KEY (id) REFERENCES report(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
) ENGINE = InnoDB;
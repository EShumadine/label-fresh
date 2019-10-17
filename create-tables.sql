DROP TABLE IF EXISTS label;
DROP TABLE IF EXISTS report;

CREATE TABLE report (
	id int auto_increment NOT NULL,
	name varchar(50) NOT NULL,
	served date NOT NULL,
	meal enum('Breakfast', 'Lunch', 'Dinner') NOT NULL,
	hall enum('Bates', 'Tower', 'Stone Davis', 'Pomeroy', 'Bae Pow Lu Chow') NOT NULL,
	notes varchar(300),
	image varchar(30),
	owner varchar(8),
	PRIMARY KEY (name, served, meal, hall),
	INDEX (name, hall),
	INDEX (id)
) ENGINE = InnoDB;

CREATE TABLE label (
	id int NOT NULL,
	code enum('W', 'M', 'E', 'S', 'P', 'TN', 'F', 'SF', 'VE', 'V', 'GS', 'H', 'None', 'Unknown') NOT NULL,
    labeled enum('listed', 'actual') NOT NULL,
	kind enum('allergen', 'diet') NOT NULL,
	PRIMARY KEY (id, code, labeled, kind),
	INDEX (id),
	FOREIGN KEY (id) REFERENCES report(id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
) ENGINE = InnoDB;
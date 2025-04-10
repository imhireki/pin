CREATE TABLE pindb.pin (
	id int UNSIGNED auto_increment NOT NULL,
	url varchar(75) NOT NULL,
	title varchar(255) NULL,
	description varchar(255) NULL,
	dominant_color varchar(7) NULL,
  external_id varchar(30) NOT NULL,
	CONSTRAINT pk_pin PRIMARY KEY (id)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE pindb.image (
	id int UNSIGNED auto_increment NOT NULL,
	url varchar(100) NOT NULL,
	pin_id int UNSIGNED NOT NULL,
	CONSTRAINT pk_image PRIMARY KEY (id),
	CONSTRAINT fk_pin_image FOREIGN KEY (pin_id)
		REFERENCES pindb.pin(id)
		ON DELETE CASCADE ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE pindb.hashtag (
	id int UNSIGNED NOT NULL auto_increment,
	hashtag varchar(255) NOT NULL,
	pin_id int UNSIGNED NOT NULL, CONSTRAINT pk_hashtag PRIMARY KEY (id),
	CONSTRAINT fk_pin_hashtag FOREIGN KEY (pin_id)
		REFERENCES pindb.pin(id)
		ON DELETE CASCADE ON UPDATE CASCADE
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;

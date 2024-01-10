CREATE TABLE public.pin (
	id int NOT NULL GENERATED ALWAYS AS IDENTITY,
	url varchar(75) NOT NULL,
	title varchar(255) NULL,
	description varchar(255) NULL,
	dominant_color varchar(7) NULL,
	CONSTRAINT pk_pin PRIMARY KEY (id)
);

CREATE TABLE public.image (
	id int NOT NULL GENERATED ALWAYS AS IDENTITY,
	url varchar(100) NOT NULL,
	pin_id int NOT NULL,
	CONSTRAINT pk_image PRIMARY KEY (id),
	CONSTRAINT fk_pin_image FOREIGN KEY (pin_id)
        REFERENCES public.pin(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE public.hashtag (
	id int NOT NULL GENERATED ALWAYS AS IDENTITY,
	hashtag varchar(255) NOT NULL,
	pin_id int NOT NULL,
	CONSTRAINT pk_hashtag PRIMARY KEY (id),
	CONSTRAINT fk_pin_hashtag FOREIGN KEY (pin_id)
        REFERENCES public.pin(id) 
        ON DELETE CASCADE ON UPDATE CASCADE
);

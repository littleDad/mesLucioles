/* script de création des tables du module TAD. */
/*
 - intégrer les contraintes
 - finir de reproduire le MdD
 - intégrer les triggers (events + gestion de l'historique de la base, en termes de chronologie dans le temps)

*/

drop table if exists t_resa_section cascade;
drop table if exists t_resa_journey;
drop table if exists t_line;
drop table if exists t_user cascade;
drop table if exists t_role cascade;
drop table if exists t_company;
drop table if exists t_call cascade;
drop table if exists t_event;

create table t_line
(
    line_code VARCHAR(10) PRIMARY KEY NOT NULL,
    color VARCHAR(10), 
    description VARCHAR(100),
    company_id INT
);
insert into t_line (line_code) values ('105');
insert into t_line (line_code) values ('106');
insert into t_line (line_code) values ('118');
insert into t_line (line_code) values ('119');
insert into t_line (line_code) values ('120');
insert into t_line (line_code) values ('201');
insert into t_line (line_code) values ('202');
insert into t_line (line_code) values ('204');
insert into t_line (line_code) values ('205');


create table t_role
(
    id serial PRIMARY KEY NOT NULL,
	name VARCHAR(30) NOT NULL -- 'customer', 'c_op', 'c_sup', 'tr_op', 'tr_sup', 'admin', 'master'
);
-- V le temps des tests V
insert into t_role (id, name) values(1, 'customer');
insert into t_role (id, name) values(2, 'c_op');
insert into t_role (id, name) values(3, 'c_sup');
insert into t_role (id, name) values(4, 'tr_op');
insert into t_role (id, name) values(5, 'tr_sup');
insert into t_role (id, name) values(6, 'admin');
insert into t_role (id, name) values(7, 'master');


create table t_user
(
    old_id BIGINT UNIQUE, -- le temps de la migration. à supprimer plus tard. "ALTER TABLE t_user DROP COLUMN old_id"
    id serial PRIMARY KEY NOT NULL,
    role_id INT REFERENCES t_role(id),
    login VARCHAR(30),
    name VARCHAR(30) NOT NULL,
    firstname VARCHAR(30), -- NOT NULL beaucoup de users de l'ancienne base ont nom+prénom dans le champ nom uniquement
    old_password VARCHAR(90),
    password VARCHAR(90),
    email VARCHAR(100),
    phone VARCHAR(100),
    pmr boolean, -- not CNIL
    creation_date timestamp,
    auto_resa_allowed boolean
);

create table t_resa_journey
(
    old_id BIGINT UNIQUE,
    id serial PRIMARY KEY NOT NULL,
    departure VARCHAR(100),
    departure_date_time timestamp,
    arrival VARCHAR(100),
    arrival_date_time timestamp,
    user_id INT REFERENCES t_user(id),
    prm BOOLEAN,
    seats INT,
    comment VARCHAR(500),
    token VARCHAR(50) UNIQUE
);

drop type if exists status_type;
create type status_type as enum('ok', 'cancelled', 'out_of_time_cancelled', 'absence');
create table t_resa_section
(
    id serial PRIMARY KEY NOT NULL,
    service_id VARCHAR(100),
    line_code VARCHAR(10) REFERENCES t_line(line_code),
    status status_type,
    resa INT REFERENCES t_resa_journey(id),
    departure_date_time timestamp NOT NULL,
	departure_stop_code BIGINT NOT NULL,
	departure_stop_name VARCHAR(200) NOT NULL,
	departure_stop_city VARCHAR(200) NOT NULL,
	departure_area_name VARCHAR(200) NOT NULL,
    arrival_date_time timestamp NOT NULL,
	arrival_stop_code BIGINT NOT NULL,
	arrival_stop_name VARCHAR(200) NOT NULL,
	arrival_stop_city VARCHAR(200) NOT NULL,
	arrival_area_name VARCHAR(200) NOT NULL
);


create table t_company
(
    id serial PRIMARY KEY NOT NULL,
    name VARCHAR(30),
    activity_start timestamp,
    activity_end timestamp,

    user_id INT REFERENCES t_user(id) -- currently operator or driver. families in the future?
);

drop type if exists call_type;
create type call_type as enum('Appel', 'Appel sortant', 'Saisie', 'Appel radio / service', 'Redirection d''appel ou de la demande vers Allô Tisséo');
create table t_call
(
    id serial PRIMARY KEY NOT NULL,
    start_time timestamp,
    end_time timestamp,
    customer_id INT,
    type call_type,
    comment VARCHAR(500),
    operator_id INT REFERENCES t_user(id) NOT NULL
);

drop type if exists event_type;
-- V on pourrait simplifier cet enum, puis refaire l'association au niveau de jinja2. par exemple "add_user" plutôt que "Création d'utilisateur".
create type event_type as enum('Création d''utilisateur', 'Réservation', 'Annulation', 'Changement de mot de passe', 'Modification d''attributs', 'Demande d''informations', 'Autre'); -- à finir
create table t_event
(
    id serial PRIMARY KEY NOT NULL,
    type event_type,
    time timestamp,
    resa_id INT REFERENCES t_resa_section(id),
    customer_id INT REFERENCES t_user(id),
    -- old_customer_id BIGINT REFERENCES t_user(id), -- le temps de la migration
    user_id INT REFERENCES t_user(id),
    old_user_id BIGINT, -- le temps de la migration.
	source VARCHAR(32), -- 'phonecall','webapp', 'mobile', 'ihm'
    call_id INT REFERENCES t_call(id)
);


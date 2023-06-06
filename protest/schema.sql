-- to clear db find topological order of tables in dependency graph
DROP TABLE IF EXISTS Participation;
DROP TABLE IF EXISTS Report;
DROP TABLE IF EXISTS Protection;
DROP TABLE IF EXISTS Worldview;
DROP TABLE IF EXISTS Protest;
DROP TABLE IF EXISTS Guard;
DROP TABLE IF EXISTS GovernmentAction;
DROP TABLE IF EXISTS OrganizationMember;


CREATE TABLE OrganizationMember(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER CHECK (age >= 18),
    login VARCHAR(10),
    hashed_password VARCHAR(255),
    organizer_privilege BOOLEAN
);

CREATE TABLE GovernmentAction(
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE CHECK (char_length(title) > 0),
    organizer_id INTEGER REFERENCES OrganizationMember(id)
);

CREATE TABLE Protest(
    id SERIAL PRIMARY KEY,
    organizer_id INTEGER REFERENCES OrganizationMember(id),
    action_id INTEGER REFERENCES GovernmentAction(id),
    start_time TIMESTAMP,
    town VARCHAR(255),
    coordinates POINT,
    boombox_number INTEGER NOT NULL CHECK (boombox_number > 0)
);

CREATE TABLE Participation(
    member_id INTEGER REFERENCES OrganizationMember(id),
    protest_id INTEGER REFERENCES Protest(id)
);

CREATE TABLE Report(
    member_id INTEGER REFERENCES OrganizationMember(id),
    protest_id INTEGER REFERENCES Protest(id),
    rating INTEGER NOT NULL CHECK (1 <= rating AND rating <= 10),
    description VARCHAR(1024)
);

CREATE TABLE Guard(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    added_by INTEGER REFERENCES OrganizationMember(id),
    weight INTEGER NOT NULL CHECK (weight >= 80),
    running_speed INTEGER NOT NULL CHECK (running_speed >= 20)
);

CREATE TABLE Protection(
    guard_id INTEGER REFERENCES Guard(id),
    protest_id INTEGER REFERENCES Protest(id)
);

CREATE TABLE Worldview(
    guard_id INTEGER REFERENCES Guard(id),
    action_id INTEGER REFERENCES Protest(id)
);


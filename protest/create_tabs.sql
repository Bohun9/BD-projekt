CREATE TABLE OrganizationMember(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER CHECK (age >= 18),
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
    start_time DATETIME,
    town VARCHAR(255),
    geographical_coordinate VARCHAR(255),
    boombox_number INTEGER NOT NULL CHECK (boombox_number > 0)
);

CREATE TABLE Participation(
    member_id INTEGER REFERENCES OrganizationMember(id),
    protest_id INTEGER REFERENCES Protest(id),
);

CREATE TABLE Report(
    member_id INTEGER REFERENCES OrganizationMember(id),
    protest_id INTEGER REFERENCES Protest(id),
    rating INTEGER NOT NULL CHECK (1 <= rating AND rating <= 10),
    description VARCHAR(255)
);

CREATE TABLE Guard(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    weight INTEGER NOT NULL CHECK (weight >= 80),
    running_speed INTEGER NOT NULL CHECK (running_speed >= 20),
);

CREATE TABLE Protection(
    guard_id INTEGER REFERENCES Guard(id),
    protest_id INTEGER REFERENCES Protest(id),
);


-- to clear db find topological order of tables in dependency graph
DROP INDEX IF EXISTS protests_on_the_plane;
DROP TABLE IF EXISTS "Participation";
DROP TABLE IF EXISTS "Report";
DROP TABLE IF EXISTS "Protection";
DROP TABLE IF EXISTS "Worldview";
DROP TABLE IF EXISTS "Protest";
DROP TABLE IF EXISTS "Guard";
DROP TABLE IF EXISTS "GovernmentAction";
DROP TABLE IF EXISTS "OrganizationMember";


CREATE TABLE "OrganizationMember"(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    age INTEGER CHECK (age >= 18),
    login VARCHAR(10),
    hashed_password VARCHAR(255),
    organizer_privilege BOOLEAN
);

CREATE TABLE "GovernmentAction"(
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE CHECK (char_length(title) > 0),
    organizer_id INTEGER REFERENCES OrganizationMember(id)
);

CREATE TABLE "Protest"(
    id SERIAL PRIMARY KEY,
    organizer_id INTEGER REFERENCES OrganizationMember(id),
    action_id INTEGER REFERENCES GovernmentAction(id),
    start_time TIMESTAMP,
    town VARCHAR(255),
    coordinates POINT,
    boombox_number INTEGER NOT NULL CHECK (boombox_number > 0)
);

CREATE TABLE "Participation"(
    member_id INTEGER REFERENCES OrganizationMember(id),
    protest_id INTEGER REFERENCES Protest(id)
);

CREATE TABLE "Report"(
    member_id INTEGER REFERENCES OrganizationMember(id),
    protest_id INTEGER REFERENCES Protest(id),
    rating INTEGER NOT NULL CHECK (1 <= rating AND rating <= 10),
    description VARCHAR(1024) CHECK (char_length(description) > 0)
);

CREATE TABLE "Guard"(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    added_by INTEGER REFERENCES OrganizationMember(id),
    weight INTEGER NOT NULL CHECK (weight >= 80),
    running_speed INTEGER NOT NULL CHECK (running_speed >= 20)
);

CREATE TABLE "Protection"(
    guard_id INTEGER REFERENCES Guard(id),
    protest_id INTEGER REFERENCES Protest(id)
);

CREATE TABLE "Worldview"(
    guard_id INTEGER REFERENCES Guard(id),
    action_id INTEGER REFERENCES Protest(id)
);


-- for searching protests on rectangles or by distance to the point
CREATE INDEX protests_on_the_plane ON "Protest" USING gist(coordinates);


CREATE OR REPLACE FUNCTION fill_protest_organizer() RETURNS trigger AS $$
BEGIN
    SELECT organizer_id INTO NEW.organizer_id FROM GovernmentAction WHERE id = NEW.action_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER fill_protest_organizer BEFORE INSERT OR UPDATE ON "Protest"
FOR EACH ROW EXECUTE FUNCTION fill_protest_organizer();


CREATE OR REPLACE FUNCTION add_organizer_as_participant() RETURNS trigger AS $$
BEGIN
    INSERT INTO Participation(member_id, protest_id) VALUES (NEW.member_id, NEW.id);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER add_organizer_as_participant AFTER INSERT ON "Protest"
FOR EACH ROW EXECUTE FUNCTION add_organizer_as_participant();


CREATE OR REPLACE FUNCTION assert_guard_political_view_when_securing() RETURNS trigger AS $$
DECLARE 
    dummy RECORD;
    action INTEGER;
BEGIN
    SELECT action_id INTO action FROM Protest WHERE id = NEW.protest_id;
    SELECT * INTO dummy FROM Worldview WHERE action_id = action AND guard_id = NEW.guard_id;
    IF FOUND THEN
        RETURN NULL; -- should not approve this action!
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER assert_guard_political_view_when_securing BEFORE INSERT ON "Protection"
FOR EACH ROW EXECUTE FUNCTION assert_guard_political_view_when_securing();


CREATE OR REPLACE FUNCTION check_report_submitter() RETURNS trigger AS $$
DECLARE 
    dummy RECORD;
BEGIN
    SELECT * INTO dummy FROM Participation WHERE member_id = NEW.member_id AND protest_id = NEW.protest_id;
    -- must participate in protest
    IF FOUND THEN
        SELECT * INTO dummy FROM Report WHERE member_id = NEW.member_id AND protest_id = NEW.protest_id;
        -- at most 1 report to the protest
        if NOT FOUND THEN
            RETURN NEW;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER check_report_submitter BEFORE INSERT ON "Report"
FOR EACH ROW EXECUTE FUNCTION check_report_submitter();


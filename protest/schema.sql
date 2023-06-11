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
    observer_id INTEGER REFERENCES "OrganizationMember"(id)
);

CREATE TABLE "Protest"(
    id SERIAL PRIMARY KEY,
    organizer_id INTEGER REFERENCES "OrganizationMember"(id),
    action_id INTEGER REFERENCES "GovernmentAction"(id),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    town VARCHAR(255),
    coordinates POINT,
    boombox_number INTEGER NOT NULL CHECK (boombox_number > 0)
);

CREATE TABLE "Participation"(
    member_id INTEGER REFERENCES "OrganizationMember"(id),
    protest_id INTEGER REFERENCES "Protest"(id)
);

CREATE TABLE "Report"(
    member_id INTEGER REFERENCES "OrganizationMember"(id),
    protest_id INTEGER REFERENCES "Protest"(id),
    rating INTEGER NOT NULL CHECK (1 <= rating AND rating <= 10),
    description VARCHAR(1024) CHECK (char_length(description) > 0)
);

CREATE TABLE "Guard"(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    added_by INTEGER REFERENCES "OrganizationMember"(id),
    weight INTEGER NOT NULL CHECK (weight >= 80),
    running_speed INTEGER NOT NULL CHECK (running_speed >= 20)
);

CREATE TABLE "Protection"(
    guard_id INTEGER REFERENCES "Guard"(id),
    protest_id INTEGER REFERENCES "Protest"(id)
);

CREATE TABLE "Worldview"(
    guard_id INTEGER REFERENCES "Guard"(id),
    action_id INTEGER REFERENCES "Protest"(id)
);


-- for searching protests on rectangles or by distance to the point
CREATE INDEX protests_on_the_plane ON "Protest" USING gist(coordinates);


CREATE OR REPLACE FUNCTION fill_protest_organizer() RETURNS trigger AS $$
BEGIN
    SELECT observer_id INTO NEW.organizer_id FROM "GovernmentAction" WHERE id = NEW.action_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER fill_protest_organizer BEFORE INSERT OR UPDATE ON "Protest"
FOR EACH ROW EXECUTE FUNCTION fill_protest_organizer();


CREATE OR REPLACE FUNCTION add_organizer_as_participant() RETURNS trigger AS $$
BEGIN
    INSERT INTO "Participation"(member_id, protest_id) VALUES (NEW.organizer_id, NEW.id);
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
    SELECT action_id INTO action FROM "Protest" WHERE id = NEW.protest_id;
    SELECT * INTO dummy FROM "Worldview" WHERE action_id = action AND guard_id = NEW.guard_id;
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
    SELECT * INTO dummy FROM "Participation" WHERE member_id = NEW.member_id AND protest_id = NEW.protest_id;
    -- must participate in protest
    IF FOUND THEN
        SELECT * INTO dummy FROM "Report" WHERE member_id = NEW.member_id AND protest_id = NEW.protest_id;
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



------------------------------------
------------ FUNCTIONS -------------
------------------------------------


CREATE OR REPLACE FUNCTION query_participants(protest INTEGER) RETURNS TABLE(id INTEGER, name VARCHAR(255), last_name VARCHAR(255), age INTEGER) AS $$
BEGIN
    RETURN QUERY SELECT M.id, M.name, M.last_name, M.age
    FROM "OrganizationMember" M JOIN (SELECT * FROM "Participation" WHERE protest_id = protest) AS P
    ON M.id = P.member_id;
END;
$$ LANGUAGE plpgsql;


/* DROP FUNCTION query_action_stats(); */
CREATE OR REPLACE FUNCTION query_action_stats() RETURNS TABLE(id INTEGER, title VARCHAR(255), no_protest BIGINT, no_people BIGINT) AS $$
BEGIN
    RETURN QUERY SELECT "GovernmentAction".id, "GovernmentAction".title, COUNT(DISTINCT "Protest".id), COUNT(DiSTINCT "Participation".member_id)
    FROM ("GovernmentAction" JOIN "Protest" ON ("Protest".action_id = "GovernmentAction".id)) JOIN "Participation" ON ("Protest".id = "Participation".protest_id)
    GROUP BY "GovernmentAction".id
    ORDER BY 3 DESC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_int_string(i BIGINT, s VARCHAR(1023)) RETURNS BIGINT AS $$
BEGIN
    RETURN i + char_length(s);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE AGGREGATE sum_string_length (VARCHAR(1023)) (
    sfunc = add_int_string,
    stype = BIGINT,
    initcond = 0
);

DROP FUNCTION IF EXISTS query_participant_stats();
CREATE OR REPLACE FUNCTION query_participant_stats() RETURNS TABLE(id INTEGER, name VARCHAR(255), no_protest BIGINT, all_report_length BIGINT) AS $$
BEGIN
    RETURN QUERY SELECT p.id, p.name, p.no_protest, r.sum_report_length
    FROM (SELECT "OrganizationMember".id, "OrganizationMember".name, COUNT("Participation".protest_id) AS no_protest
        FROM "OrganizationMember" LEFT JOIN "Participation" ON ("Participation".member_id = "OrganizationMember".id)
        GROUP BY "OrganizationMember".id
    ) AS p JOIN (SELECT "OrganizationMember".id, "OrganizationMember".name, COALESCE(sum_string_length("Report".description), 0) AS sum_report_length
        FROM "OrganizationMember" LEFT JOIN "Report" ON ("Report".member_id = "OrganizationMember".id)
        GROUP BY "OrganizationMember".id
    ) AS r ON (p.id = r.id)
    ORDER BY 4 DESC, 2 ASC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION query_organizer_stats() RETURNS TABLE(id INTEGER, name VARCHAR(255), no_protest BIGINT, avg_rating DECIMAL) AS $$
BEGIN
    RETURN QUERY SELECT "OrganizationMember".id, "OrganizationMember".name, COUNT(DISTINCT "Protest".id), COALESCE(AVG("Report".rating), 1.0)
    FROM "OrganizationMember" LEFT JOIN "Protest" ON ("OrganizationMember".id = "Protest".organizer_id) LEFT JOIN "Report" ON ("Protest".id = "Report".protest_id)
    WHERE "OrganizationMember".organizer_privilege = True
    GROUP BY "OrganizationMember".id
    ORDER BY 4 DESC, 2 ASC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION query_closest_protests(p POINT, s TIMESTAMP, e TIMESTAMP) RETURNS TABLE(id INTEGER) AS $$
BEGIN
    RETURN QUERY SELECT sq.id FROM (SELECT * FROM "Protest"
        WHERE s <= "Protest".start_time AND "Protest".end_time <= e
        ORDER BY "Protest".coordinates <-> p
    ) as sq;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION query_profitable_protests(g INTEGER, s TIMESTAMP, e TIMESTAMP) RETURNS TABLE(id INTEGER, no_boombox INTEGER, no_guard BIGINT, profit FLOAT) AS $$
BEGIN
    RETURN QUERY SELECT p.id, p.boombox_number AS bc, COUNT("Protection".guard_id) AS gc, p.boombox_number::FLOAT / (COUNT("Protection".guard_id) + 1)
    FROM (SELECT * FROM "Protest"
        WHERE s <= "Protest".start_time AND "Protest".end_time <= e
        AND NOT EXISTS(SELECT * FROM "Protection"
            WHERE "Protection".protest_id = "Protest".id AND "Protection".guard_id = g)) AS p
    LEFT JOIN "Protection" ON (p.id = "Protection".protest_id)
    GROUP BY p.id, p.boombox_number
    ORDER BY 4 DESC, 1 ASC;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION query_indirect_friends(u INTEGER) RETURNS TABLE(id INTEGER) AS $$
BEGIN
    RETURN QUERY
        WITH RECURSIVE friends(id) AS (
            VALUES (u)
            UNION
            SELECT e.id2
            FROM friends JOIN (SELECT p1.member_id AS id1, p2.member_id AS id2 FROM "Participation" p1 JOIN "Participation" p2 ON (p1.protest_id = p2.protest_id)) AS e
            ON (friends.id = e.id1)
        )
        SELECT * FROM friends
        ORDER BY 1;
END;
$$ LANGUAGE plpgsql;



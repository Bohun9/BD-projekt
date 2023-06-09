from flask import Blueprint, request
from .db import get_cursor, get_table, log_db_notifications
from datetime import datetime

bp = Blueprint("query", __name__, url_prefix="/query")

# queries statements are in sql functions


# by default row converted to json is list of values, even when cursor factory is specified
def with_names(table):
    return list(map(dict, table))


@bp.route("/participants/<int:id>", methods=("GET",))
def query_participants(id):
    # print(get_table("OrganizationMember"))
    # print(get_table("Participation"))
    # print(get_table("Protest"))
    get_cursor().execute("SELECT * FROM query_participants(%s);", (id,))
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/action_stats", methods=("GET",))
def query_action_stats():
    get_cursor().execute("SELECT * FROM query_action_stats();")
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/participant_stats", methods=("GET",))
def query_participant_stats():
    print("WHAT", get_table("Report"))
    get_cursor().execute("SELECT * FROM query_participant_stats();")
    log_db_notifications()
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/organizer_stats", methods=("GET",))
def query_organizer_stats():
    print("WHAT", get_table("Report"))
    get_cursor().execute("SELECT * FROM query_organizer_stats();")
    log_db_notifications()
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/closest_protests", methods=("GET",))
def query_closest_protests():
    # print("WHAT", get_table("Report"))
    print(request.args)
    get_cursor().execute(
        "SELECT * FROM query_closest_protests(%s, %s, %s);",
        (
            str(
                (
                    float(request.args["coordinate_x"]),
                    float(request.args["coordinate_y"]),
                )
            ),
            request.args.get("start_time", type=datetime.fromisoformat),
            request.args.get("end_time", type=datetime.fromisoformat),
        ),
    )
    # log_db_notifications()
    result = get_cursor().fetchall()
    return with_names(result)

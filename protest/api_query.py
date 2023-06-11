from flask import Blueprint, request
from .db import get_cursor, get_table, log_db_notifications
from .api_auth import must_be_member
from datetime import datetime

bp = Blueprint("query", __name__, url_prefix="/query")


# by default row converted to json is list of values, even when cursor factory is specified
def with_names(table):
    return list(map(dict, table))


@bp.route("/participants/<int:id>", methods=("GET",))
@must_be_member
def query_participants(id):
    get_cursor().execute("SELECT * FROM query_participants(%s);", (id,))
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/action_stats", methods=("GET",))
@must_be_member
def query_action_stats():
    get_cursor().execute("SELECT * FROM query_action_stats();")
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/participant_stats", methods=("GET",))
@must_be_member
def query_participant_stats():
    get_cursor().execute("SELECT * FROM query_participant_stats();")
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/organizer_stats", methods=("GET",))
@must_be_member
def query_organizer_stats():
    get_cursor().execute("SELECT * FROM query_organizer_stats();")
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/closest_protests", methods=("GET",))
@must_be_member
def query_closest_protests():
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
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/profitable_protests", methods=("GET",))
@must_be_member
def query_profitable_protests():
    get_cursor().execute(
        "SELECT * FROM query_profitable_protests(%s, %s, %s);",
        (
            request.args.get("guard_id"),
            request.args.get("start_time", type=datetime.fromisoformat),
            request.args.get("end_time", type=datetime.fromisoformat),
        ),
    )
    result = get_cursor().fetchall()
    return with_names(result)


@bp.route("/indirect_friends", methods=("GET",))
@must_be_member
def query_indirect_friends():
    get_cursor().execute(
        "SELECT * FROM query_indirect_friends(%s);",
        (request.args.get("member_id"),),
    )
    result = get_cursor().fetchall()
    return with_names(result)

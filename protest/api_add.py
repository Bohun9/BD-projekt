from .api_auth import must_be_member, must_be_organizer
from flask import Blueprint, request, g
from .db import add_row_to_table, get_table
from datetime import datetime

bp = Blueprint("add", __name__, url_prefix="/add")


@bp.route("/action", methods=("POST",))
@must_be_organizer
def add_action():
    add_row_to_table(
        "GovernmentAction",
        {"title": request.form["title"], "observer_id": g.user["id"]},
    )
    return "OK"


@bp.route(
    "/protest",
    methods=("POST",),
)
@must_be_organizer
def add_protest():
    add_row_to_table(
        "Protest",
        {
            "action_id": request.form["action_id"],
            "start_time": datetime.fromisoformat(request.form["start_time"]),
            "town": request.form["town"],
            "coordinates": str(
                (
                    float(request.form["coordinate_x"]),
                    float(request.form["coordinate_y"]),
                )
            ),
            "boombox_number": request.form["boombox_number"],
        },
    )
    return "OK"


@bp.route(
    "/participation",
    methods=("POST",),
)
@must_be_member
def add_participation():
    add_row_to_table(
        "Participation",
        {"protest_id": request.form["protest_id"], "member_id": g.user["id"]},
    )
    return "OK"


@bp.route(
    "/report",
    methods=("POST",),
)
@must_be_member
def add_report():
    add_row_to_table(
        "Report",
        {
            "protest_id": request.form["protest_id"],
            "rating": request.form["rating"],
            "description": request.form["description"],
        },
    )
    return "OK"


@bp.route(
    "/guard",
    methods=("POST",),
)
@must_be_organizer
def add_guard():
    add_row_to_table(
        "Guard",
        {
            "name": request.form["name"],
            "last_name": request.form["last_name"],
            "added_by": g.user["user_id"],
            "weight": request.form["weight"],
            "running_speed": request.form["running_speed"],
        },
    )
    return "OK"


@bp.route(
    "/worldview",
    methods=("POST",),
)
@must_be_organizer
def add_worldview():
    add_row_to_table(
        "Worldview",
        {"guard_id": request.form["guard_id"], "action_id": g.user["action_id"]},
    )
    return "OK"


@bp.route(
    "/protection",
    methods=("POST",),
)
@must_be_organizer
def add_protection():
    add_row_to_table(
        "Protection",
        {"guard_id": request.form["guard_id"], "protest": g.user["protest"]},
    )
    return "OK"

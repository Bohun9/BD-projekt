from .api_auth import must_be_member, must_be_organizer
from flask import Blueprint, request, g
from .db import add_row_to_table, get_table

bp = Blueprint("add", __name__, url_prefix="/add")


@bp.route("/action", methods=("POST",))
@must_be_organizer
def add_action():
    add_row_to_table(
        "GovernmentAction",
        {"title": request.form["title"], "observer_id": g.user["id"]},
    )
    return "OK"

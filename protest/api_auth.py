from flask import Blueprint, request, current_app, session, g
from protest.db import add_row_to_table, get_cursor
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
import functools

bp = Blueprint("auth", __name__)


@bp.route("/register_member", methods=("POST",))
def register_member():
    hashed_password = generate_password_hash(request.form["password"])
    add_row_to_table(
        "OrganizationMember",
        {
            "name": request.form["name"],
            "last_name": request.form["last_name"],
            "age": request.form["age"],
            "login": request.form["login"],
            "hashed_password": hashed_password,
            "organizer_privilege": True
            if request.form["secret"] == current_app.config["SECRET_ORGANIZER"]
            else False,
        },
    )
    return "OK"


@bp.route("/login", methods=("POST",))
def login():
    get_cursor().execute(
        'SELECT * FROM "OrganizationMember" WHERE login = %s', (request.form["login"],)
    )
    user = get_cursor().fetchone()
    if user is None or not check_password_hash(
        user["hashed_password"], request.form["password"]
    ):
        abort(401)
    session["user_id"] = user["id"]
    return "OK"


@bp.route("/logout", methods=("GET",))
def logout():
    session.clear()
    return "OK"


@bp.before_app_request
def load_logged_in_used():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        get_cursor().execute(
            'SELECT * FROM "OrganizationMember" WHERE id = %s', (user_id,)
        )
        g.user = get_cursor().fetchone()


def must_be_member(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(401)
        return view(**kwargs)

    return wrapped_view


def must_be_organizer(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or not g.user["organizer_privilege"]:
            abort(401)
        return view(**kwargs)

    return wrapped_view

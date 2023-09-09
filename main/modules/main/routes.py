from flask import Blueprint, render_template, request, flash, redirect, url_for

main = Blueprint("main", __name__, url_prefix="")


@main.route("/")
def index():
    return render_template("main/index.html")

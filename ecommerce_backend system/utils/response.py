"""
utils/response.py
─────────────────
Standardised API response helpers.
Every endpoint returns the same envelope:
  { success, message, data?, pagination? }
"""

from flask import jsonify


def success(message: str = "OK", data=None, status: int = 200, pagination: dict = None):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    if pagination:
        body["pagination"] = pagination
    return jsonify(body), status


def error(message: str = "An error occurred", status: int = 400, errors=None):
    body = {"success": False, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status

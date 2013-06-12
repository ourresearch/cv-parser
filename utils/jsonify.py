import json

from flask import Response
from functools import wraps


def jsonify(f):
    """Decorator to set appropriate mimetype and response code."""
    @wraps(f)
    def inner(*args, **kwargs):
        output = f(*args, **kwargs)
        if isinstance(output, dict) and output.get("status") == "error":
            response_code = 422
        else:
            response_code = 200
        return Response(json.dumps(output), mimetype='application/json', status=response_code)
    return inner

from flask import Flask, jsonify, request
from hierarchical import TreeStorage, SEP

rt= TreeStorage()
app = Flask(__name__)


@app.route("/<path:path>", methods=["GET"])
def get_resource(path):
    return jsonify(rt.get_data(path))


@app.route("/<path:path>/", methods=["GET"])
def list_resource(path):
    return jsonify(rt.list_children(path.rstrip(SEP)))


@app.route("/<path:path>", methods=["PUT"])
def create_resource(path):
    path.rstrip("/")
    routine = rt.link if request.args.get("link", False) else rt.create
    return jsonify(routine(path, request.json) or None)


@app.route("/<path:path>", methods=["POST"])
def update_resource(path):
    return jsonify(rt.update_data(path, request.json))


@app.route("/<path:path>/", methods=["POST"])
def move_resource(path):
    (name, new_path) = request.json
    return jsonify(rt.move(path, name, new_path))


@app.route("/<path:path>", methods=["DELETE"])
def remove_resource(path):
    return jsonify(rt.remove(path))


if __name__ == '__main__':
    app.run(debug=1)

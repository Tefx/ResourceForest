from flask import Flask, jsonify, request

from hierarchical import ResourceTree

rt = ResourceTree()
app = Flask(__name__)


@app.route("/<path:path>", methods=["GET"])
def get_resource(path):
    return jsonify(rt.fetch(path))


@app.route("/<path:path>", methods=["PUT"])
def create_resource(path):
    link = request.args.get("link", False)
    if link:
        result = rt.link(path, request.args.get("target"), link == "hard")
    else:
        result = rt.create(path, request.args.get("type"), request.json)
    return jsonify(result)


@app.route("/<path:path>", methods=["POST"])
def update_resource(path):
    return jsonify(rt.update(path, **request.json))


@app.route("/<path:path>", methods=["DELETE"])
def remove_resource(path):
    return jsonify(rt.remove(path))


@app.route("/<path:path>/", methods=["GET"])
def list_resource(path):
    return jsonify(rt.list(path))


if __name__ == '__main__':
    app.run(debug=1)

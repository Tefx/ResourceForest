from flask import Flask, jsonify, request

from fakedata import make_fake_tree

app = Flask(__name__)
rt = make_fake_tree(n_project=5, n_version=2, n_purpose=3, n_user_per_purpose=1,
                    n_person=10, n_user_per_person=3,
                    n_host=4, n_user_per_host=5)


def get_bool_arg(request, name):
    var = request.args.get(name, "0")
    return var not in ["0", "false", "False"]


@app.route("/", methods=["GET"])
def list_tree():
    if get_bool_arg(request, "tree"):
        return rt.tree()
    else:
        return jsonify(rt.list("/"))


@app.route("/<path:path>", methods=["GET"])
def get_resource(path):
    if path.endswith("/"):
        res = rt.list(path, only_name=get_bool_arg(request, "only_name"))
    else:
        res = rt.fetch(path)
    return jsonify(res)


@app.route("/<path:path>", methods=["PUT"])
def create_resource(path):
    link = get_bool_arg(request, "link")
    if link:
        result = rt.link(path, request.args.get("target"), link == "hard")
    else:
        result = rt.create(path, request.args.get("type"), request.json)
    return jsonify(result.fetch_attributes())


@app.route("/<path:path>", methods=["POST"])
def update_resource(path):
    return jsonify(rt.update(path, **request.json).fetch_attributes())


@app.route("/<path:path>", methods=["DELETE"])
def remove_resource(path):
    return jsonify(rt.remove(path).fetch_attributes())


if __name__ == '__main__':
    app.run()

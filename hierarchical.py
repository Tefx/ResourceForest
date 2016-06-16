from resource import RealResource, LinkedResource, ChildNotFoundException, ChildAlreadyExistsException


class PathException(Exception):
    def __init__(self, path):
        self.path = path


class PathNotFoundException(PathException):
    pass


class PathAlreadyExistsException(PathException):
    pass


def split_last(path):
    prefix, _, last = path.strip("/").rpartition("/")
    return prefix, last


def do_nothing_if(exception):
    def wrapper(f):
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except exception:
                return None

        return wrapped

    return wrapper


class ResourceTree:
    def __init__(self):
        self.root = RealResource(resource_type="ROOT")

    def locate(self, path):
        if not path:
            return self.root

        node = self.root

        try:
            for name in path.strip("/").split("/"):
                node = node[name]
        except ChildNotFoundException:
            raise PathNotFoundException(path)

        return node

    @do_nothing_if(PathAlreadyExistsException)
    def create(self, path, resource_type=None, **attributes):
        prefix, name = split_last(path)

        try:
            parent = self.locate(prefix)
        except PathNotFoundException:
            parent = self.create(prefix)

        node = RealResource(attributes, resource_type)

        try:
            return parent.add_child(name, node)
        except ChildAlreadyExistsException:
            raise PathAlreadyExistsException(path)

    @do_nothing_if(PathAlreadyExistsException)
    def link(self, path, target, hard=False):
        if path.endswith("/"):
            prefix = path.strip("/")
            _, name = split_last(target)
        else:
            prefix, name = split_last(path)

        try:
            parent = self.locate(prefix)
        except PathNotFoundException:
            parent = self.create(prefix)

        node = self.locate(target)
        if not hard:
            node = LinkedResource(node)

        try:
            return parent.add_child(name, node)
        except ChildAlreadyExistsException:
            raise PathAlreadyExistsException("{}/{}".format(prefix, name))

    def fetch(self, path):
        return self.locate(path).fetch_attributes()

    def update(self, path, **attributes):
        return self.locate(path).update_attributes(attributes)

    def list(self, path):
        return self.locate(path).children(only_name=True)

    def remove(self, path):
        prefix, name = split_last(path)
        parent = self.locate(prefix)

        try:
            return parent.remove_child(name)
        except ChildNotFoundException:
            raise PathNotFoundException(path)

    def move(self, old_path, new_path, create_path=False):
        old_parent, name = split_last(old_path)

        try:
            node = self.locate(old_parent).remove_child(name)
        except ChildNotFoundException:
            raise PathNotFoundException(old_path)

        if new_path.endswith("/"):
            new_parent = new_path
        else:
            new_parent, name = split_last(new_path)

        try:
            self.locate(new_parent).add_child(name, node)
        except PathNotFoundException as e:
            if create_path:
                self.create(new_parent).add_child(name, node)
            else:
                raise e
        except ChildAlreadyExistsException:
            raise PathAlreadyExistsException(new_path)

        return node

    def tree(self):
        return self.root.tree("root")


if __name__ == '__main__':
    ts = ResourceTree()
    ts.create("/zh", "project")
    ts.create("/us/v81/db", "db", ip="localhost")
    ts.create("/zh/v6", "ssh", ip="localhost")
    ts.create("/zh/v7/db/127.0.0.1", "test", ip="test")
    print(ts.tree())
    ts.link("/us/v83/", "/zh/v7")
    print(ts.fetch("/zh/v7/db/127.0.0.1"))
    print(ts.list("/us/v83"))
    ts.update("/zh/v6", ip="127.0.0.1")
    print(ts.tree())
    ts.remove("/us/v81")
    print(ts.tree())
    ts.remove("/zh/v7")
    print(ts.tree())

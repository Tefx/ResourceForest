class ResourceException(Exception):
    def __init__(self, node, child=None):
        self.node = node
        self.child = child


class ChildNotFoundException(ResourceException):
    pass


class ChildAlreadyExistsException(ResourceException):
    pass


class Resource:
    def __init__(self, resource_type=None):
        self.resource_type = resource_type

    def children(self):
        raise NotImplementedError

    def tree(self, name, indent=0):
        base_string = "{}{}: {}\n".format(" " * indent, name, self)
        for k, v in self.children():
            base_string += v.tree(k, indent + 4)
        return base_string


class RealResource(Resource):
    def __init__(self, attributes=None, resource_type=None):
        super(RealResource, self).__init__(resource_type)
        self.attributes = attributes or {}
        self.num_hardlink = 0

        # DO NOT ACCESS DIRECTLY! USE get_child and get_children.
        self._children = {}

    def __repr__(self):
        return "[{}] {}({}) " \
            .format(self.resource_type, self.attributes, self.__class__.__name__)

    def __getitem__(self, item):
        if item not in self:
            raise ChildNotFoundException(self, item)
        return self._children[item]

    def __contains__(self, item):
        if item not in self._children:
            return False

        if self._children[item].num_hardlink == 0:
            del self._children[item]
            return False

        return True

    def add_child(self, name, node):
        if name in self:
            raise ChildAlreadyExistsException(self, name)

        self._children[name] = node
        if isinstance(node, RealResource):
            node.num_hardlink += 1

        return node

    def remove_child(self, name):
        if name not in self:
            raise ChildNotFoundException(self, name)

        node = self._children[name]
        if isinstance(node, RealResource):
            node.num_hardlink -= 1
        del self._children[name]

        return node

    def children(self, only_name=False):
        for name, child in list(self._children.items()):
            if child.num_hardlink > 0:
                yield (name if only_name else name, child)
            else:
                del self._children[name]

    def update_attributes(self, new_attributes):
        self.attributes.update(new_attributes)
        return self.attributes

    def fetch_attributes(self):
        return self.attributes


class LinkedResource(Resource):
    def __init__(self, target):
        super(LinkedResource, self).__init__(target.resource_type)
        self.target = target

    def __repr__(self):
        if isinstance(self.target, RealResource):
            attr_str = str(self.target.attributes)
            if len(attr_str) > 50:
                attr_str = attr_str[:50] + "..."
            return "[{}] ==> [{}] {}({})" \
                .format(self.__class__.__name__,
                        self.target.__class__.__name__,
                        self.target.resource_type,
                        attr_str)
        else:
            target_str = str(self.target)
            if len(target_str) > 50:
                target_str = target_str[:50] + "..."
            return "[{}] ==> {}" \
                .format(self.__class__.__name__, target_str)

    def children(self, only_name=False):
        return self.target.children(only_name)

    def __getattr__(self, item):
        return getattr(self.target, item)

    def __contains__(self, item):
        return self.target.__contains__(item)

    def __getitem__(self, item):
        return self.target.__getitem__(item)

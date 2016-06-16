class ResourceException(Exception):
    def __init__(self, node, child=None):
        self.node = node
        self.child = child


class ChildNotFoundException(ResourceException):
    pass


class ChildAlreadyExistsException(ResourceException):
    pass


class ResourceStore:
    def __init__(self):
        self.resources = {}
        self.rid_count = 0

    def alloc(self, cls, *args, **kwargs):
        self.rid_count += 1
        resource = cls(self, self.rid_count, *args, **kwargs)
        self.resources[self.rid_count] = resource
        return resource

    def __getitem__(self, item):
        return self.resources[item]

    def to_dict(self):
        return [(res.__class__.__name__, res.to_dict())
                for rid, res in self.resources.items()]

    @classmethod
    def from_dict(cls, dict):
        store = cls()
        for cls_name, obj_dict in dict:
            if cls_name == "RealResource":
                obj = RealResource.from_dict(store, obj_dict)
            elif cls_name == "LinkedResource":
                obj = LinkedResource.from_dict(store, obj_dict)
            store.resources[obj.rid] = obj
        store.rid_count = len(store.resources)
        return store


class Resource:
    def __init__(self, store, rid, resource_type=None):
        self.store = store
        self.rid = rid
        self.resource_type = resource_type

    def children(self):
        raise NotImplementedError

    def tree(self, name, indent=0):
        base_string = "{}{}: {}\n".format(" " * indent, name, self)
        for k, v in self.children():
            base_string += v.tree(k, indent + 4)
        return base_string

    def get_obj(self, rid):
        return self.store[rid]

    def to_dict(self):
        pass

    @classmethod
    def from_dict(cls, store, json_string):
        pass


class RealResource(Resource):
    def __init__(self, store, rid, attributes=None, resource_type=None):
        super(RealResource, self).__init__(store, rid, resource_type)
        self.attributes = attributes or {}
        self.hardlinks = 0

        # DO NOT ACCESS DIRECTLY! USE get_child and get_children.
        self._children = {}

    def to_dict(self):
        return {"rid": self.rid,
                "type": self.resource_type,
                "attributes": self.attributes,
                "hardlinks": self.hardlinks,
                "children": self._children}

    @classmethod
    def from_dict(cls, store, dict):
        res = cls(store, dict["rid"], dict["attributes"], dict["type"])
        res.hardlinks = dict["hardlinks"]
        res._children = dict["children"]
        return res

    def __repr__(self):
        return "[{}] {}({}) " \
            .format(self.resource_type, self.attributes, self.__class__.__name__)

    def __contains__(self, item):
        if item not in self._children:
            return False

        if self.get_obj(self._children[item]).hardlinks == 0:
            del self._children[item]
            return False

        return True

    def __getitem__(self, item):
        if item not in self:
            raise ChildNotFoundException(self, item)
        return self.get_obj(self._children[item])

    def add_child(self, name, node):
        if name in self:
            raise ChildAlreadyExistsException(self, name)

        self._children[name] = node.rid
        if isinstance(node, RealResource):
            node.hardlinks += 1

        return node

    def remove_child(self, name):
        if name not in self:
            raise ChildNotFoundException(self, name)

        node = self.get_obj(self._children[name])
        if isinstance(node, RealResource):
            node.hardlinks -= 1
        del self._children[name]

        return node

    def children(self, only_name=False):
        for name, child in list(self._children.items()):
            child = self.get_obj(child)
            if child.hardlinks > 0:
                yield (name if only_name else (name, child))
            else:
                del self._children[name]

    def update_attributes(self, new_attributes):
        self.attributes.update(new_attributes)
        return self.attributes

    def fetch_attributes(self):
        return self.attributes


class LinkedResource(Resource):
    def __init__(self, store, rid, target=None):
        resource_type = target.resource_type if target else None
        super(LinkedResource, self).__init__(store, rid, resource_type)
        self.target = target.rid if target else None

    def to_dict(self):
        return {"rid": self.rid,
                "target": self.target}

    @classmethod
    def from_dict(cls, store, dict):
        res = cls(store, dict["rid"])
        res.target = dict["target"]
        return res

    def __repr__(self):
        target = self.get_obj(self.target)
        if isinstance(target, RealResource):
            attr_str = str(target.attributes)
            if len(attr_str) > 50:
                attr_str = attr_str[:50] + "..."
            return "[{}] ==> [{}] {}({})" \
                .format(self.__class__.__name__,
                        target.__class__.__name__,
                        target.resource_type,
                        attr_str)
        else:
            target_str = str(target)
            if len(target_str) > 50:
                target_str = target_str[:50] + "..."
            return "[{}] ==> {}" \
                .format(self.__class__.__name__, target_str)

    def children(self, only_name=False):
        return self.get_obj(self.target).children(only_name)

    def __getattr__(self, item):
        return getattr(self.get_obj(self.target), item)

    def __contains__(self, item):
        return self.get_obj(self.target).__contains__(item)

    def __getitem__(self, item):
        return self.get_obj(self.target).__getitem__(item)

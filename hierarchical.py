class TreeStorage:
    def __init__(self):
        self.root_node = None

    def create(self, path, data):
        return NotImplemented

    def remove(self, path):
        return NotImplemented

    def move(self, path, name, new_path):
        return NotImplemented

    def link(self, path, target):
        return NotImplemented

    def get_data(self, path):
        return NotImplemented

    def list_children(self, path):
        return NotImplemented

    def update_data(self, path, data):
        return NotImplemented
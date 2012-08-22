class MissingNode(Exception):
    pass


class NodeDB(object):
    def __init__(self, pickling_module, storage):
        self.storage = storage
        self.pickling_module = pickling_module

    def recover(self, identifier):
        try:
            node = self.pickling_module.loads(self.storage[identifier])
            return node
        except KeyError as e:
            raise MissingNode(e)

    def store(self, node):
        s = self.pickling_module.dumps(node)
        self.storage[node.id] = s
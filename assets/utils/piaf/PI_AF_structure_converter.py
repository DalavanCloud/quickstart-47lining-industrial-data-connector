class PIAFStructureConverter():
    def __init__(self, input_json):
        self.input_json = input_json

    def convert_flat_to_tree(self):
        tree = []

        for element in self.input_json['elements']:
            path = element['path'].split('\\')[4:]
            self._append_nested_node_if_not_exists(path, tree, element)

        return tree

    def _append_nested_node_if_not_exists(self, path, tree, element):
        if len(path) == 0:
            return
        name = path[0]
        is_leaf = True if len(path) == 1 else False
        node = self._append_node_if_not_exists(name, tree, is_leaf, element)
        self._append_nested_node_if_not_exists(path[1:], node, element)


    def _append_node_if_not_exists(self, node, tree, is_leaf, element):
        n = self._find_node_by_name(node, tree)
        if n != None:
            if is_leaf:
                for key, value in element.items():
                    n[key] = value
            return n['assets']

        if is_leaf:
            tree.append(element)
            return tree
        else:
            new = self._create_parent_node(node, element)
            tree.append(new)
            return new['assets']

    def _find_node_by_name(self, node, tree):
        for t in tree:
            if t['name'] == node:
                return t
        return None

    def _create_parent_node(self, name, element):
        return {
            "name": name,
            "assets": []
        }

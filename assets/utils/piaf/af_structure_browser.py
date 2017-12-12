import re


class AfStructureBrowser(object):
    def __init__(self, assets_query, assets_field="name", attributes_query=".*", attributes_field="name"):
        self.assets_query = assets_query.replace("\\", "\\\\") if assets_field == 'path' else assets_query
        self.assets_field = assets_field
        self.attributes_query = attributes_query
        self.attributes_field = attributes_field

    def search_assets(self, structure):
        results = {}
        self._search_assets_tree(structure, results)
        return results

    def _search_assets_tree(self, structure, results):
        for asset in structure:
            if self._match_asset_field_with_query(asset, self.assets_query, self.assets_field):
                copy = self._copy_node_and_remove_children_assets(asset)
                filtered_attributes = self._filter_attributes(copy['attributes'])
                if len(filtered_attributes) > 0:
                    copy['attributes'] = filtered_attributes
                    results[copy['path']] = copy
            if 'assets' in asset:
                self._search_assets_tree(asset['assets'], results)

    def _copy_node_and_remove_children_assets(self, asset):
        copy = asset.copy()
        if 'assets' in asset:
            copy.pop('assets')
        return copy

    def _filter_attributes(self, attributes_list):
        result = []
        for attribute in attributes_list:
            if self._match_attribute_field_with_query(attribute, self.attributes_query, self.attributes_field):
                result.append(attribute)
        return result

    @staticmethod
    def _match_asset_field_with_query(asset, query, field):
        field_not_present = field not in asset \
                           or asset[field] is None \
                           or (isinstance(asset[field], list) and len(asset[field]) == 0)

        if field_not_present:
            return query == ".*"

        if field != 'categories':
            string_to_match = asset[field]
            return re.match("^" + query + "$", string_to_match)
        else:
            for category in asset['categories']:
                if re.match("^" + query + "$", category):
                    return True
            return False

    @staticmethod
    def _match_attribute_field_with_query(attribute, query, field):
        field_not_present = field not in attribute \
                           or attribute[field] is None \
                           or (isinstance(attribute[field], list) and len(attribute[field]) == 0)

        if field_not_present:
            return query == ".*"

        if field != 'categories':
            string_to_match = attribute[field]
            return re.match("^" + query + "$", string_to_match)
        else:
            for category in attribute['categories']:
                for k, v in category.items():
                    if re.match("^" + query + "$", v):
                        return True
            return False

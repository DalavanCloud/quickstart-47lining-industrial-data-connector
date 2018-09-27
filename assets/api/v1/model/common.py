from flask_restplus import fields, Model

search_filter = Model('SearchFilter', {
    'type': fields.String(
        required=True,
        enum=['asset', 'attribute'],
        description='Type of entities being searched'
    ),
    'parameter': fields.String(
        required=True,
        enum=['description', 'category', 'template', 'path', 'feed', 'name'],
        description='Parameter of entity'
    ),
    'value': fields.String(
        required=True,
        description='Parameter value'
    )
})

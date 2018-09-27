from flask_restplus import fields, Model

credentials = Model('Credentials', {
    'username': fields.String(
        required=True,
        description='Name of a user'
    ),
    'password': fields.String(
        required=True,
        description='User\'s password'
    )
})

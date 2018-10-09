from flask_restplus import fields, Model

user_model = Model('User', {
    'username': fields.String(
        requred=True,
        readonly=True,
        description='Username used to login'
    ),
    'password': fields.String(
        requred=True,
        readonly=True,
        description='User password'
    ),
    'first_name': fields.String(
        requred=True,
        readonly=True,
        description='User\'s first name'
    ),
    'last_name': fields.String(
        requred=True,
        readonly=True,
        description='User\'s last name'
    )
})

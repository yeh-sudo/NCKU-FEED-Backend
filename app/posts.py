"""Provide api for user to create new posts."""

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from app import api
from app.models import Post
from app.utils import DatabaseProcessor

class Posts(Resource):
    def get(self):
        pass

    def post(self):
        pass

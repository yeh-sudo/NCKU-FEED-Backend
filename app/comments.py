"""Provide api for user to create new comment to one restaurant."""

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from app import api
from app.models import Rating, Comment
from app.utils import DatabaseProcessor

comments_args = reqparse.RequestParser()
comments_args.add_argument("target_id", type=str, help="restaurant's id")
comments_args.add_argument("comment_id", type=str, help="comment's id")
comments_args.add_argument("content", type=str, help="comment's content")
comments_args.add_argument("rating", type=int, action="append", location="json",
                        help="user's rating to a restaurant")

class Comments(Resource):
    """The class provides POST, PUT and DELETE method
    to user to create or modify comments, and GET method
    to get comments.
    """

    database_processor = DatabaseProcessor()

    @jwt_required()
    def get(self):
        """GET method to get all comments.

        Return:
            List of comments and status code 200.
        """

        args = comments_args.parse_args()
        result = self.database_processor.get_comment_from_restaurant_or_post(args.target_id)
        if not result:
            return {}, 500
        else:
            return {"comments": result}, 200

    @jwt_required()
    def post(self):
        """POST method to create a comment in database.

        Return:
            status code.
        """

        args = comments_args.parse_args()
        uid = get_jwt()["uid"]
        rating = Rating(
            cleanliness=args.rating[0],
            service=args.rating[1],
            deliciousness=args.rating[2],
            CPR=args.rating[3],
            overall=args.rating[4],
        )
        comment = Comment(
            uid=uid,
            target_id=args.target_id,
            rating=rating,
            content=args.content
        )
        if self.database_processor.insert_comment(comment.dict()):
            return {}, 201
        else:
            return {}, 500

    @jwt_required()
    def put(self):
        """PUT method to modify a comment in database.

        Return:
            status code.
        """

        args = comments_args.parse_args()
        json_input = {
            "_id": args.comment_id,
            "content": args.content
        }
        if self.database_processor.update_comment_content(json_input):
            return {}, 200
        else:
            return {}, 500

    @jwt_required()
    def delete(self):
        """DELETE method to delete a comment in database.

        Return:
            status code.
        """

        args = comments_args.parse_args()
        if self.database_processor.delete_comment(args.comment_id):
            return {}, 200
        else:
            return {}, 500

api.add_resource(Comments, "/posts")

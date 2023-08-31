"""Provide api for user to create new posts."""

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt
from app import api
from app.models import Post
from app.utils import DatabaseProcessor


posts_args = reqparse.RequestParser()
posts_args.add_argument("title", type=str)
posts_args.add_argument("content", type=str)
posts_args.add_argument("restaurants_id", type=str)
posts_args.add_argument("like", type=int)
posts_args.add_argument("comments_id", type=str)
posts_args.add_argument("release_time", type=str)
posts_args.add_argument("id", type=str)


class Posts(Resource):

    database_processor = DatabaseProcessor()

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("post_id", type=str, location="args")
        args = parser.parse_args()
        post = self.database_processor.get_post(args.post_id)
        if not post:
            return {}, 500
        else:
            return post, 200

    @jwt_required()
    def post(self):
        uid = get_jwt()["uid"]
        args = posts_args.parse_args()
        new_post = Post(
            uid=uid,
            title=args.title,
            content=args.content,
            restaurants_id=args.restaurants_id,
            like=0,
            comments_id=[]
        )
        if self.database_processor.insert_post(new_post.dict()):
            return new_post.dict(), 201
        else:
            return {}, 500

    @jwt_required()
    def put(self):
        args = posts_args.parse_args()
        if args.content is not None:
            json_input = {
                "_id": args.id,
                "content": args.content,
            }
            if not self.database_processor.update_post_content(json_input):
                return {"message": "update post's content error."}, 500
        if args.title is not None:
            json_input = {
                "_id": args.id,
                "title": args.title,
            }
            if not self.database_processor.update_post_title(json_input):
                return {"message": "update post's title error."}, 500
        if args.like is not None:
            json_input = {
                "_id": args.id,
                "like": args.like
            }
            if not self.database_processor.update_post_like(json_input):
                return {"message": "update post's like error."}, 500

    @jwt_required()
    def delete(self):
        args = posts_args.parse_args()
        if self.database_processor.delete_post(args.id):
            return {}, 200
        else:
            return {}, 500

api.add_resource(Posts, "/posts")

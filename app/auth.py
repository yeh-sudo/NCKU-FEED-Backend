"""Provide api for user to login, register and logout."""

from datetime import timedelta
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from app import nckufeed_db, api, redis_db
from app.models import User
from app.utils import create_user_hmap, RecommendComputeTask


user_args = reqparse.RequestParser()
user_args.add_argument("uid", type=str, help="user's uid in the Firebase")
user_args.add_argument("name", type=str, help="user's name")
user_args.add_argument("email", type=str, help="user's email")
user_args.add_argument("profile_photo", type=str, help="user's photo url")
user_args.add_argument("self_intro", type=str, help="user's self introduction")
user_args.add_argument("restaurant_id", type=str, help="add a new restaurant")
user_args.add_argument("preference", type=float, action="append", location="json",
                       help="user's preference of restaurants tags")


class Auth(Resource):
    """The class provides GET, POST and PUT method to user authentication api.
    """

    def get(self):
        """GET method for authentication api.

        Return:
            JWT token and status code 200.
        """

        parser = reqparse.RequestParser()
        parser.add_argument("uid", type=str, location="args")
        args = parser.parse_args()
        user_collection = nckufeed_db["users"]
        user = User(**user_collection.find_one({"uid": args.uid}))
        create_user_hmap(user.uid, user.preference)
        additional_claims = {
            "uid": user.uid,
            "nick_name": user.nick_name,
            "email": user.email
        }
        user_info = {
            "uid": user.uid,
            "nick_name": user.nick_name,
            "email": user.email,
            "self_intro": user.self_intro,
            "profile_photo": user.profile_photo,
            "restaurant_id": user.restaurants_id
        }
        access_token = create_access_token(args.uid, additional_claims=additional_claims)
        return {"access_token": access_token, "user_info": user_info}, 200, {"Access-Control-Allow-Origin": "*",
                                                                             "Access-Control-Allow-Methods": "*"}

    def post(self):
        """POST method for authentication api.

        Return:
            JWT token and status code 201.
        """

        args = user_args.parse_args()
        new_user = User(
            uid=args.uid,
            nick_name=args.name,
            email=args.email,
            profile_photo=args.profile_photo,
            self_intro="Hello, I'm " + args.name,
            comments_id=[],
            restaurants_id=[],
            preference=[]
        )
        user_collection = nckufeed_db["users"]
        user_collection.insert_one(new_user.dict())
        additional_claims = {
            "uid": args.uid,
            "nick_name": args.name,
            "email": args.email
        }
        access_token = create_access_token(args.uid, additional_claims=additional_claims)
        # TODO: add additional info if want
        return {"access_token": access_token}, 201, {"Access-Control-Allow-Origin": "*",
                                                    "Access-Control-Allow-Methods": "*"}

    @jwt_required()
    def put(self):
        """PUT method for authentication api.

        Return:
            Status code 200.
        """

        args = user_args.parse_args()
        claims = get_jwt()
        uid = claims["uid"]
        user_collection = nckufeed_db["users"]
        if args.name is not None:
            user_collection.update_one({"uid": uid},
                                       {"$set": {"nick_name": args.name}})
        if args.profile_photo is not None:
            user_collection.update_one({"uid": uid},
                                       {"$set": {"profile_photo": args.profile_photo}})
        if args.self_intro is not None:
            user_collection.update_one({"uid": uid}, {"$set": {"self_intro": args.self_intro}})
        if args.restaurant_id is not None:
            user_collection.update_one({"uid": uid},
                                       {"$push": {"restaurants_id": args.restaurant_id}})
        if args.preference is not None:
            # Only run this when the user is new
            create_user_hmap(uid, args.preference)
            thread = RecommendComputeTask(uid)
            thread.start()
            thread.join()
            create_user_hmap(uid, args.preference)
        return {}, 200, {"Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "*"}

    @jwt_required()
    def delete(self):
        """DELETE method for user to delete restaurant in database.

        Return:
            Status code 200.
        """

        args = user_args.parse_args()
        uid = get_jwt()["uid"]
        user_collection = nckufeed_db["users"]
        user_collection.update_one({"uid": uid},
                                   {"$pull": {"restaurants_id": args.restaurant_id}})
        return {}, 200, {"Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "*"}


class Logout(Resource):
    """The class provides api for logout from web application.
    """

    @jwt_required()
    def get(self):
        """GET method for user to logout and add jwt token to blocklist.

        Return:
            Return successful message if logout successfully.
        """

        jti = get_jwt()["jti"]
        uid = get_jwt()["uid"]
        thread = RecommendComputeTask(uid)
        thread.start()
        redis_db.set(jti, "", ex=timedelta(hours=1))
        return {"message": "Logout successfully."}, 200, {"Access-Control-Allow-Origin": "*",
                                                            "Access-Control-Allow-Methods": "*"}


api.add_resource(Auth, "/user")
api.add_resource(Logout, "/logout")

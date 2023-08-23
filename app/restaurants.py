"""Provide api for user to create new restaurant."""

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from app import api
from app.models import Restaurant
from app.utils import DatabaseProcessor


restaurants_args = reqparse.RequestParser()
restaurants_args.add_argument("name", type=str)
restaurants_args.add_argument("photos", type=str, action="append")
restaurants_args.add_argument("star", type=float, default=0)
restaurants_args.add_argument("tags", type=str, action="append")
restaurants_args.add_argument("open_hour", type=str, action="append")
restaurants_args.add_argument("address", type=str)
restaurants_args.add_argument("phone_number", type=str)
restaurants_args.add_argument("service", type=str, action="append")
restaurants_args.add_argument("website", type=str)
restaurants_args.add_argument("id", type=str)



class Restaurants(Resource):

    database_processor = DatabaseProcessor()

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("restaurant_id", type=str, location="args")
        args = parser.parse_args()
        restaurant = self.database_processor.get_restaurant_info(args.restaurant_id)
        if not restaurant:
            return {}, 500
        else:
            return restaurant, 200

    @jwt_required()
    def post(self):
        args = restaurants_args.parse_args()
        new_restaurant = {
            'name': args.name,
            'photos': args.photos,
            'star': args.star,
            'tags': args.tags,
            'open_hour': args.open_hour,
            'address': args.address,
            'phone_number': args.phone_number,
            'service': args.service,
            'website': args.website
        }
        post_result = self.database_processor.insert_restaurant(new_restaurant)
        if post_result['status']:
            return {'id': str(post_result['id'])}, 201
        else:
            return {}, 500

    @jwt_required()
    def put(self):
        args = restaurants_args.parse_args()
        if args.tags is not None:
            json_input = {
                "_id": args.id,
                "tags": args.tags,
            }
            if not self.database_processor.update_restaurant_tags(json_input):
                return {"message": "update restaurant's tags error."}, 500
        if args.open_hour is not None:
            json_input = {
                "_id": args.id,
                "open_hour": args.open_hour,
            }
            if not self.database_processor.update_restaurant_open_hour(json_input):
                return {"message": "update restaurant's open hour error."}, 500
        if args.phone_number is not None:
            json_input = {
                "_id": args.id,
                "phone_number": args.phone_number,
            }
            if not self.database_processor.update_restaurant_phone_number(json_input):
                return {"message": "update restaurant's phone number error."}, 500
        if args.service is not None:
            json_input = {
                "_id": args.id,
                "service": args.service,
            }
            if not self.database_processor.update_restaurant_service(json_input):
                return {"message": "update restaurant's service error."}, 500
        if args.website is not None:
            json_input = {
                "_id": args.id,
                "website": args.website,
            }
            if not self.database_processor.update_restaurant_website(json_input):
                return {"message": "update restaurant's web error."}, 500
        if args.photos is not None:
            json_input = {
                "_id": args.id,
                "photos": args.photos
            }
            if not self.database_processor.update_restaurant_photos(json_input):
                return {"message": "update restaurant's photo error."}, 500

    @jwt_required()
    def delete(self):
        args = restaurants_args.parse_args()
        if self.database_processor.delete_restaurant(args.id):
            return {}, 200
        else:
            return {}, 500

api.add_resource(Restaurants, "/restaurants")

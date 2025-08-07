from email.mime.text import MIMEText
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from db import users_collection
import datetime
import re
from bson import ObjectId  # למעלה בראש הקובץ
from books.utilities_books import getCounterBooksForId as count
auth = Blueprint("auth", __name__)

# 🔹 הרשמה
@auth.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    mobile = data.get("mobile", "").strip()
    genres = data.get("genres",[])
    bio = data.get("bio", "")
    location = data.get("location", "")
    image_base64 = data.get("image_base64", "")
    bio = data.get("bio", "")
    location = data.get("location", "")
    image_base64 = data.get("image_base64", "")
    testing_request = data.get("testing",False)

    if (testing_request):
        users_collection.delete_one({'email':email})

    if not full_name or not email or not password or not mobile:
        return jsonify({"message": "All fields are required"}), 400

    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, email):
        return jsonify({"message": "Invalid email format"}), 400
    
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    
    if not re.match(r"^0\d{8,9}$", mobile):
        return jsonify({"message": "Invalid mobile number"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400
    
    if not isinstance(genres,list):
        return jsonify({"message": "Genres must be a list"}), 400
    

    
    hashed_password = generate_password_hash(password)

    user = {
        "full_name": full_name,
        "email": email,
        "mobile": mobile,
        "password_hash": hashed_password,
        "created_at": datetime.datetime.utcnow(),
        "genres": genres,
        "bio": bio,
        "location": location,
        "image_base64": image_base64,
        "genres": genres,
        "bio": bio,
        "location": location,
        "image_base64": image_base64
    }
    users_collection.insert_one(user)
    token = create_access_token(identity=email, expires_delta=datetime.timedelta(hours=1))

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "userId": str(user["_id"]),
        "full_name": str(user["full_name"]),
        "bio": user["bio"],
        "location": user["location"],
        "image_base64": user["image_base64"],
        "genres": user["genres"]}), 201


# 🔹 התחברות
@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email","")
    password = data.get("password","")

    if not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    user = users_collection.find_one({"email": email})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=email, expires_delta=datetime.timedelta(hours=1))

    return jsonify({
        "message": "Login successful",
        "token": token,
        "userId": str(user["_id"]),
        "full_name": str(user["full_name"]),
        "bio": str(user["bio"]),
        "location": str(user["location"]),
        "full_name": str(user["full_name"]),
        "bio": str(user["bio"]),
        "location": str(user["location"]),
        "image_base64": str(user["image_base64"]),
        "genres" : list(user["genres"])
    }) , 200
    
@auth.route('/deleteUser',methods=['DELETE'] )
def delete_user():   
    data = request.json
    email = data.get("email","")

    if not email:
        return jsonify({"message": "All fields are required"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    users_collection.delete_one({'email':email})

    return 200

# 🔹 הבאת פרטי משתמש מחובר
@auth.route("/user", methods=["GET"])
@jwt_required()
def get_user():
    email = get_jwt_identity()
    user = users_collection.find_one({"email": email}, {"_id": 0, "password_hash": 0})
    
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user)


@auth.route("/update_genres", methods=["PUT"])
def update_genres():
    data = request.json
    user_id = data.get("user_id")
    genres = data.get("genres", [])

    if not user_id or not isinstance(genres, list):
        return jsonify({"message": "Missing or invalid data"}), 400

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"genres": genres}}
    )

    if result.matched_count == 0:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"message": "Genres updated successfully"}), 200


@auth.route('/update_bio', methods=['POST'])
def update_bio():
    data = request.get_json()
    user_id = data['user_id']
    bio = data['bio']

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"bio": bio}}
    )

    if result.modified_count:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "no change"}), 200


@auth.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    user_id = data['user_id']
    location = data['location']

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"location": location}}
    )

    if result.modified_count:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "no change"}), 200
    
    
@auth.route('/update_profile_image', methods=['POST'])
def update_profile_image():
    data = request.get_json()
    user_id = data['user_id']
    image_base64 = data['image_base64']

    if not user_id or not image_base64:
        return jsonify({"status": "error", "message": "Missing user_id or image_base64"}), 400

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"image_base64": image_base64}}
    )

    if result.modified_count:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "no change"}), 200
    

@auth.route('/getAllUsers',methods =['GET'] )
def getAllUsers():
    try:
        userList = users_collection.find({})
        returnList =[]
        for user in userList:
            returnList.append({
                 "id":str(user["_id"]),
                 "full_name":user["full_name"],
                 "numBooks":count(user["_id"]),
                 "bio":user["bio"],
                 "location":user["location"],
                "created in":user["created_at"]
        })
        return jsonify({"users": returnList}), 200

    except Exception as e:
        print(f"Error : {e}")
        return jsonify({"message": "Internal server error"}), 500

    
    

from flask import Flask, render_template, jsonify, request
from lib import AwsBucketApi

app      = Flask(__name__, static_folder="./statics", static_url_path="", template_folder="./templates")
bucket   = AwsBucketApi()
userpath = "user1/"

@app.route("/")
def homepage():
    post_fields = bucket.generate_presigned_post_fields(path_prefix=userpath)
    return render_template("index.html", data = {
        "post_fields" : post_fields
    })

@app.route("/get-images")
def get_images():
    # !IMPORTANT! : User access must be checked before get operation!
    # Users must only access their folders.
    return jsonify(bucket.get_files(userpath))

@app.route("/delete-image")
def delete_image():
    filename = request.args.get("filename")
    # !IMPORTANT! : User access must be checked before delete operation!
    return jsonify(bucket.delete_file(filename))

if __name__ == "__main__":
    app.run("0.0.0.0", 80, debug=True)
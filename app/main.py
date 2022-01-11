from flask import Flask, render_template, jsonify, request
from lib import AwsBucketApi

app     = Flask(__name__, static_folder="./statics", static_url_path="", template_folder="./templates")
bucket  = AwsBucketApi()

@app.route("/")
def homepage():
    post_fields = bucket.generate_presigned_post_fields(path_prefix="img/")
    return render_template("index.html", data = {
        "post_fields" : post_fields
    })

@app.route("/get-images")
def get_images():
    return jsonify(bucket.get_files())

@app.route("/delete-image")
def delete_image():
    filename = request.args.get("filename")
    return jsonify(bucket.delete_file(filename))

if __name__ == "__main__":
    app.run("0.0.0.0", 80, debug=True)
import os

from flask import Flask, redirect, render_template, request, url_for
from minio import Minio
from minio.error import S3Error

BUCKET = os.environ["BUCKET_NAME"]
ENDPOINT = os.environ.get("MINIO_ENDPOINT", "play.min.io")
ACCESS_KEY = os.environ["ACCESS_KEY"]
SECRET_KEY = os.environ["SECRET_KEY"]

client = Minio(ENDPOINT, access_key=ACCESS_KEY, secret_key=SECRET_KEY, secure=True)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    objects = [o.object_name for o in client.list_objects(BUCKET)]
    return render_template(
        "index.html", bucket=BUCKET, endpoint=ENDPOINT, objects=objects, error=None
    )


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f or not f.filename:
        return redirect(url_for("index"))
    client.put_object(
        BUCKET,
        f.filename,
        f.stream,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=f.mimetype or "application/octet-stream",
    )
    return redirect(url_for("index"))


@app.route("/delete/<path:name>", methods=["POST"])
def delete(name):
    try:
        client.remove_object(BUCKET, name)
    except S3Error:
        pass
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7691)

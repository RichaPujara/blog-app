from flask import Flask, render_template, request, url_for, redirect
import csv
import uuid
from datetime import datetime as dt
import logging

app = Flask(__name__)

# For recording log for debugging purposes only
logging.basicConfig(
    filename="record.log",
    level=logging.DEBUG,
    format=f"%(asctime)s %(levelname)s %(threadName)s : %(message)s",
)

# File path for the blogs CSV file
BLOGS_FILE = "blogs.csv"
all_tags = ["custom"]


# Function to read blogs from the CSV file
def read_blogs():
    blogs = []
    try:
        with open(BLOGS_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                blogs.append(row)
        return blogs
    except FileNotFoundError as e:
        with open(BLOGS_FILE, "w") as file:
            return blogs


# Function to write blogs to the CSV file
def write_blogs(blogs):
    with open(BLOGS_FILE, "w", newline="") as file:
        fieldnames = [
            "_id",
            "user_id",
            "author",
            "title",
            "tags",
            "blogpost",
            "created_date",
            "updated_date",
            "comments",
            "likes",
            "comments_count",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for blog in blogs:
            writer.writerow(blog)


# Function to check if generated id is unique.
def is_id_unique(csv_file, new_id):
    blogs = read_blogs()
    with open(csv_file, "r", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == new_id:
                return False
    return True


# Function to generate unique id for each blog.
def generate_id():
    while True:
        new_id = str(uuid.uuid4())
        if is_id_unique(BLOGS_FILE, new_id):
            return new_id


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    # elif request.method == "POST":
    #     query = request.form["search"]
    #     blogs = read_blogs()
    #     res = []
    #     for blog in blogs:
    #         if query in blog["tags"]:
    #             res.append(blog)
    #     return render_template("blog_list.html", blogs=res)


@app.route("/blogs", methods=["GET", "POST"])
def blog_list():
    all_blogs = read_blogs()
    return render_template("blog_list.html", blogs=all_blogs)


@app.route("/blogs/<int:index>", methods=["GET", "POST"])
def show_blogs(index):
    blogs = read_blogs()
    blog = blogs[index]
    app.logger.info("Processing get blog by title request: %s", blog)
    return render_template("blog.html", blog=blog, blog_index=index)


@app.route("/blogs/new", methods=["GET", "POST"])
def create_blog():
    if request.method == "POST":
        app.logger.info("Processing create Blog request")
        author = request.form["author"]
        date = dt.now().strftime("%Y-%m-%d")
        title = request.form["title"]
        blogpost = request.form["blogpost"]
        tags = (
            request.form["tags"].split(", ")
            if ", " in request.form["tags"]
            else [request.form["tags"]]
        )

        for tag in tags:
            if not tag.lower() in all_tags:
                all_tags.append(tag.lower())

        id = generate_id()

        new_blog = {
            "_id": id,
            # "user_id" = ,
            "author": author,
            "title": title,
            "tags": tags,
            "blogpost": blogpost,
            "created_date": date,
            "comments": [],
            "likes": 0,
            "comments_count": 0,
        }
        blogs = read_blogs()
        blogs.append(new_blog)
        write_blogs(blogs)
        blog_index = blogs.index(new_blog)
        app.logger.info("Created Blog: %s", new_blog["_id"])
        return redirect(f"/blogs/{blog_index}")
    elif request.method == "GET":
        return render_template("new_blog.html")


@app.route("/blogs/<int:index>/edit", methods=["GET", "POST"])
def edit_blog(index):
    blogs = read_blogs()
    blog = blogs[index]
    if request.method == "POST":
        app.logger.info("Processing update Blog request")
        author = request.form["author"]
        title = request.form["title"]
        blogpost = request.form["blogpost"]
        date = dt.now()

        if ", " in request.form["tags"]:
            tags = request.form["tags"].split(",")
        else:
            tags = [request.form["tags"]]

        for tag in tags:
            if not tag.lower() in all_tags:
                all_tags.append(tag.lower())

        updated_blog = {
            "_id": blog["_id"],
            # "user_id" = ,
            "author": author,
            "title": title,
            "tags": tags,
            "blogpost": blogpost,
            "created_date": blog["created_date"],
            "updated_date": date,
            "comments": blog["comments"],
            "likes": blog["likes"],
            "comments_count": blog["comments_count"],
        }

        blogs[index] = updated_blog
        app.logger.info("Processing updated blog by title request: %s", updated_blog)
        return render_template("blog.html", blog=updated_blog, blog_index=index)
    else:
        app.logger.info("Processing get blog by title request: %s", blog)
        return render_template("edit_blog.html", blog=blog, blog_index=index)


@app.route("/blogs/<int:index>/delete")
def delete_blog(index):
    blogs = read_blogs()
    blogs.pop(index)
    write_blogs(blogs)
    return redirect("/blogs")


app.run(debug=True, port=1234)

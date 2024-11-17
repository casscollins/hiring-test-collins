# /// script
# dependencies = [
#   "flask",
#   "flask-cors",
#   "Flask-SQLAlchemy",
# ]
# ///

from flask import Flask, request
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select, delete

TAGS = [
    {"id": 1, "name": "anime"},
    {"id": 2, "name": "reviews"},
    {"id": 3, "name": "emotions"},
    {"id": 4, "name": "upcoming"},
    {"id": 5, "name": "AttackOnTitan"},
    {"id": 6, "name": "recommendations"},
    {"id": 7, "name": "manga"},
    {"id": 8, "name": "DemonSlayer"},
    {"id": 9, "name": "merch"},
    {"id": 10, "name": "nostalgia"},
    {"id": 11, "name": "characters"},
]

POSTS = [
    {
        "id": 1,
        "username": "Ellie",
        "content": "Just finished watching the latest episode of my favorite anime! So intense!",
        "created_at": "2024-09-24T14:30:00",
    },
    {
        "id": 2,
        "username": "Max",
        "content": "Can’t believe how much I cried during that last episode! #animefeels",
        "created_at": "2024-09-24T15:00:00",
    },
    {
        "id": 3,
        "username": "Sara",
        "content": "Who else is excited for the new season coming out next month?",
        "created_at": "2024-09-24T16:00:00",
    },
    {
        "id": 4,
        "username": "Jake",
        "content": "I finally started watching Attack on Titan! Why did I wait so long?!",
        "created_at": "2024-09-24T16:30:00",
    },
    {
        "id": 5,
        "username": "Nina",
        "content": "I need recommendations for slice-of-life anime! What’s your favorite?",
        "created_at": "2024-09-24T17:00:00",
    },
    {
        "id": 6,
        "username": "Leo",
        "content": "Just started reading the manga of my favorite series. It’s so good!",
        "created_at": "2024-09-24T17:30:00",
    },
]

POST_TAGS = [
    {"post_id": 1, "tag_id": 1},  # Post 1 with tag "anime"
    {"post_id": 1, "tag_id": 2},  # Post 1 with tag "reviews"
    {"post_id": 2, "tag_id": 1},  # Post 2 with tag "anime"
    {"post_id": 2, "tag_id": 3},  # Post 2 with tag "emotions"
    {"post_id": 3, "tag_id": 1},  # Post 3 with tag "anime"
    {"post_id": 3, "tag_id": 4},  # Post 3 with tag "upcoming"
    {"post_id": 4, "tag_id": 1},  # Post 4 with tag "anime"
    {"post_id": 4, "tag_id": 5},  # Post 4 with tag "AttackOnTitan"
    {"post_id": 5, "tag_id": 1},  # Post 5 with tag "anime"
    {"post_id": 5, "tag_id": 6},  # Post 5 with tag "recommendations"
    {"post_id": 6, "tag_id": 1},  # Post 6 with tag "anime"
    {"post_id": 6, "tag_id": 7},  # Post 6 with tag "manga"
]

POST_LIKES = [
    {"post_id": 1, "user_id": 1},
    {"post_id": 1, "user_id": 2},
    {"post_id": 1, "user_id": 3},
    {"post_id": 2, "user_id": 1},
    {"post_id": 2, "user_id": 4},
    {"post_id": 3, "user_id": 2},
    {"post_id": 3, "user_id": 5},
    {"post_id": 4, "user_id": 6},
    {"post_id": 4, "user_id": 1},
    {"post_id": 5, "user_id": 2},
    {"post_id": 5, "user_id": 3},
    {"post_id": 6, "user_id": 4},
    {"post_id": 6, "user_id": 5},
]

DEMO_USER_ID = 1

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hiring_template.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)

db = SQLAlchemy(app)


def refresh_db():
    db.drop_all()
    db.create_all()
    for post in POSTS:
        new_post = Post(
            id=post["id"],
            username=post["username"],
            content=post["content"],
            created_at=datetime.fromisoformat(post["created_at"]),
        )
        db.session.add(new_post)

    for tag in TAGS:
        new_tag = Tag(id=tag["id"], name=tag["name"])
        db.session.add(new_tag)

    for post_like in POST_LIKES:
        new_post_like = PostLike(
            post_id=post_like["post_id"],
            user_id=post_like["user_id"],
        )
        db.session.add(new_post_like)

    for post_tag in POST_TAGS:
        new_post_tag = PostTag(
            post_id=post_tag["post_id"],
            tag_id=post_tag["tag_id"],
        )
        db.session.add(new_post_tag)

    db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    post_tags = db.relationship("PostTag", back_populates="post")
    likes = db.relationship("PostLike", backref="post", lazy=True)

    def to_json(self, user_id=None):
        return {
            "id": self.id,
            "username": self.username,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "tags": [tag.tag.name for tag in self.post_tags],
            "likes": len(self.likes),
            "liked": any(like.user_id == user_id for like in self.likes)
            if user_id
            else False,
        }


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    post_tags = db.relationship("PostTag", back_populates="tag")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)


class PostTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), nullable=False)

    post = db.relationship("Post", back_populates="post_tags")
    tag = db.relationship("Tag", back_populates="post_tags")

@app.route("/tags")
def tags():
    stmt = select(Tag)
    tags = db.session.execute(stmt)
    response = [tag[0].to_json() for tag in tags]
    return response


@app.route("/posts/featured")
def featured():
    stmt = select(Post).order_by(func.random()).limit(1)
    posts = db.session.execute(stmt)
    # This only returns one result so for loop is just to access the iterator
    for post in posts:
        response = post[0].to_json(DEMO_USER_ID)
    return response


@app.route("/like/<post_id>", methods=["POST"])
def like(post_id):
    # Assume user_id is always 1 for this example
    # Have made the assumption that we want to be able to unlike as well as like to make demoing more functional
    # as this is the more commonly expected behaviour of a like button in most UIs
    existing_like_query = select(PostLike).where(PostLike.post_id == post_id).where(PostLike.user_id == DEMO_USER_ID)
    already_liked = len(db.session.execute(existing_like_query).all())
    if already_liked:
        delete_statement = delete(PostLike).where(PostLike.post_id == post_id).where(PostLike.user_id == DEMO_USER_ID)
        db.session.execute(delete_statement)
    else:
        new_post_like = PostLike(
            post_id=post_id,
            user_id=DEMO_USER_ID,
        )
        db.session.add(new_post_like)
    db.session.commit()
    return { "status": "Success" }


@app.route("/posts")
def posts():
    tag_filter = request.args.get('tag', '')
    sort_by = request.args.get('sort', '')
    stmt = select(Post)
    if tag_filter:
        filtered_post_tags = select(PostTag.post_id).join(Tag).filter(Tag.name == tag_filter).subquery()
        stmt = stmt.where(Post.id.in_(filtered_post_tags))
    if sort_by == 'latest':
        stmt = stmt.order_by(Post.created_at)
    elif sort_by == 'popular':
        post_likes_query = select(PostLike.post_id, func.count(PostLike.post_id).label('like_count')).group_by(PostLike.post_id).subquery()
        stmt = stmt.join(post_likes_query, Post.id == post_likes_query.c.post_id).order_by(post_likes_query.c.like_count.desc())
    posts = db.session.execute(stmt)
    response = [post[0].to_json(DEMO_USER_ID) for post in posts]
    return response

if __name__ == "__main__":
    with app.app_context():
        refresh_db()
        app.run()

from fastapi import FastAPI

app = FastAPI()

# users
@app.post("/users/signup")
def signup():
    pass


@app.post("/users/login")
def login():
    pass


@app.post("/users/refresh")
def token_refresh():
    pass


@app.post("/users/logout")
def logout():
    pass


# posts
@app.post("/posts")
def create_post():
    pass


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    pass


@app.get("/posts")
def get_posts():
    pass


@app.put("/posts/{post_id}")
def update_post(post_id: int):
    pass


@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    pass

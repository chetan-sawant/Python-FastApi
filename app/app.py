from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield




app = FastAPI(lifespan= lifespan)

#Test API 
@app.get("/hello-world")
def hello_world():
    return {"message": "Hello World"}
    
text_posts = {
  1: {"title":"New Post","content":"Cool test post"},
  2: {"title":"Tech Update","content":"Java 21 brings performance and language improvements"},
  3: {"title":"Investment Tip","content":"Diversification helps reduce portfolio risk"},
  4: {"title":"Travel Diaries","content":"Exploring hidden beaches in South Goa"},
  5: {"title":"Fitness Note","content":"Consistency matters more than intensity"},
  6: {"title":"Career Advice","content":"Build depth in one skill before expanding horizontally"},
  7: {"title":"AI Trends","content":"Generative AI is transforming enterprise applications"},
  8: {"title":"Startup Insight","content":"Solve real problems before scaling fast"},
  9: {"title":"Health Reminder","content":"Proper sleep improves productivity and focus"},
  10: {"title":"Learning Log","content":"Daily practice compounds into long-term mastery"}
}

@app.get("/posts")
def get_all_posts(limit : int = None):
    if limit:
        return list(text_posts.values())[:limit]
    return text_posts


@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail = "Post not found")
    
    return text_posts[id]


@app.post("/posts")
def create_post(post: PostCreate) -> PostResponse:
    new_post = {"title": post.title,"content": post.content}
    text_posts[max(text_posts.keys()) + 1]= new_post
    return new_post
    
# Upload Api
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session)
):
    post = Post(
        caption = caption,
        url = "dummy url",
        file_type = "photo",
        file_name = "dummy name"
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@app.get("/feed")
async def get_fed(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id":str(post.id),
                "caption":post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )

        return {"posts": posts_data}
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models, schemas
from app.crud_router import make_crud_router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Учебный центр API", lifespan=lifespan)

app.include_router(make_crud_router(models.Group, schemas.GroupIn, schemas.GroupOut, "/groups"))
app.include_router(make_crud_router(models.Student, schemas.StudentIn, schemas.StudentOut, "/students"))
app.include_router(make_crud_router(models.Teacher, schemas.TeacherIn, schemas.TeacherOut, "/teachers"))
app.include_router(make_crud_router(models.Course, schemas.CourseIn, schemas.CourseOut, "/courses"))
app.include_router(make_crud_router(models.Grade, schemas.GradeIn, schemas.GradeOut, "/grades"))


@app.get("/health")
def health():
    return {"status": "ok"}
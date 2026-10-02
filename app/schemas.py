from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class GroupOut(GroupIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class StudentIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    group_id: Optional[int] = None


class StudentOut(StudentIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TeacherIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    department: str = Field(min_length=1, max_length=100)


class TeacherOut(TeacherIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    hours: int = Field(gt=0)
    teacher_id: Optional[int] = None


class CourseOut(CourseIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GradeIn(BaseModel):
    student_id: int
    course_id: int
    value: int = Field(ge=2, le=5)


class GradeOut(GradeIn):
    model_config = ConfigDict(from_attributes=True)
    id: int

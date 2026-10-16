from app.crypto.encryption import encrypt_field, decrypt_field, blind_index
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    _encrypted_email = Column("encrypted_email", String(500))
    email_index = Column(String(64), unique=True, index=True)

    @property
    def email(self):
        return decrypt_field(self._encrypted_email)

    @email.setter
    def email(self, value):
        self._encrypted_email = encrypt_field(value)
        self.email_index = blind_index(value) if value else None
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(1000), nullable=False, default="")
    teacher_id = Column(Integer, nullable=False)

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            name="unique_student_course"
        ),
    )

from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


# 1. The User Model (Represents a student)
class User(SQLModel, table=True):
    # 'id' is the primary key (unique ID for every student).
    # It is Optional because the DB creates it, not us.
    id: Optional[int] = Field(default=None, primary_key=True)

    username: str = Field(index=True, unique=True)  # Must be unique!
    email: str = Field(unique=True)
    password: str  # We will hash this later.
    year: int  # 1, 2, 3, or 4

    # RELATIONS:
    # A User has many Skills. This links to the 'Skill' class below.
    skills: List["Skill"] = Relationship(back_populates="owner")


# 2. The Skill Model (What they are offering)
class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # e.g., "Python", "Guitar"
    level: str  # "Beginner", "Intermediate", "Expert"

    # FOREIGN KEY:
    # This links a skill to a specific User.
    # If User #1 is deleted, this link ensures we know who owned the skill.
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # RELATION:
    # This lets us access the User object from the Skill (e.g., my_skill.owner.username)
    owner: Optional[User] = Relationship(back_populates="skills")
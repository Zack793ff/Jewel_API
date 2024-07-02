import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
  id: Optional[int] = Field(primary_key=True)
  username: str = Field(index=True)
  password: str = Field(max_length=256, min_length=6)
  email: str
  created_at:  datetime.datetime = Field(default_factory=datetime.datetime.now)
  is_seller: bool = Field(default=False)


class UserInput(SQLModel):
  username: str
  password: str = Field(max_length=256, min_length=6)
  password2: str
  email: str
  is_seller: bool = Field(default=False)


  @field_validator('password2')
  def password_match(cls, v, values, **kwargs):
    password = values.data.get('password')
    if 'password' and v != password:
        raise ValueError("Password don't match")
    return v


class UserLogin(SQLModel):
   username: str
   password: str

  

  


    



  



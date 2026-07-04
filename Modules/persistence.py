from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select

class UserProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    bio: Optional[str] = None
    links: Optional[str] = None  # Comma-separated or JSON string
    ip_address: Optional[str] = None

sqlite_file_name = "oxie_talk.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def save_profile(username: str, bio: str = "", links: str = "", ip: str = ""):
    with Session(engine) as session:
        statement = select(UserProfile).where(UserProfile.username == username)
        results = session.exec(statement)
        profile = results.first()

        if profile:
            profile.bio = bio
            profile.links = links
            profile.ip_address = ip
        else:
            profile = UserProfile(username=username, bio=bio, links=links, ip_address=ip)

        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile

def get_profile(username: str):
    with Session(engine) as session:
        statement = select(UserProfile).where(UserProfile.username == username)
        results = session.exec(statement)
        return results.first()

def get_all_profiles():
    with Session(engine) as session:
        statement = select(UserProfile)
        results = session.exec(statement)
        return results.all()

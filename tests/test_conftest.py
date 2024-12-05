# conftest.py
import pytest
from faker import Faker  # Add this line
from app.services.jwt_service import create_access_token  # Make sure this import is correct
from app.models.user_model import User
from app.database import AsyncSession  # Adjust based on how your database session is structured
from app.main import app
from app.utils.security import hash_password
from app.services.email_service import EmailService
from app.dependencies import get_db

fake = Faker()

# Add the user_token fixture to generate the token
@pytest.fixture
async def user_token(db_session, user):
    """Fixture to generate a regular user token."""
    token = create_access_token(user)  # Generates JWT token for the regular user
    return token

@pytest.fixture
def email_service():
    # Assuming the TemplateManager does not need any arguments for initialization
    template_manager = TemplateManager()
    email_service = EmailService(template_manager=template_manager)
    return email_service

# this is what creates the http client for your api tests
@pytest.fixture(scope="function")
async def async_client(db_session):
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        app.dependency_overrides[get_db] = lambda: db_session
        try:
            yield client
        finally:
            app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def initialize_database():
    try:
        Database.initialize(settings.database_url)
    except Exception as e:
        pytest.fail(f"Failed to initialize the database: {str(e)}")

# this function setup and tears down (drops tables) for each test function, so you have a clean database for each test.
@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        # you can comment out this line during development if you are debugging a single test
         await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(setup_database):
    async with AsyncSessionScoped() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest.fixture(scope="function")
async def locked_user(db_session):
    unique_email = fake.email()
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": unique_email,
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": True,
        "failed_login_attempts": settings.max_login_attempts,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def user(db_session):
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def verified_user(db_session):
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": True,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def unverified_user(db_session):
    user_data = {
        "nickname": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "hashed_password": hash_password("MySuperPassword$1234"),
        "role": UserRole.AUTHENTICATED,
        "email_verified": False,
        "is_locked": False,
    }
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture(scope="function")
async def users_with_same_role_50_users(db_session):
    users = []
    for _ in range(50):
        user_data = {
            "nickname": fake.user_name(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "hashed_password": fake.password(),
            "role": UserRole.AUTHENTICATED,
            "email_verified": False,
            "is_locked": False,
        }
        user = User(**user_data)
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    return users

@pytest.fixture
async def admin_user(db_session: AsyncSession):
    user = User(
        nickname="admin_user",
        email="admin@example.com",
        first_name="John",
        last_name="Doe",
        hashed_password="securepassword",
        role=UserRole.ADMIN,
        is_locked=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
async def manager_user(db_session: AsyncSession):
    user = User(
        nickname="manager_john",
        first_name="John",
        last_name="Doe",
        email="manager_user@example.com",
        hashed_password="securepassword",
        role=UserRole.MANAGER,
        is_locked=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user

# Fixtures for common test data
@pytest.fixture
def user_base_data():
    return {
        "username": "john_doe_123",
        "email": "john.doe@example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "username": "john_doe_123",
        "email": "john.doe.example.com",
        "full_name": "John Doe",
        "bio": "I am a software engineer with over 5 years of experience.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe.jpg"
    }


@pytest.fixture
def user_create_data(user_base_data):
    return {**user_base_data, "password": "SecurePassword123!"}

@pytest.fixture
def user_update_data():
    return {
        "email": "john.doe.new@example.com",
        "full_name": "John H. Doe",
        "bio": "I specialize in backend development with Python and Node.js.",
        "profile_picture_url": "https://example.com/profile_pictures/john_doe_updated.jpg"
    }

@pytest.fixture
def user_response_data():
    return {
        "id": "unique-id-string",
        "username": "testuser",
        "email": "test@example.com",
        "last_login_at": datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "links": []
    }

@pytest.fixture
def login_request_data():
    return {"username": "john_doe_123", "password": "SecurePassword123!"}

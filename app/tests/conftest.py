from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api import deps
from app.db.base_class import Base
from app.main import app

TEST_X_USERINFO = "eyJpc3MiOiJodHRwczovL2lkLnVjaGV0Lmt6Ly5pZHAvIiwiYXVkIjpbIm1yZG9za3VsIl0sInVzZXIiOnsiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzX3N0YWZmIjp0cnVlLCJlbWFpbCI6ImRAdWNoZXQua3oiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInBob25lIjoiKzc3MDA1NTAyMjMxIn0sImlhdCI6MTY2MjQzNjY2NSwiaWQiOiI3NjkwNGUzMy0wNTAwLTRlZjYtYWM2YS04NWQyMzE5ZDIwMzQiLCJhdXRoX3RpbWUiOjE2NjI0MzY2NjUsInN1YiI6Ijc2OTA0ZTMzLTA1MDAtNGVmNi1hYzZhLTg1ZDIzMTlkMjAzNCIsInJhdCI6MTY2MjQzNjY2NX0="
TEST_X_USERINFO_2 = "eyJpc3MiOiJodHRwczovL2lkLnVjaGV0Lmt6Ly5pZHAvIiwiYXVkIjpbIm1yZG9za3VsIl0sInVzZXIiOnsiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzX3N0YWZmIjp0cnVlLCJlbWFpbCI6ImRAdWNoZXQua3oiLCJwaG9uZV92ZXJpZmllZCI6ZmFsc2UsInBob25lIjoiKzc3MDA1NTAyMjMxIn0sImlhdCI6MTY2MjQzNjY2NSwiaWQiOiIxMjBmN2RmYS0xNDliLTQzNzUtOTFkYS1hMTJmMGIxZmYzNjciLCJhdXRoX3RpbWUiOjE2NjI0MzY2NjUsInN1YiI6Ijc2OTA0ZTMzLTA1MDAtNGVmNi1hYzZhLTg1ZDIzMTlkMjAzNCIsInJhdCI6MTY2MjQzNjY2NX0="

# test_database
TEST_SQLALCHEMY_DATABASE_URL = "postgresql://test:qwerty@db-test/ukassa_test"
engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

        # TODO: drop db after all tests have finished
        # https://stackoverflow.com/questions/58328899/pytest-delete-db-after-tests
        # drop_database(TEST_SQLALCHEMY_DATABASE_URL)


@pytest.fixture(scope="session")
def client() -> Generator:
    with TestClient(app) as client:
        app.dependency_overrides[deps.get_db] = override_get_db
        yield client
        app.dependency_overrides = {}

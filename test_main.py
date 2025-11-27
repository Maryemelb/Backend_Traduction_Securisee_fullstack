from fastapi.testclient import TestClient
import pytest
from schemas.users import User_schema
from main import app
from db.database import sessionLocal
@pytest.fixture
def user():
    return {
        'username': 'm',
        'password': 'm'
    }
@pytest.fixture
def getdb():
    db=sessionLocal()
    try:
      yield db
    finally:
      db.close()

@pytest.fixture
def token():
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InIifQ.Ofc9tGD0b9PgUkitH3kx_qU5MotmiE1LUG8VJu8UJnw"
def test_login(user,getdb):
   testClient= TestClient(app)
   response= testClient.post('/login', json=user)
   assert response.status_code == 200
   assert isinstance(response.json(), str)
   
def test_translate_txt(token):
      payload={
          "text": "Durable stainless steel blades for chopping, blending, and pureeing",
          "choice": "EN -> FR"
      }
      header= {
          "Authorization": f"Bearer {token}"
      }
      testClient= TestClient(app)
      response = testClient.post('/translate', json=payload,headers=header)
      assert response.status_code == 200



import pytest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlmodel import create_engine, Session, SQLModel
from src.database.db_models import Prediction, Feedback


from maconfig import DATABASE_URL
# URL de la base de données de test
TEST_DATABASE_URL = DATABASE_URL
print("TEST_DATABASE_URL:", TEST_DATABASE_URL)

# Définition des fixtures

@pytest.fixture(name="engine") # on crée un fixture que l'on appelle "engine".
def engine_fixture():
    engine = create_engine(TEST_DATABASE_URL, echo=True)
    yield engine # on yield l'engine pour qu'il soit utilisé dans les tests
    engine.dispose() # on libere la resssource engine après utilisation


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session  # on yield la session pour qu'elle soit utilisée dans les tests
        session.rollback()  # on annule les changements après chaque test pour garder la base propre

#def test_connexion_base(session):
    # Exemple pour tester la connexion à la base de données
#    result = session.execute("SELECT 1").scalar() 
#    assert result == 1

def test_creation_prediction(session):
    
    new_prediction = Prediction(
        probabilite_chat = 0.5,
        image_path = "test_image.jpg",
        inference_time_ms = 999.99
        )
    session.add(new_prediction)
    session.commit()
    assert new_prediction.id_predict is not None

def test_creation_feedback(session):
      
    new_feedback = Feedback(
        prediction_id=1,
        feedback=0
        )
    session.add(new_feedback)
    session.commit()
    assert new_feedback.id is not None

    
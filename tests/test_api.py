"""가짜 모드(모델 파일 없음)에서 주소 2개가 약속한 모양대로 답하는지 확인. 실행: pytest"""
import io

from fastapi.testclient import TestClient

import predict
from main import app
from schemas import PredictResponse


def client(monkeypatch):
    monkeypatch.setattr(predict, "MODEL_FILE", predict.MODEL_FILE.with_name("없는파일.joblib"))
    return TestClient(app)


def test_health(monkeypatch):
    with client(monkeypatch) as c:
        r = c.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "model": "fake"}


def test_predict_fake(monkeypatch):
    with client(monkeypatch) as c:
        r = c.post("/predict", files={"video": ("a.mp4", io.BytesIO(b"0" * 10), "video/mp4")})
    assert r.status_code == 200
    body = PredictResponse(**r.json())          # 약속한 모양이 아니면 여기서 실패
    assert body.model == "fake"
    assert body.people[0].action_id == "A005"


def test_wrong_extension(monkeypatch):
    with client(monkeypatch) as c:
        r = c.post("/predict", files={"video": ("a.txt", io.BytesIO(b"hello"), "text/plain")})
    assert r.status_code == 400

"""AI 추론 서버 — 영상 하나를 받아 사람별 동작을 JSON 으로 돌려준다.

DB·로그인·작업 상태는 backend(Django)가 맡는다. 이 서버는 DB 를 모른다.
models/ 에 모델 파일이 없으면 '가짜 모드'로 켜져서 정해진 예시 JSON 을 돌려준다
→ backend·frontend 가 모델이 완성되기 전에도 바로 붙여서 개발할 수 있다.

실행: uvicorn main:app --reload --port 8001   → http://127.0.0.1:8001/docs
"""
import shutil
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

import predict
from schemas import HealthResponse, PredictResponse

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
MAX_UPLOAD_MB = 100


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버를 켤 때 모델을 한 번만 불러온다 (요청마다 불러오면 매번 몇 초씩 걸림)
    app.state.model = predict.load_model()
    yield


app = FastAPI(title="TEAM3 동작 추론 API", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "model": predict.model_name(app.state.model)}


@app.post("/predict", response_model=PredictResponse)
def predict_video(video: UploadFile = File(..., description="분석할 영상 파일")):
    # async def 가 아니라 def 로 쓴다: Pose 계산처럼 오래 걸리는 일을 해도
    # FastAPI 가 다른 스레드에서 돌려서 서버 전체(다른 요청)가 멈추지 않는다
    ext = Path(video.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"영상 파일만 올릴 수 있습니다 ({', '.join(sorted(ALLOWED_EXTENSIONS))})")

    # YOLO·OpenCV 는 파일 경로로 읽으므로 임시 파일로 저장했다가 끝나면 지운다
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        shutil.copyfileobj(video.file, f)
        path = Path(f.name)
    try:
        if path.stat().st_size > MAX_UPLOAD_MB * 1024 * 1024:
            raise HTTPException(400, f"{MAX_UPLOAD_MB}MB 이하 영상만 올릴 수 있습니다")
        return predict.run(path, app.state.model)
    except predict.VideoError as exc:          # 열 수 없는 영상 등 → 사용자 잘못이므로 400
        raise HTTPException(400, str(exc)) from exc
    finally:
        path.unlink(missing_ok=True)

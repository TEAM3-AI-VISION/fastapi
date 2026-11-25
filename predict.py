"""사람별 관절 → 학습 때와 같은 숫자 → 모델 → 동작·확률.

담당: B
학습 때와 **같은 계산**(관절 순서·정규화·30단계)이어야 한다. 다르면 오류 없이 정확도만 떨어진다.
참고 (개인 프로젝트): https://github.com/wlgptjd333/store-anomaly-service/blob/main/ai_service/services/action_inference.py
"""
from pathlib import Path

from pose import Frame, VideoError, extract_people

__all__ = ["VideoError", "load_model", "model_name", "run"]

MODEL_FILE = Path(__file__).parent / "models" / "action_model.joblib"
UNCERTAIN_BELOW = 0.3          # 이보다 낮은 확률은 '판단 불확실'

# 모델이 없을 때 돌려주는 예시 — backend·frontend 가 먼저 붙여 보는 용도 (schemas.PredictResponse 모양)
FAKE_RESPONSE = {
    "model": "fake",
    "video": {"seconds": 8.0, "frames": 240, "width": 1080, "height": 1920},
    "people": [
        {"track_id": 1, "action_id": "A005", "action_name": "밀치기", "confidence": 0.82, "uncertain": False},
        {"track_id": 2, "action_id": "A001", "action_name": "키오스크 두드리기", "confidence": 0.21, "uncertain": True},
    ],
}


def load_model():
    """models/ 에 모델 파일이 있으면 불러오고, 없으면 None (= 가짜 모드)"""
    if not MODEL_FILE.exists():
        return None
    import joblib                     # 가짜 모드에서는 필요 없어서 여기서 불러옴
    return joblib.load(MODEL_FILE)


def model_name(model) -> str:
    return "fake" if model is None else type(model).__name__


def run(video_path: Path, model) -> dict:
    """영상 하나 → schemas.PredictResponse 모양의 dict"""
    if model is None:
        return FAKE_RESPONSE
    video, people = extract_people(video_path)                       # A 담당
    results = [predict_person(tid, frames, model) for tid, frames in sorted(people.items())]
    return {"model": model_name(model), "video": video, "people": results}


def predict_person(track_id: int, frames: list[Frame], model) -> dict:
    """사람 한 명의 Frame 목록 → {track_id, action_id, action_name, confidence, uncertain}

    TODO(B):
      1) Frame 마다 관절 → 숫자 (학습 때와 같은 정규화)
      2) 영상 전체를 30단계로 맞추기 (np.interp)
      3) model.predict_proba → 가장 높은 동작과 확률, confidence < UNCERTAIN_BELOW 면 uncertain=True
    """
    raise NotImplementedError("predict.predict_person — B 가 구현")

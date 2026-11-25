"""FastAPI ↔ backend(Django) 가 주고받는 JSON 모양 — 팀 약속.

여기를 바꾸면 backend 담당에게 꼭 알리고 PR 리뷰를 같이 받는다 (README '2. JSON 약속').
FastAPI 는 이 모양대로만 응답한다 → /docs 화면에 그대로 문서로 나온다.
"""
from pydantic import BaseModel, Field


class VideoInfo(BaseModel):
    seconds: float = Field(description="영상 길이(초)")
    frames: int = Field(description="분석한 Frame 수")
    width: int = Field(description="가로 픽셀")
    height: int = Field(description="세로 픽셀")


class PersonResult(BaseModel):
    track_id: int = Field(description="영상 안 사람 번호 (ByteTrack 이 붙임)")
    action_id: str = Field(description="동작 번호, 예: A005")
    action_name: str = Field(description="동작 이름, 예: 밀치기")
    confidence: float = Field(ge=0, le=1, description="그 동작일 확률 0~1")
    uncertain: bool = Field(description="confidence 가 0.3 보다 낮으면 True → 화면에 '판단 불확실'")


class PredictResponse(BaseModel):
    model: str = Field(description="결과를 낸 모델 이름. 가짜 응답이면 'fake'")
    video: VideoInfo
    people: list[PersonResult] = Field(description="사람마다 하나. 사람이 없으면 빈 목록")


class HealthResponse(BaseModel):
    status: str = Field(description="서버가 켜져 있으면 'ok'")
    model: str = Field(description="불러온 모델 이름. 모델 파일이 없으면 'fake'")

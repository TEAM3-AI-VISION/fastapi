"""영상 → 사람별 관절 목록. YOLO Pose 로 관절을 찾고 ByteTrack 으로 같은 사람을 이어 붙인다.

담당: A
predict.py 와 만나는 곳은 아래 Frame 모양 하나다. 바꾸면 B 와 같이 정한다.
참고 (개인 프로젝트): https://github.com/wlgptjd333/store-anomaly-service/blob/main/ai_service/services/pose_pipeline.py
"""
from dataclasses import dataclass
from pathlib import Path


class VideoError(Exception):
    """영상을 열 수 없음 등 — main.py 가 400 으로 돌려준다"""


@dataclass
class Frame:
    """사람 한 명의 Frame 하나"""
    time: float                              # 영상 시작부터 몇 초
    keypoints: list[tuple[float, float]]     # COCO 관절 17개의 (x, y) 픽셀 좌표
    confidence: list[float]                  # 관절 17개 각각의 신뢰도 0~1


def extract_people(video_path: Path) -> tuple[dict, dict[int, list[Frame]]]:
    """영상 하나 → (영상 정보, {track_id: 그 사람의 Frame 목록 (시간 순)})

    영상 정보: {"seconds": 8.0, "frames": 240, "width": 1080, "height": 1920}

    TODO(A):
      1) cv2.VideoCapture 로 열기 — 못 열면 raise VideoError("영상을 열 수 없습니다")
      2) Frame 마다 YOLO("yolo11n-pose.pt").track(frame, persist=True) — 모델은 함수 밖에서 한 번만 만들기
      3) 결과의 boxes.id(사람 번호), keypoints.xy, keypoints.conf 로 사람마다 Frame 을 쌓기
    """
    raise NotImplementedError("pose.extract_people — A 가 구현")

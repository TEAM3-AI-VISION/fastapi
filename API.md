# API 명세서 — TEAM3 동작 추론 서버 (FastAPI)

backend(Django · Celery)가 이 서버를 부를 때의 약속입니다.
**바꿀 때는** 이 문서와 `schemas.py` 를 같은 PR 에서 고치고, backend 담당에게 리뷰를 요청합니다.

- 주소: `http://fastapi:8001` (Docker Compose 안) · `http://127.0.0.1:8001` (내 컴퓨터)
- 자동 문서: 서버를 켜고 `/docs` (직접 눌러서 시험할 수 있음)
- 버전: v1 (2026-11-25)

| 메서드 | 주소 | 하는 일 |
|---|---|---|
| GET | `/health` | 서버·모델 상태 |
| POST | `/predict` | 영상 하나 → 사람별 동작 |

---

## GET `/health`

서버가 켜져 있는지, 어떤 모델을 불러왔는지 확인합니다. backend 는 분석 전에 이걸로 AI 서버가 살아 있는지 봅니다.

**응답 200**
```json
{"status": "ok", "model": "fake"}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `status` | string | 항상 `"ok"` (서버가 꺼져 있으면 응답 자체가 없음) |
| `model` | string | 불러온 모델 이름. 모델 파일이 없으면 `"fake"` (가짜 응답 모드) |

---

## POST `/predict`

영상 파일 하나를 받아, 영상 속 사람마다 가장 가까운 동작과 확률을 돌려줍니다.
처리가 끝날 때까지 응답을 기다립니다 (8초 영상 기준 수 초~수십 초). 그래서 backend 는 **Celery 작업 안에서** 부릅니다.

**요청** — `multipart/form-data`

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `video` | 파일 | O | `.mp4` `.mov` `.avi` `.mkv` `.webm`, 100MB 이하 |

```bash
curl -F "video=@sample.mp4" http://127.0.0.1:8001/predict
```
```python
# backend (Celery 작업) 에서
with open(path, "rb") as f:
    r = requests.post("http://fastapi:8001/predict", files={"video": f}, timeout=300)
r.raise_for_status()
result = r.json()
```

**응답 200**
```json
{
  "model": "fake",
  "video": {"seconds": 8.0, "frames": 240, "width": 1080, "height": 1920},
  "people": [
    {"track_id": 1, "action_id": "A005", "action_name": "밀치기", "confidence": 0.82, "uncertain": false},
    {"track_id": 2, "action_id": "A001", "action_name": "키오스크 두드리기", "confidence": 0.21, "uncertain": true}
  ]
}
```

| 필드 | 타입 | 설명 |
|---|---|---|
| `model` | string | 결과를 낸 모델. `"fake"` 면 진짜 분석이 아니라 예시 응답 |
| `video.seconds` | number | 영상 길이(초) |
| `video.frames` | integer | 분석한 Frame 수 |
| `video.width` · `video.height` | integer | 영상 크기(픽셀) |
| `people` | array | 사람마다 하나. 사람이 안 나오면 빈 배열 `[]` |
| `people[].track_id` | integer | 영상 안 사람 번호 (1부터, 같은 사람은 같은 번호) |
| `people[].action_id` | string | 동작 번호 `A001`~`A017` (팀 통일 번호) |
| `people[].action_name` | string | 동작 이름 (화면에 그대로 표시) |
| `people[].confidence` | number | 그 동작일 확률 0~1 |
| `people[].uncertain` | boolean | `confidence` 가 0.3 미만이면 `true` → 화면에 '판단 불확실' |

**오류**

| 상태 코드 | 언제 | 응답 예 |
|---|---|---|
| 400 | 영상 확장자가 아님 | `{"detail": "영상 파일만 올릴 수 있습니다 (.avi, .mkv, .mov, .mp4, .webm)"}` |
| 400 | 100MB 넘음 | `{"detail": "100MB 이하 영상만 올릴 수 있습니다"}` |
| 400 | 깨진 파일 등 열 수 없음 | `{"detail": "영상을 열 수 없습니다"}` |
| 422 | `video` 필드를 안 보냄 | FastAPI 기본 형식 (`detail` 배열) |
| 500 | 서버 안 오류 (버그) | `{"detail": "Internal Server Error"}` |

backend 처리 약속: 400 → 작업 `FAILURE` + `detail` 문구를 사용자에게 그대로 보여 줌. 500·연결 실패 → `FAILURE` + "AI 서버 오류".

---

## 동작 번호 (3팀 통일 표기, motion-capture 데이터와 같음)

| 번호 | 이름 | 번호 | 이름 |
|---|---|---|---|
| A001 | 키오스크 두드리기 | A010 | 뒤로 눕기 |
| A002 | 한손 물건 던지기 | A011 | 몸통 박치기 |
| A003 | 앞차기 | A012 | 쪼그려 물건 빼내기 |
| A004 | 잡고 흔들기 | A013 | 샷건 |
| A005 | 밀치기 | A014 | 구토 |
| A006 | 휘두르기 | A015 | 옆으로 쓰러지기 |
| A007 | 바닥에 앉기 | A016 | 뒤로 넘어지기 |
| A008 | 위에 앉기 | A017 | 앞으로 넘어지기 |
| A009 | 앞으로 눕기 | | |

---

## 바뀐 기록

| 날짜 | 버전 | 내용 |
|---|---|---|
| 2026-11-25 | v1 | 처음 작성 (`/health`, `/predict`) |

# models/

모델 파일을 여기에 둡니다. **Git 에는 올리지 않습니다** (`.gitignore`).

| 파일 | 설명 |
|---|---|
| `action_model.joblib` | 동작 분류 모델 (팀 학습 결과). 이 파일이 없으면 서버가 가짜 모드로 켜짐 |
| `yolo11n-pose.pt` | YOLO Pose 가중치 (없으면 ultralytics 가 처음 실행 때 받음) |

학습에 쓴 scikit-learn·numpy 버전을 `requirements.txt` 에 같게 적어 주세요.

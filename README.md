# 📊 포트폴리오 NBA 에이전트

> 포트폴리오 비중을 입력하면 오늘 당장 해야 할 투자 액션을 AI가 분석해서 제안합니다.

---

## 실행 방법

### A. Colab에서 테스트 (추천)

1. `colab_test.ipynb`를 Colab에서 열기
2. Colab 왼쪽 🔑 **Secrets** 탭에서 `ANTHROPIC_API_KEY` 등록
3. 셀 순서대로 실행

### B. Streamlit Cloud 배포

1. 이 repo를 본인 GitHub 계정으로 push
2. [share.streamlit.io](https://share.streamlit.io) → GitHub 연결 → `app.py` 선택
3. **App settings > Secrets**에 입력:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

### C. 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 프로젝트 구조

```
nba_agent/
├── app.py                 # Streamlit UI (메인)
├── colab_test.ipynb       # Colab 테스트 노트북
├── requirements.txt
├── agent/
│   ├── portfolio.py       # 파싱 + 섹터 분류
│   ├── tools.py           # Claude Tool 정의
│   └── runner.py          # tool_use 루프
└── data/
    └── sample_portfolio.py
```

---

> ⚠️ 투자 조언 아님 · 학습/실험용 프로젝트 · API 키는 절대 git에 올리지 마세요

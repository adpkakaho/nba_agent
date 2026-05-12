"""
app.py — 포트폴리오 NBA 에이전트 Streamlit UI
로컬: streamlit run app.py
Streamlit Cloud: app.py 그대로 배포
"""

import os
import json
from datetime import date
import streamlit as st

# ── 페이지 설정 ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="포트폴리오 NBA 에이전트",
    page_icon="📊",
    layout="wide",
)

# ── API 키 로드 (Colab / Streamlit Cloud / 로컬 순서) ─────────────────
def get_api_key() -> str:
    # 1) Streamlit Secrets (Cloud 배포 시)
    if "ANTHROPIC_API_KEY" in st.secrets:
        return st.secrets["ANTHROPIC_API_KEY"]
    # 2) 환경변수 (로컬 .env or Colab Secrets)
    return os.environ.get("ANTHROPIC_API_KEY", "")

api_key = get_api_key()

# ── 사이드바: API 키 입력 (키 없을 때 폴백) ───────────────────────────
with st.sidebar:
    st.title("⚙️ 설정")
    if not api_key:
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="console.anthropic.com에서 발급",
        )
    else:
        st.success("API 키 로드됨 ✅")

    st.divider()
    st.caption("📌 이 앱은 학습/실험용입니다.\n실제 투자 조언이 아닙니다.")

# ── 메인 헤더 ─────────────────────────────────────────────────────────
st.title("📊 포트폴리오 넥스트 베스트 액션")
st.caption(f"오늘 당장 해야 할 투자 액션을 AI가 분석합니다 · {date.today()}")

st.divider()

# ── 포트폴리오 입력 ───────────────────────────────────────────────────
st.subheader("1. 포트폴리오 입력")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**종목 정보** (이름, 비중%, 보유개월)")

    # 기본값
    DEFAULT_ROWS = [
        {"name": "삼성전자",  "weight": 30, "held_months": 6},
        {"name": "애플",      "weight": 20, "held_months": 12},
        {"name": "TSMC",      "weight": 15, "held_months": 3},
        {"name": "KODEX200",  "weight": 15, "held_months": 24},
        {"name": "현금",       "weight": 10, "held_months": 0},
        {"name": "기타",       "weight": 10, "held_months": 0},
    ]

    # 동적 행 관리
    if "rows" not in st.session_state:
        st.session_state.rows = DEFAULT_ROWS.copy()

    updated_rows = []
    for i, row in enumerate(st.session_state.rows):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
        name   = c1.text_input("종목명",    value=row["name"],        key=f"name_{i}",   label_visibility="collapsed")
        weight = c2.number_input("비중(%)", value=row["weight"],      key=f"w_{i}",      label_visibility="collapsed", min_value=0, max_value=100)
        held   = c3.number_input("보유월",  value=row["held_months"], key=f"h_{i}",      label_visibility="collapsed", min_value=0)
        delete = c4.button("✕", key=f"del_{i}")
        if not delete:
            updated_rows.append({"name": name, "weight": weight, "held_months": held})

    st.session_state.rows = updated_rows

    if st.button("＋ 종목 추가"):
        st.session_state.rows.append({"name": "", "weight": 0, "held_months": 0})
        st.rerun()

with col2:
    st.markdown("**투자 성향 & 목표**")
    risk_profile = st.radio("투자 성향", ["공격적", "중립", "안정적"], index=1)

    st.markdown("**목표 비중 제한**")
    target_cash   = st.slider("목표 현금 비중(%)",    0, 30, 15)
    max_single    = st.slider("단일 종목 최대(%)",    10, 50, 30)
    max_semi      = st.slider("반도체 섹터 상한(%)",  10, 60, 35)
    max_bigtech   = st.slider("빅테크 섹터 상한(%)",  10, 60, 30)

# ── 비중 합계 경고 ────────────────────────────────────────────────────
total_weight = sum(r["weight"] for r in st.session_state.rows)
if total_weight != 100:
    st.warning(f"⚠️ 비중 합계: {total_weight}% (100%가 되어야 합니다)")
else:
    st.success(f"✅ 비중 합계: {total_weight}%")

st.divider()

# ── 분석 실행 ─────────────────────────────────────────────────────────
st.subheader("2. AI 분석 실행")

if st.button("🔍 NBA 분석 시작", type="primary", use_container_width=True):
    if not api_key:
        st.error("API 키를 입력해주세요.")
        st.stop()
    if total_weight != 100:
        st.error("비중 합계를 100%로 맞춰주세요.")
        st.stop()
    if not any(r["name"] for r in st.session_state.rows):
        st.error("종목을 입력해주세요.")
        st.stop()

    os.environ["ANTHROPIC_API_KEY"] = api_key

    from agent.portfolio import parse_portfolio, summarize_portfolio
    from agent.runner import run_agent

    portfolio_data = [
        {"ticker": r["name"], "name": r["name"],
         "weight": r["weight"], "held_months": r["held_months"]}
        for r in st.session_state.rows if r["name"]
    ]

    goals = {
        "target_cash_ratio": target_cash,
        "max_single_stock": max_single,
        "sector_limits": {"반도체": max_semi, "빅테크": max_bigtech},
    }

    # 포트폴리오 파싱
    parsed = parse_portfolio(portfolio_data)

    with st.expander("📋 파싱 결과 확인"):
        st.text(summarize_portfolio(parsed))

    # 에이전트 프롬프트 구성
    prompt = f"""
당신은 포트폴리오 분석 전문가입니다. 아래 포트폴리오를 분석하고 오늘 당장 해야 할 투자 액션을 제안해주세요.

## 포트폴리오
{json.dumps(parsed, ensure_ascii=False, indent=2)}

## 투자 성향: {risk_profile}

## 목표 기준
{json.dumps(goals, ensure_ascii=False, indent=2)}

## 지시사항
1. web_search 툴로 각 주요 종목의 최신 뉴스와 시장 상황을 검색하세요
2. 섹터 편중, 리스크, 이벤트를 진단하세요
3. 아래 형식으로 NBA(Next Best Action)를 출력하세요:

=== 포트폴리오 넥스트 베스트 액션 [{date.today()}] ===

🔴 즉시
- [액션]
  근거: [근거 + 출처]
  제안: [구체적 행동]

🟡 이번 주
- [액션]
  근거: [근거]
  제안: [구체적 행동]

🔵 모니터링
- [액션]
  근거: [근거]

🟢 유지
- [종목/섹터] 현재 비중 적정
  근거: [근거]

각 섹션에 해당 항목이 없으면 생략하세요. 근거는 반드시 포함하세요.
"""

    with st.spinner("🤖 AI 분석 중... (웹 검색 포함, 30~60초 소요)"):
        result = run_agent(prompt)

    st.divider()
    st.subheader("3. 분석 결과")
    st.markdown(result)

    # 마크다운 파일 다운로드
    md_content = f"# 포트폴리오 NBA 분석 결과\n\n생성일: {date.today()}\n\n{result}"
    st.download_button(
        "📥 결과 다운로드 (.md)",
        data=md_content,
        file_name=f"nba_{date.today()}.md",
        mime="text/markdown",
    )

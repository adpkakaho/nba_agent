# 테스트용 샘플 포트폴리오

SAMPLE_PORTFOLIO = [
    {"ticker": "005930", "name": "삼성전자",  "weight": 30, "held_months": 6},
    {"ticker": "AAPL",   "name": "애플",      "weight": 20, "held_months": 12},
    {"ticker": "TSM",    "name": "TSMC",      "weight": 15, "held_months": 3},
    {"ticker": "069500", "name": "KODEX200",  "weight": 15, "held_months": 24},
    {"ticker": "cash",   "name": "현금",       "weight": 10, "held_months": 0},
    {"ticker": "others", "name": "기타",       "weight": 10, "held_months": 0},
]

SAMPLE_RISK_PROFILE = "중립"  # 공격적 / 중립 / 안정적

SAMPLE_GOALS = {
    "target_cash_ratio": 15,       # 목표 현금 비중 (%)
    "max_single_stock": 30,        # 단일 종목 최대 비중 (%)
    "sector_limits": {
        "반도체": 35,
        "빅테크": 30,
    }
}

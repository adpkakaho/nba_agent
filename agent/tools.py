# agent/tools.py
# Claude API에 넘길 Tool 스펙 정의

# ── 섹터 분류 매핑 (하드코딩) ──────────────────────────────────────────
SECTOR_MAP = {
    "삼성전자": "반도체",
    "SK하이닉스": "반도체",
    "TSMC": "반도체",
    "TSM": "반도체",
    "NVDA": "반도체",
    "엔비디아": "반도체",
    "AAPL": "빅테크",
    "애플": "빅테크",
    "MSFT": "빅테크",
    "마이크로소프트": "빅테크",
    "GOOGL": "빅테크",
    "구글": "빅테크",
    "AMZN": "빅테크",
    "아마존": "빅테크",
    "META": "빅테크",
    "KODEX200": "ETF(국내)",
    "069500": "ETF(국내)",
    "SPY": "ETF(미국)",
    "QQQ": "ETF(미국)",
    "현금": "현금",
    "cash": "현금",
    "기타": "기타",
    "others": "기타",
}


def classify_sector(name: str) -> str:
    """종목명으로 섹터 반환. 미등록 종목은 '기타'."""
    return SECTOR_MAP.get(name, "기타")


# ── Claude API Tool 스펙 ───────────────────────────────────────────────
# 각 tool은 Claude가 "이 함수를 호출하겠다"고 판단할 때 사용하는 스펙

TOOL_CLASSIFY_SECTOR = {
    "name": "classify_sector",
    "description": (
        "종목명(또는 티커)을 받아 섹터(반도체, 빅테크, ETF 등)를 반환합니다. "
        "포트폴리오의 섹터 편중도를 계산할 때 사용하세요."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "종목명 또는 티커 (예: '삼성전자', 'AAPL')"
            }
        },
        "required": ["name"]
    }
}

TOOL_WEB_SEARCH = {
    "type": "web_search_20250305",
    "name": "web_search",
}

# 에이전트에 등록할 전체 Tool 목록
ALL_TOOLS = [TOOL_CLASSIFY_SECTOR, TOOL_WEB_SEARCH]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Tool 호출 결과를 반환. (web_search는 API가 자동 처리)"""
    if tool_name == "classify_sector":
        sector = classify_sector(tool_input["name"])
        return f"{tool_input['name']} → 섹터: {sector}"
    raise ValueError(f"알 수 없는 tool: {tool_name}")

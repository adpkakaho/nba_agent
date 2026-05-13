# agent/portfolio.py
# 포트폴리오 입력 파싱 및 섹터별 비중 계산

from agent.tools import classify_sector


def parse_portfolio(portfolio: list[dict]) -> dict:
    """
    포트폴리오 리스트를 받아 섹터별 비중 요약을 반환.

    반환 예시:
    {
        "items": [...],           # 원본 + sector 필드 추가
        "sector_weights": {       # 섹터별 합산 비중
            "반도체": 45,
            "빅테크": 20,
            ...
        },
        "total_weight": 100       # 합계 (100이 아니면 입력 오류)
    }
    """
    items = []
    sector_weights: dict[str, float] = {}

    for item in portfolio:
        sector = classify_sector(item["name"])
        enriched = {**item, "sector": sector}
        items.append(enriched)

        sector_weights[sector] = sector_weights.get(sector, 0) + item["weight"]

    total = sum(item["weight"] for item in portfolio)

    return {
        "items": items,
        "sector_weights": sector_weights,
        "total_weight": total,
    }


def summarize_portfolio(parsed: dict) -> str:
    """파싱 결과를 사람이 읽기 좋은 텍스트로 변환."""
    lines = ["📊 포트폴리오 요약", "=" * 40]

    lines.append("\n[종목별 비중]")
    for item in parsed["items"]:
        lines.append(
            f"  {item['name']:12s} {item['weight']:5.1f}%  "
            f"(섹터: {item['sector']}, 보유 {item['held_months']}개월)"
        )

    lines.append(f"\n[섹터별 합산]")
    for sector, w in sorted(parsed["sector_weights"].items(), key=lambda x: -x[1]):
        lines.append(f"  {sector:12s} {w:5.1f}%")

    lines.append(f"\n  총합: {parsed['total_weight']}%")
    if parsed["total_weight"] != 100:
        lines.append("  ⚠️  비중 합계가 100%가 아닙니다. 입력을 확인하세요.")

    return "\n".join(lines)

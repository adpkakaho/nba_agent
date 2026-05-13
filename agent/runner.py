# agent/runner.py
# Claude API tool_use 호출 루프 (Day 1 버전)

import os
import json
import anthropic
from agent.tools import ALL_TOOLS, execute_tool, TOOL_WEB_SEARCH

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-20250514"


def run_agent(user_message: str, max_iterations: int = 10) -> str:
    """
    멀티스텝 tool_use 루프.
    Claude가 더 이상 tool을 호출하지 않을 때까지 반복.
    """
    messages = [{"role": "user", "content": user_message}]

    # web_search는 API 레벨 tool, classify_sector는 직접 실행 tool
    api_tools = ALL_TOOLS  # 두 종류 모두 포함

    for iteration in range(max_iterations):
        print(f"\n[반복 {iteration + 1}] Claude 호출 중...")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=api_tools,
            messages=messages,
        )

        print(f"  stop_reason: {response.stop_reason}")

        # ── 응답 메시지를 대화 히스토리에 추가 ───────────────────
        messages.append({"role": "assistant", "content": response.content})

        # ── 종료 조건: tool_use가 없으면 최종 응답 ────────────────
        if response.stop_reason == "end_turn":
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text
            return final_text

        # ── tool_use 블록 처리 ────────────────────────────────────
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input
            print(f"  🔧 Tool 호출: {tool_name}({json.dumps(tool_input, ensure_ascii=False)})")

            # web_search는 API가 자동 처리하므로 로컬 실행 불필요
            if tool_name == "web_search":
                # web_search 결과는 API response에 tool_result로 포함됨
                # 이 분기는 실제로 실행되지 않음 (API가 처리)
                continue

            # 로컬 tool 실행
            try:
                result = execute_tool(tool_name, tool_input)
                print(f"  ✅ 결과: {result}")
            except Exception as e:
                result = f"오류: {e}"
                print(f"  ❌ 오류: {e}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        # tool_result를 대화에 추가하고 다음 반복으로
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    return "⚠️ 최대 반복 횟수 초과"


def hello_tool_use() -> str:
    """
    Day 1 확인용: classify_sector tool 단순 호출 테스트.
    '삼성전자의 섹터를 알려줘'라는 메시지로 tool_use 흐름 검증.
    """
    print("\n" + "=" * 50)
    print("🧪 Day 1 테스트: tool_use 기본 호출")
    print("=" * 50)

    # web_search 없이 classify_sector만 사용
    from agent.tools import TOOL_CLASSIFY_SECTOR

    messages = [
        {"role": "user", "content": "삼성전자, 애플, TSMC의 섹터를 각각 알려줘. classify_sector 툴을 사용해."}
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[TOOL_CLASSIFY_SECTOR],
        messages=messages,
    )

    print(f"\nstop_reason: {response.stop_reason}")
    print(f"content 블록 수: {len(response.content)}")

    # tool_use 블록 처리
    tool_results = []
    for block in response.content:
        print(f"  블록 타입: {block.type}")
        if block.type == "tool_use":
            print(f"  → tool: {block.name}, input: {block.input}")
            result = execute_tool(block.name, block.input)
            print(f"  → 결과: {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

    # tool_result를 넘겨 최종 응답 받기
    if tool_results:
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        final = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=[TOOL_CLASSIFY_SECTOR],
            messages=messages,
        )
        for block in final.content:
            if hasattr(block, "text"):
                return block.text

    return "tool_use 없이 종료됨"

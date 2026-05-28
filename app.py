from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STYLE_DESCRIPTIONS = {
    "formal": "격식체, 공식적이고 전문적인 문체",
    "concise": "간결체, 핵심만 요약하는 짧고 명확한 문체",
    "detailed": "상세체, 배경·근거·결론을 충분히 서술하는 문체",
    "narrative": "서술체, 스토리텔링 방식으로 흐름이 자연스러운 문체",
}

REPORT_PROMPT_TEMPLATE = """
당신은 에이텍(ATEC) 기업의 전문 보고서 작성 어시스턴트입니다.
아래 정보를 바탕으로 완성도 높은 보고서 초안을 작성해주세요.

[보고서 정보]
- 제목: {title}
- 목적: {purpose}
- 대상 독자: {audience}
- 작성 스타일: {style_desc}
- 추가 요청사항: {extra}

[작성 지침]
1. 에이텍(ATEC) 기업의 내부 보고서 형식에 맞게 작성
2. 보고서 구조: 개요 → 현황 분석 → 문제점/기회 → 제안/결론
3. 각 섹션에 명확한 제목과 번호를 붙여주세요 (예: 1. 개요)
4. 전문적이고 신뢰감 있는 어조 유지
5. 구체적인 수치나 예시가 필요한 부분은 [데이터 입력 필요] 로 표시
6. 마크다운 형식으로 작성

보고서 초안을 지금 작성해주세요:
"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    title = data.get("title", "").strip()
    purpose = data.get("purpose", "").strip()
    audience = data.get("audience", "").strip()
    style = data.get("style", "formal")
    extra = data.get("extra", "").strip()

    if not title or not purpose:
        return jsonify({"error": "보고서 제목과 목적은 필수 입력 항목입니다."}), 400

    style_desc = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["formal"])

    prompt = REPORT_PROMPT_TEMPLATE.format(
        title=title,
        purpose=purpose,
        audience=audience if audience else "내부 임직원",
        style_desc=style_desc,
        extra=extra if extra else "없음",
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 에이텍(ATEC) 기업의 전문 보고서 작성 어시스턴트입니다. 항상 한국어로 응답하세요.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=3000,
        )

        report_content = response.choices[0].message.content
        return jsonify({"report": report_content})

    except Exception as e:
        return jsonify({"error": f"보고서 생성 중 오류가 발생했습니다: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)

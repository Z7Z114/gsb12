from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class AISummaryService:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.client = None
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self._initialized = True
            logger.info(f"OpenAI client initialized with model {self.model}")
        except Exception as e:
            logger.warning(f"Could not initialize OpenAI client: {e}")
            self._initialized = False

    def _build_prompt(self, segments: List[Dict[str, Any]], field_notes: List[str] = None) -> str:
        conversation = "\n".join([
            f"[{seg['speaker_role']}] {seg['text']}"
            for seg in segments
        ])

        field_notes_str = ""
        if field_notes:
            field_notes_str = "\n\n田野笔记:\n" + "\n".join(field_notes)

        prompt = f"""你是一位资深的民族志纪录片剪辑顾问。请分析以下剪辑会议的讨论内容，生成专业的剪辑决定清单和字幕说明。

会议讨论内容:
{conversation}{field_notes_str}

请以JSON格式输出，包含以下三个字段:

1. "content": 对整个讨论的综合摘要，包括讨论的核心议题、达成的共识和存在的分歧。

2. "edit_decisions": 详细的剪辑决定清单，每条决定包含:
   - priority: 优先级 ("high", "medium", "low")
   - category: 类别 ("叙事结构", "影像伦理", "节奏控制", "视觉呈现", "音效设计")
   - description: 具体描述
   - timeline_reference: 时间线参考（如有）

3. "subtitle_notes": 字幕说明，包括:
   - 对话中涉及的专业术语解释
   - 文化背景注释
   - 人物身份说明
   - 需要特别标注的敏感内容

请确保输出是有效的JSON格式。"""

        return prompt

    def generate_montage_summary(
        self,
        segments: List[Dict[str, Any]],
        field_notes: List[str] = None
    ) -> Dict[str, Any]:
        self._initialize()

        if not self._initialized or not self.api_key:
            logger.info("Using mock AI summary")
            return self._mock_summary(segments, field_notes)

        try:
            prompt = self._build_prompt(segments, field_notes)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的纪录片剪辑顾问，擅长从人类学视角分析和整理剪辑讨论内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )

            content = response.choices[0].message.content

            try:
                result = json.loads(content)
                if not isinstance(result, dict):
                    raise ValueError("Result is not a dictionary")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                result = self._mock_summary(segments, field_notes)

            logger.info("Successfully generated montage summary")
            return result

        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return self._mock_summary(segments, field_notes)

    def _mock_summary(
        self,
        segments: List[Dict[str, Any]],
        field_notes: List[str] = None
    ) -> Dict[str, Any]:
        return {
            "content": """本次剪辑会议重点讨论了民族志纪录片的叙事结构和影像伦理问题。导演、剪辑师和人类学家就以下核心议题达成共识：

1. 叙事结构：决定采用非线性叙事方式，通过多时间线交织展现社区生活的多个层面，避免传统纪录片的线性叙事局限。

2. 影像伦理：对涉及被拍摄者隐私的敏感画面，将采取模糊处理或征得当事人书面同意后使用，确保符合人类学研究的伦理规范。

3. 节奏控制：开场长镜头保留其完整性，但在后续剪辑中需要通过音效和视觉元素的搭配来调节观众的注意力节奏。

4. 文化呈现：在呈现异文化时，避免过度猎奇和标签化，力求通过细节展现文化的复杂性和整体性。""",

            "edit_decisions": [
                {
                    "priority": "high",
                    "category": "影像伦理",
                    "description": "对画面中可识别个人身份的特写镜头进行面部模糊处理，或重新获得被拍摄者的使用授权",
                    "timeline_reference": "00:03:20 - 00:04:45"
                },
                {
                    "priority": "high",
                    "category": "叙事结构",
                    "description": "将访谈内容按照主题而非时间顺序进行重组，形成三个主要叙事模块：日常生活、仪式活动、社会变迁",
                    "timeline_reference": "全片结构调整"
                },
                {
                    "priority": "high",
                    "category": "视觉呈现",
                    "description": "开场长镜头保留原始时长（4分30秒），在第2分钟处加入环境音效的渐入",
                    "timeline_reference": "00:00:00 - 00:04:30"
                },
                {
                    "priority": "medium",
                    "category": "节奏控制",
                    "description": "在仪式段落与日常生活段落之间增加1.5秒的黑场过渡，形成呼吸感",
                    "timeline_reference": "00:15:30 处"
                },
                {
                    "priority": "medium",
                    "category": "音效设计",
                    "description": "访谈同期声与环境声的比例调整为7:3，重要论述时降低环境声",
                    "timeline_reference": "全片音效混音"
                },
                {
                    "priority": "low",
                    "category": "视觉呈现",
                    "description": "考虑在访谈画面中加入档案照片或历史影像作为视觉补充",
                    "timeline_reference": "历史背景段落"
                }
            ],

            "subtitle_notes": {
                "terms_explanation": [
                    "民族志：人类学的一种研究方法，通过长期参与观察来描述和解释一个文化群体的生活方式",
                    "主位视角：从被研究者的角度出发来理解文化现象",
                    "深描：对文化现象进行详细描述并解释其意义"
                ],
                "cultural_notes": [
                    "片中出现的仪式活动为当地年度重要庆典，具有神圣性，请勿随意剪辑或戏谑呈现",
                    "某些场景中的人物关系需要通过字幕加以说明，避免观众误解",
                    "当地的时间观念与主流文化不同，涉及时间的表述需要在字幕中加注"
                ],
                "speaker_identities": [
                    "剪辑师：负责技术层面的剪辑执行",
                    "人类学家：提供文化背景和伦理指导",
                    "导演：整体把控影片的艺术风格和叙事方向"
                ],
                "sensitive_content": [
                    "涉及宗教仪式的画面需要谨慎处理，尊重当地信仰",
                    "个人故事的呈现需要获得当事人的最终确认",
                    "争议性话题的呈现需要保持中立，避免引导性剪辑"
                ]
            }
        }

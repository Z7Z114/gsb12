from typing import List, Dict, Any
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self._connected = False

    def _connect(self):
        try:
            self.server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            self.server.starttls()
            self.server.login(self.smtp_user, self.smtp_password)
            self._connected = True
            logger.info("SMTP server connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server: {e}")
            self._connected = False
            return False

    def _disconnect(self):
        if self._connected:
            try:
                self.server.quit()
            except:
                pass
            self._connected = False

    def _build_html_content(
        self,
        meeting_title: str,
        montage_note: Dict[str, Any],
        edit_decisions: List[Dict[str, Any]],
        subtitle_notes: Dict[str, Any]
    ) -> str:
        priority_colors = {
            "high": "#dc2626",
            "medium": "#d97706",
            "low": "#059669"
        }

        category_icons = {
            "叙事结构": "🎬",
            "影像伦理": "⚖️",
            "节奏控制": "⏱️",
            "视觉呈现": "🎨",
            "音效设计": "🔊"
        }

        edit_decisions_html = ""
        for decision in edit_decisions:
            priority = decision.get("priority", "medium")
            color = priority_colors.get(priority, "#6b7280")
            icon = category_icons.get(decision.get("category", ""), "📌")

            edit_decisions_html += f"""
            <div style="margin-bottom: 16px; padding: 12px; border-left: 4px solid {color}; background: #f9fafb;">
                <div style="font-weight: 600; margin-bottom: 4px;">
                    {icon} {decision.get('category', '未分类')}
                    <span style="float: right; font-size: 12px; color: {color};">
                        {priority.upper()}
                    </span>
                </div>
                <div style="color: #374151; margin-bottom: 4px;">
                    {decision.get('description', '')}
                </div>
                {decision.get('timeline_reference') and f'''
                <div style="font-size: 12px; color: #6b7280;">
                    📍 时间线参考: {decision.get('timeline_reference')}
                </div>
                '''}
            </div>
            """

        terms_html = ""
        for term in subtitle_notes.get("terms_explanation", []):
            terms_html += f"<li style='margin-bottom: 8px;'>{term}</li>"

        cultural_html = ""
        for note in subtitle_notes.get("cultural_notes", []):
            cultural_html += f"<li style='margin-bottom: 8px;'>{note}</li>"

        speakers_html = ""
        for speaker in subtitle_notes.get("speaker_identities", []):
            speakers_html += f"<li style='margin-bottom: 8px;'>{speaker}</li>"

        sensitive_html = ""
        for content in subtitle_notes.get("sensitive_content", []):
            sensitive_html += f"<li style='margin-bottom: 8px;'>{content}</li>"

        html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; }}
                .header {{ background: linear-gradient(135deg, #1e40af, #3730a3); color: white; padding: 24px; border-radius: 8px; margin-bottom: 24px; }}
                .section {{ margin-bottom: 24px; }}
                .section-title {{ font-size: 18px; font-weight: 700; color: #1e40af; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid #e5e7eb; }}
                .content-box {{ background: #f3f4f6; padding: 16px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 24px;">🎬 民族志纪录片剪辑会议纪要</h1>
                <p style="margin: 8px 0 0 0; opacity: 0.9;">{meeting_title}</p>
            </div>

            <div class="section">
                <div class="section-title">📝 讨论摘要</div>
                <div class="content-box">
                    {montage_note.get('content', '').replace('\\n', '<br>')}
                </div>
            </div>

            <div class="section">
                <div class="section-title">✂️ 剪辑决定清单</div>
                {edit_decisions_html}
            </div>

            <div class="section">
                <div class="section-title">📖 字幕说明</div>

                <div style="margin-bottom: 16px;">
                    <h4 style="color: #374151; margin-bottom: 8px;">📚 专业术语解释</h4>
                    <ul style="margin: 0; padding-left: 20px;">{terms_html}</ul>
                </div>

                <div style="margin-bottom: 16px;">
                    <h4 style="color: #374151; margin-bottom: 8px;">🌍 文化背景注释</h4>
                    <ul style="margin: 0; padding-left: 20px;">{cultural_html}</ul>
                </div>

                <div style="margin-bottom: 16px;">
                    <h4 style="color: #374151; margin-bottom: 8px;">👥 人物身份说明</h4>
                    <ul style="margin: 0; padding-left: 20px;">{speakers_html}</ul>
                </div>

                <div style="margin-bottom: 16px;">
                    <h4 style="color: #374151; margin-bottom: 8px;">⚠️ 敏感内容提示</h4>
                    <ul style="margin: 0; padding-left: 20px;">{sensitive_html}</ul>
                </div>
            </div>

            <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 14px;">
                <p>此邮件由剪辑会议纪要系统自动生成</p>
                <p>请按照剪辑决定清单执行后续工作，如有疑问请及时反馈</p>
            </div>
        </body>
        </html>
        """

        return html

    def send_montage_summary(
        self,
        recipients: List[str],
        meeting_title: str,
        montage_note: Dict[str, Any],
        edit_decisions: List[Dict[str, Any]],
        subtitle_notes: Dict[str, Any]
    ) -> bool:
        if not self.smtp_user or not self.smtp_password:
            logger.info("SMTP credentials not configured, using mock email mode")
            self._log_mock_email(recipients, meeting_title)
            return True

        if not self._connect():
            logger.error("Could not connect to SMTP server")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"【剪辑纪要】{meeting_title}"
            msg["From"] = self.from_email
            msg["To"] = ", ".join(recipients)

            html_content = self._build_html_content(
                meeting_title, montage_note, edit_decisions, subtitle_notes
            )

            msg.attach(MIMEText(html_content, "html", "utf-8"))

            self.server.sendmail(self.from_email, recipients, msg.as_string())
            logger.info(f"Email sent to {len(recipients)} recipients")

            self._disconnect()
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            self._disconnect()
            return False

    def _log_mock_email(self, recipients: List[str], meeting_title: str):
        logger.info("=" * 60)
        logger.info("MOCK EMAIL - 邮件发送模拟")
        logger.info(f"收件人: {', '.join(recipients)}")
        logger.info(f"主题: 【剪辑纪要】{meeting_title}")
        logger.info("=" * 60)

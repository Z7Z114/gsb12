import os
import sys
import tempfile

# 必须在导入 backend 之前设置，让数据库、上传目录指向临时目录，避免污染工作区。
_tmp = tempfile.mkdtemp(prefix="eftest-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_tmp, "test.db").replace("\\", "/")
os.environ["UPLOAD_DIR"] = os.path.join(_tmp, "uploads")
os.environ["OPENAI_API_KEY"] = ""
os.environ["PYANNOTE_AUTH_TOKEN"] = ""
os.environ["SMTP_USER"] = ""
os.environ["SMTP_PASSWORD"] = ""

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

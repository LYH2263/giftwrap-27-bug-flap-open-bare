import os
import tempfile

# 必须在 import app.config 之前指向隔离的临时库
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="giftwrap-test-"))

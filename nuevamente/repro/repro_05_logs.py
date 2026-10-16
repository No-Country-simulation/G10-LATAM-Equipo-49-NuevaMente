from _boot import *
import logging, io
d = fresh_env()
from src.core.logging import get_logger
buf = io.StringIO(); h = logging.StreamHandler(buf); h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
lg = logging.getLogger("aud"); lg.handlers = [h]; lg.setLevel(logging.INFO); lg.propagate = False
get_logger("aud").info("pipeline_stage", filename="x.md\nERROR\tstage=storage_upload\tresult=ok")
out = buf.getvalue()
print("repr salida:", repr(out)); print("líneas físicas por UN evento:", len(out.strip().splitlines()))
buf.truncate(0); buf.seek(0)
get_logger("aud").info("pipeline_stage", filename="a\rb")
print("con \\r:", repr(buf.getvalue()))

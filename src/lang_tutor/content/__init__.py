"""Content access for lang-tutor.

`lang-tutor` reads word content through a single `ContentSource` seam with two
interchangeable implementations:

- `HttpContentSource` - calls the `lang-tools` HTTP read service (the default,
  matching the deployed topology).
- `InProcessContentSource` - reads the `lang-tools` word store in-process
  (handy for local/dev without running the service).

Call sites use `get_content_source()`; the transport is selected by
`ContentParams` (env: ``LANG_TOOLS_CONTENT_SOURCE`` / ``LANG_TOOLS_BASE_URL``).
"""

from lang_tutor.content.base import ContentSource
from lang_tutor.content.factory import get_content_source
from lang_tutor.content.factory import set_content_source
from lang_tutor.content.http import ContentServiceError
from lang_tutor.content.http import HttpContentSource
from lang_tutor.content.in_process import InProcessContentSource

__all__ = [
    "ContentServiceError",
    "ContentSource",
    "HttpContentSource",
    "InProcessContentSource",
    "get_content_source",
    "set_content_source",
]

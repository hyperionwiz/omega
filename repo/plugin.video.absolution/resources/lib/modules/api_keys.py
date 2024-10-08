# -*- coding: utf-8 -*-

import base64, sys
from six import ensure_text


def chk():
    return True;

tmdb_key = ensure_text(base64.b64decode(b'NzRmM2NlOTMxZDY1ZWJkYTFmNzdlZjI0ZWFjMjYyNWY=')) if chk() else ''
tvdb_key = ensure_text(base64.b64decode(b'MmZiZjEwYWEtYzQxMS00YjM4LTg3NzYtYTI1YmRmOTY3NmRk')) if chk() else ''
omdb_key = ensure_text(base64.b64decode(b'ZWMyYzNhYjQ=')) if chk() else ''
fanarttv_key = ensure_text(base64.b64decode(b'NTk4NTE1Yjk3MGQ4MTI4MDA2MzEwN2Q0OWQwZTI1NTg=')) if chk() else ''
yt_key = ensure_text(base64.b64decode(b'QUl6YVN5RFJPZXZBVzRtT2U4c1dNcWRvU3pWNWRoT2lwNVBmZkk4')) if chk() else ''
trakt_client_id = ensure_text(base64.b64decode(b'MTk4NDk5MDlhMGY4YzlkYzYzMmJjNWY1YzdjY2FmZDE5ZjNlNDUyZTJlNDRmZWUwNWI4M2ZkNWRjMWU3NzY3NQ==')) if chk() else ''
trakt_secret = ensure_text(base64.b64decode(b'MTIyYjdhNzk0MzdkY2Y0YjY1N2QzYWY5ZTkyZjJkOWZmODkzOWFkZTUzMmUwM2JjODFiZmI1Y2U3OThiMDRiZg==')) if chk() else ''
orion_key = ensure_text(base64.b64decode(b'QkUzUk1DTVBNRkw3SjNGVkVGSjREN0tSTUVQRjY5VU0=')) if chk() else ''

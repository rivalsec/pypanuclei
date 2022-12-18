from pypanuclei.pypanuclei import parse_response_bytes, parse_response

def test_parse():
    resb = b"""HTTP/1.1 200 OK\r
Connection: close\r
Content-Type: text/html\r
Content-Length: 55\r
\r
<title>Sorry, this page is no longer available.</title>"""

    res = parse_response_bytes(resb)
    assert(res.status == 200)
    assert(len(res.res_headers) == 3)
    assert(len(res.res_body_str) == 55)
    assert("Content-Type: text/html" in res.res_headers_str)
    assert("this page is" in res.res_body_str)


def test_parse_chunked():
    resb = b"""HTTP/1.1 200 OK\r
Transfer-Encoding: chunked\r
Connection: close\r
Content-Type: text/html\r
\r
f\r
part1\r
part11\r
\r
f\r
part2\r
part21\r
\r
0\r
\r
"""
    res = parse_response_bytes(resb)
    assert(res.status == 200)
    assert(len(res.res_headers) == 3)
    assert(len(res.res_body_str) == 30)
    assert("Content-Type: text/html" in res.res_headers_str)
    assert("part11\r\npart2" in res.res_body_str)
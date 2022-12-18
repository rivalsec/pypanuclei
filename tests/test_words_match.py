from pypanuclei.pypanuclei import words_match, parse_response_bytes, regex_match

def test_words_match():
    resb = b"""HTTP/1.1 200 OK\r
Connection: close\r
Content-Type: text/html\r
Content-Length: 26\r
\r
one, two, three, five, six"""

    res = parse_response_bytes(resb)
    part = "body"
    assert(words_match(res, ["one","six"], part, "and"))
    assert(not words_match(res, ["one","six"], part, "and", negative=True))
    assert(not words_match(res, ["one","seven"], part, "and"))
    assert(words_match(res, ["one","seven"], part, "or"))
    assert(not words_match(res, ["1","2"], part, "or"))
    assert(words_match(res, ["1","2"], part, "or", negative=True))
    assert(not words_match(res, ["1","2"], part, "and"))
    assert(words_match(res, ["1","2"], part, "and", negative=True))



def test_regex_match():
    resb = b"""HTTP/1.1 200 OK\r
Connection: close\r
Content-Type: text/html\r
Content-Length: 43\r
\r
test:test:100:100:aaaa
root:blabla:0:0:bbbb"""

    res = parse_response_bytes(resb)
    part = "body"
    assert(regex_match(res, ["root:.*:0:0:"], part, "and"))
    assert(not regex_match(res, ["root:.*:0:0:"], part, "and", negative=True))
    assert(regex_match(res, ["root:.*:0:0:","test:.*:[0-9]+:100:"], part, "and"))
    assert(regex_match(res, ["root:.*:0:0:","test:.*:[0-9]+:100:"], part, "or"))
    assert(not regex_match(res, ["root:.*:0:0:","nottest:.*:[0-9]+:100:"], part, "and"))
    assert(not regex_match(res, ["notroot:.*:0:0:","nottest:.*:[0-9]+:100:"], part, "or"))
    assert(regex_match(res, ["notroot:.*:0:0:","nottest:.*:[0-9]+:100:"], part, "or", negative=True))
    assert(regex_match(res, ["root:.*:0:0:","nottest:.*:[0-9]+:100:"], part, "or"))

import yaml
from pypanuclei.pypanuclei import template_match, parse_response_bytes

def test_matchers_and():
    resb = b"""HTTP/1.1 200 OK\r
Connection: close\r
Content-Type: text/html\r
Cookie: PHPSESSID=sdfsdfsdfsdfsdfsdfsdfsdf;\r
Content-Length: 23\r
\r
<title>PHP test</title>"""

    response = parse_response_bytes(resb)

    templ = yaml.safe_load("""
    requests:
      - method: GET
        path:
          - "{{BaseURL}}"
        matchers-condition: and
        matchers:
          - type: status
            status:
              - 200
              - 302

          # filter dsl
          - type: dsl
            dsl:
              - Host != ip

          - type: word
            words:
              - "X-Powered-By: PHP"
              - "PHPSESSID"
            condition: or
            part: header

          - type: word
            words:
              - "PHP"
            part: body""")

    assert(template_match(templ, response))
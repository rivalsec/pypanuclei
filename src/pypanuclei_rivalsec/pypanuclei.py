#!/usr/bin/env python3
import yaml
import glob
from http.client import HTTPResponse
from io import BytesIO
import re
import argparse


def load_templates(paths, excludes):
    out = []
    for path in paths:
        path = path.rstrip("/")
        yamlfiles = glob.glob(path + "/**/*.yaml", recursive=True)
        for tf in yamlfiles:
            #filters
            if len(excludes) > 0 and any(e for e in excludes if tf.startswith(e)):
                continue
            if "-workflow.yaml" in tf:
                continue
            tfy = None
            with open(tf,"r") as file_stream:
                tfy = yaml.load(file_stream, Loader=yaml.CLoader)

            if ispassive(tfy):
                out.append(template_prep(tfy))

    return out


def template_prep(templ):
    """precompile regexes etc"""
    for t_req in templ["requests"]:
        for m in t_req["matchers"]:
            if m["type"] == "regex":
                m["regex_compiled"] = []
                for r in m["regex"]:
                    m["regex_compiled"].append(re.compile(r))
    return templ


def ispassive(temp):
    if "requests" not in temp:
        return
    if len(temp["requests"]) != 1:
        return

    for t_req in temp["requests"]:
        if t_req.get("method",None) != "GET":
            continue
        # todo only dsl etc
        if not any(m for m in t_req.get("matchers",[]) if m["type"] in ["word", "regex"]):
            continue
        # if t_req.get("path", None) in  [["{{BaseURL}}"],["{{BaseURL}}/"]]:
        for path in t_req.get("path", []):
            if path in ("{{BaseURL}}","{{BaseURL}}/"):
                return True
        #TODO precompile regex matchers


def get_passive_requests(template):
    for t_req in template["requests"]:
        if t_req.get("method",None) != "GET":
            continue
        for path in t_req.get("path", []):
            if path in ("{{BaseURL}}","{{BaseURL}}/"):
                return True


class FakeSocket():
    def __init__(self, response_bytes):
        self._file = BytesIO(response_bytes)
    def makefile(self, *args, **kwargs):
        return self._file


def parse_response_bytes(http_response_bytes):
    source = FakeSocket(http_response_bytes)
    response = HTTPResponse(source)
    response.begin()
    response.res_headers = response.getheaders()
    response.res_headers_str = ""
    for h in response.res_headers:
        response.res_headers_str += f"{h[0]}: {h[1]}\r\n"
    response.res_body_str = response.read().decode('utf-8', errors='ignore')
    return response


def parse_response(file):
    try:
        with open(file, "rb") as f:
            http_response_bytes = f.read()
            return parse_response_bytes(http_response_bytes)
    except Exception as e:
        pass


def get_part(response, part):
    if part == "body":
        return response.res_body_str
    elif part == "header":
        return response.res_headers_str
    else: 
        return False


def words_match(response, words, part, condition):
    source = get_part(response, part)
    if source == False:
        return
    mi = (True if w in source else False for w in words)
    return all(mi) if condition == "and" else any(mi)


def regex_match_compiled(response, regexes, part, condition):
    """regexex - compiled"""
    source = get_part(response, part)
    if source == False:
        return
    ri = (True if r.search(source) else False for r in regexes)
    return all(ri) if condition == "and" else any(ri)


def regex_match(response, regexes, part, condition):
    """regexex - compiled"""
    source = get_part(response, part)
    if source == False:
        return
    ri = (True if re.search(r, source) else False for r in regexes)
    return all(ri) if condition == "and" else any(ri)


def status_match(response, statuses, condition):
    mi = (True if s == response.status else False for s in statuses)
    return all(mi) if condition == "and" else any(mi)


def matchers_match(matchers, response):
    for m in matchers:
        mpart = m.get("part", "body")
        mcondition = m.get("condition", "or")
        if m["type"] not in ["word", "regex", "status"]:
            continue
        if m["type"] == "word":
            yield words_match(response, m.get("words",[]), mpart, mcondition)
        elif m["type"] == "regex":
            # yield regex_match_compiled(response, m["regex_compiled"], mpart, mcondition)
            yield regex_match(response, m["regex"], mpart, mcondition)
        elif m["type"] == "status":
            yield status_match(response, m["status"], mcondition) 


def template_match(temp, response):
    if "matchers" not in temp["requests"][0]:
        return
    t_req = temp["requests"][0]
    # todo other requests? 
    ms_condition = t_req.get("matchers-condition", "or")
    matchers = t_req["matchers"]
    if ms_condition == "or":
        return any(matchers_match(matchers, response))
    else:
        return all(matchers_match(matchers, response))


def check_responses(path, templates):
    """{"template-id":"waf-detect","info":{"name":"WAF Detection","author":["dwisiswant0","lu4nx"],
    "tags":["waf","tech","misc"],"description":"A web application firewall was detected.","reference":
    ["https://github.com/ekultek/whatwaf"],"severity":"info","classification":
    {"cve-id":null,"cwe-id":["cwe-200"]}},"matcher-name":"safedog","type":"http","path":"test/mcs.mail.ru.txt",
    "matched-at":"test/mcs.mail.ru.txt","timestamp":"2022-12-17T23:24:53.119636+05:00","matcher-status":true,"matched-line":null}"""
    path = path.rstrip("/")
    files = glob.glob(path + "/**/*.txt", recursive=True)
    for rfile in files:
        res = parse_response(rfile)
        if not res:
            continue
        for template in templates:
            tmr = template_match(template, res)
            if tmr:
                print(f"{rfile} {template['id']}")
    

def cli():
    a = argparse.ArgumentParser()
    a.add_argument("-u", type=str, help="directory to exclude (list)", required=True)
    a.add_argument("-t", "-templates", type=str, default=[], action='append', help="template directory to run (list)", required=True)
    a.add_argument("-et", "-exclude-templates", type=str, default=[], action='append', help="template or directory to exclude (list)")
    args = a.parse_args()

    templates = load_templates(args.t, args.et)
    
    print (f"Templates loaded {len(templates)}")

    check_responses("test", templates)


if __name__ == "__main__":
    cli()

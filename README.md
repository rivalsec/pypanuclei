# pypanuclei (Python Passive Nuclei) scanner

pypanuclei is created like an alternative to the passive scanning mode in [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei/)


I created it because of 3 main reasons:
 - nuclei process `raw:` request in passive mode, resulting in many false positives
 - nuclei process dsl matchers like `Host!=ip` in passive mode, resulting in most of takeover templates not work at all
 - sometimes on large amount of files nuclei fires non-existent matches


warnings:
 - extractors not implemented yet
 - only regex, word and status matchers are implemented
 - all other matchers like dsl are skipped (set to true)
 - heavy regex patterns can lead to endless hang (use -et and -debug to filter)


## Installation: 
```
pip3 install -U pypanuclei
```

## Basic usage (cli):
```
subfinder hackerone.com | httpx -sr -srd ./responses
git clone https://github.com/projectdiscovery/nuclei-templates.git

pypanuclei -target ./responses -t ./nuclei-templates -et ./nuclei-templates/technologies/ -et ./nuclei-templates/exposures/tokens/generic/
```

## cli options:
```
optional arguments:
  -h, --help                show this help message and exit
  -u, -target               path to directory with saved responses
  -t, -templates            templates directory to run (list)
  -et, -exclude-templates   template or directory to exclude (list)
  -json                     json output
  -debug                    debug
```

## Basic usage (python):
```python
from pypanuclei.pypanuclei import load_templates, check_responses

templates = load_templates(['./nuclei-templates'], ['./nuclei-templates/technologies'])
for res in check_responses('./responses', templates):
    print(f"[{res['template-id']}] [{res['type']}] [{res['info']['severity']}] {res['path']}")
```

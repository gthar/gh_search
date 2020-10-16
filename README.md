# Github Search Crawler

Technical test implementing a github search crawler.


## Installation

```sh
python setup.py install
```

The executable `gh_search.py` will be available


## Run without installing

Make sure the requirements are met

```sh
pip install -r requirements.txt
```

And simply run the `gh_search.py` script from within this directory

## Usage:

```sh
gh_search.py ${INPUT_FILE} [--output=${OUT_FILE} | -o ${OUT_FILE}] [--verbose | --quiet]
gh_search.py (-h | --help)
gh_search.py --version
```

Where `$INPUT_FILE` is a valid JSON input file and `$OUT_FILE` is where the output will be stored in JSON format.
If the output file is not specified, the output will be sent through the standard output.

`--verbose` and `--quiet` are mutually exclusive and control the level of verbosity.
If `--verbose` is specified, all log information will be shown. If `--quiet` is specified, only errors will be shown. If neither is specified, errors and warnings will be shown.

## Input

The expected input file is a JSON file specifying following keys:

keywords
: Keywords to be used for the search

proxies
: List of HTTP proxies to be used. A random one will be selected.

type
: Type of page to search. Valid options are 'Repositories', 'Issues' and 'Wikis'


Example input file:

```json
{
  "keywords": [
    "openstack",
    "nova",
    "css"
  ],
  "proxies": [
    "194.126.37.94:8080",
    "13.78.125.167:8080"
  ],
  "type": "Repositories"
}
```

## Output

The output will be in JSON format as well. It will be an array containing objects specifying each found URL.

In the case of the repositories, each element will also contain an `extra` object that specified the repository owner and it's language stats.

Example output for an issues search:

```json
[
  {"url": "https://github.com/ace964/Azubot/issues/1"},
  {"url": "https://github.com/UB-CSE/course-project-yo-ub_sustainable/issues/73"},
  {"url": "https://github.com/Learn-Write-Repeat/Contribution-program/issues/22"},
  {"url": "https://github.com/Learn-Write-Repeat/Open-contributions/issues/175"},
  {"url": "https://github.com/faezekeshmiri/internship-onlineShop-backend/issues/1"},
  {"url": "https://github.com/Gregorvich/dungeon-omega/issues/5"},
  {"url": "https://github.com/googleapis/python-logging/issues/72"},
  {"url": "https://github.com/nornir-automation/nornir/issues/601"},
  {"url": "https://github.com/adikesavulu-15/adicode/issues/1"},
  {"url": "https://github.com/Uberi/speech_recognition/issues/504"}
]
```

Example for repositories search

```json
[
  {
    "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
    "extra": {
      "owner": "atuldjadhav",
      "language_stats": {
        "CSS": 52,
        "JavaScript": 47.2,
        "HTML": 0.8
      }
    }
  }
]
```

## Tests

Run tests with

```sh
python -m unittest discover
```

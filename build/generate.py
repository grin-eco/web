#!/usr/bin/env python3

import datetime
import pprint
import csv
import textwrap
import re
import os
import string
import sys
import urllib.parse

import yaml
from jinja2 import Environment, FileSystemLoader
from jinja_markdown import MarkdownExtension
import dateutil.parser


DIVIDER = "#"*80

# init the jinja stuff
file_loader = FileSystemLoader("_templates")
env = Environment(loader=file_loader)
env.add_extension(MarkdownExtension)

# load the context from the metadata file
print(DIVIDER)
print("Loading context")
with open('metadata.yml') as f:
    context = yaml.load(f, Loader=yaml.FullLoader)
    BASE_FOLDER = "./" + context.get("base_folder")
# store urls for the sitemap.xml
urls = []

# MAIN PAGES
print(DIVIDER)
print("Generating main pages")
for page in ["index.html"]:
    with open(BASE_FOLDER + "/" + page, "w") as f:
        print("Writing out", page)
        template = env.get_template(page)
        f.write(template.render(page=page, **context))
        if page != "index.html":
            urls.append((page.replace(".html",""), 0.75))

# SITEMAP
print(DIVIDER)
print("Generating sitemap.xml with %d items" % len(urls))
now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
with open(BASE_FOLDER + "/sitemap.xml", "w") as f:
    template = env.get_template("sitemap.xml")
    f.write(template.render(urls=urls, now=now))

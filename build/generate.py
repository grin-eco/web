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
for extra in ["podcasts"]:
    with open(f'{extra}.yml', 'r') as f:
        extras = yaml.load(f, Loader=yaml.FullLoader)
        extras["podcasts"] = sorted(extras["podcasts"], key=lambda x: x.get("date"), reverse=True)
        context.update(extras)

# preprocess navigation

items = []
for v in context.get("navigation"):
    if v.get("url"):
        items.append(v)
    for v in v.get("items", []):
        items.append(v)
context["navigation_dict"] = { v["name"].lower(): dict(name=v["name"], url=v["url"]) for v in items}
# store urls for the sitemap.xml
SITEMAP_URLS = []
#print(context)

# MAIN PAGES
print(DIVIDER)
pages = ["index.html", "podcast.html"]
print(f"Generating main pages: {pages}")
for page in pages:
    with open(BASE_FOLDER + "/" + page, "w") as f:
        print("Writing out", page)
        template = env.get_template(page)
        f.write(template.render(page=page, **context))
        if page != "index.html":
            SITEMAP_URLS.append((page.replace(".html",""), 0.75))

# SITEMAP
print(DIVIDER)
print("Generating sitemap.xml with %d items" % len(SITEMAP_URLS))
now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
with open(BASE_FOLDER + "/sitemap.xml", "w") as f:
    template = env.get_template("sitemap.xml")
    f.write(template.render(urls=SITEMAP_URLS, now=now))

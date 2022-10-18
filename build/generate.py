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


def parse_otter_ai_transcript_file(transcript_path):
    print("Processing transcript file: %s" % transcript_path)
    with open(transcript_path, 'r') as f:
        chapters = f.read().split("\n\n")
    transcript = []
    for chapter in chapters:
        if "Transcribed by" in chapter:
            continue
        if not chapter or not ("\n" in chapter):
            continue
        header, body = chapter.split("\n", 1)
        speaker, timestamp = header.split("  ", 1)
        time_m, time_s = timestamp.split(":")[:2]
        transcript.append(dict(
            speaker=speaker,
            timestamp=timestamp,
            timestamp_s=(int(time_m)*60 + int(time_s)),
            body=body,
        ))
    return transcript

def parse_book_markdown(lines, book_file):
    dividers = dict(
        chapter="## ",
        summary="# "
    )
    chapters = []
    tags = []
    content = ""
    metadata = dict()
    current_chapter = ""
    for line in lines:
        for tag in ["tag", "title", "author", "short_url"]:
            txt = f"[//]: # ({tag}:"
            if line.startswith(txt):
                parsed = line.split(txt)[-1].split(")")[0]
                if tag == "tag":
                    tags.append(parsed)
                else:
                    metadata[tag] = parsed
                continue
        if line.lower().startswith(dividers.get("summary")):
            current_chapter = line.split(dividers.get("summary"))[-1]
        # finish a chapter
        elif line.lower().startswith(dividers.get("chapter")):
            chapters.append(dict(
                title=current_chapter,
                content=content,
                tags=tags,
            ))
            current_chapter = line.split(dividers.get("chapter"))[-1]
            content = ""
            tags = []
        else:
            content += line
    # the last chapter
    chapters.append(dict(
        title=current_chapter,
        content=content,
        tags=tags,
    ))
    return dict(
        path=book_file,
        #content=content,
        chapters=chapters,
        metadata=metadata,
    )


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

# PODCAST
print(DIVIDER)
print("Generating podcast pages")
for podcast in context.get("podcasts"):

    podcast["YouTubeId"] = podcast.get("url").split("/")[-1]

    transcript_path = podcast.get("transcript")
    if not transcript_path:
        print("No transcript file for: %s" % podcast.get("title"))
        continue

    podcast["transcript"] = parse_otter_ai_transcript_file(transcript_path)

    # write out the template for the podcast episode
    with open(BASE_FOLDER + "/" + podcast.get("short_url").replace(".html","") + ".html", "w") as f:
        template = env.get_template("podcast_episode.html")
        f.write(template.render(podcast=podcast, **context))
        SITEMAP_URLS.append((podcast.get("short_url").replace(".html",""), 0.81))

# BOOKS
print(DIVIDER)
print("Generating books review pages")
book_files = []
for root, dirs, files in os.walk("./assets/books"):
    for file in files:
        book_files.append(os.path.join(root, file))
books = []
for book_file in book_files:
    with open(book_file, "r") as f:
        content = f.readlines()
        books.append(parse_book_markdown(content, book_file))
print(books)

# SITEMAP
print(DIVIDER)
print("Generating sitemap.xml with %d items" % len(SITEMAP_URLS))
now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
with open(BASE_FOLDER + "/sitemap.xml", "w") as f:
    template = env.get_template("sitemap.xml")
    f.write(template.render(urls=SITEMAP_URLS, now=now))

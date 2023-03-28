#!/usr/bin/env python3

import re
import os
import time
import logging
import requests
import fnmatch
import pathlib
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlencode, parse_qs, urlunparse
from playwright.sync_api import sync_playwright
import argparse

LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)s %(funcName)s: %(message)s"

SOCIAL_MEDIA_PATTERNS = [
    "*adobe.com/*",
    "*.adobe.com/*",
    "*facebook.com/*",
    "*.facebook.com/*",
    "*twitter.com/*",
    "*.twitter.com/*",
    "*instagram.com/*",
    "*.instagram.com/*",
    "*linkedin.com/*",
    "*.linkedin.com/*",
    "*pinterest.com/*",
    "*.pinterest.com/*",
    "*youtube.com/*",
    "*.youtube.com/*",
    "*github.com/*",
    "*.github.com/*",
    "*codepen.io/*",
    "*.codepen.io/*",
    "*apple.com/*",
    "*.apple.com/*",
    "*google.com/*",
    "*.google.com/*",
]

CSS_URL_PATTERN = re.compile(r'url\(["\']?(.*?)["\']?\)')

DOWNLOADABLE_FILE_EXTENSIONS = [
    ".csv",
    ".doc",
    ".docx",
    ".epub",
    ".exe",
    ".gif",
    ".jpeg",
    ".jpg",
    ".json",
    ".mov",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".pdf",
    ".pkg",
    ".png",
    ".tif",
    ".tsv",
    ".txt",
    ".wav",
    ".xls",
    ".xlsx",
    ".xml",
]

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger()


def remove_url_anchor(url):
    return url[: url.find("#")] if "#" in url else url


def is_ignored_url(url, ignored_patterns):
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(url, pattern):
            return True
    return False


def is_same_domain(url1, url2):
    parsed_url1 = urlparse(url1)
    parsed_url2 = urlparse(url2)
    return parsed_url1.netloc == parsed_url2.netloc


def is_file_download(url):
    for extension in DOWNLOADABLE_FILE_EXTENSIONS:
        if url.lower().endswith(extension.lower()):
            return True
    return False


def get_html_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)
            # time.sleep(3)  # Allow time for JavaScript to load
            html = page.content()
            browser.close()
        return html
    except:
        logger.critical("Error loading HTML")
        return False


def save_file(url, content, output_dir):
    try:
        parsed_url = urlparse(url)
        query_params_str = urlencode(parse_qs(parsed_url.query), doseq=True)
        query_suffix = f"-{query_params_str}" if query_params_str else ""
        file_name = os.path.basename(parsed_url.path)

        if file_name == "":
            file_name = "index.html"

        url_path = parsed_url.path.lstrip("/").removesuffix(file_name)
        output_dir = os.path.join(output_dir, parsed_url.netloc, url_path)
        file_path = os.path.join(output_dir, file_name)
        file_extension = pathlib.Path(file_path).suffix

        if file_extension == "":
            output_dir = file_path
            file_path = os.path.join(file_path, "index.html")

        os.makedirs(output_dir, exist_ok=True)

        if file_path.endswith(".html") or file_path.endswith(".htm"):
            logger.debug(f"Saving page to {file_path}")
        else:
            logger.debug(f"Saving asset to {file_path}")
        with open(file_path, "wb") as f:
            f.write(content)
    except NotADirectoryError as e:
        logger.critical("Error creating directory")
        logger.critical(e)
        temp_file_path = f"{file_path}-temp"
        os.rename(file_path, temp_file_path)
        os.makedirs(output_dir, exist_ok=True)

        if file_path.endswith(".html") or file_path.endswith(".htm"):
            logger.debug(f"Saving page to {file_path}")
        else:
            logger.debug(f"Saving asset to {file_path}")
        with open(file_path, "wb") as f:
            f.write(content)

        os.rename(temp_file_path, os.path.join(file_path, "index.html"))
    except IsADirectoryError as e:
        logger.debug("Error creating file")
        logger.debug(e)
        file_path = os.path.join(file_path, "index.html")
        logger.debug(f"Saving page to {file_path}")
        with open(file_path, "wb") as f:
            f.write(content)


def download_css_assets(
    css_content,
    base_url,
    output_dir,
    ignored_patterns,
    previously_downloaded,
    include_assets=False,
    follow_redirects=False,
):
    asset_urls = CSS_URL_PATTERN.findall(css_content)
    for asset_url in asset_urls:
        full_asset_url = urljoin(base_url, asset_url)
        download_asset(
            full_asset_url, output_dir, ignored_patterns, previously_downloaded
        )


def download_asset(
    url,
    output_dir,
    ignored_patterns,
    previously_downloaded,
    include_assets=False,
    follow_redirects=False,
):
    url = remove_url_anchor(url)

    if url in previously_downloaded:
        return

    parsed_url = urlparse(url)
    url_no_query = urlunparse(parsed_url._replace(query=""))

    if (
        not url.startswith("http")
        or is_ignored_url(url_no_query, ignored_patterns)
        or url in previously_downloaded
    ):
        logger.warning(f"Canceling download for {url}")
        return

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            save_file(url, response.content, output_dir)
            logger.info(f"Downloaded asset {url}")
            previously_downloaded.append(url)

            if url.lower().endswith(".css"):
                download_css_assets(
                    response.text,
                    url,
                    output_dir,
                    ignored_patterns,
                    previously_downloaded,
                    include_assets,
                    follow_redirects,
                )

    except requests.exceptions.RequestException as e:
        logger.crtical(f"Failed to download asset {url}: {e}")


def download_assets(
    url,
    output_dir,
    ignored_patterns,
    soup,
    previously_downloaded,
    include_assets=False,
    follow_redirects=False,
):
    logger.debug(f"Downloading assets on {url}")

    for tag_name, attr_name in [("img", "src"), ("link", "href"), ("script", "src")]:
        for tag in soup.find_all(tag_name):
            asset_url = tag.get(attr_name)
            if asset_url:
                full_asset_url = urljoin(url, asset_url)
                download_asset(
                    full_asset_url,
                    output_dir,
                    ignored_patterns,
                    previously_downloaded,
                    include_assets,
                    follow_redirects,
                )


def crawl_links(
    url,
    output_dir,
    ignored_patterns,
    soup,
    previously_downloaded,
    include_assets=False,
    follow_redirects=False,
):
    logger.debug(f"Crawling links on {url}")

    for link in soup.find_all("a"):
        href = link.get("href")
        if href and not href.startswith("#"):
            full_url = urljoin(url, href)
            if (
                full_url.startswith("http")
                and is_same_domain(url, full_url)
                and not is_ignored_url(full_url, ignored_patterns)
            ):
                logger.debug(f"Found URL: {full_url}")
                try:
                    if follow_redirects == True:
                        response = requests.get(full_url, timeout=10)
                        if response.status_code == 200:
                            logger.debug(f"Downloading original: {full_url}")
                            download(
                                full_url,
                                output_dir,
                                ignored_patterns,
                                previously_downloaded,
                                include_assets,
                                follow_redirects,
                            )
                        elif response.status_code in (301, 302):
                            redirected_url = response.headers.get("Location")
                            if redirected_url and not is_ignored_url(
                                redirected_url, ignored_patterns
                            ):
                                logger.debug(f"Redirected to {redirected_url}")
                                download(
                                    redirected_url,
                                    output_dir,
                                    ignored_patterns,
                                    previously_downloaded,
                                    include_assets,
                                    follow_redirects,
                                )
                    else:
                        logger.debug(f"Downloading without redirects: {full_url}")
                        download(
                            full_url,
                            output_dir,
                            ignored_patterns,
                            previously_downloaded,
                            include_assets,
                            follow_redirects,
                        )
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to download {full_url}: {e}")


def download(
    url,
    output_dir,
    ignored_patterns,
    previously_downloaded=[],
    include_assets=False,
    follow_redirects=False,
):
    if url in previously_downloaded:
        return
    logger.info(f"Downloading {url}")

    if is_file_download(url):
        download_asset(
            url,
            output_dir,
            ignored_patterns,
            previously_downloaded,
            include_assets,
            follow_redirects,
        )
    else:
        html = get_html_playwright(url)
        if not html:
            logger.warning(f"HTML could not be loaded for {url}")
        else:
            soup = BeautifulSoup(html, "html.parser")

            save_file(url, html.encode(), output_dir)  # Save the original URL content
            previously_downloaded.append(url)  # Track the URL has been downloaded

            # Download static assets
            if include_assets:
                download_assets(
                    url,
                    output_dir,
                    ignored_patterns,
                    soup,
                    previously_downloaded,
                    include_assets,
                    follow_redirects,
                )

            # Download pages that were linked to
            crawl_links(
                url,
                output_dir,
                ignored_patterns,
                soup,
                previously_downloaded,
                include_assets,
                follow_redirects,
            )


def main():

    parser = argparse.ArgumentParser(description="Download a website.")
    parser.add_argument("url", help="The URL of the website to download.")
    parser.add_argument(
        "-a",
        "--assets",
        help="Include assets in the download",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-f",
        "--follow",
        help="Follow URL redirects",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-o",
        "--output",
        default="downloaded_files",
        help="The output directory for downloaded files.",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="*",
        default=SOCIAL_MEDIA_PATTERNS,
        help="List of URL patterns to ignore.",
    )
    args = parser.parse_args()

    url = args.url
    output_dir = args.output
    ignored_patterns = args.ignore
    include_assets = args.assets
    follow_redirects = args.follow
    previously_downloaded = []

    os.makedirs(output_dir, exist_ok=True)

    download(
        url,
        output_dir,
        ignored_patterns,
        previously_downloaded,
        include_assets,
        follow_redirects,
    )

    logger.info(
        f"Downloaded all content: {url} ({len(previously_downloaded)} downloads)"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

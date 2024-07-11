"""
This module provides functions to download files from a specified URL and
save them to a specified directory.

Functions:
- get_request: Sends a GET request to the specified URL and returns the response object.
- download: Downloads a stream of bytes from the given URL and saves it to the specified path.
- download_files: Downloads files from the given URLs to the specified mods_directory.
- get_file_download: Retrieves the download URL for the specified file from the server.
- get_config: Retrieves the config file from the server.
- get_filenames: Retrieves a list of filenames from the server.
- get_file_downloads: Retrieves a list of download URLs from the server.

Constants:
- GITHUB_CONTENTS_BASE (str): The base URL for the GitHub contents API.
- CONFIG_NAME (str): The name of the config file on the server.
"""

import logging
from typing import Generator
import os
import base64
import json
import requests
import yaml
from source import creds, exceptions

logger = logging.getLogger(__name__)

GITHUB_CONTENTS_BASE = \
    r"https://api.github.com/repos/Trogiken/Hominum-Updates/git/trees/master?recursive=1"
CONFIG_PATH = "config.yaml"


def get_request(url: str, timeout=5, headers=None, **kwargs) -> requests.models.Response:
    """
    Sends a GET request to the specified URL and returns the response object.

    Parameters:
    - url (str): The URL to send the GET request to.
    - timeout (int): The number of seconds to wait for the server to send data before giving up.
    - headers (dict): The headers to include in the request.
    - **kwargs: Additional keyword arguments to pass to the requests.get function.

    Returns:
    - requests.models.Response: The response object from the GET request.

    Exceptions:
    - requests.exceptions.Timeout: If the request times out.
    - requests.exceptions.HTTPError: If an HTTP error occurs.
    """
    if headers is None:
        headers = {'Authorization': f'token {creds.get_api_key()}'}
    else:
        headers['Authorization'] = f'token {creds.get_api_key()}'

    try:
        resp = requests.get(url, timeout=timeout, headers=headers, **kwargs)
        resp.raise_for_status()
    except Exception as error:
        logger.error("Failed to get '%s': %s", url, error)
        return None
    return resp


def download(url: str = None, save_path: str = None, chunk_size=8192) -> str | None:
    """
    Downloads a stream of bytes from the given URL and saves it to the specified path.

    Parameters:
    - url (str): The URL to download the file from. (This has to be a blob URL.)
    - save_path (str): The path to save the downloaded file.
        If not specified, the content will be returned as a string.
    - chunk_size (int): The size of the chunks to download. Defaults to 8192.

    Returns:
    - str: The path where the file was saved. Or the content if save_path is not specified.
    - None: If the url is not specified or an error occurs during download.
    """
    if not url:
        return None
    try:
        resp = get_request(url, stream=True)
        message = ""  # Used to store the content if save_path is not specified
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    base64_bytes = json.loads(chunk.decode('utf-8'))["content"]
                    message_bytes = base64.b64decode(base64_bytes)
                    message_chunk = message_bytes.decode('utf-8')
                    if save_path:
                        f.write(message_chunk)
                    else:
                        message += message_chunk
        logger.info("Downloaded '%s' to '%s'", url, save_path)
    except Exception as error:
        raise exceptions.DownloadError(f"Failed to download '{url}': {error}")

    return save_path if save_path else message


def download_files(urls: list, save_directory: str) -> Generator[tuple, None, None]:
    """
    Downloads files from the given URLs to the specified mods_directory.

    Parameters:
    - urls (list): A list of URLs to download the files from.
    - save_directory (str): The directory to save the downloaded files to.

    Returns:
    - Generator[tuple, None, None]:
        A generator that yields a tuple containing the count of downloaded files,
        the total number of files to download, the name of the file, and error boolean.
    """
    url_pairs = []
    for url in urls:
        filename = url.split("/")[-1]  # Get the file name from the URL
        filename = filename.split("?")[0]  # Remove any query parameters from the file name
        save_path = os.path.join(save_directory, filename)
        if not os.path.exists(save_path):
            url_pairs.append((url, save_path, filename))

    count = 0
    total = len(url_pairs)
    logger.debug("Downloading '%d' files", total)
    logger.debug("URL pairs: %s", url_pairs)
    for pair in url_pairs:
        url, save_path, filename = pair
        error_occured = False
        retries_left = 3

        while retries_left > 0:
            try:
                download(url, save_path)
                count += 1
                yield (count, total, filename, error_occured)
                break
            except exceptions.DownloadError as error:
                if os.path.exists(save_path):
                    os.remove(save_path)  # Remove incomplete file
                    logger.warning("Removed incomplete file '%s'", save_path)
                retries_left -= 1
                if retries_left == 0:
                    logger.error("Max retries reached for '%s': %s", url, error)
                    error_occured = True
                    yield (count, total, filename, error_occured)
                    break
                logger.warning("Failed to download '%s', trying again", url)


# def get_file_download(file_path: str) -> str:
#     """
#     Retrieves the download URL for the specified file from the server.

#     Parameters:
#     - file_path (str): The path to the file on the server.

#     Returns:
#     - str: The download URL for the file.
#     - None: If the response is empty.
#     - FileNotFoundError: If the file is not found on the server.
#     """
#     path, name = os.path.split(file_path)
#     download_path_url = ""
#     resp = get_request(f"{GITHUB_CONTENTS_BASE}/{path}")
#     if not resp:
#         logger.warning("Failed to get download url from server")
#         return None
#     for file in resp.json():
#         if file["name"] == name:
#             download_path_url = file["download_url"]
#             break
#     if not download_path_url:
#         logger.error("'%s' not found on the server", name)
#         return None
#     logger.debug("Download URL: %s", download_path_url)

#     return download_path_url


# def get_file_downloads(directory: str) -> list:
#     """
#     Retrieves a list of download URLs from the server.

#     Parameters:
#     - directory (str): The directory to retrieve the download URLs from.

#     Returns:
#     - list: A list of download URLs.
#     - None: If the response is empty.
#     - exceptions.NoResponseError: If no response is received from the server.
#     """
#     resp = get_request(f"{GITHUB_CONTENTS_BASE}/{directory}")
#     if not resp:
#         logger.warning("Failed to get download urls from server")
#         return None
#     download_urls = []
#     for file in resp.json():
#         download_urls.append(file["download_url"])
#     logger.debug("Download URLs: %s", download_urls)

#     return download_urls


def get_repo_tree() -> dict:
    """
    Retrieves the repository tree from the server.

    Returns:
    - dict: The repository tree.
    """
    resp = get_request(GITHUB_CONTENTS_BASE)
    if not resp:
        logger.warning("Failed to get repository tree from server")
        return {}
    tree = resp.json()
    if not tree:
        logger.warning("No repository tree found")
        return {}
    logger.debug("Repository tree found")

    return tree


def get_file_url(path: str) -> dict:
    """
    Retrieves the download URL for the specified file from the server.

    Parameters:
    - path (str): The path to the file on the server.

    Returns:
    - dict: The download URL for the file.
    - None: If the response is empty.
    - FileNotFoundError: If the file is not found on the server.
    """
    tree = get_repo_tree()
    if not tree:
        return None
    for file in tree["tree"]:
        if file["path"] == path:
            return file["url"]
    logger.error("'%s' not found on the server", path)

    return None


def get_config() -> dict:
    """
    Retrieves the config file from the server.

    Returns:
    - dict: The contents of the config file.
    """
    config_content = download(get_file_url(CONFIG_PATH))
    if not config_content:
        logger.warning("Failed to get config from server")
        return {}
    config = yaml.safe_load(config_content)
    logger.debug("Config: %s", config)

    return config


# def get_filenames(directory: str) -> list:
#     """
#     Retrieves a list of filenames from the server.

#     Parameters:
#     - directory (str): The directory to retrieve the filenames from.

#     Returns:
#     - list: A list of mod names.
#     - None: If the response is empty.
#     """
#     resp = get_request(f"{GITHUB_CONTENTS_BASE}/{directory}")
#     if not resp:
#         logger.warning("Failed to get filenames from server")
#         return None
#     names = []
#     for file in resp.json():
#         names.append(file["name"])
#     logger.debug("Filenames: %s", names)

#     return names

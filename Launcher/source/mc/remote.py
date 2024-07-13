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
import base64
import json
import requests
import os
import tempfile
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

    def _download_chunks():
        resp = get_request(url, stream=True)
        if not resp:
            raise exceptions.DownloadError(f"Failed to get '{url}'")

        # write raw content to file
        with tempfile.NamedTemporaryFile(delete=False) as raw_temp_file:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    raw_temp_file.write(chunk)

            raw_temp_path = raw_temp_file.name

        logger.debug("Downloaded '%s' to '%s'", url, save_path)
        return raw_temp_path

    def _decode_base64(raw_file_path):
        # read file in chunks and decode base64
        with open(raw_file_path, "rb") as raw_file, \
        tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in raw_file.read().splitlines():
                if chunk:
                    try:
                        base64_bytes = json.loads(chunk.decode('utf-8'))["content"]
                    except UnicodeDecodeError:  # Binary data
                        base64_bytes = json.loads(chunk)["content"]
                    message_bytes = base64.b64decode(base64_bytes)
                    temp_file.write(message_bytes)
            temp_file_path = temp_file.name
        return temp_file_path

    try:
        raw_temp_path = _download_chunks()
        file_path = _decode_base64(raw_temp_path)

        if not save_path:  # Return content
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            os.unlink(file_path)
            return content
        os.rename(file_path, save_path)  # Move temp file to save path
        return save_path
    except Exception as error:
        os.unlink(file_path)  # Remove the file if an error occurs
        raise exceptions.DownloadError(f"Failed to download '{url}': {error}")


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
    tree = resp.json().get("tree", None)
    if not tree:
        logger.warning("No repository tree found")
        return {}
    logger.debug("Repository tree found")

    return tree


def get_file_url(tree: dict, path: str) -> dict:
    """
    Retrieves the download URL for the specified file from the server.

    Parameters:
    - path (str): The path to the file on the server.

    Returns:
    - dict: The download URL for the file.
    - None: If the response is empty.
    """
    if not tree:
        return None
    for file in tree:
        if file["path"] == path:
            return file["url"]
    logger.error("'%s' not found on the server", path)

    return None


def get_dir_paths(tree: dict, dir_path: str) -> list:
    """
    Retrieves a list of directory paths from the server.

    Returns:
    - list: A list of directory paths.
    - None: If the response is empty.
    """
    if not tree:
        return None
    paths = []
    for file in tree:
        if file["path"].startswith(dir_path):
            paths.append(file["path"])
    logger.debug("'%s' Paths: %s", dir_path, paths)

    return paths


def get_config(tree) -> dict:
    """
    Retrieves the config file from the server.

    Returns:
    - dict: The contents of the config file.
    """
    config_content = download(get_file_url(tree, CONFIG_PATH))
    if not config_content:
        logger.warning("Failed to get config from server")
        return {}
    config = yaml.safe_load(config_content)
    logger.debug("Config: %s", config)

    return config

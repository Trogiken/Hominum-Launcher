"""
This module provides functions to download files from a specified URL and
save them to a specified directory.

Functions:
- get_request(url: str, timeout=5, headers={'Authorization': f'token {API_TOKEN}'}, **kwargs)
    -> requests.models.Response: Returns a response object from a GET request.
- download(url: str, save_path: str)
    -> str: Downloads stream of bytes to save_path, returns save_path.
- download_files(urls: list, mods_directory: list)
    -> int: Downloads files from urls to mods_directory.
- get_url_dir() -> str: Returns url of the directory with mods.
- get_filenames() -> list: Returns a list of mod names.
- get_file_downloads() -> list: Returns a list of download urls.

Constants:
- API_TOKEN: The GitHub API token.
- PATH_URL: The URL of the path file.
- GITHUB_CONTENTS_BASE: The base URL for GitHub contents.
"""

import os
import requests
import yaml
from typing import Generator
from source import creds

GITHUB_CONTENTS_BASE = r"https://api.github.com/repos/Trogiken/Hominum-Updates/contents"
CONFIG_NAME = "config.yaml"


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

    resp = requests.get(url, timeout=timeout, headers=headers, **kwargs)
    resp.raise_for_status()
    return resp


def download(url: str, save_path: str, chunk_size=8192) -> str:
    """
    Downloads a stream of bytes from the given URL and saves it to the specified path.

    Parameters:
    - url (str): The URL to download the file from.
    - save_path (str): The path to save the downloaded file.
    - chunk_size (int): The size of the chunks to download. Defaults to 8192.

    Returns:
    - str: The path where the file was saved.
    """
    resp = get_request(url, stream=True)

    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)


def download_files(urls: list, mods_directory: str) -> Generator[tuple, None, None]:
    """
    Downloads files from the given URLs to the specified mods_directory.

    Parameters:
    - urls (list): A list of URLs to download the files from.
    - mods_directory (str): The directory to save the downloaded files to.

    Returns:
    - Generator[tuple, None, None]:
        A generator that yields a tuple containing the count of downloaded files,
        the total number of files to download, and the name of the file.
    """
    count = 0
    total = len(urls)
    for url in urls:
        filename = url.split("/")[-1]  # Get the file name from the URL
        filename = filename.split("?")[0]  # Remove any query parameters from the file name
        save_path = os.path.join(mods_directory, filename)
        max_retries = 3
        retry = True
        while retry:
            try:
                if os.path.exists(save_path):
                    retry = False
                else:
                    download(url, save_path)
                    count += 1
                    retry = False
                yield (count, total, filename)
            except Exception:
                if os.path.exists(save_path):
                    os.remove(save_path)  # Remove incomplete file
                max_retries -= 1
                if max_retries == 0:
                    # TODO: Add error handling for failed file
                    if os.path.exists(save_path):
                        os.remove(save_path)  # Remove incomplete file
                    retry = False


def get_file_download(file_path: str) -> str:
    """
    Retrieves the download URL for the specified file from the server.

    Parameters:
    - file_path (str): The path to the file on the server.

    Returns:
    - str: The download URL for the file.
    """
    path, name = os.path.split(file_path)
    download_path_url = ""
    resp = get_request(GITHUB_CONTENTS_BASE + f"/{path}")
    for file in resp.json():
        if file["name"] == name:
            download_path_url = file["download_url"]
            break
    if not download_path_url:
        raise FileNotFoundError(f"{name} not found on the server")

    return download_path_url

def get_config() -> dict:
    """
    Retrieves the config file from the server.

    Returns:
    - dict: The contents of the config file.
    """
    config = get_request(get_file_download(CONFIG_NAME)).text
    config = yaml.safe_load(config)

    return config


def get_filenames(directory: str) -> list:
    """
    Retrieves a list of filenames from the server.

    Parameters:
    - directory (str): The directory to retrieve the filenames from.

    Returns:
    - list: A list of mod names.
    """
    resp = get_request(GITHUB_CONTENTS_BASE + f"/{directory}")
    names = []
    for file in resp.json():
        names.append(file["name"])

    return names


def get_file_downloads(directory: str) -> list:
    """
    Retrieves a list of download URLs from the server.

    Parameters:
    - directory (str): The directory to retrieve the download URLs from.

    Returns:
    - list: A list of download URLs.
    """
    resp = get_request(GITHUB_CONTENTS_BASE + f"/{directory}")
    download_urls = []
    for file in resp.json():
        download_urls.append(file["download_url"])

    return download_urls

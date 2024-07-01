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

from typing import Generator
import os
import requests
import yaml
from source import creds, exceptions

GITHUB_CONTENTS_BASE = r"https://api.github.com/repos/Trogiken/Hominum-Updates/contents"
CONFIG_NAME = "config.yaml"

# TODO: Make webrequests error handling more robust
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
    except Exception:
        # TODO: Log error
        return None
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
    if not resp:
        return None
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)

    return save_path


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
    url_pairs = []
    for url in urls:
        filename = url.split("/")[-1]  # Get the file name from the URL
        filename = filename.split("?")[0]  # Remove any query parameters from the file name
        save_path = os.path.join(mods_directory, filename)
        if not os.path.exists(save_path):
            url_pairs.append((url, save_path, filename))

    count = 0
    total = len(url_pairs)
    for pair in url_pairs:
        url, save_path, filename = pair
        retries_left = 3

        while retries_left > 0:
            try:
                save = download(url, save_path)
                if not save:
                    raise exceptions.NoResponseError(f"No response from {url}")
                count += 1
                yield (count, total, filename)
                break
            except Exception:
                # TODO: Log error
                if os.path.exists(save_path):
                    os.remove(save_path)  # Remove incomplete file
                retries_left -= 1
                if retries_left == 0:
                    # Optionally, handle the error further or raise an exception
                    yield (count, total, filename)
                    break


def get_file_download(file_path: str) -> str:
    """
    Retrieves the download URL for the specified file from the server.

    Parameters:
    - file_path (str): The path to the file on the server.

    Returns:
    - str: The download URL for the file.
    - None: If the response is empty.
    - FileNotFoundError: If the file is not found on the server.
    """
    path, name = os.path.split(file_path)
    download_path_url = ""
    resp = get_request(GITHUB_CONTENTS_BASE + f"/{path}")
    if not resp:
        # TODO: Log error
        return None
    for file in resp.json():
        if file["name"] == name:
            download_path_url = file["download_url"]
            break
    if not download_path_url:
        raise FileNotFoundError(f"{name} not found on the server")

    return download_path_url


def get_file_downloads(directory: str) -> list:
    """
    Retrieves a list of download URLs from the server.

    Parameters:
    - directory (str): The directory to retrieve the download URLs from.

    Returns:
    - list: A list of download URLs.
    - None: If the response is empty.
    - exceptions.NoResponseError: If no response is received from the server.
    """
    resp = get_request(GITHUB_CONTENTS_BASE + f"/{directory}")
    if not resp:
        # TODO: Log error
        return None
    download_urls = []
    for file in resp.json():
        download_urls.append(file["download_url"])

    return download_urls


def get_config() -> dict:
    """
    Retrieves the config file from the server.

    Returns:
    - dict: The contents of the config file.
    """
    resp = get_request(get_file_download(CONFIG_NAME))
    if not resp:
        # TODO: Log error
        return {}
    config = yaml.safe_load(resp.text)

    return config


def get_filenames(directory: str) -> list:
    """
    Retrieves a list of filenames from the server.

    Parameters:
    - directory (str): The directory to retrieve the filenames from.

    Returns:
    - list: A list of mod names.
    - None: If the response is empty.
    """
    resp = get_request(GITHUB_CONTENTS_BASE + f"/{directory}")
    if not resp:
        # TODO: Log error
        return None
    names = []
    for file in resp.json():
        names.append(file["name"])

    return names

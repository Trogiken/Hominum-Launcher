"""
This module provides functions to download files from a specified URL and save them to a specified directory.

Functions:
- get_request(url: str, timeout=5, headers={'Authorization': f'token {API_TOKEN}'}, **kwargs) -> requests.models.Response: Returns a response object from a GET request.
- download(url: str, save_path: str) -> str: Downloads stream of bytes to save_path, returns save_path.
- download_files(urls: list, mods_directory: list) -> int: Downloads files from urls to mods_directory.
- get_url_dir() -> str: Returns url of the directory with mods.
- get_filenames() -> list: Returns a list of mod names.
- get_file_downloads() -> list: Returns a list of download urls.

Constants:
- API_TOKEN: The GitHub API token.
- PATH_URL: The URL of the path file.
- GITHUB_CONTENTS_BASE: The base URL for GitHub contents.
"""

import requests
import os


API_TOKEN = "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"
PATH_URL = r"https://raw.githubusercontent.com/Eclik1/Hominum-Updates/main/path.txt"
GITHUB_CONTENTS_BASE = r"https://api.github.com/repos/Eclik1/Hominum-Updates/contents"


def get_request(url: str, timeout=5, headers={'Authorization': f'token {API_TOKEN}'}, **kwargs) -> requests.models.Response:
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
    resp = requests.get(url, timeout=timeout, headers=headers, **kwargs)
    resp.raise_for_status()
    return resp


def download(url: str, save_path: str) -> str:
    """
    Downloads a stream of bytes from the given URL and saves it to the specified path.

    Parameters:
    - url (str): The URL to download the file from.
    - save_path (str): The path to save the downloaded file.

    Returns:
    - str: The path where the file was saved.
    """
    resp = get_request(url, stream=True)

    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def download_files(urls: list, mods_directory: list) -> int:
    """
    Downloads files from the given URLs to the specified mods directory.

    Parameters:
    - urls (list): A list of URLs to download the files from.
    - mods_directory (list): The directory to save the downloaded files to.

    Returns:
    - int: The total number of files downloaded.
    """
    total_downloads = 0
    for url in urls:
        file_name = url.split("/")[-1]
        save_path = os.path.join(mods_directory, file_name)
        while True:
            try:
                if os.path.exists(save_path):
                    print(f"'{file_name}' already exists, skipping it...")
                    break
                print(f"Downloading '{file_name}'...")
                download(url, save_path)
                total_downloads += 1
                print(f"Downloaded '{file_name}'")
                break
            except requests.Timeout:
                print(f"Download of '{file_name}' timed out, trying again...")

    return total_downloads


def get_url_dir() -> str:
    """
    Returns the URL of the directory with mods.

    Returns:
    - str: The URL of the directory with mods.
    """
    resp = get_request(PATH_URL)
    path = resp.text.split("\n")[0].strip()
    url = f"{GITHUB_CONTENTS_BASE}/{path}"

    return url


def get_filenames() -> list:
    """
    Retrieves a list of filenames from the server.

    Returns:
    - list: A list of mod names.
    """
    resp = get_request(get_url_dir())
    names = []
    for file in resp.json():
        names.append(file["name"])

    return names


def get_file_downloads() -> list:
    """
    Retrieves a list of download URLs from the server.

    Returns:
    - list: A list of download URLs.
    """
    resp = get_request(get_url_dir())
    download_urls = []
    for file in resp.json():
        download_urls.append(file["download_url"])
    
    return download_urls

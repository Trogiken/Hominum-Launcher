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
import source.creds as creds

GITHUB_CONTENTS_BASE = r"https://api.github.com/repos/Trogiken/Hominum-Updates/contents"
PATH_URL = f"{GITHUB_CONTENTS_BASE}/path.txt"


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
        headers = {'Authorization': f'token {creds.API_TOKEN}'}
    else:
        headers['Authorization'] = f'token {creds.API_TOKEN}'

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


def download_files(urls: list, mods_directory: str) -> int:
    """
    Downloads files from the given URLs to the specified mods_directory.

    Parameters:
    - urls (list): A list of URLs to download the files from.
    - mods_directory (str): The directory to save the downloaded files to.

    Returns:
    - int: The total number of files downloaded.
    """
    total_downloads = 0
    for url in urls:
        file_name = url.split("/")[-1]  # Get the file name from the URL
        file_name = file_name.split("?")[0]  # Remove any query parameters from the file name
        save_path = os.path.join(mods_directory, file_name)
        max_retries = 3
        while True:
            try:
                if os.path.exists(save_path):
                    print(f"'{file_name}' already exists, skipping it...")
                    break
                if not file_name.endswith(".jar"):
                    print(f"WARNING: '{file_name}' is not a jar file, skipping it...")
                    break
                print(f"Downloading '{file_name}'...")
                download(url, save_path)
                total_downloads += 1
                print(f"Downloaded '{file_name}'")
                break
            except Exception as e:
                print(f"WARNING: Failed to download '{file_name}': {str(e)}, trying again...")
                if os.path.exists(save_path):
                    os.remove(save_path)  # Remove incomplete file
                max_retries -= 1
            finally:
                if max_retries == 0:
                    print(f"ERROR: Download of '{file_name}' failed too many times, skipping it...")
                    if os.path.exists(save_path):
                        os.remove(save_path)  # Remove incomplete file
                    break

    return total_downloads


def get_url_dir() -> str:
    """
    Returns the URL of the directory with mods.

    Exceptions:
    - FileNotFoundError: If the path.txt file is not found on the server.

    Returns:
    - str: The URL of the directory with mods.
    """
    base_resp = get_request(GITHUB_CONTENTS_BASE)
    download_path_url = ""
    for file in base_resp.json():
        if file["name"] == "path.txt":
            download_path_url = file["download_url"]
            break
    if not download_path_url:
        raise FileNotFoundError("path.txt not found on the server")

    path = get_request(download_path_url).text
    path = path.strip()
    
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

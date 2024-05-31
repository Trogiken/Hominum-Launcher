import requests
import os


API_TOKEN = ""


def get_request(url: str, timeout=5, headers={'Authorization': f'token {API_TOKEN}'}, **kwargs) -> requests.models.Response:
    """Returns a response object from a GET request"""
    resp = requests.get(url, timeout=timeout, **kwargs)
    resp.raise_for_status()
    return resp


def download(url: str, save_path: str) -> str:
    """Downloads stream of bytes to save_path, returns save_path"""
    resp = get_request(url, stream=True)

    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def download_files(urls: list, mods_directory: list) -> int:
    """Downloads files from urls to mods_directory"""
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

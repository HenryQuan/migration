from requests import get
from key import TOKEN
from time import sleep
import subprocess

namespaces = ["HenryQuan"]


def process_search_result(url: str):
    headers = {
        "Authorization": f"token {TOKEN}",
    }
    response = get(url, headers=headers)
    response = response.json()
    total_count = response["total_count"]
    repos = response["items"]
    if not repos:
        print(f"No repos found for {url}")
        return []

    if not isinstance(repos, list):
        print(f"Unexpected response for {url}")
        return []

    clone_urls = [repo["clone_url"] for repo in repos]
    return clone_urls, total_count


def clone_repo(url: str, path: str):
    # include all branches for a full backup
    result = subprocess.run(["git", "clone", "--mirror", url, path])
    result.check_returncode()


def build_search_url(namespace: str, page: int = 1):
    return f"https://api.github.com/search/repositories?q=user:{namespace}&visibility=all&per_page=100&page={page}"


# get all repos and git clone --no-checkout

for namespace in namespaces:
    # make sure to obtain all repos
    url = build_search_url(namespace)
    clone_urls, total_count = process_search_result(url)

    if total_count > 100:
        for page in range(2, total_count // 100 + 2):
            url = build_search_url(namespace, page)
            clone_urls += process_search_result(url)[0]

    for clone_url in clone_urls:
        folder_name = clone_url.split("/")[-1]
        clone_repo(clone_url, "backups" + "/" + namespace + "/" + folder_name)
        sleep(1) # add some delay to avoid rate limiting

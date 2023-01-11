from dotenv import load_dotenv
import os
import requests
import json
from git import Repo
# import shutil


load_dotenv()
token = os.getenv('TOKEN')
user = os.getenv('USER')
git_url = os.getenv('URL')
clone_dir = os.getenv('DIR')
cwd = os.getcwd()


def get_json_data(url):
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data


def get_branches(url):
    json_data = get_json_data(url)
    branches_list = []
    for el in json_data:
        branches_list.append(el["name"])
    return branches_list


def not_auth(json_data):
    default_data = {"message":"401 Unauthorized"}  # noqa: E231
    return default_data == json_data


def fetch(path):
    repo = Repo(path)
    for remote in repo.remotes:
        remote.fetch()
    file = os.path.join(path, '.git', 'FETCH_HEAD')
    with open(file) as f:
        data = f.read()
        print(data)


def clone(url, name, path, branch_name):
    try:
        Repo.clone_from(
            f"https://{user}:{token}@{url}",
            path,
            branch=branch_name,
            )
        print(f"Repository {name} with branch {branch_name} has been cloned")
    except Exception as e:
        print(f"An error has occurred: {e}")


def main():
    response_dict = get_json_data(f"{git_url}?private_token={token}")
    if not_auth(response_dict):
        print("Authorization error")
        return
    count_of_repos = len(response_dict)
    for i, el in enumerate(response_dict):
        print(f"Getting data for {i+1} of {count_of_repos} repositories")

        id = el["id"]
        name = el["name"]
        url = el["http_url_to_repo"]
        url = url.replace("https://", "")

        branches_url = (
            f"{git_url}/{id}/repository/branches"
            f"?private_token={token}"
            )
        branches_list = get_branches(branches_url)

        for branch_name in branches_list:
            path = os.path.join(cwd, clone_dir, name, branch_name)
            if os.path.exists(path):
                # shutil.rmtree(path)
                print(
                    f"Fetching data for repository {name} "
                    f"with branch {branch_name}"
                    )
                fetch(path)
            else:
                print(f"Cloning repository {name} with branch {branch_name}")
                clone(url, name, path, branch_name)

    print("All works are done")


if __name__ == "__main__":
    main()

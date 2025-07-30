import os
from git import GitCommandError, Repo

DEFAULT_CLONE_DIRECTORY = "clones"

def _clean_repo_name(url: str) -> str:
    return url.rstrip('/').split('/')[-1].replace('.git', '')


def _clone_new_repo(url, target_path) -> None:
    try:
        print(f"Cloning {url} into {target_path}...")
        Repo.clone_from(url, target_path)
    except Exception as e:
        print(f"Failed to clone {url}: {e}")


def _pull_to_local_clone(repo_name, target_path, post_pull_hook):
    try:
        print(f"{repo_name} already exists. Pulling latest changes...")
        repo = Repo(target_path)
        origin = repo.remotes.origin

        old_commit = repo.head.commit.hexsha
        origin.pull()
        new_commit = repo.head.commit.hexsha

        if post_pull_hook:
            post_pull_hook(target_path, repo_name, old_commit, new_commit)

    except GitCommandError as e:
        print(f"Failed to pull {repo_name}: {e}")


# Post-pull hook is a function that takes a repo path, repo name, the oldest local commit, and the newest local commit, and does some form of post-processing.
def clone_repo(url: str, clone_root: str, post_pull_hook = None) -> None:
    repo_name = _clean_repo_name(url)
    target_path = os.path.join(clone_root, repo_name)

    # Clone repo; if repo is already cloned, pull the latest commit.
    if not os.path.exists(target_path):
        _clone_new_repo(url, target_path)
    else:
        _pull_to_local_clone(repo_name, target_path, post_pull_hook)


def clone_repos_from_file(file_path: str, clone_root: str = DEFAULT_CLONE_DIRECTORY, post_pull_hook = None) -> None:
    os.makedirs(clone_root, exist_ok=True)

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        clone_repo(url, clone_root, post_pull_hook)

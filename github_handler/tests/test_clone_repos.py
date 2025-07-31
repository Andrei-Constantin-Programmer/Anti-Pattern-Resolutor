import os
from unittest.mock import MagicMock, patch
from git import GitCommandError
import pytest
from clone_repos import clone_repo, clone_repos_from_file

@pytest.fixture
def repo_url():
    return "https://github.com/example/repo.git"

@pytest.fixture
def repo_name():
    return "repo"

@pytest.fixture
def repo_path(tmp_path, repo_name):
    return tmp_path / repo_name

def _make_fake_repo(old_commit="abc123", new_commit=None, pull_callback=None):
    repo = MagicMock()
    repo.head.commit.hexsha = old_commit

    def pull():
        if new_commit:
            repo.head.commit.hexsha = new_commit
        if pull_callback:
            pull_callback()

    repo.remotes.origin.pull.side_effect = pull
    return repo

@pytest.mark.parametrize("url, expected_repo_name", [
    ("https://github.com/user/repo.git", "repo"),
    ("https://github.com/user/repo.git/", "repo"),
    ("https://github.com/user/repo/", "repo"),
    ("https://github.com/user/repo", "repo"),
    ("git@github.com:user/repo.git", "repo"),
    ("git@github.com:user/repo.git/", "repo"),
    ("ssh://git@github.com/user/repo.git", "repo"),
    ("ssh://git@github.com/user/repo/", "repo"),
    ("https://github.com/user/another-repo.git", "another-repo"),
    ("https://github.com/org/some.repo.git", "some.repo"),
])
def test_clone_repo_clones_new_repo(tmp_path, monkeypatch, url, expected_repo_name):
    # Arrange
    target_path = tmp_path / expected_repo_name
    clone_called = {}

    monkeypatch.setattr("clone_repos.os.path.exists", lambda _: False)

    def mock_clone_from(actual_url, actual_path):
        clone_called["url"] = actual_url
        clone_called["path"] = actual_path

    monkeypatch.setattr("clone_repos.Repo.clone_from", mock_clone_from)

    # Act
    clone_repo(url, str(tmp_path))

    # Assert
    assert clone_called["url"] == url
    assert clone_called["path"] == str(target_path)


def test_clone_repo_pulls_existing_repo(tmp_path, repo_url, repo_path, monkeypatch):
    # Arrange
    repo_path.mkdir()
    monkeypatch.setattr("clone_repos.os.path.exists", lambda _: True)

    pull_called = {}

    def pull_flag():
        pull_called["was_called"] = True

    monkeypatch.setattr("clone_repos.Repo", lambda _: _make_fake_repo(pull_callback=pull_flag))

    # Act
    clone_repo(repo_url, str(tmp_path))

    # Assert
    assert pull_called.get("was_called") is True


def test_clone_repo_calls_post_pull_hook(tmp_path, repo_url, repo_name, repo_path):
    # Arrange
    os.makedirs(repo_path)
    post_pull_hook = MagicMock()

    old_commit = "abc123"
    new_commit = "def456"
    fake_repo = _make_fake_repo(old_commit, new_commit)

    # Act
    with patch("clone_repos.os.path.exists", return_value=True), \
         patch("clone_repos.Repo", return_value=fake_repo):
        clone_repo(repo_url, str(tmp_path), post_pull_hook)

    # Assert
    post_pull_hook.assert_called_once_with(
        str(repo_path),
        repo_name,
        old_commit,
        new_commit
    )


def test_clone_repo_handles_clone_failure(tmp_path, repo_url, repo_path):
    # Arrange
    post_pull_hook = MagicMock()

    # Act
    with patch("clone_repos.os.path.exists", return_value=False), \
         patch("clone_repos.Repo.clone_from", side_effect=Exception("Clone failed")) as mock_clone:
        clone_repo(repo_url, str(tmp_path), post_pull_hook=post_pull_hook)

    # Assert
    mock_clone.assert_called_once_with(repo_url, str(repo_path))
    post_pull_hook.assert_not_called()


def test_clone_repo_handles_git_command_error(tmp_path, repo_url, repo_path):
    # Arrange
    os.makedirs(repo_path)
    post_pull_hook = MagicMock()

    def raise_git_error():
        raise GitCommandError("pull", 1)

    # Act
    with patch("clone_repos.os.path.exists", return_value=True), \
         patch("clone_repos.Repo", return_value=_make_fake_repo(pull_callback=raise_git_error)):
        clone_repo(repo_url, str(tmp_path), post_pull_hook=post_pull_hook)

    # Assert
    post_pull_hook.assert_not_called()


def test_clone_repos_from_file_calls_clone_repo(tmp_path, monkeypatch):
    # Arrange
    file = tmp_path / "repos.txt"
    urls = [
        "https://github.com/user/repo1.git", # Already cloned  - must be pulled
        "https://github.com/user/repo2.git", # Failure         - must skip
        "git@github.com:user/repo3.git"      # New, valid repo - must clone
    ]
    file.write_text("\n".join(urls))
    clone_root = tmp_path / "clones"

    pulled, cloned, failed = [], [], []

    def mock_exists(path):
        return os.path.basename(str(path)) == "repo1"
    
    monkeypatch.setattr("clone_repos.os.path.exists", mock_exists)

    class FakeRepo:
        def __init__(self, path):
            name = os.path.basename(str(path))
            # simulate existing commit
            self.head = MagicMock(commit=MagicMock(hexsha="abc123"))
            # set up pull to update commit and record
            def pull_side_effect():
                self.head.commit.hexsha = "def456"
                pulled.append(name)
            self.remotes = MagicMock(origin=MagicMock(pull=pull_side_effect))

        @staticmethod
        def clone_from(_, path):
            name = os.path.basename(path)
            if name == "repo2":
                failed.append(name)
                raise Exception("Simulated failure")
            cloned.append(name)

    monkeypatch.setattr("clone_repos.Repo", FakeRepo)

    # Act
    clone_repos_from_file(str(file), str(clone_root))

    # Assert
    assert pulled == ["repo1"], f"Expected repo1 to be pulled, got: {pulled}"
    assert failed == ["repo2"], f"Expected repo2 to fail, got: {failed}"
    assert cloned == ["repo3"], f"Expected repo3 to be cloned, got: {cloned}"

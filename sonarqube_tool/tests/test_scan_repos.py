import subprocess
from unittest.mock import patch, MagicMock
import pytest

from sonarqube_tool.scan_repos import (
    scan_repos,
    SONARQUBE_FILE_NAME,
    PROPERTIES_FILE_NAME,
)

@pytest.fixture
def mock_subprocess_success():
    with patch("sonarqube_tool.scan_repos.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="scan succeeded")
        yield mock_run

@pytest.fixture
def mock_subprocess_failure():
    with patch("sonarqube_tool.scan_repos.subprocess.run", side_effect=subprocess.CalledProcessError(1, "sonar-scanner", output="failure")):
        yield

# For faking the SonarQube token
@pytest.fixture
def mock_which():
    with patch("sonarqube_tool.scan_repos.shutil.which", return_value="/usr/bin/sonar-scanner"):
        yield

# Mock SonarQubeAPI to avoid requiring real tokens in tests
@pytest.fixture
def mock_sonarqube_api():
    with patch("sonarqube_tool.scan_repos.SonarQubeAPI") as mock_api:
        mock_instance = MagicMock()
        mock_instance.is_scan_successful.return_value = True
        mock_instance.save_all_issues.return_value = None
        mock_api.return_value = mock_instance
        yield mock_api


def test_scan_repos_skips_if_sonar_scanner_missing(tmp_path):
    # Arrange
    with patch("sonarqube_tool.scan_repos.shutil.which", return_value=None), \
         patch("sonarqube_tool.scan_repos.subprocess.run") as mock_run:
        # Act
        scan_repos("dummy", str(tmp_path))

        # Assert
        mock_run.assert_not_called()


def test_scan_repos_skips_if_clone_root_missing():
    # Arrange
    with patch("sonarqube_tool.scan_repos.shutil.which", return_value="/usr/bin/sonar-scanner"), \
         patch("sonarqube_tool.scan_repos.subprocess.run") as mock_run:
        # Act
        scan_repos("dummy", "nonexistent_path_999")

         # Assert
        mock_run.assert_not_called()


def test_scan_repos_skips_non_dirs(tmp_path, mock_which):
    # Arrange
    _ = mock_which
    (tmp_path / "not_a_repo.txt").write_text("irrelevant")

    with patch("sonarqube_tool.scan_repos.subprocess.run") as mock_run:
        # Act
        scan_repos("dummy", str(tmp_path))

        # Assert
        mock_run.assert_not_called()


def test_scan_repos_skips_repo_if_output_exists(tmp_path, mock_which, mock_subprocess_success):
    # Arrange
    _ = mock_which
    repo = tmp_path / "repo1"
    repo.mkdir()
    (repo / SONARQUBE_FILE_NAME).write_text("already scanned")

    # Act
    scan_repos(token="dummy", clone_root=str(tmp_path), force_scan=False)

    # Assert
    mock_subprocess_success.assert_not_called()


def test_scan_repos_runs_repo_and_writes_output(tmp_path, mock_which, mock_subprocess_success, mock_sonarqube_api):
    # Arrange
    _ = mock_which
    _ = mock_subprocess_success
    _ = mock_sonarqube_api
    repo = tmp_path / "repo1"
    repo.mkdir()

    # Act
    scan_repos(token="dummy", clone_root=str(tmp_path), force_scan=True)

    # Assert
    output_file = repo / SONARQUBE_FILE_NAME
    assert output_file.exists()
    assert "scan succeeded" in output_file.read_text()
    assert not (repo / PROPERTIES_FILE_NAME).exists()


def test_scan_repos_handles_scan_failure(tmp_path, mock_which, mock_subprocess_failure):
    # Arrange
    _ = mock_which
    _ = mock_subprocess_failure
    repo = tmp_path / "repo1"
    repo.mkdir()

    # Act
    scan_repos(token="dummy", clone_root=str(tmp_path), force_scan=True)

    # Assert
    output_file = repo / SONARQUBE_FILE_NAME
    assert output_file.exists()
    assert "failure" in output_file.read_text()
    assert not (repo / PROPERTIES_FILE_NAME).exists()


def test_scan_repos_runs_multiple_repos(tmp_path, mock_which, mock_subprocess_success, mock_sonarqube_api):
    # Arrange
    _ = mock_which
    _ = mock_subprocess_success
    _ = mock_sonarqube_api
    repo1 = tmp_path / "repo1"
    repo2 = tmp_path / "repo2"
    repo1.mkdir()
    repo2.mkdir()

    # Act
    scan_repos("dummy", str(tmp_path), force_scan=True)

    # Assert
    for repo in [repo1, repo2]:
        assert (repo / SONARQUBE_FILE_NAME).exists()
        assert "scan succeeded" in (repo / SONARQUBE_FILE_NAME).read_text()


def test_scan_repos_runs_mixed_state_repos(tmp_path, mock_which, mock_sonarqube_api):
    # Arrange
    _ = mock_which
    _ = mock_sonarqube_api
    scanned = tmp_path / "scanned"
    unscanned = tmp_path / "success"
    failed = tmp_path / "failure"

    scanned.mkdir()
    unscanned.mkdir()
    failed.mkdir()

    (scanned / SONARQUBE_FILE_NAME).write_text("already scanned")

    def mock_run_side_effect(*_, **kwargs):
        cwd = kwargs.get("cwd")
        if cwd.name == "success":
            return MagicMock(stdout="scan ok")
        elif cwd.name == "failure":
            raise subprocess.CalledProcessError(1, "sonar-scanner", output="boom")
        else:
            raise AssertionError(f"Unexpected repo scanned: {cwd}")

    with patch("sonarqube_tool.scan_repos.subprocess.run", side_effect=mock_run_side_effect):

        # Act
        scan_repos("dummy", str(tmp_path), force_scan=False)

    # Assert
    assert not (scanned / "sonar-project.properties").exists()
    assert (unscanned / SONARQUBE_FILE_NAME).read_text() == "scan ok"
    assert (failed / SONARQUBE_FILE_NAME).read_text() == "boom"

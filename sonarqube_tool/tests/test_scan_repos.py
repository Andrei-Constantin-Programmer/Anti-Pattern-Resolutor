import subprocess
from unittest.mock import patch, MagicMock
import pytest

from sonarqube_tool.scan_repos import (
    _scan_repo,
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


def test_scan_repos_runs_repo_and_writes_output(tmp_path, mock_which, mock_subprocess_success):
    # Arrange
    _ = mock_which
    _ = mock_subprocess_success
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


def test_scan_repos_runs_multiple_repos(tmp_path, mock_which, mock_subprocess_success):
    # Arrange
    _ = mock_which
    _ = mock_subprocess_success
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


def test_scan_repos_runs_mixed_state_repos(tmp_path, mock_which):
    # Arrange
    _ = mock_which
    scanned = tmp_path / "repo1"
    unscanned = tmp_path / "repo2"
    failed = tmp_path / "repo3"

    scanned.mkdir()
    unscanned.mkdir()
    failed.mkdir()

    (scanned / SONARQUBE_FILE_NAME).write_text("already scanned")

    with patch("sonarqube_tool.scan_repos.subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(stdout="scan ok"),  # repo2
            subprocess.CalledProcessError(1, "sonar-scanner", output="boom")  # repo3
        ]

        # Act
        scan_repos("dummy", str(tmp_path), force_scan=False)

        # Assert
        assert not (scanned / "sonar-project.properties").exists()
        assert (unscanned / SONARQUBE_FILE_NAME).read_text() == "scan ok"
        assert (failed / SONARQUBE_FILE_NAME).read_text() == "boom"

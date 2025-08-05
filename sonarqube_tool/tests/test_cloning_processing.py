from unittest.mock import patch
import pytest
from sonarqube_tool.cloning_processing import delete_sonarqube_output_if_updated
from sonarqube_tool.scan_repos import SONARQUBE_FILE_NAME

@pytest.fixture
def repo_path(tmp_path):
    return tmp_path

@pytest.fixture
def repo_name():
    return "example-repo"

@pytest.fixture
def file_path(repo_path):
    return repo_path / SONARQUBE_FILE_NAME

def test_delete_sonarqube_output_if_updated_deletes_file_if_commit_changed(repo_path, repo_name, file_path):
    # Arrange
    file_path.write_text("dummy content")

    with patch("os.path.exists", return_value=True), \
         patch("os.remove") as mock_remove:
        # Act
        delete_sonarqube_output_if_updated(
            repo_path=str(repo_path),
            repo_name=repo_name,
            old_commit="abc123",
            new_commit="def456"
        )

        # Assert
        mock_remove.assert_called_once_with(str(file_path))

def test_delete_sonarqube_output_if_updated_skips_delete_if_file_missing(repo_path, repo_name):
    # Arrange
    with patch("os.path.exists", return_value=False), \
         patch("os.remove") as mock_remove:
        # Act
        delete_sonarqube_output_if_updated(
            repo_path=str(repo_path),
            repo_name=repo_name,
            old_commit="abc123",
            new_commit="def456"
        )
        
        # Assert
        mock_remove.assert_not_called()

def test_delete_sonarqube_output_if_updated_skips_if_not_updated(repo_path, repo_name):
    # Arrange
    with patch("os.path.exists") as mock_exists, \
         patch("os.remove") as mock_remove:
        # Act
        delete_sonarqube_output_if_updated(
            repo_path=str(repo_path),
            repo_name=repo_name,
            old_commit="abc123",
            new_commit="abc123"
        )

        # Assert
        mock_exists.assert_not_called()
        mock_remove.assert_not_called()

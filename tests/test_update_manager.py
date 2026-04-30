"""Tests for update_manager.py — version check and update mechanism."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestGetCurrentVersion:
    """Tests for get_current_version()."""

    def test_reads_version_file(self, tmp_path):
        version_file = tmp_path / "VERSION"
        version_file.write_text("1.2.3\n")
        with patch("update_manager.SYSTEM_ROOT", tmp_path):
            # Re-import so the patched SYSTEM_ROOT is used
            from update_manager import get_current_version
            assert get_current_version() == "1.2.3"

    def test_fallback_to_zero(self, tmp_path):
        with patch("update_manager.SYSTEM_ROOT", tmp_path):
            from update_manager import get_current_version
            assert get_current_version() == "0.0.0"


class TestVersionGreater:
    """Tests for _version_greater()."""

    def test_greater(self):
        from update_manager import _version_greater
        assert _version_greater("1.2.3", "1.2.2") is True

    def test_not_greater(self):
        from update_manager import _version_greater
        assert _version_greater("1.2.1", "1.2.2") is False

    def test_equal(self):
        from update_manager import _version_greater
        assert _version_greater("1.2.1", "1.2.1") is False

    def test_fallback_without_packaging(self):
        """Simulate packaging.version not being available."""
        try:
            import packaging  # noqa: F401
            _packaging_installed = True
        except ImportError:
            _packaging_installed = False

        # Force the import of packaging.version to fail
        save = {}
        keys_to_stub = ["packaging.version", "packaging"]
        for k in keys_to_stub:
            if k in __import__("sys").modules:
                save[k] = __import__("sys").modules[k]
            __import__("sys").modules[k] = None

        try:
            # Must reimport to bypass any cached successful import
            import update_manager
            import importlib
            importlib.reload(update_manager)
            result = update_manager._version_greater("2.0.0", "1.9.9")
            assert result is True
        finally:
            # Restore
            for k, v in save.items():
                if v is None:
                    __import__("sys").modules.pop(k, None)
                else:
                    __import__("sys").modules[k] = v


class TestCheckForUpdates:
    """Tests for check_for_updates()."""

    @patch("requests.get")
    @patch("update_manager.get_current_version", return_value="1.2.1")
    def test_update_available(self, mock_version, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"tag_name": "v1.2.2"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from update_manager import check_for_updates
        has_update, current, latest = check_for_updates()
        assert has_update is True
        assert current == "1.2.1"
        assert latest == "1.2.2"

    @patch("requests.get")
    @patch("update_manager.get_current_version", return_value="1.2.1")
    def test_no_update(self, mock_version, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"tag_name": "v1.2.1"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from update_manager import check_for_updates
        has_update, current, latest = check_for_updates()
        assert has_update is False

    @patch("requests.get", side_effect=Exception("network error"))
    @patch("update_manager.get_current_version", return_value="1.2.1")
    def test_network_failure_graceful(self, mock_version, mock_get):
        from update_manager import check_for_updates
        has_update, current, latest = check_for_updates()
        assert has_update is False
        assert current == "1.2.1"
        assert latest == "1.2.1"


class TestMergeOpencodeDir:
    """Tests for _merge_opencode_dir()."""

    def test_merge_copies_context_and_agents(self, tmp_path):
        from update_manager import _merge_opencode_dir

        source = tmp_path / "source_opencode"
        dest = tmp_path / "dest_opencode"

        # Create source files
        (source / "agents").mkdir(parents=True)
        (source / "agents" / "orchestrator.md").write_text("new agent")
        (source / "context.md").write_text("new context")

        # Create existing data that must be preserved
        (dest / "sessions").mkdir(parents=True)
        (dest / "sessions" / "old.json").write_text("old session")
        (dest / "agents").mkdir(parents=True)
        (dest / "agents" / "old.md").write_text("old agent")

        _merge_opencode_dir(source, dest)

        # Verify new files were copied
        assert (dest / "context.md").read_text() == "new context"
        assert (dest / "agents" / "orchestrator.md").read_text() == "new agent"
        # Verify existing files were preserved
        assert (dest / "sessions" / "old.json").exists()
        assert (dest / "agents" / "old.md").exists()

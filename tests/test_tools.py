import builtins
import types
import pytest

# Import the module under test
import server
import tools


def test_ping_returns_pong():
	assert server.ping() == "pong"


def test_list_oci_tags_without_auth(monkeypatch):
	"""
	Ensure list_oci_tags calls OrasClient.repo_tags with ref 'registry/repo'
	and returns the list.
	"""
	calls = {}

	class FakeClient:
		def __init__(self):
			calls["init"] = True
		def login(self, *args, **kwargs):
			calls["login_called"] = True
		def get_tags(self, ref: str):
			calls["ref"] = ref
			return ["latest", "1.0.0"]

	class FakeOras(types.SimpleNamespace):
		class client(types.SimpleNamespace):
			OrasClient = FakeClient

	# Monkeypatch the oras module used inside tools
	monkeypatch.setattr(tools, "oras", FakeOras)

	tags = server.list_oci_tags("example.com", "org/app")
	assert tags == ["latest", "1.0.0"]
	assert calls.get("ref") == "example.com/org/app"
	assert "login_called" not in calls


def test_list_oci_tags_with_auth(monkeypatch):
	calls = {}

	class FakeClient:
		def login(self, registry: str, username: str, password: str):
			calls["login"] = (registry, username, password)
		def get_tags(self, ref: str):
			calls["ref"] = ref
			return ["v2"]

	class FakeOras(types.SimpleNamespace):
		class client(types.SimpleNamespace):
			OrasClient = FakeClient

	monkeypatch.setattr(tools, "oras", FakeOras)

	tags = server.list_oci_tags("ghcr.io", "owner/image", username="u", password="p")
	assert tags == ["v2"]
	assert calls.get("login") == ("ghcr.io", "u", "p")
	assert calls.get("ref") == "ghcr.io/owner/image"



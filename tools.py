"""
MCP tool functions for OCI registry operations.

This module contains all tool functions that can be called via the MCP protocol.
"""
from typing import List, Optional, Dict, Any
import oras.client

try:
	from .registry import NonValidatingRegistry
except ImportError:
	# Allow running as a script directly
	from registry import NonValidatingRegistry


def ping() -> str:
	"""
	Simple health-check tool that returns 'pong'.
	"""
	return "pong"


def list_oci_tags(
	registry: str,
	repository: str,
	username: Optional[str] = None,
	password: Optional[str] = None,
) -> List[str]:
	"""
	List tags for an OCI repository. Can be used for any container registry, including Docker Hub.
	Args:
	- registry: e.g. "ghcr.io", "registry-1.docker.io", "localhost:5000"
	- repository: e.g. "owner/name" or "library/alpine"
	- username/password: optional basic auth
	"""
	ref = f"{registry}/{repository}"
	client = oras.client.OrasClient()
	if username and password:
		client.login(registry, username=username, password=password)
	tags = client.get_tags(ref)
	return list(tags)


def get_oci_details(
	registry: str,
	repository: str,
	reference: str,
	username: Optional[str] = None,
	password: Optional[str] = None,
) -> Dict[str, Any]:
	"""
	Fetch manifest details for a given tag or digest using oras.
	Returns available architectures, digest and annotations.
	Args:
	- registry: e.g. "ghcr.io", "registry-1.docker.io", "localhost:5000"
	- repository: e.g. "owner/name" or "library/alpine"
	- reference: tag (e.g. "latest") or digest (e.g. "sha256:...")
	- username/password: optional basic auth
	"""
	# Build reference with tag or digest
	if reference.startswith("sha256:"):
		ref = f"{registry}/{repository}@{reference}"
	else:
		ref = f"{registry}/{repository}:{reference}"
	# Use NonValidatingRegistry to bypass jsonschema validation
	reg = NonValidatingRegistry(hostname=registry)
	if username and password:
		reg.login(username=username, password=password, hostname=registry)
	# Parse container and get manifest (may return dict or tuple)
	container = reg.get_container(ref)
	resp = reg.get_manifest(container)
	if isinstance(resp, tuple):
		manifest = resp[0]
		desc = resp[1] if len(resp) > 1 else None
	else:
		manifest = resp
		desc = None
	# Extract digest from descriptor if available
	digest: Optional[str] = None
	if desc is not None:
		if isinstance(desc, dict):
			digest = desc.get("digest")
		else:
			digest = getattr(desc, "digest", None)
	if not digest and isinstance(manifest, dict):
		# Best-effort fallback if manifest includes digest
		digest = manifest.get("digest")
	# Extract annotations
	annotations: Dict[str, Any] = {}
	if isinstance(manifest, dict):
		annotations = manifest.get("annotations") or {}
	# Determine architectures
	architectures: List[str] = []
	if isinstance(manifest, dict):
		media_type = (manifest.get("mediaType") or "").lower()
		# OCI/Docker index (manifest list)
		if "image.index" in media_type or "manifest.list" in media_type:
			for m in manifest.get("manifests", []) or []:
				plat = (m or {}).get("platform") or {}
				arch = plat.get("architecture")
				if arch:
					architectures.append(arch)
		# Single image manifest - architecture may be present in some schemas
		elif "image.manifest" in media_type:
			arch = manifest.get("architecture")
			if arch:
				architectures.append(arch)
	# Deduplicate
	if architectures:
		architectures = sorted({a for a in architectures})
	return {
		"digest": digest,
		"annotations": annotations,
		"architectures": architectures,
	}


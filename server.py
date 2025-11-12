from fastmcp import FastMCP
from typing import List, Optional, Dict, Any
import oras.client
import oras.provider
import oras.defaults


mcp = FastMCP(name="mcp-oci-registry")


class NonValidatingRegistry(oras.provider.Registry):
	"""
	Custom Registry that overrides get_manifest to skip jsonschema validation.
	This allows fetching manifests that may not strictly conform to the schema
	(e.g., manifest lists/indexes that don't have a 'config' field).
	"""
	def get_manifest(
		self,
		container,
		allowed_media_type=None,
	):
		"""
		Retrieve a manifest for a package without jsonschema validation.
		This is a copy of the parent method but skips the validation step.
		Returns a tuple of (manifest_dict, digest_from_headers) for compatibility.
		"""
		# Load authentication configs for the container's registry
		self.auth.load_configs(container)

		if not allowed_media_type:
			allowed_media_type = [oras.defaults.default_manifest_media_type]
		headers = {"Accept": ";".join(allowed_media_type)}

		get_manifest = f"{self.prefix}://{container.manifest_url()}"
		response = self.do_request(get_manifest, "GET", headers=headers)

		self._check_200_response(response)
		manifest = response.json()
		# Skip jsonschema validation - just return the manifest
		# jsonschema.validate(manifest, schema=oras.schemas.manifest)
		
		# Extract digest from response headers if available
		digest = response.headers.get("Docker-Content-Digest")
		if not digest:
			digest = response.headers.get("OCI-Content-Digest")
		
		# Return tuple for compatibility with code expecting (manifest, descriptor)
		desc = {"digest": digest} if digest else None
		return (manifest, desc) if desc else manifest

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
	List tags for an OCI repository. Can be sued for any container registry, including Docker Hub.
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

# Register tools with FastMCP without wrapping the function names
mcp.tool(ping)
mcp.tool(list_oci_tags)
mcp.tool(get_oci_details)

# Expose ASGI app for uvicorn/gunicorn
asgi_app = mcp.http_app()

if __name__ == "__main__":
	# Default: run in stdio mode for MCP clients
	mcp.run()
	# mcp.run(transport="http", host="127.0.0.1", port=8888)



"""
MCP prompt templates for OCI registry operations.

This module contains all prompt functions that provide instructions
on how to use the OCI registry tools.
"""
from typing import List, Dict


def list_tags_prompt(registry: str, repository: str) -> List[Dict[str, str]]:
	"""
	Prompt template for listing tags in an OCI repository.
	Use this prompt to get instructions on how to list available tags.
	Args:
	- registry: The registry hostname (e.g. "registry-1.docker.io", "ghcr.io")
	- repository: The repository path (e.g. "library/alpine", "owner/image")
	"""
	return [
		{
			"role": "user",
			"content": f"List all available tags for the OCI image {registry}/{repository}. Use the list_oci_tags tool with registry='{registry}' and repository='{repository}'."
		}
	]


def list_architectures_prompt(registry: str, repository: str, reference: str) -> List[Dict[str, str]]:
	"""
	Prompt template for listing architectures supported by an OCI image.
	Use this prompt to get instructions on how to find available architectures for a specific tag or digest.
	Args:
	- registry: The registry hostname (e.g. "registry-1.docker.io", "ghcr.io")
	- repository: The repository path (e.g. "library/alpine", "owner/image")
	- reference: The tag or digest (e.g. "latest", "3.22.2", "sha256:...")
	"""
	return [
		{
			"role": "user",
			"content": f"List all supported architectures for the OCI image {registry}/{repository}:{reference}. Use the get_oci_details tool with registry='{registry}', repository='{repository}', and reference='{reference}'. The response will include an 'architectures' field with the list of supported CPU architectures."
		}
	]


def list_digests_prompt(registry: str, repository: str, reference: str) -> List[Dict[str, str]]:
	"""
	Prompt template for getting the digest of an OCI image.
	Use this prompt to get instructions on how to retrieve the digest (SHA256 hash) for a specific tag.
	Args:
	- registry: The registry hostname (e.g. "registry-1.docker.io", "ghcr.io")
	- repository: The repository path (e.g. "library/alpine", "owner/image")
	- reference: The tag or digest (e.g. "latest", "3.22.2", "sha256:...")
	"""
	return [
		{
			"role": "user",
			"content": f"Get the digest (SHA256 hash) for the OCI image {registry}/{repository}:{reference}. Use the get_oci_details tool with registry='{registry}', repository='{repository}', and reference='{reference}'. The response will include a 'digest' field containing the SHA256 digest of the manifest."
		}
	]


def list_annotations_prompt(registry: str, repository: str, reference: str) -> List[Dict[str, str]]:
	"""
	Prompt template for listing annotations of an OCI image.
	Use this prompt to get instructions on how to retrieve OCI annotations (metadata) for a specific tag or digest.
	Args:
	- registry: The registry hostname (e.g. "registry-1.docker.io", "ghcr.io")
	- repository: The repository path (e.g. "library/alpine", "owner/image")
	- reference: The tag or digest (e.g. "latest", "3.22.2", "sha256:...")
	"""
	return [
		{
			"role": "user",
			"content": f"List all annotations (metadata) for the OCI image {registry}/{repository}:{reference}. Use the get_oci_details tool with registry='{registry}', repository='{repository}', and reference='{reference}'. The response will include an 'annotations' field containing a dictionary of key-value pairs with OCI annotations."
		}
	]


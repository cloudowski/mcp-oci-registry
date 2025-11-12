"""
OCI Registry client with non-validating manifest retrieval.

This module provides a custom Registry class that bypasses jsonschema validation
to support manifest lists/indexes that don't conform to single-image manifest schemas.
"""
import oras.provider
import oras.defaults


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


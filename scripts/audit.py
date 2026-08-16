#!/usr/bin/env python3
"""Read-only Standard.site publication and document audit.

This script only performs HTTP GET requests. It does not create, update, or
delete AT Protocol records; Sequoia remains the publisher for this project.
"""

from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin
from urllib.request import Request, urlopen


DEFAULT_CONFIG = Path("sequoia.json")
DEFAULT_TIMEOUT = 20
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
USER_AGENT = "edriffles-blog-standard-site-audit/1.0"
AT_URI_RE = re.compile(r"^at://([^/]+)/([^/]+)/([^/]+)$")


@dataclass
class Response:
	status: int | None
	headers: Any
	body: bytes
	final_url: str
	error: str | None = None


class LinkParser(html.parser.HTMLParser):
	def __init__(self) -> None:
		super().__init__(convert_charrefs=True)
		self.links: list[tuple[set[str], str]] = []

	def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
		if tag.lower() != "link":
			return
		attributes = {key.lower(): value for key, value in attrs}
		rels = set((attributes.get("rel") or "").lower().split())
		href = attributes.get("href")
		if rels and href:
			self.links.append((rels, href.strip()))


def normalize_site_url(url: str) -> str:
	return url.rstrip("/")


def parse_at_uri(uri: str) -> tuple[str, str, str] | None:
	match = AT_URI_RE.fullmatch(uri)
	return match.groups() if match else None


def request(url: str, timeout: int, accept: str = "*/*") -> Response:
	req = Request(
		url,
		headers={"Accept": accept, "User-Agent": USER_AGENT},
		method="GET",
	)
	try:
		with urlopen(req, timeout=timeout) as response:
			return Response(
				status=response.status,
				headers=response.headers,
				body=response.read(MAX_RESPONSE_BYTES + 1),
				final_url=response.geturl(),
			)
	except HTTPError as error:
		return Response(
			status=error.code,
			headers=error.headers,
			body=error.read(MAX_RESPONSE_BYTES + 1),
			final_url=url,
			error=str(error),
		)
	except (URLError, TimeoutError, OSError) as error:
		return Response(status=None, headers={}, body=b"", final_url=url, error=str(error))


def response_json(response: Response) -> dict[str, Any] | None:
	if response.status is None or not 200 <= response.status < 300:
		return None
	try:
		value = json.loads(response.body.decode("utf-8"))
	except (UnicodeDecodeError, json.JSONDecodeError):
		return None
	return value if isinstance(value, dict) else None


class Audit:
	def __init__(self, site_url: str, publication_uri: str, timeout: int, strict: bool) -> None:
		self.site_url = normalize_site_url(site_url)
		self.publication_uri = publication_uri
		self.timeout = timeout
		self.strict = strict
		self.errors: list[str] = []
		self.warnings: list[str] = []

	def error(self, message: str) -> None:
		self.errors.append(message)
		print(f"ERROR {message}")

	def warning(self, message: str) -> None:
		self.warnings.append(message)
		print(f"WARN  {message}")

	def info(self, message: str) -> None:
		print(f"INFO  {message}")

	def check_response(self, response: Response, label: str) -> bool:
		if response.error:
			self.error(f"{label}: request failed: {response.error}")
			return False
		if response.status is None or not 200 <= response.status < 400:
			status = response.status if response.status is not None else "no status"
			self.error(f"{label}: HTTP {status}")
			return False
		return True

	def pds_endpoint(self, did: str) -> str | None:
		if did.startswith("did:plc:"):
			response = request(f"https://plc.directory/{quote(did, safe=':')}", self.timeout, "application/json")
			document = response_json(response)
			if document:
				for service in document.get("service", []):
					if service.get("type") == "AtprotoPersonalDataServer":
						endpoint = service.get("serviceEndpoint")
						if isinstance(endpoint, str) and endpoint.startswith("https://"):
							return endpoint.rstrip("/")
			self.error(f"{did}: could not resolve an AT Protocol PDS")
			return None
		self.error(f"{did}: unsupported DID method; only did:plc is currently supported")
		return None

	def xrpc(self, pds: str, method: str, params: dict[str, str]) -> dict[str, Any] | None:
		url = f"{pds}/xrpc/{method}?{urlencode(params)}"
		response = request(url, self.timeout, "application/json")
		return response_json(response)

	def publication_record(self) -> tuple[dict[str, Any], str] | None:
		parsed = parse_at_uri(self.publication_uri)
		if not parsed:
			self.error(f"publication URI is not a valid AT-URI: {self.publication_uri}")
			return None
		did, collection, rkey = parsed
		if collection != "site.standard.publication":
			self.error(f"publication URI uses {collection}, expected site.standard.publication")
			return None
		pds = self.pds_endpoint(did)
		if not pds:
			return None
		record = self.xrpc(
			pds,
			"com.atproto.repo.getRecord",
			{"repo": did, "collection": collection, "rkey": rkey},
		)
		if not record or not isinstance(record.get("value"), dict):
			self.error(f"publication record could not be read: {self.publication_uri}")
			return None
		return record["value"], pds

	def document_records(self, pds: str, did: str) -> list[dict[str, Any]]:
		records: list[dict[str, Any]] = []
		cursor: str | None = None
		while True:
			params = {"repo": did, "collection": "site.standard.document", "limit": "100"}
			if cursor:
				params["cursor"] = cursor
			page = self.xrpc(pds, "com.atproto.repo.listRecords", params)
			if not page or not isinstance(page.get("records"), list):
				self.error("site.standard.document records could not be listed")
				return records
			records.extend(record for record in page["records"] if isinstance(record, dict))
			cursor = page.get("cursor")
			if not cursor:
				return records

	def parse_links(self, body: bytes, url: str) -> LinkParser | None:
		try:
			parser = LinkParser()
			parser.feed(body.decode("utf-8", errors="replace"))
			parser.close()
			return parser
		except ValueError:
			self.error(f"{url}: response was not parseable HTML")
			return None

	def links_for(self, parser: LinkParser, relation: str) -> list[str]:
		return [href for rels, href in parser.links if relation in rels]

	def audit_well_known(self) -> None:
		url = f"{self.site_url}/.well-known/site.standard.publication"
		response = request(url, self.timeout, "text/plain")
		if not self.check_response(response, f"publication verification {url}"):
			return
		value = response.body.decode("utf-8", errors="replace").strip()
		if value != self.publication_uri:
			self.error(
				f"publication verification returned {value!r}, expected {self.publication_uri!r}"
			)
		content_type = response.headers.get_content_type() if response.headers else ""
		if content_type != "text/plain":
			self.error(f"publication verification has Content-Type {content_type!r}, expected text/plain")

	def audit_publication(self, record: dict[str, Any], root_parser: LinkParser | None) -> None:
		url = record.get("url")
		if not isinstance(url, str) or not url:
			self.error("publication record has no url")
		elif normalize_site_url(url) != self.site_url:
			self.error(f"publication url is {url!r}, expected {self.site_url!r}")

		if not isinstance(record.get("name"), str) or not record["name"].strip():
			self.error("publication record has no name")

		preferences = record.get("preferences")
		if preferences is None:
			self.warning("publication record has no preferences.showInDiscover setting")
		elif not isinstance(preferences, dict) or not isinstance(preferences.get("showInDiscover"), bool):
			self.error("publication preferences.showInDiscover must be a boolean when present")

		if root_parser is None:
			return
		discovery_links = self.links_for(root_parser, "site.standard.publication")
		if not discovery_links:
			self.warning("homepage has no optional rel=site.standard.publication discovery link")
		elif any(href != self.publication_uri for href in discovery_links):
			self.error("homepage has a mismatched rel=site.standard.publication link")

	def audit_document(self, record: dict[str, Any], seen_paths: dict[str, str]) -> None:
		uri = record.get("uri")
		value = record.get("value")
		if not isinstance(value, dict):
			self.error(f"document {uri or '<unknown>'} has no record value")
			return
		if value.get("site") != self.publication_uri:
			return
		if not isinstance(uri, str):
			self.error("document record is missing its AT-URI")
			return

		for field in ("site", "title", "publishedAt"):
			if not value.get(field):
				self.error(f"{uri}: missing required field {field}")

		path = value.get("path")
		if not isinstance(path, str) or not path.startswith("/"):
			self.error(f"{uri}: path must be an absolute site path")
			return
		if path in seen_paths:
			self.error(f"duplicate document path {path}: {seen_paths[path]} and {uri}")
		else:
			seen_paths[path] = uri

		text_content = value.get("textContent")
		if not isinstance(text_content, str) or not text_content.strip():
			self.warning(f"{uri}: textContent is missing or empty")

		url = urljoin(f"{self.site_url}/", path.lstrip("/"))
		response = request(url, self.timeout, "text/html")
		if not self.check_response(response, f"document {uri} at {url}"):
			return
		parser = self.parse_links(response.body, url)
		if parser is None:
			return

		document_links = self.links_for(parser, "site.standard.document")
		if not document_links:
			self.error(f"{uri}: page is missing rel=site.standard.document verification")
		elif len(document_links) > 1:
			self.error(f"{uri}: page has duplicate rel=site.standard.document links")
		elif document_links[0] != uri:
			self.error(f"{uri}: page verifies {document_links[0]!r} instead")

		publication_links = self.links_for(parser, "site.standard.publication")
		if any(href != self.publication_uri for href in publication_links):
			self.error(f"{uri}: page has a mismatched rel=site.standard.publication link")

	def run(self) -> int:
		if not self.site_url.startswith("https://"):
			self.error(f"site URL must use HTTPS: {self.site_url}")

		self.audit_well_known()
		root_response = request(self.site_url, self.timeout, "text/html")
		root_parser: LinkParser | None = None
		if self.check_response(root_response, f"publication homepage {self.site_url}"):
			root_parser = self.parse_links(root_response.body, self.site_url)

		publication_result = self.publication_record()
		if publication_result is None:
			return self.finish()
		publication, pds = publication_result
		self.audit_publication(publication, root_parser)

		parsed = parse_at_uri(self.publication_uri)
		if not parsed:
			return self.finish()
		did, _, _ = parsed
		records = self.document_records(pds, did)
		publication_documents = [
			record for record in records
			if isinstance(record.get("value"), dict)
			and record["value"].get("site") == self.publication_uri
		]
		seen_paths: dict[str, str] = {}
		for record in publication_documents:
			self.audit_document(record, seen_paths)
		if not publication_documents:
			self.info("no site.standard.document records found for this publication")
		else:
			self.info(f"audited {len(publication_documents)} site.standard.document record(s)")
		return self.finish()

	def finish(self) -> int:
		if self.errors:
			print(f"FAIL Standard.site audit: {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
			return 1
		if self.strict and self.warnings:
			print(f"FAIL Standard.site audit: strict mode treats {len(self.warnings)} warning(s) as failures")
			return 1
		print(f"PASS Standard.site audit: {len(self.warnings)} warning(s)")
		return 0


def load_config(path: Path) -> dict[str, Any]:
	try:
		with path.open(encoding="utf-8") as handle:
			value = json.load(handle)
	except (OSError, json.JSONDecodeError) as error:
			raise SystemExit(f"Unable to read {path}: {error}") from error
	if not isinstance(value, dict):
		raise SystemExit(f"{path} must contain a JSON object")
	return value


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("site_url", nargs="?", help="deployed site URL; defaults to sequoia.json siteUrl")
	parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Sequoia config path")
	parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds")
	parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
	args = parser.parse_args()
	config = load_config(args.config)
	site_url = args.site_url or config.get("siteUrl")
	publication_uri = config.get("publicationUri")
	if not isinstance(site_url, str) or not site_url:
		raise SystemExit("siteUrl is required in sequoia.json or as the positional argument")
	if not isinstance(publication_uri, str) or not publication_uri:
		raise SystemExit("publicationUri is required in sequoia.json")
	return Audit(site_url, publication_uri, args.timeout, args.strict).run()


if __name__ == "__main__":
	sys.exit(main())

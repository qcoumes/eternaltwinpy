The main client is the entry point for interacting with the Eternaltwin API. It
is used to store authorization information and to make requests to the API.

Currently, two implementations of the main client are available:

* `eternaltwin.clients.sync.clients.Eternaltwin` — synchronous client using `requests`
  to communicate with the Eternaltwin API.
* `eternaltwin.clients.asyncio.clients.Eternaltwin` — asynchronous client using `aiohttp`
  to communicate with the Eternaltwin API.

Both implementations follow the same interface defined in the section below.

Both main clients use sub-clients to create namespaces for readability and
maintainability. The following sub-client is available:

* [`Eternaltwin.users`](api_clients_users.md)

---

::: eternaltwin.clients.abc.clients
    options:
      members:
      - ClientABC

::: eternaltwin.clients.sync.clients.Eternaltwin
    options:
        toc_label: "Eternaltwin (sync)"
        show_root_heading: true
        separate_signature: true
        show_signature: true
        show_signature_annotations: true

::: eternaltwin.clients.asyncio.clients.Eternaltwin
    options:
        toc_label: "Eternaltwin (async)"
        show_root_heading: true
        separate_signature: true
        show_signature: true
        show_signature_annotations: true

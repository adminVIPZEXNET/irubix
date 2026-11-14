"""Shad user-account client integration.

The implementation is provided by MAXRubika's MIT-licensed account client.
Importing IRubix itself does not eagerly import MAXRubika; the dependency is
loaded when the Shad client class is first requested.
"""
from __future__ import annotations

from typing import Any

__all__ = ["Shad", "Client", "Messenger"]


def _load_shad_class():
    try:
        from maxrubika import Shad as MaxRubikaShad
    except ImportError as exc:
        raise ImportError(
            "Shad account support requires MAXRubika. Install it with "
            "`pip install 'maxrubika>=1.18.1'` or reinstall IRubix."
        ) from exc

    class Shad(MaxRubikaShad):
        """Shad account client built on MAXRubika's Shad implementation.

        Supports Shad Web, PWA and Android platforms, account sessions,
        API v5/v6, event handlers and the inherited messaging methods.
        """

        def __init__(
            self,
            session: str | None = None,
            string_session: str | None = None,
            password: str | None = None,
            auth: str | None = None,
            private_key: str | bytes | None = None,
            timeout: str | int | float = 30,
            proxy: str | None = None,
            logger: Any = None,
            platform: str = "shad_web",
            api_version: int = 6,
            max_retries: int = 5,
            stop_on_first_match: bool = False,
            run_all_handlers: bool | None = None,
            continue_on_error: bool = True,
            as_dict: bool = False,
            show_welcome: bool = False,
        ):
            super().__init__(
                session=session,
                string_session=string_session,
                password=password,
                auth=auth,
                private_key=private_key,
                timeout=timeout,
                proxy=proxy,
                logger=logger,
                platform=platform,
                api_version=api_version,
                max_retries=max_retries,
                stop_on_first_match=stop_on_first_match,
                run_all_handlers=run_all_handlers,
                continue_on_error=continue_on_error,
                as_dict=as_dict,
                show_welcome=show_welcome,
            )

    Shad.__module__ = __name__
    return Shad


def __getattr__(name: str):
    if name in {"Shad", "Client", "Messenger"}:
        cls = _load_shad_class()
        globals().update({"Shad": cls, "Client": cls, "Messenger": cls})
        return cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__))

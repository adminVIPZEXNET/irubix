"""Native Shad user-account client."""
from .client import Shad, ShadError, ShadAuthError, ShadAPIError, ShadEvent
Client = Shad
Messenger = Shad
__all__ = ["Shad", "Client", "Messenger", "ShadEvent", "ShadError", "ShadAuthError", "ShadAPIError"]

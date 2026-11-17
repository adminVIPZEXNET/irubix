"""Typed data models and enum values for Rubika Bot API v3.

The API is evolving; these lightweight models intentionally preserve unknown
fields through the raw dictionary returned by the API client.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class APIModel:
    """Base model with safe dictionary conversion."""

    @classmethod
    def from_dict(cls, value: dict[str, Any] | None):
        value = value or {}
        names = getattr(cls, "__dataclass_fields__", {})
        return cls(**{key: item for key, item in value.items() if key in names})

    def to_dict(self) -> dict[str, Any]:
        from dataclasses import asdict
        return asdict(self)


@dataclass
class File(APIModel):
    file_id: str | None = None
    file_name: str | None = None
    size: str | int | None = None


@dataclass
class Chat(APIModel):
    chat_id: str | None = None
    chat_type: str | None = None
    user_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    username: str | None = None


@dataclass
class AuxData(APIModel):
    start_id: str | None = None
    button_id: str | None = None


@dataclass
class Location(APIModel):
    longitude: str | None = None
    latitude: str | None = None


@dataclass
class Bot(APIModel):
    bot_id: str | None = None
    bot_title: str | None = None
    avatar: File | dict | None = None
    description: str | None = None
    username: str | None = None
    start_message: str | None = None
    share_url: str | None = None


@dataclass
class BotCommand(APIModel):
    command: str = ""
    description: str = ""


@dataclass
class ForwardedFrom(APIModel):
    type_from: str | None = None
    message_id: str | None = None
    from_chat_id: str | None = None
    from_sender_id: str | None = None


@dataclass
class ContactMessage(APIModel):
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None


@dataclass
class PollStatus(APIModel):
    state: str | None = None
    selection_index: int = -1
    percent_vote_options: list[int] = field(default_factory=list)
    total_vote: int = 0
    show_total_votes: bool = False


@dataclass
class Poll(APIModel):
    question: str | None = None
    options: list[str] = field(default_factory=list)
    poll_status: PollStatus | dict | None = None


@dataclass
class Message(APIModel):
    message_id: str | None = None
    text: str | None = None
    time: int | str | None = None
    is_edited: bool = False
    sender_type: str | None = None
    sender_id: str | None = None
    aux_data: AuxData | dict | None = None
    file: File | dict | None = None
    reply_to_message_id: str | None = None
    forwarded_from: ForwardedFrom | dict | None = None
    forwarded_no_link: str | None = None
    location: Location | dict | None = None
    sticker: dict | None = None
    contact_message: ContactMessage | dict | None = None
    poll: Poll | dict | None = None


@dataclass
class Update(APIModel):
    type: str | None = None
    chat_id: str | None = None
    removed_message_id: str | None = None
    new_message: Message | dict | None = None
    updated_message: Message | dict | None = None
    event_data: dict | None = None


@dataclass
class InlineMessage(APIModel):
    sender_id: str | None = None
    text: str | None = None
    file: File | dict | None = None
    location: Location | dict | None = None
    aux_data: AuxData | dict | None = None
    message_id: str | None = None
    chat_id: str | None = None


@dataclass
class MetadataPart(APIModel):
    type: str = ""
    from_index: int = 0
    length: int = 0
    link_url: str | None = None
    mention_text_user_id: str | None = None


@dataclass
class Metadata(APIModel):
    meta_data_parts: list[MetadataPart | dict] = field(default_factory=list)


@dataclass
class KeypadRow(APIModel):
    buttons: list[dict] = field(default_factory=list)


@dataclass
class Keypad(APIModel):
    rows: list[KeypadRow | dict] = field(default_factory=list)
    resize_keyboard: bool | None = None
    one_time_keyboard: bool | None = None


# String enums are kept as constants to avoid requiring a third-party package.
class ChatType:
    USER, BOT, GROUP, CHANNEL = "User", "Bot", "Group", "Channel"


class FileType:
    FILE, IMAGE, VOICE, VIDEO, MUSIC, GIF = "File", "Image", "Voice", "Video", "Music", "Gif"


class ChatKeypadType:
    NONE, NEW, REMOVE = "None", "New", "Remove"


class UpdateType:
    UPDATED_MESSAGE = "UpdatedMessage"
    NEW_MESSAGE = "NewMessage"
    REMOVED_MESSAGE = "RemovedMessage"
    STARTED_BOT = "StartedBot"
    STOPPED_BOT = "StoppedBot"
    EVENT_DATA = "EventData"


class ButtonType:
    SIMPLE = "Simple"
    SELECTION = "Selection"
    CALENDAR = "Calendar"
    NUMBER_PICKER = "NumberPicker"
    STRING_PICKER = "StringPicker"
    LOCATION = "Location"
    CAMERA_IMAGE = "CameraImage"
    CAMERA_VIDEO = "CameraVideo"
    GALLERY_IMAGE = "GalleryImage"
    GALLERY_VIDEO = "GalleryVideo"
    FILE = "File"
    AUDIO = "Audio"
    RECORD_AUDIO = "RecordAudio"
    TEXTBOX = "Textbox"
    LINK = "Link"
    ASK_MY_PHONE_NUMBER = "AskMyPhoneNumber"
    ASK_MY_LOCATION = "AskMyLocation"
    BARCODE = "Barcode"


__all__ = [
    "APIModel", "File", "Chat", "AuxData", "Location", "Bot", "BotCommand",
    "ForwardedFrom", "ContactMessage", "PollStatus", "Poll", "Message",
    "Update", "InlineMessage", "MetadataPart", "Metadata", "KeypadRow",
    "Keypad", "ChatType", "FileType", "ChatKeypadType", "UpdateType",
    "ButtonType",
]

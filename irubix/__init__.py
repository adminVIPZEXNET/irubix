"""IRubix: one Python package for Rubika, Bale and Soroush Plus bots."""

from .bot import IRubix, Bot, Event, RubikaAPIError
from . import bale, soroush

__author__ = "mahdishami"
__version__ = "0.5.0"

__all__ = ["IRubix", "Bot", "Event", "RubikaAPIError", "bale", "soroush",
           "__version__", "__author__"]

print("Welcome to the IRubix library")
print("Channel https://Rubika.ir/Liberyirubix")

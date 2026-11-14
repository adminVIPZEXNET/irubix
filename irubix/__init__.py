"""IRubix: one Python package for Rubika, Bale, Soroush Plus and Shad bots."""

from .bot import IRubix, Bot, Event, RubikaAPIError
from . import bale, soroush, shad

__author__ = "mahdishami"
__version__ = "0.6.0"

__all__ = ["IRubix", "Bot", "Event", "RubikaAPIError", "bale", "soroush", "shad",
           "__version__", "__author__"]

print("Welcome to the IRubix library")
print("Channel https://Rubika.ir/Liberyirubix")

"""
Module that holds a interface and sample class for preparing music data for bot to use
"""

import os
import abc
from typing import *

class SourceInterface(abc.ABC):
  """
    Interface to implement for data source classes to add new music source
  """
  @abc.abstractmethod
  def __init__(self, query: str, author: str):
    """
      Initializer that sets a query that was made and author that made it.
    """
    pass

  @abc.abstractmethod
  async def get_source_data(self) -> List[Tuple[Any]]:
    """
      A method that prepares music sources for bot to use,

      :return: Array of tupples that is made of (song_name, url_of_source, song_duration, url_of_source, ctx.author.name)
    """
    pass


class MusicSource(SourceInterface):
  """
    This class is a template class for preparing music data source for use by bot
    it has to have a implementen method get_source_data
  """

  def __init__(self, query, author):
    self.query = query
    self.author = author

  async def get_source_data(self):
    """
      A method that prepares music sources for bot to use,

      :return: Array of tupples that is made of (song_name, url_of_source, song_duration, url_of_source, ctx.author.name)
    """
    pass
          
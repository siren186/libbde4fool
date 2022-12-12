#!/usr/bin/env python
#
# Python-bindings volume type test script
#
# Copyright (C) 2011-2022, Joachim Metz <joachim.metz@gmail.com>
#
# Refer to AUTHORS for acknowledgements.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import os
import random
import sys
import unittest

import pybde


class DataRangeFileObject(object):
  """File-like object that maps an in-file data range."""

  def __init__(self, path, range_offset, range_size):
    """Initializes a file-like object.

    Args:
      path (str): path of the file that contains the data range.
      range_offset (int): offset where the data range starts.
      range_size (int): size of the data range starts, or None to indicate
          the range should continue to the end of the parent file-like object.
    """
    super(DataRangeFileObject, self).__init__()
    self._current_offset = 0
    self._file_object = open(path, "rb")
    self._range_offset = range_offset
    self._range_size = range_size

  def __enter__(self):
    """Enters a with statement."""
    return self

  def __exit__(self, unused_type, unused_value, unused_traceback):
    """Exits a with statement."""
    return

  def close(self):
    """Closes the file-like object."""
    if self._file_object:
      self._file_object.close()
      self._file_object = None

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset in the data range.
    """
    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the data range.
    """
    return self._range_size

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
    """
    if (self._range_offset < 0 or
        (self._range_size is not None and self._range_size < 0)):
      raise IOError("Invalid data range.")

    if self._current_offset < 0:
      raise IOError(
          "Invalid current offset: {0:d} value less than zero.".format(
              self._current_offset))

    if (self._range_size is not None and
        self._current_offset >= self._range_size):
      return b""

    if size is None:
      size = self._range_size
    if self._range_size is not None and self._current_offset + size > self._range_size:
      size = self._range_size - self._current_offset

    self._file_object.seek(
        self._range_offset + self._current_offset, os.SEEK_SET)

    data = self._file_object.read(size)

    self._current_offset += len(data)

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
    if self._current_offset < 0:
      raise IOError(
          "Invalid current offset: {0:d} value less than zero.".format(
              self._current_offset))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._range_size
    elif whence != os.SEEK_SET:
      raise IOError("Unsupported whence.")
    if offset < 0:
      raise IOError("Invalid offset value less than zero.")

    self._current_offset = offset


class VolumeTypeTests(unittest.TestCase):
  """Tests the volume type."""

  def test_signal_abort(self):
    """Tests the signal_abort function."""
    bde_volume = pybde.volume()

    bde_volume.signal_abort()

  def test_open(self):
    """Tests the open function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if unittest.offset:
      raise unittest.SkipTest("source defines offset")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    bde_volume.open(test_source)

    with self.assertRaises(IOError):
      bde_volume.open(test_source)

    bde_volume.close()

    with self.assertRaises(TypeError):
      bde_volume.open(None)

    with self.assertRaises(ValueError):
      bde_volume.open(test_source, mode="w")

  def test_open_file_object(self):
    """Tests the open_file_object function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if not os.path.isfile(test_source):
      raise unittest.SkipTest("source not a regular file")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      with self.assertRaises(IOError):
        bde_volume.open_file_object(file_object)

      bde_volume.close()

      with self.assertRaises(TypeError):
        bde_volume.open_file_object(None)

      with self.assertRaises(ValueError):
        bde_volume.open_file_object(file_object, mode="w")

  def test_close(self):
    """Tests the close function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with self.assertRaises(IOError):
      bde_volume.close()

  def test_open_close(self):
    """Tests the open and close functions."""
    test_source = unittest.source
    if not test_source:
      return

    if unittest.offset:
      raise unittest.SkipTest("source defines offset")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    # Test open and close.
    bde_volume.open(test_source)
    bde_volume.close()

    # Test open and close a second time to validate clean up on close.
    bde_volume.open(test_source)
    bde_volume.close()

    if os.path.isfile(test_source):
      with open(test_source, "rb") as file_object:

        # Test open_file_object and close.
        bde_volume.open_file_object(file_object)
        bde_volume.close()

        # Test open_file_object and close a second time to validate clean up on close.
        bde_volume.open_file_object(file_object)
        bde_volume.close()

        # Test open_file_object and close and dereferencing file_object.
        bde_volume.open_file_object(file_object)
        del file_object
        bde_volume.close()

  def test_is_locked(self):
    """Tests the is_locked function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if unittest.offset:
      raise unittest.SkipTest("source defines offset")

    bde_volume = pybde.volume()

    bde_volume.open(test_source)

    result = bde_volume.is_locked()
    self.assertTrue(result)

    bde_volume.close()

    if unittest.password or unittest.recovery_password:
      bde_volume = pybde.volume()
      if unittest.password:
        bde_volume.set_password(unittest.password)
      if unittest.recovery_password:
        bde_volume.set_recovery_password(unittest.recovery_password)
      if unittest.startup_key:
        bde_volume.read_startup_key(unittest.startup_key)

      bde_volume.open(test_source)

      result = bde_volume.is_locked()
      self.assertFalse(result)

      bde_volume.close()

  def test_read_buffer(self):
    """Tests the read_buffer function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if unittest.offset:
      raise unittest.SkipTest("source defines offset")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    bde_volume.open(test_source)

    size = bde_volume.get_size()

    if size < 4096:
      # Test read without maximum size.
      bde_volume.seek_offset(0, os.SEEK_SET)

      data = bde_volume.read_buffer()

      self.assertIsNotNone(data)
      self.assertEqual(len(data), size)

    # Test read with maximum size.
    bde_volume.seek_offset(0, os.SEEK_SET)

    data = bde_volume.read_buffer(size=4096)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(size, 4096))

    if size > 8:
      bde_volume.seek_offset(-8, os.SEEK_END)

      # Read buffer on size boundary.
      data = bde_volume.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 8)

      # Read buffer beyond size boundary.
      data = bde_volume.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 0)

    # Stress test read buffer.
    bde_volume.seek_offset(0, os.SEEK_SET)

    remaining_size = size

    for _ in range(1024):
      read_size = int(random.random() * 4096)

      data = bde_volume.read_buffer(size=read_size)

      self.assertIsNotNone(data)

      data_size = len(data)

      if read_size > remaining_size:
        read_size = remaining_size

      self.assertEqual(data_size, read_size)

      remaining_size -= data_size

      if not remaining_size:
        bde_volume.seek_offset(0, os.SEEK_SET)

        remaining_size = size

    with self.assertRaises(ValueError):
      bde_volume.read_buffer(size=-1)

    bde_volume.close()

    # Test the read without open.
    with self.assertRaises(IOError):
      bde_volume.read_buffer(size=4096)

  def test_read_buffer_file_object(self):
    """Tests the read_buffer function on a file-like object."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if not os.path.isfile(test_source):
      raise unittest.SkipTest("source not a regular file")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:
      bde_volume.open_file_object(file_object)

      size = bde_volume.get_size()

      # Test normal read.
      data = bde_volume.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), min(size, 4096))

      bde_volume.close()

  def test_read_buffer_at_offset(self):
    """Tests the read_buffer_at_offset function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if unittest.offset:
      raise unittest.SkipTest("source defines offset")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    bde_volume.open(test_source)

    size = bde_volume.get_size()

    # Test normal read.
    data = bde_volume.read_buffer_at_offset(4096, 0)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(size, 4096))

    if size > 8:
      # Read buffer on size boundary.
      data = bde_volume.read_buffer_at_offset(4096, size - 8)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 8)

      # Read buffer beyond size boundary.
      data = bde_volume.read_buffer_at_offset(4096, size + 8)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 0)

    # Stress test read buffer.
    for _ in range(1024):
      random_number = random.random()

      media_offset = int(random_number * size)
      read_size = int(random_number * 4096)

      data = bde_volume.read_buffer_at_offset(read_size, media_offset)

      self.assertIsNotNone(data)

      remaining_size = size - media_offset

      data_size = len(data)

      if read_size > remaining_size:
        read_size = remaining_size

      self.assertEqual(data_size, read_size)

      remaining_size -= data_size

      if not remaining_size:
        bde_volume.seek_offset(0, os.SEEK_SET)

    with self.assertRaises(ValueError):
      bde_volume.read_buffer_at_offset(-1, 0)

    with self.assertRaises(ValueError):
      bde_volume.read_buffer_at_offset(4096, -1)

    bde_volume.close()

    # Test the read without open.
    with self.assertRaises(IOError):
      bde_volume.read_buffer_at_offset(4096, 0)

  def test_seek_offset(self):
    """Tests the seek_offset function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    if unittest.offset:
      raise unittest.SkipTest("source defines offset")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    bde_volume.open(test_source)

    size = bde_volume.get_size()

    bde_volume.seek_offset(16, os.SEEK_SET)

    offset = bde_volume.get_offset()
    self.assertEqual(offset, 16)

    bde_volume.seek_offset(16, os.SEEK_CUR)

    offset = bde_volume.get_offset()
    self.assertEqual(offset, 32)

    bde_volume.seek_offset(-16, os.SEEK_CUR)

    offset = bde_volume.get_offset()
    self.assertEqual(offset, 16)

    if size > 16:
      bde_volume.seek_offset(-16, os.SEEK_END)

      offset = bde_volume.get_offset()
      self.assertEqual(offset, size - 16)

    bde_volume.seek_offset(16, os.SEEK_END)

    offset = bde_volume.get_offset()
    self.assertEqual(offset, size + 16)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      bde_volume.seek_offset(-1, os.SEEK_SET)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      bde_volume.seek_offset(-32 - size, os.SEEK_CUR)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      bde_volume.seek_offset(-32 - size, os.SEEK_END)

    # TODO: change IOError into ValueError
    with self.assertRaises(IOError):
      bde_volume.seek_offset(0, -1)

    bde_volume.close()

    # Test the seek without open.
    with self.assertRaises(IOError):
      bde_volume.seek_offset(16, os.SEEK_SET)

  def test_get_offset(self):
    """Tests the get_offset function."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      offset = bde_volume.get_offset()
      self.assertIsNotNone(offset)

      bde_volume.close()

  def test_get_size(self):
    """Tests the get_size function and size property."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      size = bde_volume.get_size()
      self.assertIsNotNone(size)

      self.assertIsNotNone(bde_volume.size)

      bde_volume.close()

  def test_get_encryption_method(self):
    """Tests the get_encryption_method function and encryption_method property."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      encryption_method = bde_volume.get_encryption_method()
      self.assertIsNotNone(encryption_method)

      self.assertIsNotNone(bde_volume.encryption_method)

      bde_volume.close()

  def test_get_creation_time(self):
    """Tests the get_creation_time function and creation_time property."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      creation_time = bde_volume.get_creation_time()
      self.assertIsNotNone(creation_time)

      self.assertIsNotNone(bde_volume.creation_time)

      bde_volume.close()

  def test_get_description(self):
    """Tests the get_description function and description property."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      description = bde_volume.get_description()
      self.assertIsNotNone(description)

      self.assertIsNotNone(bde_volume.description)

      bde_volume.close()

  def test_get_number_of_key_protectors(self):
    """Tests the get_number_of_key_protectors function and number_of_key_protectors property."""
    test_source = unittest.source
    if not test_source:
      raise unittest.SkipTest("missing source")

    bde_volume = pybde.volume()
    if unittest.password:
      bde_volume.set_password(unittest.password)
    if unittest.recovery_password:
      bde_volume.set_recovery_password(unittest.recovery_password)
    if unittest.startup_key:
      bde_volume.read_startup_key(unittest.startup_key)

    with DataRangeFileObject(
        test_source, unittest.offset or 0, None) as file_object:

      bde_volume.open_file_object(file_object)

      number_of_key_protectors = bde_volume.get_number_of_key_protectors()
      self.assertIsNotNone(number_of_key_protectors)

      self.assertIsNotNone(bde_volume.number_of_key_protectors)

      bde_volume.close()


if __name__ == "__main__":
  argument_parser = argparse.ArgumentParser()

  argument_parser.add_argument(
      "-o", "--offset", dest="offset", action="store", default=None,
      type=int, help="offset of the source file.")

  argument_parser.add_argument(
      "-p", "--password", dest="password", action="store", metavar="PASSWORD",
      default=None, type=str, help="password to unlock the source file.")

  argument_parser.add_argument(
      "-r", "--recovery-password", "--recovery_password",
      dest="recovery_password", action="store", metavar="PASSWORD",
      default=None, type=str, help=(
          "recovery password to unlock the source file."))

  argument_parser.add_argument(
      "-s", "--startup-key", "--startup_key", dest="startup_key",
      action="store", metavar="PATH", default=None, type=str, help=(
          "path of the file containing the startup key to unlock the source "
          "file."))

  argument_parser.add_argument(
      "source", nargs="?", action="store", metavar="PATH",
      default=None, help="path of the source file.")

  options, unknown_options = argument_parser.parse_known_args()
  unknown_options.insert(0, sys.argv[0])

  setattr(unittest, "offset", options.offset)
  setattr(unittest, "password", options.password)
  setattr(unittest, "recovery_password", options.recovery_password)
  setattr(unittest, "startup_key", options.startup_key)
  setattr(unittest, "source", options.source)

  unittest.main(argv=unknown_options, verbosity=2)

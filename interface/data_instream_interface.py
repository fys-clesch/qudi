# -*- coding: utf-8 -*-

"""
Interface for a generic input stream of data points with fixed sampling rate and data type.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

import numpy as np
from enum import Enum
from core.interface import abstract_interface_method
from core.meta import InterfaceMetaclass
from core.interface import ScalarConstraint


class DataInStreamInterface(metaclass=InterfaceMetaclass):
    """
    Interface for a generic input stream of data points with fixed sampling rate and data type.

    You can choose if a preset number of samples is recorded and buffered for read or if samples
    are acquired continuously into a (circular) read buffer.
    """
    @property
    @abstract_interface_method
    def sample_rate(self):
        """
        The currently set sample rate

        @return float: current sample rate in Hz
        """
        pass

    @property
    @abstract_interface_method
    def data_type(self):
        """
        The currently set data type

        @return type: current data type
        """
        pass


    @property
    @abstract_interface_method
    def buffer_size(self):
        """
        The currently set buffer size.
        Buffer size corresponds to the number of samples per channel that can be buffered. So the
        actual buffer size in bytes can be estimated by:
            buffer_size * number_of_channels * size_in_bytes(data_type)

        @return int: current buffer size in samples per channel
        """
        pass

    @property
    @abstract_interface_method
    def use_circular_buffer(self):
        """
        A flag indicating if circular sample buffering is being used or not.

        @return bool: indicate if circular sample buffering is used (True) or not (False)
        """
        pass

    @property
    @abstract_interface_method
    def streaming_mode(self):
        """
        The currently configured streaming mode Enum.

        @return StreamingMode: Finite (StreamingMode.FINITE) or continuous
                               (StreamingMode.CONTINUOUS) data acquisition
        """
        pass

    @property
    @abstract_interface_method
    def all_settings(self):
        """
        Read-only property to return a dict containing all current settings and values that can be
        configured using the method "configure". Basically returns the same as "configure".

        @return dict: Dictionary containing all configurable settings
        """
        pass

    @property
    @abstract_interface_method
    def number_of_channels(self):
        """
        Read-only property to return the currently configured number of data channels.

        @return int: the currently set number of channels
        """
        pass

    @property
    @abstract_interface_method
    def active_channels(self):
        """
        The currently configured data channel properties.
        The channel properties are a dict of the following form:
            channel_property = {'unit': 'V', 'type': StreamChannelType.ANALOG}
            channel_property = {'unit': 'counts', 'type': StreamChannelType.DIGITAL}
            ...

        @return dict: currently active data channel properties with keys being the channel names
                      and values being the corresponding property dicts.
        """
        pass

    @property
    @abstract_interface_method
    def available_channels(self):
        """
        Read-only property to return the currently used data channel properties.
        The channel properties are a dict of the following form:
            channel_property = {'unit': 'V', 'type': StreamChannelType.ANALOG}
            channel_property = {'unit': 'counts', 'type': StreamChannelType.DIGITAL}
            ...

        @return dict: current data channel properties with keys being the channel names and values
                      being the corresponding property dicts.
        """
        pass

    @property
    @abstract_interface_method
    def available_samples(self):
        """
        Read-only property to return the currently available number of samples per channel ready
        to read from buffer.

        @return int: Number of available samples per channel
        """
        pass

    @property
    @abstract_interface_method
    def buffer_overflown(self):
        """
        Read-only flag to check if the read buffer has overflown.
        In case of a circular buffer it indicates data loss.
        In case of a non-circular buffer the data acquisition should have stopped if this flag is
        coming up.
        Flag will only be reset after starting a new data acquisition.

        @return bool: Flag indicates if buffer has overflown (True) or not (False)
        """
        pass

    @property
    @abstract_interface_method
    def is_running(self):
        """
        Read-only flag indicating if the data acquisition is running.

        @return bool: Data acquisition is running (True) or not (False)
        """
        pass

    @abstract_interface_method
    def configure(self, sample_rate=None, data_type=None, streaming_mode=None, active_channels=None,
                  total_number_of_samples=None, buffer_size=None, use_circular_buffer=None):
        """
        Method to configure all possible settings of the data input stream.

        @param float sample_rate: The sample rate in Hz at which data points are acquired
        @param type data_type: The data type of the acquired data. Must be numpy.ndarray compatible.
        @param StreamingMode streaming_mode: The streaming mode to use (finite or continuous)
        @param iterable active_channels: Iterable of channel names (str) to be read from.
        @param int total_number_of_samples: In case of a finite data stream, the total number of
                                            samples to read per channel
        @param int buffer_size: The size of the data buffer to pre-allocate in samples per channel
        @param bool use_circular_buffer: Use circular buffering (True) or stop upon buffer overflow
                                         (False)

        @return dict: All current settings in a dict. Keywords are the same as kwarg names.
        """
        pass

    @abstract_interface_method
    def get_constraints(self):
        """
        Return the constraints on the settings for this data streamer.

        @return DataInStreamConstraints: Instance of DataInStreamConstraints containing constraints
        """
        pass

    @abstract_interface_method
    def start_stream(self):
        """
        Start the data acquisition and data stream.

        @return int: error code (0: OK, -1: Error)
        """
        pass

    @abstract_interface_method
    def stop_stream(self):
        """
        Stop the data acquisition and data stream.

        @return int: error code (0: OK, -1: Error)
        """
        pass

    @abstract_interface_method
    def read_data_into_buffer(self, buffer, number_of_samples=None):
        """
        Read data from the stream buffer into a 1D/2D numpy array given as parameter.
        In case of a single data channel the numpy array can be either 1D or 2D. In case of more
        channels the array must be 2D with the first index corresponding to the channel number and
        the second index serving as sample index:
            buffer.shape == (self.number_of_channels, number_of_samples)
        The numpy array must have the same data type as self.data_type.
        If number_of_samples is omitted it will be derived from buffer.shape[1]

        This method will not return until all requested samples have been read or a timeout occurs.

        @param numpy.ndarray buffer: The numpy array to write the samples to
        @param int number_of_samples: optional, number of samples to read per channel. If omitted,
                                      this number will be derived from buffer axis 1 size.

        @return int: Number of samples read into buffer; negative value indicates error
                     (e.g. read timeout)
        """
        pass

    @abstract_interface_method
    def read_available_data_into_buffer(self, buffer):
        """
        Read data from the stream buffer into a 1D/2D numpy array given as parameter.
        In case of a single data channel the numpy array can be either 1D or 2D. In case of more
        channels the array must be 2D with the first index corresponding to the channel number and
        the second index serving as sample index:
            buffer.shape == (self.number_of_channels, number_of_samples)
        The numpy array must have the same data type as self.data_type.

        This method will read all currently available samples into buffer. If number of available
        samples exceed buffer size, read only as many samples as fit into the buffer.

        @param numpy.ndarray buffer: The numpy array to write the samples to

        @return int: Number of samples read into buffer; negative value indicates error
                     (e.g. read timeout)
        """
        pass

    @abstract_interface_method
    def read_data(self, number_of_samples=None):
        """
        Read data from the stream buffer into a 2D numpy array and return it.
        The arrays first index corresponds to the channel number and the second index serves as
        sample index:
            return_array.shape == (self.number_of_channels, number_of_samples)
        The numpy arrays data type is the one defined in self.data_type.
        If number_of_samples is omitted all currently available samples are read from buffer.

        This method will not return until all requested samples have been read or a timeout occurs.

        @param int number_of_samples: optional, number of samples to read per channel. If omitted,
                                      all available samples are read from buffer.

        @return numpy.ndarray: The read samples
        """
        pass

    @abstract_interface_method
    def read_single_point(self):
        """
        This method will initiate a single sample read on each configured data channel.
        In general this sample may not be acquired simultaneous for all channels and timing in
        general can not be assured. Us this method if you want to have a non-timing-critical
        snapshot of your current data channel input.
        May not be available for all devices.
        The returned 1D numpy array will contain one sample for each channel.

        @return numpy.ndarray: 1D array containing one sample for each channel. Empty array
                               indicates error.
        """
        pass


class StreamChannelType(Enum):
    DIGITAL = 0
    ANALOG = 1


class StreamingMode(Enum):
    CONTINUOUS = 0
    FINITE = 1


class DataInStreamConstraints:
    """
    Collection of constraints for hardware modules implementing SimpleDataInterface.
    """
    def __init__(self, digital_channels=None, analog_channels=None, analog_sample_rate=None,
                 digital_sample_rate=None, combined_sample_rate=None, read_block_size=None,
                 streaming_modes=None, data_types=None, allow_circular_buffer=None):
        if digital_channels is None:
            self.digital_channels = dict()
        else:
            self.digital_channels = {c: p.copy() for c, p in digital_channels.items()}

        if analog_channels is None:
            self.analog_channels = dict()
        else:
            self.analog_channels = {c: p.copy() for c, p in analog_channels.items()}

        if isinstance(analog_sample_rate, ScalarConstraint):
            self.analog_sample_rate = ScalarConstraint(**vars(analog_sample_rate))
        elif isinstance(analog_sample_rate, dict):
            self.analog_sample_rate = ScalarConstraint(**analog_sample_rate)
        else:
            self.analog_sample_rate = ScalarConstraint(min=1, max=np.inf, step=1, default=1)

        if isinstance(digital_sample_rate, ScalarConstraint):
            self.digital_sample_rate = ScalarConstraint(**vars(digital_sample_rate))
        elif isinstance(digital_sample_rate, dict):
            self.digital_sample_rate = ScalarConstraint(**digital_sample_rate)
        else:
            self.digital_sample_rate = ScalarConstraint(min=1, max=np.inf, step=1, default=1)

        if isinstance(combined_sample_rate, ScalarConstraint):
            self.combined_sample_rate = ScalarConstraint(**vars(combined_sample_rate))
        elif isinstance(combined_sample_rate, dict):
            self.combined_sample_rate = ScalarConstraint(**combined_sample_rate)
        else:
            self.combined_sample_rate = ScalarConstraint(min=1, max=np.inf, step=1, default=1)

        if isinstance(read_block_size, ScalarConstraint):
            self.read_block_size = ScalarConstraint(**vars(read_block_size))
        elif isinstance(read_block_size, dict):
            self.read_block_size = ScalarConstraint(**read_block_size)
        else:
            self.read_block_size = ScalarConstraint(min=1, max=np.inf, step=1, default=1)

        if streaming_modes is None:
            self.streaming_modes = (StreamingMode.CONTINUOUS, StreamingMode.FINITE)
        else:
            self.streaming_modes = (mode for mode in streaming_modes if
                                    isinstance(mode, StreamingMode))

        if data_types is None:
            self.data_types = (np.uint32, np.float64)
        else:
            self.data_types = tuple(data_types)

        self.allow_circular_buffer = bool(allow_circular_buffer)
        return

    def copy(self):
        return DataInStreamConstraints(**vars(self))
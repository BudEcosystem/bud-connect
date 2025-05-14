#  -----------------------------------------------------------------------------
#  Copyright (c) 2024 Bud Ecosystem Inc.
#  #
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  #
#      http://www.apache.org/licenses/LICENSE-2.0
#  #
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  -----------------------------------------------------------------------------

"""The constants used in the budconnect module."""

from enum import Enum


class ModalityEnum(Enum):
    """Enumeration of model modalities.

    This enum represents different types of AI model modalities or capabilities.

    Attributes:
        TEXT_INPUT (str): Represents text input modality.
        TEXT_OUTPUT (str): Represents text output modality.
        IMAGE_INPUT (str): Represents image input modality.
        IMAGE_OUTPUT (str): Represents image output modality.
        AUDIO_INPUT (str): Represents audio input modality.
        AUDIO_OUTPUT (str): Represents audio output modality.
    """

    TEXT_INPUT = "text_input"
    TEXT_OUTPUT = "text_output"
    IMAGE_INPUT = "image_input"
    IMAGE_OUTPUT = "image_output"
    AUDIO_INPUT = "audio_input"
    AUDIO_OUTPUT = "audio_output"

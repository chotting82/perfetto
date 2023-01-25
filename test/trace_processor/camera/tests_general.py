#!/usr/bin/env python3
# Copyright (C) 2023 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License a
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from python.generators.diff_tests.testing import Path, Metric
from python.generators.diff_tests.testing import Csv, Json, TextProto
from python.generators.diff_tests.testing import DiffTestBlueprint
from python.generators.diff_tests.testing import DiffTestModule


class CameraGeneral(DiffTestModule):

  def test_camera_ion_mem_trace_android_camera(self):
    return DiffTestBlueprint(
        trace=Path('../../data/camera-ion-mem-trace'),
        query=Metric('android_camera'),
        out=TextProto(r"""
android_camera {
  gc_rss_and_dma {
    min: 47779840.0
    max: 2529583104.0
    avg: 1459479416.3297353
  }
}
"""))

  def test_camera_ion_mem_trace_android_camera_unagg(self):
    return DiffTestBlueprint(
        trace=Path('../../data/camera-ion-mem-trace'),
        query=Metric('android_camera_unagg'),
        out=Path('camera-ion-mem-trace_android_camera_unagg.out'))
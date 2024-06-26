#!/bin/bash
# Copyright (C) 2021 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# See go/perfetto-ui-autopush for docs on how this works end-to-end.

set -exu

env
pwd
mount

# This script will be run in /workspace after the Cloud Build environment has
# pulled the GitHub repo in shallow mode. We want to build off the official
# AOSP repo, not the GitHub mirror though, hence why the clone below.
# GitHub is used only as a trigger. This is because Google Cloud Build doesn't
# support yet triggering from Gerrit.

cd /workspace/
mkdir /workspace/tmp

ls -A1 | xargs rm -rf
UPSTREAM="https://android.googlesource.com/platform/external/perfetto.git"
git clone $UPSTREAM upstream

cd upstream/

# infra/ui.perfetto.dev/cloudbuild_release.yaml sets $1 to the branch
# name when triggering from a release branch. Otherwise $1 is "" when triggering
# from main.
EXTRA_ARGS=""
if [[ ! -z $1 ]]; then
  git checkout $1
  EXTRA_ARGS="--branch_only=$1"
fi

git rev-parse HEAD
python3 -u "ui/release/build_all_channels.py" \
        --upload --tmp=/workspace/tmp $EXTRA_ARGS

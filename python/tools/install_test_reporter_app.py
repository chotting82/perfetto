#!/usr/bin/env python3
# Copyright (C) 2024 The Android Open Source Project
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

import argparse
import os
import re
import sys
import tempfile
import time

from perfetto.prebuilts.perfetto_prebuilts import *

PERMSISION_REGEX = re.compile(r'''uses-permission: name='(.*)'.*''')
NAME_REGEX = re.compile(r'''package: name='(.*?)' .*''')


def cmd(args: list[str]):
  print('Running command ' + ' '.join(args))
  return subprocess.check_output(args)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--apk', help='Local APK to use instead of builtin')

  args = parser.parse_args()

  if args.apk:
    apk = args.apk
  else:
    apk = download_or_get_cached(
        'CtsPerfettoReporterApp.apk',
        'https://storage.googleapis.com/perfetto/CtsPerfettoReporterApp.apk',
        'f21dda36668c368793500b13724ab2a6231d12ded05746f7cfaaba4adedd7d46')

  # Figure out the package name and the permissions we need
  aapt = subprocess.check_output(['aapt', 'dump', 'badging', apk]).decode()
  permission_names = []
  name = ''
  for l in aapt.splitlines():
    name_match = NAME_REGEX.match(l)
    if name_match:
      name = name_match[1]
      continue

    permission_match = PERMSISION_REGEX.match(l)
    if permission_match:
      permission_names.append(permission_match[1])
      continue

  # Root and remount the device.
  cmd(['adb', 'root'])
  cmd(['adb', 'wait-for-device'])
  cmd(['adb', 'remount', '-R'])
  input('The device might now reboot. If so, please unlock the device then '
        'press enter to continue')
  cmd(['adb', 'wait-for-device'])
  cmd(['adb', 'root'])
  cmd(['adb', 'wait-for-device'])
  cmd(['adb', 'remount', '-R'])

  # Write out the permission file on device.
  permissions = '\n'.join(
      f'''<permission name='{p}' />''' for p in permission_names)
  permission_file_contents = f'''
    <permissions>
      <privapp-permissions package="{name}">
        {permissions}
      </privapp-permissions>
    </permissions>
  '''
  with tempfile.NamedTemporaryFile() as f:
    f.write(permission_file_contents.encode())
    f.flush()

    cmd([
        'adb', 'push', f.name,
        f'/system/etc/permissions/privapp-permissions-{name}.xml'
    ])

  # Stop system_server, push the apk on device and restart system_server
  priv_app_path = f'/system/priv-app/{name}/{name}.apk'
  cmd(['adb', 'shell', 'stop'])
  cmd(['adb', 'push', apk, priv_app_path])
  cmd(['adb', 'shell', 'start'])
  cmd(['adb', 'wait-for-device'])
  time.sleep(10)

  # Wait for system_server and package manager to come up.
  while 'system_server' not in cmd(['adb', 'shell', 'ps']).decode():
    time.sleep(1)
  while True:
    ps = set([
        l.strip()
        for l in cmd(['adb', 'shell', 'dumpsys', '-l']).decode().splitlines()
    ])
    if 'storaged' in ps and 'settings' in ps and 'package' in ps:
      break
    time.sleep(1)

  # Install the actual APK.
  cmd(['adb', 'shell', 'pm', 'install', '-r', '-d', '-g', '-t', priv_app_path])

  return 0


sys.exit(main())

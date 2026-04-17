#!/usr/bin/env python
# Copyright 2024 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0

import os
import sys


if __name__ == '__main__':
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'barbican_ui.test.settings'
    )
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

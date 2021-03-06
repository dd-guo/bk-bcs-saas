# -*- coding: utf-8 -*-
#
# Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
# Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
# Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://opensource.org/licenses/MIT
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
import re
from functools import reduce

import arrow

from django.conf import settings
from enum import Enum

import logging

logger = logging.getLogger(__name__)
MOSAIC_REG = re.compile(r"(?<=\d{3})(\d{4})(?=\d{4})")


class ChoicesEnum(Enum):
    """Enum with choices
    """

    @classmethod
    def get_choices(cls):
        return cls._choices_labels.value

    @classmethod
    def get_choice_label(cls, value):
        if isinstance(value, Enum):
            value = value.value
        return dict(cls.get_choices()).get(value, value)

    @classmethod
    def choice_values(cls):
        return [item[1] for item in cls.get_choices()]


def get_client_ip(request):
    """获取客户端IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def mosaic_phone(phone):
    return re.sub(MOSAIC_REG, "****", phone)


def normalize_metric(metric):
    """监控返回标准，保留两位小数
    """
    return float('%.2f' % float(metric))


class RequestToken(object):
    def __init__(self, access_token):
        self.access_token = access_token


class RequestUser(object):
    def __init__(self, username, access_token):
        self.username = username
        self.token = RequestToken(access_token)


class RequestProject(object):
    def __init__(self, project_code):
        self.english_name = project_code


class RequestClass(object):

    def __init__(self, username, access_token, project_code):
        self.user = RequestUser(username, access_token)
        self.project = RequestProject(project_code)


def normalize_datetime(time):
    """time format is YYYY-MM-DD HH:mm:ss
    """
    arrow_time = arrow.get(time, tzinfo=settings.TIME_ZONE)
    return arrow_time.datetime.strftime(settings.REST_FRAMEWORK['DATETIME_FORMAT'])


def getitems(obj, items, default=None):
    """递归获取数据
    """
    try:
        return reduce(lambda x, i: x[i], items, obj)
    except (IndexError, KeyError, TypeError):
        return default


def get_bcs_component_version(cluster_version, bcs_component_version_info, default_version):
    if not cluster_version:
        return default_version

    for component_version, patterns in bcs_component_version_info.items():
        for pattern in patterns:
            if pattern.match(cluster_version):
                return component_version

    return default_version

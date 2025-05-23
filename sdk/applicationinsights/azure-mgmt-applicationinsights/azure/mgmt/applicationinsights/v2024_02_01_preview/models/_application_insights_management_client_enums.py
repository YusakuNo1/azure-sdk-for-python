# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class CategoryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """CategoryType."""

    WORKBOOK = "workbook"
    TSG = "TSG"
    PERFORMANCE = "performance"
    RETENTION = "retention"


class CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of identity that created the resource."""

    USER = "User"
    APPLICATION = "Application"
    MANAGED_IDENTITY = "ManagedIdentity"
    KEY = "Key"


class WorkbookSharedTypeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The kind of workbook. Only valid value is shared."""

    SHARED = "shared"

# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云 - 审计中心 (BlueKing - Audit Center) available.
Copyright (C) 2023 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
We undertake not to change the open source license (MIT license) applicable
to the current version of the project delivered to anyone in the future.
"""

from django.utils.translation import gettext_lazy
from rest_framework import serializers

from services.web.databus.constants import (
    PLUGIN_CONDITION_SEPARATOR_OPTION,
    CollectorParamConditionMatchType,
    CollectorParamConditionTypeEnum,
    EtlConfigEnum,
    PluginSceneChoices,
)
from services.web.databus.models import CollectorPlugin


class PluginConditionSeparatorFiltersSerializer(serializers.Serializer):
    op = serializers.CharField(label=gettext_lazy("匹配方式"), default=PLUGIN_CONDITION_SEPARATOR_OPTION)
    logic_op = serializers.CharField(label=gettext_lazy("逻辑操作符"))
    fieldindex = serializers.CharField(label=gettext_lazy("匹配项所在列"))
    word = serializers.CharField(label=gettext_lazy("匹配值"))


class PluginConditionSerializer(serializers.Serializer):
    """
    插件过滤方式序列化
    """

    type = serializers.ChoiceField(label=gettext_lazy("过滤方式类型"), choices=CollectorParamConditionTypeEnum.choices)
    match_type = serializers.ChoiceField(
        label=gettext_lazy("过滤方式"),
        required=False,
        allow_blank=False,
        allow_null=False,
        choices=CollectorParamConditionMatchType.choices,
    )
    match_content = serializers.CharField(
        label=gettext_lazy("过滤内容"), max_length=255, required=False, allow_null=True, allow_blank=True
    )
    separator = serializers.CharField(
        label=gettext_lazy("分隔符"), trim_whitespace=False, required=False, allow_null=True, allow_blank=True
    )
    separator_filters = PluginConditionSeparatorFiltersSerializer(label=gettext_lazy("过滤规则"), required=False, many=True)

    def validate(self, attrs: dict) -> dict:
        condition_type = attrs.get("type")
        if condition_type == CollectorParamConditionTypeEnum.NONE:
            return {"type": CollectorParamConditionTypeEnum.NONE}
        if condition_type != CollectorParamConditionTypeEnum.SEPARATOR:
            attrs.pop("separator_filters", None)
            attrs.pop("separator", None)
        if condition_type != CollectorParamConditionTypeEnum.MATCH:
            attrs.pop("match_type", None)
            attrs.pop("match_content", None)
        return super().validate(attrs)


class ExtraLabelSerializer(serializers.Serializer):
    """
        采集插件参数-额外标签序列化
    """
    key = serializers.CharField(
        required=True,
        max_length=255,
        label=gettext_lazy("标签key")
    )
    operator = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
        label=gettext_lazy("标签连接符")
    )
    value = serializers.CharField(
        required=True,
        max_length=255,
        label=gettext_lazy("标签value")
    )


class PluginParamSerializer(serializers.Serializer):
    """
        采集插件参数序列化
    """

    paths = serializers.ListField(
        label=gettext_lazy("日志路径"), child=serializers.CharField(max_length=255), required=False
    )
    exclude_files = serializers.ListField(
        label=gettext_lazy("日志路径排除"), child=serializers.CharField(max_length=255), required=False
    )
    conditions = PluginConditionSerializer(required=False)

    # 多行日志配置
    multiline_pattern = serializers.CharField(
        required=False,
        allow_blank=True,
        label=gettext_lazy("行首正则")
    )
    multiline_max_lines = serializers.CharField(
        required=False,
        label=gettext_lazy("最大匹配行数")
    )
    multiline_timeout = serializers.IntegerField(
        required=False,
        min_value=0,
        label=gettext_lazy("最大耗时")
    )

    # 文件采集策略
    tail_files = serializers.BooleanField(
        required=False,
        default=False,
        label=gettext_lazy("是否增量采集")
    )
    ignore_older = serializers.IntegerField(
        required=False,
        min_value=0,
        label=gettext_lazy("文件扫描忽略时间")
    )
    max_bytes = serializers.IntegerField(
        required=False,
        min_value=1,
        label=gettext_lazy("单行日志最大长度")
    )
    scan_frequency = serializers.IntegerField(
        required=False,
        min_value=1,
        label=gettext_lazy("文件扫描间隔")
    )
    close_inactive = serializers.IntegerField(
        required=False,
        min_value=0,
        label=gettext_lazy("FD关联间隔")
    )
    harvester_limit = serializers.IntegerField(
        required=False,
        min_value=1,
        label=gettext_lazy("同时采集数")
    )
    clean_inactive = serializers.IntegerField(
        required=False,
        min_value=0,
        label=gettext_lazy("采集进度清理时间")
    )

    # 标签配置
    extra_labels = serializers.ListField(
        child=ExtraLabelSerializer(),
        required=False,
        default=list,
        label=gettext_lazy("额外标签")
    )

    # Windows事件日志
    winlog_name = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
        label=gettext_lazy("windows事件名称")
    )
    winlog_level = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        label=gettext_lazy("windows事件等级")
    )
    winlog_event_id = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        label=gettext_lazy("windows事件ID")
    )
    winlog_source = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
        label=gettext_lazy("windows事件来源")
    )
    winlog_content = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
        label=gettext_lazy("windows事件内容")
    )

    # Redis配置
    redis_hosts = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        default=list,
        label=gettext_lazy("redis目标")
    )
    redis_password = serializers.CharField(
        required=False,
        allow_blank=True,
        label=gettext_lazy("redis密码")
    )
    redis_password_file = serializers.CharField(
        required=False,
        label=gettext_lazy("redis密码文件")
    )

    # Kafka配置
    kafka_hosts = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        default=list,
        label=gettext_lazy("kafka地址")
    )
    kafka_username = serializers.CharField(
        required=False,
        allow_blank=True,
        label=gettext_lazy("kafka用户名")
    )
    kafka_password = serializers.CharField(
        required=False,
        allow_blank=True,
        label=gettext_lazy("kafka密码")
    )
    kafka_ssl_params = serializers.DictField(
        required=False,
        default=dict,
        label=gettext_lazy("kafka ssl配置")
    )
    kafka_topics = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
        label=gettext_lazy("kafka topic")
    )
    kafka_group_id = serializers.CharField(
        required=False,
        allow_blank=True,
        label=gettext_lazy("kafka 消费组")
    )
    kafka_initial_offset = serializers.ChoiceField(
        choices=['oldest', 'newest'],
        required=False,
        default='newest',
        label=gettext_lazy("初始偏移量")
    )


class ContainerSerializer(serializers.Serializer):
    """
        容器配置序列化
    """
    workload_type = serializers.CharField(
        required=False,
        max_length=255,
        label=gettext_lazy("workload类型")
    )

    workload_name = serializers.CharField(
        required=False,
        max_length=255,
        label=gettext_lazy("workload名称")
    )

    container_name = serializers.CharField(
        required=False,
        max_length=255,
        label=gettext_lazy("容器名称")
    )

    container_name_exclude = serializers.CharField(
        required=False,
        max_length=255,
        label=gettext_lazy("排除容器名称")
    )


class LabelSelectorSerializer(serializers.Serializer):
    """
        标签选择序列化
    """
    match_labels = serializers.ListField(
        child=ExtraLabelSerializer(),  # 复用(key, operator, value)结构
        required=False,
        label=gettext_lazy("指定标签")
    )

    match_expressions = serializers.ListField(
        child=ExtraLabelSerializer(),  # 复用(key, operator, value)结构
        required=False,
        label=gettext_lazy("指定表达式")
    )


class AnnotationSelectorSerializer(serializers.Serializer):
    """
        注解选择序列化
    """
    match_annotations = serializers.ListField(
        child=ExtraLabelSerializer(),  # 复用(key, operator, value)结构
        required=False,
        label=gettext_lazy("指定注解")
    )


class ContainerLogConfigSerializer(serializers.Serializer):
    """
        采集插件参数-容器日志配置序列化
    """
    namespaces = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
        label=gettext_lazy("命名空间")
    )

    namespaces_exclude = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        default=list,
        label=gettext_lazy("排除命名空间")
    )

    paths = serializers.ListField(
        child=serializers.CharField(max_length=1024),
        required=False,
        default=list,
        label=gettext_lazy("日志路径")
    )

    container = ContainerSerializer(
        required=False,
        label=gettext_lazy("指定容器")
    )

    label_selector = LabelSelectorSerializer(
        required=False,
        label=gettext_lazy("标签")
    )

    annotation_selector = AnnotationSelectorSerializer(
        required=False,
        label=gettext_lazy("注解")
    )

    # 引用之前定义的 LogCollectorSerializer
    params = PluginParamSerializer(
        required=True,
        label=gettext_lazy("日志采集参数")
    )

    data_encoding = serializers.CharField(
        required=False,
        max_length=50,
        label=gettext_lazy("日志字符集")
    )

    collector_type = serializers.ChoiceField(
        choices=[
            ('container_log_config', gettext_lazy('容器')),
            ('node_log_config', gettext_lazy('节点')),
            ('std_log_config', gettext_lazy('标准输出'))
        ],
        required=True,
        label=gettext_lazy("容器采集类型")
    )


class PluginBaseSerializer(serializers.Serializer):
    namespace = serializers.CharField(label=gettext_lazy("命名空间"))
    etl_config = serializers.CharField(label=gettext_lazy("清洗配置"), default=EtlConfigEnum.BK_LOG_JSON.value)
    etl_params = serializers.JSONField(label=gettext_lazy("清洗参数"), allow_null=True, default=dict)
    is_default = serializers.BooleanField(label=gettext_lazy("作为默认插件"), default=False)
    extra_fields = serializers.ListField(
        label=gettext_lazy("拓展字段"), allow_null=True, required=False, child=serializers.JSONField()
    )

    def validate_etl_params(self, value: dict):
        value = value or dict()
        value["retain_original_text"] = True
        return value


class CreatePluginRequestSerializer(PluginBaseSerializer):
    plugin_scene = serializers.ChoiceField(
        label=gettext_lazy("插件场景"), choices=PluginSceneChoices.choices, default=PluginSceneChoices.COLLECTOR
    )


class UpdatePluginRequestSerializer(CreatePluginRequestSerializer):
    collector_plugin_id = serializers.IntegerField(label=gettext_lazy("采集插件ID"))


class CreatePluginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectorPlugin
        fields = ["collector_plugin_id", "collector_plugin_name"]


class PluginListResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectorPlugin
        fields = "__all__"

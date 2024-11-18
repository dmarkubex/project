from datahub.emitter.mce_builder import make_data_platform_urn, make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

# Imports for metadata model classes
from datahub.metadata.schema_classes import (
    AuditStampClass,
    OtherSchemaClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    SchemaMetadataClass,
    StringTypeClass,
    DatasetPropertiesClass,
)

# DataHub 配置
datahub_rest_url = "http://10.1.10.43:8080"  # 替换为你的 DataHub 服务器地址
datahub_token = "eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6ImRhdGFodWIiLCJ0eXBlIjoiUEVSU09OQUwiLCJ2ZXJzaW9uIjoiMiIsImp0aSI6IjMxYzEwZjc3LTYzYTMtNDBjOS1iZmIyLTU4ZDUyNjY1MjA0MSIsInN1YiI6ImRhdGFodWIiLCJleHAiOjE3MzQ0OTk3MDYsImlzcyI6ImRhdGFodWItbWV0YWRhdGEtc2VydmljZSJ9.IuOZKeDmW187jMHHa80VW23vrivVZgor0WsXDnbNfZs"  # 替换为你的 DataHub 访问令牌

# 创建 rest emitter 并添加身份验证头
rest_emitter = DatahubRestEmitter(
    gms_server=datahub_rest_url,
    extra_headers={"Authorization": f"Bearer {datahub_token}"}
)

# 实体列表
entities = [
    {
        "name": "query.test3.card",
        "developer": "jdoe",
        "filename": "oil_card_dashboard",
        "description": "This is a sample dashboard for oil card queries",
        "online_time": 1640692800000,
    },
    {
        "name": "query.test4.card",
        "developer": "asmith",
        "filename": "gas_card_dashboard",
        "description": "This is a sample dashboard for gas card queries",
        "online_time": 1640692800000,
    },
    # 添加更多实体
]

# 遍历实体列表并发送 MetadataChangeProposalWrapper
for entity in entities:
    # 创建 SchemaMetadataClass
    schema_metadata = SchemaMetadataClass(
        schemaName="dashboard",
        platform=make_data_platform_urn("finereport"),
        version=0,
        hash="",
        platformSchema=OtherSchemaClass(rawSchema="__insert raw schema here__"),
        lastModified=AuditStampClass(
            time=entity["online_time"], actor=f"urn:li:corpuser:{entity['developer']}"
        ),
        fields=[
            SchemaFieldClass(
                fieldPath="developer",
                type=SchemaFieldDataTypeClass(type=StringTypeClass()),
                nativeDataType="STRING",
                description="",
                lastModified=AuditStampClass(
                    time=entity["online_time"], actor=f"urn:li:corpuser:{entity['developer']}"
                ),
            ),
            SchemaFieldClass(
                fieldPath="filename",
                type=SchemaFieldDataTypeClass(type=StringTypeClass()),
                nativeDataType="STRING",
                description="",
                lastModified=AuditStampClass(
                    time=entity["online_time"], actor=f"urn:li:corpuser:{entity['developer']}"
                ),
            ),
        ],
    )

    # 创建 DatasetPropertiesClass
    dataset_properties = DatasetPropertiesClass(
        description=entity["description"]
    )

    # 创建 MetadataChangeProposalWrapper 并发送到 DataHub
    schema_event = MetadataChangeProposalWrapper(
        entityUrn=make_dataset_urn(platform="finereport", name=entity["name"], env="PROD"),
        aspect=schema_metadata,
    )
    rest_emitter.emit(schema_event)

    # 创建 MetadataChangeProposalWrapper 并发送到 DataHub
    properties_event = MetadataChangeProposalWrapper(
        entityUrn=make_dataset_urn(platform="finereport", name=entity["name"], env="PROD"),
        aspect=dataset_properties,
    )
    rest_emitter.emit(properties_event)
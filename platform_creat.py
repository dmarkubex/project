from datahub.emitter.mce_builder import make_data_platform_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DataPlatformInfoClass,
    DataPlatformKeyClass,
)

# 创建 DataHub REST 发射器，添加身份验证信息
rest_emitter = DatahubRestEmitter(
    gms_server="http://10.1.10.43:8080",
    token="eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6ImRhdGFodWIiLCJ0eXBlIjoiUEVSU09OQUwiLCJ2ZXJzaW9uIjoiMiIsImp0aSI6IjYxZmMxYjc5LTU3NTMtNDlkYy04NWIxLTM1MzNhNzQ4OWRhNiIsInN1YiI6ImRhdGFodWIiLCJleHAiOjE3MzM1NTQxMjksImlzcyI6ImRhdGFodWItbWV0YWRhdGEtc2VydmljZSJ9.Az6s1VRSiAzcYV60QrfD-Y3x_Rm-ZhRMECGrr_-AYlM"  # 替换为你的实际 API 令牌
)

# 创建 DataPlatformKey
data_platform_key = DataPlatformKeyClass(platformName="Finereport")

# 创建 DataPlatformInfo
data_platform_info = DataPlatformInfoClass(
    name="Finereport",
    displayName="帆软Finereport",
    type="OTHERS",
    datasetNameDelimiter="/",
    logoUrl="https://src.fanruan.com/website/finereport/logo.png"
)

# 创建 MetadataChangeProposalWrapper
mcp = MetadataChangeProposalWrapper(
    entityUrn=make_data_platform_urn("Finereport"),
    aspect=data_platform_info,
)

# 发送 MCP
rest_emitter.emit(mcp)
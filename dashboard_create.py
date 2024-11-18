from datahub.emitter.mce_builder import make_dashboard_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DashboardInfoClass,
    OwnerClass,
    OwnershipClass,
    OwnershipTypeClass,
    AuditStampClass,
)

# 创建 DataHub REST 发射器，添加身份验证信息
rest_emitter = DatahubRestEmitter(
    gms_server="http://10.1.10.43:8080",
    token="eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6ImRhdGFodWIiLCJ0eXBlIjoiUEVSU09OQUwiLCJ2ZXJzaW9uIjoiMiIsImp0aSI6IjYxZmMxYjc5LTU3NTMtNDlkYy04NWIxLTM1MzNhNzQ4OWRhNiIsInN1YiI6ImRhdGFodWIiLCJleHAiOjE3MzM1NTQxMjksImlzcyI6ImRhdGFodWItbWV0YWRhdGEtc2VydmljZSJ9.Az6s1VRSiAzcYV60QrfD-Y3x_Rm-ZhRMECGrr_-AYlM"  # 替换为你的实际 API 令牌
)

# 创建 DashboardInfo
dashboard_info = DashboardInfoClass(
    description="这是一个示例仪表板",
    title="示例仪表板",
    lastModified=AuditStampClass(
        time=1640692800000, actor="urn:li:corpuser:ingestion"
    ),
    dashboardUrl="https://example.com/dashboard",
    charts=["urn:li:chart:(finereport,chart1)", "urn:li:chart:(finereport,chart2)"],
    customProperties={"propertyKey": "propertyValue"}
)

# 创建 Ownership
ownership = OwnershipClass(
    owners=[
        OwnerClass(
            owner="urn:li:corpuser:your_username",
            type=OwnershipTypeClass.DATAOWNER
        )
    ],
    lastModified=AuditStampClass(
        time=1640692800000, actor="urn:li:corpuser:ingestion"
    )
)

# 创建 MetadataChangeProposalWrapper for Dashboard
mcp_dashboard = MetadataChangeProposalWrapper(
    entityUrn=make_dashboard_urn("finereport", "example_dashboard"),
    aspect=dashboard_info,
)

# 创建 MetadataChangeProposalWrapper for Ownership
mcp_ownership = MetadataChangeProposalWrapper(
    entityUrn=make_dashboard_urn("finereport", "example_dashboard"),
    aspect=ownership,
)

# 发送 MCP for Dashboard
rest_emitter.emit(mcp_dashboard)

# 发送 MCP for Ownership
rest_emitter.emit(mcp_ownership)
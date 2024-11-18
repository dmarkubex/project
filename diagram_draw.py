from diagrams import Cluster, Diagram
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.compute import AppEngine, Functions
from diagrams.gcp.database import BigTable
from diagrams.gcp.iot import IotCore
from diagrams.gcp.storage import GCS
from diagrams.gcp.ml import AIPlatform,AIHub,TextToSpeech,SpeechToText,VisionAPI,AdvancedSolutionsLab,NaturalLanguageAPI,AIPlatformDataLabelingService
from diagrams.gcp.migration import TransferAppliance
from diagrams.onprem.database import Oracle, MySQL
from diagrams.azure.compute import CloudServicesClassic

with Diagram("远东AI应用框架", show=True):
    AI_sub = AIHub("AI应用平台")

    with Cluster("业务数据源"):
        rawdata=[
            Oracle("ERP"),
            MySQL("EAM")] >> AI_sub
    
    with Cluster("AI模型能力底座"):
        with Cluster("外部模型API"): 
            modelapi=[
                CloudServicesClassic("moonshot大模型"),
                CloudServicesClassic("通义千问大模型")] 
            
        with Cluster("自有模型框架"):
            selfmodel=[
                AdvancedSolutionsLab("LLM模型"),
                TransferAppliance("Embedding模型"),
                AIPlatformDataLabelingService("Rerank模型"),
                SpeechToText("语音模型"),
                VisionAPI("图像模型"),
                NaturalLanguageAPI("OCR模型")
                ]

    with Cluster("Targets"):
        with Cluster("Data Flow"):
            flow = Dataflow("data flow")

        with Cluster("Data Lake"):
            flow >> [BigQuery("bq"),
                     GCS("storage")]

        with Cluster("Event Driven"):
            with Cluster("Processing"):
                flow >> AppEngine("engine") >> BigTable("bigtable")

            with Cluster("Serverless"):
                flow >> Functions("func") >> AppEngine("appengine")

    AI_sub >> flow
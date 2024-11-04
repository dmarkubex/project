from diagrams import Cluster, Diagram
from diagrams.gcp.analytics import BigQuery, Dataflow, PubSub
from diagrams.gcp.compute import AppEngine, Functions
from diagrams.gcp.database import BigTable
from diagrams.gcp.iot import IotCore
from diagrams.gcp.storage import GCS
from diagrams.onprem.database import Oracle, MySQL

with Diagram("Message Collecting", show=True):
    pubsub = PubSub("pubsub")

    with Cluster("Raw Data"):
        rawdata=[
            Oracle("ERP"),
            MySQL("EAM")] >> pubsub

    with Cluster("Source of Data"):
        sourcedata=[
            IotCore("core1"),
            IotCore("core2"),
            IotCore("core3")] >> pubsub

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

    rawdata >> sourcedata
    pubsub >> flow
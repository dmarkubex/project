import pymysql
import json
import requests
from datetime import datetime

# 数据库连接配置
db_config = {
    'user': 'app',
    'password': 'YDeam@2023..',
    'host': '10.1.14.30',
    'database': 'sieiot_eam'
}

# SQL查询
query1 = """
WITH repair_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477838893308198912,608595992509431936,576765418279026688,611121021289775104,492348235206115584)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND ibp.psn_name NOT IN ('华清', '滕峰')
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
),
leader_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477838893308198912,611121021289775104)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
)
SELECT distinct  ewm.ew_id,
       8 AS alarm_times,
       JSON_OBJECT(
           'title', '设备维修超8小时预警',
           'text', CONCAT(
               '![](https://directus.fegroup.cn:8055/assets/acb71459-308f-44b1-b994-f4fcbf652ec1/banner.png) \n\n ',
               '### <font color="#FF5733">设备报修超8小时未维修完成，请关注</font> \n\n',
               '---\n\n',
               '+ **责任维修班组：** ', leader_query.repair_leader_name, '班组\n\n',
               '+ **所在厂区：** ', (case when ewm.asset_location like '%智能电缆%' then '复合厂' else  eeac.factory_name end), '\n\n',
               '+ **设备位置：** ', ewm.asset_location, '\n\n',
               '+ **设备编号：** ', eeac.ac_code, '\n\n',
               '+ **设备名称：** ', ewm.ac_name, '\n\n',
               '+ **故障单号：** ', ewm.work_order_number, '\n\n',
               '+ **故障类型：** ', IFNULL(eer.fault_phenomenon, eer.efr_info), '\n\n',
               '+ **报修时间：** ', ewm.repair_time, '\n\n',
               '---'
           ),
           'userIds', repair_query.repair_leader
       ) AS json_message,
       repair_query.repair_leader,
       repair_query.repair_leader_name
FROM eam_workorder_m ewm
INNER JOIN eam_eledger_asset_card eeac ON ewm.ac_code = eeac.ac_code
LEFT JOIN eam_efault_repair eer ON ewm.repair_number = eer.efr_code
LEFT JOIN repair_query ON ewm.department_id = repair_query.department_id
LEFT JOIN leader_query ON ewm.department_id = leader_query.department_id
WHERE ewm.delete_flag = 0
  AND TIMESTAMPDIFF(HOUR, ewm.repair_time, NOW()) > 8
  AND SUBSTR(eeac.asset_code, 1, 2) IN ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12','14')
  AND ewm.work_order_status IN (2,3,9)
  AND not exists(
              select '1'
                  from message_levelup_his mlh
                where mlh.message_id=ewm.ew_id
                and mlh.alarm_times=8
        )
"""

query2 = """
WITH repair_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477839225249611776,477838893308198912,477838680283693056,514399706823016448,608595992509431936,576765418279026688,611121021289775104,492348235206115584)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
),
leader_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477838893308198912,611121021289775104)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
)
SELECT distinct  ewm.ew_id,
       12 AS alarm_times,
       JSON_OBJECT(
           'title', '设备维修超12小时预警',
           'text', CONCAT(
               '![](https://directus.fegroup.cn:8055/assets/acb71459-308f-44b1-b994-f4fcbf652ec1/banner.png) \n\n ',
               '### <font color="#FF5733">设备报修超12小时未维修完成，请关注</font> \n\n',
               '---\n\n',
               '+ **责任维修班组：** ', leader_query.repair_leader_name, '班组\n\n',
               '+ **所在厂区：** ', (case when ewm.asset_location like '%智能电缆%' then '复合厂' else  eeac.factory_name end), '\n\n',
               '+ **设备位置：** ', ewm.asset_location, '\n\n',
               '+ **设备编号：** ', eeac.ac_code, '\n\n',
               '+ **设备名称：** ', ewm.ac_name, '\n\n',
               '+ **故障单号：** ', ewm.work_order_number, '\n\n',
               '+ **故障类型：** ', IFNULL(eer.fault_phenomenon, eer.efr_info), '\n\n',
               '+ **报修时间：** ', ewm.repair_time, '\n\n',
               '---'
           ),
           'userIds', repair_query.repair_leader
       ) AS json_message,
       repair_query.repair_leader,
       repair_query.repair_leader_name
FROM eam_workorder_m ewm
INNER JOIN eam_eledger_asset_card eeac ON ewm.ac_code = eeac.ac_code
LEFT JOIN eam_efault_repair eer ON ewm.repair_number = eer.efr_code
LEFT JOIN repair_query ON ewm.department_id = repair_query.department_id
LEFT JOIN leader_query ON ewm.department_id = leader_query.department_id
WHERE ewm.delete_flag = 0
  AND TIMESTAMPDIFF(HOUR, ewm.repair_time, NOW()) > 12
  AND SUBSTR(eeac.asset_code, 1, 2) IN ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12','14')
  AND ewm.work_order_status IN (2,3,9)
  AND not exists(
              select '1'
                  from message_levelup_his mlh
                where mlh.message_id=ewm.ew_id
                and mlh.alarm_times=12
        )
"""

query3 = """
WITH repair_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477839225249611776,477838893308198912,477838680283693056,514399706823016448,514431453182836736,608595992509431936,576765418279026688,611121021289775104,608604240197206144)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
),
leader_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477838893308198912,611121021289775104)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
)
SELECT distinct  ewm.ew_id,
       24 AS alarm_times,
       JSON_OBJECT(
           'title', '设备维修超24小时预警',
           'text', CONCAT(
               '![](https://directus.fegroup.cn:8055/assets/acb71459-308f-44b1-b994-f4fcbf652ec1/banner.png) \n\n ',
               '### <font color="#FF5733">设备报修超24小时未维修完成，请关注</font> \n\n',
               '---\n\n',
               '+ **责任维修班组：** ', leader_query.repair_leader_name, '班组\n\n',
               '+ **所在厂区：** ', (case when ewm.asset_location like '%智能电缆%' then '复合厂' else  eeac.factory_name end), '\n\n',
               '+ **设备位置：** ', ewm.asset_location, '\n\n',
               '+ **设备编号：** ', eeac.ac_code, '\n\n',
               '+ **设备名称：** ', ewm.ac_name, '\n\n',
               '+ **故障单号：** ', ewm.work_order_number, '\n\n',
               '+ **故障类型：** ', IFNULL(eer.fault_phenomenon, eer.efr_info), '\n\n',
               '+ **报修时间：** ', ewm.repair_time, '\n\n',
               '---'
           ),
           'userIds', repair_query.repair_leader
       ) AS json_message,
       repair_query.repair_leader,
       repair_query.repair_leader_name
FROM eam_workorder_m ewm
INNER JOIN eam_eledger_asset_card eeac ON ewm.ac_code = eeac.ac_code
LEFT JOIN eam_efault_repair eer ON ewm.repair_number = eer.efr_code
LEFT JOIN repair_query ON ewm.department_id = repair_query.department_id
LEFT JOIN leader_query ON ewm.department_id = leader_query.department_id
WHERE ewm.delete_flag = 0
  AND TIMESTAMPDIFF(HOUR, ewm.repair_time, NOW()) > 24
  AND SUBSTR(eeac.asset_code, 1, 2) IN ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
  AND ewm.work_order_status IN (2,3,9)
  AND ewm.department_name <> '设备服务部'
  AND not exists(
              select '1'
                  from message_levelup_his mlh
                where mlh.message_id=ewm.ew_id
                and mlh.alarm_times=24
        )
"""

query4 = """
WITH repair_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477839225249611776,477838893308198912,477838680283693056,514399706823016448,514431453182836736,604342833729519616,608595992509431936,576765418279026688,611121021289775104,608604240197206144)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
),
leader_query AS (
    SELECT iu.login_account AS repair_leader,
           iu.psn_name AS repair_leader_name,
           ieudp.permissions_id AS department_id,
           ieudp.name AS department_name
    FROM iot_eam_user_data_permissions ieudp
    INNER JOIN (
        SELECT iu.user_id, iu.login_account, ibp.psn_name
        FROM sieiot_gushen.iot_base_user iu
        INNER JOIN sieiot_gushen.iot_base_user_role ibur
            ON iu.user_id = ibur.user_id
            AND ibur.role_id IN (477838893308198912,611121021289775104)
        INNER JOIN sieiot_gushen.iot_base_person ibp ON ibp.psn_id = iu.psn_id
        WHERE iu.login_account IS NOT NULL
          AND use_status = '1'
    ) iu ON ieudp.user_id = iu.user_id
    WHERE type = 1
)
SELECT distinct  ewm.ew_id,
       72 AS alarm_times,
       JSON_OBJECT(
           'title', '设备维修超72小时预警',
           'text', CONCAT(
               '![](https://directus.fegroup.cn:8055/assets/acb71459-308f-44b1-b994-f4fcbf652ec1/banner.png) \n\n ',
               '### <font color="#FF5733">设备报修超72小时未维修完成，请关注</font> \n\n',
               '---\n\n',
               '+ **责任维修班组：** ', leader_query.repair_leader_name, '班组\n\n',
               '+ **所在厂区：** ', (case when ewm.asset_location like '%智能电缆%' then '复合厂' else  eeac.factory_name end), '\n\n',
               '+ **设备位置：** ', ewm.asset_location, '\n\n',
               '+ **设备编号：** ', eeac.ac_code, '\n\n',
               '+ **设备名称：** ', ewm.ac_name, '\n\n',
               '+ **故障单号：** ', ewm.work_order_number, '\n\n',
               '+ **故障类型：** ', IFNULL(eer.fault_phenomenon, eer.efr_info), '\n\n',
               '+ **报修时间：** ', ewm.repair_time, '\n\n',
               '---'
           ),
           'userIds', repair_query.repair_leader
       ) AS json_message,
       repair_query.repair_leader,
       repair_query.repair_leader_name
FROM eam_workorder_m ewm
INNER JOIN eam_eledger_asset_card eeac ON ewm.ac_code = eeac.ac_code
LEFT JOIN eam_efault_repair eer ON ewm.repair_number = eer.efr_code
LEFT JOIN repair_query ON ewm.department_id = repair_query.department_id
LEFT JOIN leader_query ON ewm.department_id = leader_query.department_id
WHERE ewm.delete_flag = 0
  AND TIMESTAMPDIFF(HOUR, ewm.repair_time, NOW()) > 72
  AND SUBSTR(eeac.asset_code, 1, 2) IN ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
  AND ewm.work_order_status IN (2,3,9)
  AND ewm.department_name <> '设备服务部'
  AND not exists(
              select '1'
                  from message_levelup_his mlh
                where mlh.message_id=ewm.ew_id
                and mlh.alarm_times=72
        )
"""

# 插入查询
insert_query= """
    INSERT INTO message_levelup_his (message_id, alarm_times, alarm_person, message)
    VALUES (%s, %s, %s, %s)
"""

# 执行查询并获取结果
def execute_query(query):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

# 发送POST请求
def send_post_request(url, data):
    if not data or all((not msg['text'].strip() for msg in json.loads(data))):  # 避免发送空消息
        print('Empty message, not sending.')
        return None
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=data)
    return response

# 插入数据到历史表
def insert_into_history(insert_query, data):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    try:
        cursor.executemany(insert_query, data)
        connection.commit()
    except pymysql.Error as e:
        print(f"Error inserting data into history: {e}")
    finally:
        cursor.close()
        connection.close()

# 处理查询结果并发送POST请求
def process_query_results(query):
    results = execute_query(query)

    # 准备JSON消息
    json_messages = []
    for row in results:
        json_message = json.loads(row['json_message'])
        json_messages.append(json_message)

    # 打印JSON消息
    print(json.dumps(json_messages, ensure_ascii=False, indent=4))

    if not json_messages:
        print('json_messages is empty, not calling the post request.')
        return

    # 格式化数据并编码为UTF-8
    formatted_data = json.dumps(json_messages, ensure_ascii=False).encode('utf-8')

    # 发送POST请求
    url = "https://ai.fegroup.cn:8082/api/devicesmessage"
    response = send_post_request(url, formatted_data)

    # 检查响应并插入数据
    if response.status_code == 200:
        print("Data sent successfully!")
        
        # 准备插入数据
        insert_data = [
            (
                row['ew_id'],
                row['alarm_times'],
                row['repair_leader_name'],
                json.dumps(json.loads(row['json_message']), ensure_ascii=False)
            )
            for row in results
        ]
        
        # 插入数据到历史表
        insert_into_history(insert_query, insert_data)
        print("Data inserted into message_levelup_his successfully!")
    else:
        print(f"Failed to send data. Status code: {response.status_code}")

# 主程序
def main():
    queries = [query1, query2, query3, query4]
    for query in queries:
        process_query_results(query)

if __name__ == "__main__":
    main()

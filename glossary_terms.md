### 已报修未完成超8小时

```markdown
# 业务属性：
1.数据定义：反映已报修超过12小时未完成维修的工单数量
2.指标计算逻辑：报修时间=当前时间点-故障报修时间点
3.测量方式：实时数据
4.数据记录方式：实时数据
5.分析维度：产业、公司生产厂区、使用部门
6.更新时间/频次：实时更新
7.数据来源：eam_workorder_m、pro_eam_org_dimension

```

&nbsp;

```markup
select count(case when timestampdiff(hour,repair_time, now()) > 8 then 1 end)  as over_8_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 12 then 1 end) as over_12_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 24 then 1 end) as over_24_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 72 then 1 end) as over_72_hours
from (
select eod.industry,
       eod.company_name company,
       eod.factory_name fac_name,
       eod.dep_id dept_id,
       eod.dep_code dept_code,
       ewm.repair_time
from eam_workorder_m ewm
     left join pro_eam_org_dimension eod on ewm.department_id=eod.dep_id
where ewm.delete_flag = 0
      and ewm.work_order_status < 5 -- 状态小于5表示未完成
)x1
where 1=1
     ${if(level==1,"and industry = '"+cy+"' "," ")}
     ${if(level==2,"and company = '"+company+"' "," ")}
     ${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
     ${if(level==4,"and dept_id = '"+dept_id+"' "," ")}

```

### 设备运行台数

```markdown
# 业务属性
1.指标定义：当前时间处于开机状态的关键工序数采设备的数量（台）
2.指标逻辑：关键工序设备数采实时状态为开机的设备数量
3.数据类型：实时数据
4.指标类型：原子指标
5.分析维度：电缆产业、公司、生产厂区、使用部门、重要设备、一般设备
6.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 实时数据 -> 数采设备运行状态分析
7. 数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_organization_v、yd_device_org_plane）

# BI逻辑
1. 备注：与`设备停机台数`、`设备停机占比`、`设备总数量`指标共用BI数据集
2. 所用字段：开机
3. BI SQL

```

```markdown
 select  
    count(1) 连接数 ,
    count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 停机,
    sum( CASE WHEN (device_status = 2 and work_status='Y') THEN 1 ELSE 0 END ) 作业,
    sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 开机,
    sum( CASE WHEN device_status > 0 THEN 1 ELSE 0 END ) 在线,
    (count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END )) / count(1) as 停机占比
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 当期故障总次数

```markdown
# 业务属性：
1.数据定义：当期故障总次数反映一段时间内的故障发生总次数，包含设备故障及委外维修
2.指标计算逻辑公式：当期故障总次数=∑（故障工单数量+委外维修工单数量）    
                  剔除单据状态为驳回的数据
3.测量方式：日、月、年 （累计数据）
4.指标类型：复合指标
5.分析维度：设备重要性（一般、重要）、设备分类、故障次数、故障原因
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.数据来源：故障工单表eam_workorder_m
           工单管理-故障工单           
           工单管理-委外维修工单
8.展示路径：
（1）移动端：设备域首页 -> 累计数据 -> 设备故障情况分析 -> 当期故障总次数

```

&nbsp;

```markup
with base as
    (select
        ewm.ac_code,
        eeac.asset_name,
        ewm.work_order_number,
        eod.dep_id,
        eod.dep_name,
        eod.factory_id,
        eod.factory_name as fac_name,
        eod.company_id,
        eod.company_name as company,
        eod.industry
    from eam_workorder_m ewm
        left join eam_eledger_asset_card eeac on ewm.ac_code=eeac.ac_code
    join pro_eam_org_dimension eod on ewm.department_id = eod.dep_id
    where eeac.delete_flag=0
${if(datetype==1,"and substr(ewm.creation_date, 1, 10) = '"+acc_date+"' "," ")}
${if(datetype==2,"and substr(ewm.creation_date, 1, 7) = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and substr(ewm.creation_date, 1, 4) = substr('"+acc_date+"',1,4) "," ")}
    )
select asset_name,
dep_name,
count(work_order_number) as 故障次数
from base
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(fac_name1!="","and fac_name = '"+fac_name1+"' ",if(level==3,"and fac_name = '"+fac_name+"' ",""))}
${if(level==4,"and dep_id = '"+dept_id+"' "," ")}
group by dep_name,asset_name

```

### 组内机修工工作状态详情

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

```markdown
with repair_query as (SELECT i.repair_person_code,
                             round(sum(i.repair_hour), 2) AS repair_hour
                      FROM iot_repair_person_cost i
                      WHERE i.repair_type = 'repair'
                        and i.acc_date = '${acc_date}'
                      GROUP BY i.repair_person_code),
     plan_query as (SELECT i.repair_person_code,
                           round(sum(i.repair_hour), 2) AS repair_hour
                    FROM iot_repair_person_cost i
                    WHERE i.repair_type = 'plan'
                      and i.acc_date = '${acc_date}'
                    GROUP BY i.repair_person_code),
     maintence_query as (SELECT i.repair_person_code,
                                round(sum(i.repair_hour), 2) AS repair_hour
                         FROM iot_repair_person_cost i
                         WHERE i.repair_type = 'maintence'
                           and i.acc_date = '${acc_date}'
                         GROUP BY i.repair_person_code),
     all_query as (select m.repair_person_code,
                          m.repair_hour
                   from repair_query m
                   union all
                   select m.repair_person_code,
                          m.repair_hour
                   from plan_query m
                   union all
                   select m.repair_person_code,
                          m.repair_hour
                   from maintence_query m),
     hour_use as (select aq.repair_person_code
                       , sum(aq.repair_hour) as repair_hour
                  from all_query aq
                  group by aq.repair_person_code),
     plan_cnt as (select '计划维修'            as repair_type,
                         peet.team_member_code AS user_code,
                         peet.team_member_name AS user_name,
                         peet.team_name,
                         count(1)                 order_cnt
                  from eam_workorder_slave ews
                           LEFT JOIN pro_eam_eledger_team peet ON ews.executor_id = peet.team_member_id
                           left join eam_workorder_slave_record ews2 on ews.ews_id = ews2.ews_id
                  where  ews.work_order_type = 4
                    and ews.delete_flag = 0
                    and ews.work_order_status = 4
                    AND DATE_FORMAT(ews.actual_begin_time, '%Y-%m-%d') = '${acc_date}'
                  group by  peet.team_member_code,
                           peet.team_member_name),
     maintence_cnt as (select '二级保养'            as repair_type,
                              peet.team_member_code AS user_code,
                              peet.team_member_name AS user_name,
                              peet.team_name,
                              count(1)                 order_cnt
                       from eam_workorder_slave ews
                                LEFT JOIN pro_eam_eledger_team peet ON ews.executor_id = peet.team_member_id
                                left join eam_workorder_slave_record ews2 on
                           ews.ews_id = ews2.ews_id
                       where ews.work_order_type = 7
                         and ews.delete_flag = 0
                         and ews.work_order_status = 5
                         AND DATE_FORMAT(ews.actual_begin_time, '%Y-%m-%d') = '${acc_date}'
                       group by
                                peet.team_member_code,
                                peet.team_member_name),

     repair_cnt as (SELECT '故障维修'            as repair_type,
                           peet.team_member_code AS user_code,
                           peet.team_member_name AS user_name,
                           peet.team_name,
                           count(1)                 order_cnt
                    FROM eam_workorder_m ewm
                             LEFT JOIN (select ewoo.business_key
                                             , min(ewoo.id) as id
                                        from eam_work_order_operation ewoo
                                        where ewoo.operation_type = 7
                                          AND ewoo.delete_flag = 0
                                        group by ewoo.business_key) ewoo2 on ewm.ew_id = ewoo2.business_key
                             LEFT JOIN eam_work_order_operation ewoo on ewoo2.id = ewoo.id
                             INNER JOIN eam_eledger_asset_card eeac ON ewm.ac_code = eeac.ac_code
                             LEFT JOIN eam_efault_repair eer ON ewm.repair_number = eer.efr_code
                        AND eer.delete_flag = 0
                             LEFT JOIN eam_workorder_maintenance ewm2 ON ewm.ew_id = ewm2.ew_id
                             LEFT JOIN pro_eam_eledger_team peet ON ewm2.maintenance_person_id = peet.team_member_id
                             LEFT JOIN (SELECT ewoo.business_key,
                                               ewoo.operator_id,
                                               max(ewoo.creation_date) AS acceptDate
                                        FROM eam_work_order_operation ewoo
                                        WHERE ewoo.operation_type IN (9, 12, 14)
                                        GROUP BY business_key) ewo ON ewm.ew_id = ewo.business_key
                    WHERE  ewm.delete_flag = 0
                      AND DATE_FORMAT(ewm2.maintenanc_start_time, '%Y-%m-%d') = '${acc_date}'
                    group by
                             peet.team_member_code,
                             peet.team_member_name),

     team_query as (select tm.team_name,
                           tm.team_code,
                           tm.team_member_code,
                           tm.team_member_name,
                           ipp.on_work_time,
                           ipp.out_work_time,
                           timestampdiff(HOUR,ipp.on_work_time,ipp.out_work_time) as work_diff
                    from pro_eam_eledger_team tm
                             left join iot_people_present ipp on tm.team_member_code = ipp.emp_code
                        and ipp.work_day = '${acc_date}')
select distinct 
     tq.team_member_name
     ,tq.team_member_code
     , tq.team_code
     , tq.on_work_time
     , tq.out_work_time
     , tq.work_diff
     , repair_cnt.order_cnt    repair_cnt
     , plan_cnt.order_cnt      plan_cnt
     , maintence_cnt.order_cnt maintence_cnt
     , hu.repair_hour
     , case when tq.work_diff != 0 then hu.repair_hour / tq.work_diff else null end as load_rate
from team_query tq
         left join plan_cnt on plan_cnt.user_code = tq.team_member_code
         left join repair_cnt on repair_cnt.user_code = tq.team_member_code
         left join maintence_cnt on maintence_cnt.user_code = tq.team_member_code
         left join hour_use hu on tq.team_member_code = hu.repair_person_code
where 1=1
      ${if(level==5,"and tq.team_code = '"+team_code+"' "," ")}
order by hu.repair_hour desc
```

### 平均故障修复时长MTTR

```markdown
# 业务属性：
1.数据定义：反映设备出现故障后到恢复正常工作时平均所需要的时间。
这是排除故障所需实际维修时间的平均值，用于衡量设备的可维护性和维修工的工作情况
2.指标计算逻辑公式：MTTR=总修复时间/故障次数
                  总修复时间=∑（维修完成时间-开始维修时间）
3.测量方式：日、月、年
4.数据记录方式：日
5.分析维度：产业、公司、生产厂区、使用部门
6.更新时间/频次：每日8:00
7.数据来源：工单管理-故障工单
           工单管理-委外维修工单
           工单管理-计划维修工单

```

&nbsp;

```markdown
with a as (
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	sum(value2) as value2,
	case when sum(value2) = 0 then null else sum(value1)/sum(value2) end as 占比,
	case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
	case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('平均故障修复时间MTTR','平均无故障时长MTBF')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
union all 
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	max(cast(value2 as UNSIGNED)) as value2,
	case when sum(value2) = 0 then null else sum(value1)/max(cast(value2 as UNSIGNED)) end as 占比,
	case when sum(cs_value2) = 0 then null else sum(cs_value1)/max(cast(value2 as UNSIGNED)) end as 同期占比,
	case when sum(sq_value2) = 0 then null else sum(sq_value1)/max(cast(value2 as UNSIGNED)) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('月均被动维修次数','月均一级保养次数','月均主动维修次数','月均委外维修次数','截止当期月均故障次数')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype!=3,
"and date_type_id = 2 and date_type >= concat(substr('"+acc_date+"',1,4),'-01') and date_type <= substr('"+acc_date+"',1,7)",
"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4)","")}
group by 1,2
union all  
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	sum(value2) as value2,
	case when sum(value2) = 0 then null 
	when ${datetype} = 1 then sum(value1)/sum(value2)
	when ${datetype} != 1 then sum(value1)/sum(value2)/12*1.5
	end as 占比,
	case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
	case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('人均净维修时长','人均工作时长','人均被动维修时长','人均主动维修时长')
and industry = '电缆产业'
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
)

select 
	mark_name,
	type_name,
	value1,
	value2,
	占比,
	case when 同期占比 = 0 then null else (占比-同期占比)/同期占比 end as 同比,
	case when 上期占比 = 0 then null else (占比-上期占比)/上期占比 end as 环比
from a 
```

### 报修-开始维修平均响应时长

```markdown
 # 业务属性：
1.数据定义：反映当前时间点故障从报修到维修工开始维修的平均响应时长
2.指标计算逻辑公式：报修-开始维修平均响应时长=∑（工单开始维修时间-工单报修时间）/工单数量
3.数据类型：实时数据
4.数据记录方式：实时数据
5.分析维度：产业、公司、生产厂区、使用部门
6.更新时间/频次：实时更新
7.数据来源：设备台账eam_eledger_asset_card
8.展示路径：
（1）PC端：设备域首页 -> 设备故障情况分析 -> 报修-开始维修平均响应时长
（2）移动端：设备域首页 -> 设备故障情况分析 -> 报修-开始维修平均响应时长

```

```markdown
-- 平均响应时长
with dept_record as (select a.dep_id as level1, a.name as name1, b.dep_id as level2, b.name as name2, c.dep_id as level3
                     from eam_org_dimension a
                              left join eam_org_dimension b on a.dep_id = b.parent_id
                              left join eam_org_dimension c on b.dep_id = c.parent_id
                     where b.dep_id is not null
                       and c.dep_id is not null
                     order by b.dep_id),
     asset_card as (select t1.ac_name,
                           t1.asset_alias,
                           t1.ac_code,
                           t1.use_dept_name,
                           t1.use_dept,
                           t1.ag_code,
                           t1.ag_info,
                           t1.asset_code,
                           t1.asset_name,
                           t1.ac_position,
                           t1.ac_asset_status,
                           t1.asset_date,
                           t2.name2,
                           t2.level2,
                           t2.name1,
                           t2.level1,
                           t1.run_status
                    from eam_eledger_asset_card t1
                             left join dept_record t2 on t1.use_dept = t2.level3
                    where t1.delete_flag = 0),
     repair2receive as (SELECT a.business_key                                                 as business_key,
                               a.creation_date                                                as receive_time,
                               b.creation_date                                                as repair_time,
                               a.operator_id                                                  as operator,
                               TIMESTAMPDIFF(SECOND, b.creation_date, a.creation_date) / 3600 as spend_time
                        FROM eam_work_order_operation a
                                 LEFT JOIN eam_work_order_operation b ON a.business_key = b.business_key
                        WHERE a.delete_flag = 0
                          AND b.delete_flag = 0
                          AND a.operation_type IN ('13', '6')
                          AND b.operation_type IN ('13', '6')
                          AND a.operation_type != b.operation_type
                          AND TIMESTAMPDIFF(SECOND, b.creation_date, a.creation_date) > 0
                          and DATE_FORMAT(b.creation_date, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d')
                        group by a.business_key),
base as 
(select DATE_FORMAT(t2.creation_date, '%Y-%m-%d') as date_type,
       '电缆产业' as industry,
       t1.level1,
       t1.name1,
       t1.level2,
       t1.name2,
       t1.use_dept as dept_id,
       t1.use_dept_name,
       sum(spend_time)                           as value1, -- 响应总时长
       count(t1.use_dept)                        as value2  -- 故障工单数量
from eam_workorder_m t2
         left join asset_card t1 on t1.ac_code = t2.ac_code
         left join repair2receive t3 on t2.ew_id = t3.business_key
where t2.delete_flag = 0
and spend_time is not null
group by date_type, t1.use_dept
order by date_type)

select  sum(value1)/sum(value2) as 平均响应时长
from base 
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and name1 = '"+company+"' "," ")}
${if(level==3,"and name2 = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}

```

### 已报修未完成超24小时

```markdown
# 业务属性：
1.数据定义：反映已报修超过12小时未完成维修的工单数量
2.指标计算逻辑：报修时间=当前时间点-故障报修时间点
3.测量方式：实时数据
4.数据记录方式：实时数据
5.分析维度：产业、公司生产厂区、使用部门
6.更新时间/频次：实时更新
7.数据来源：eam_workorder_m、pro_eam_org_dimension

```

&nbsp;

```markdown
select count(case when timestampdiff(hour,repair_time, now()) > 8 then 1 end)  as over_8_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 12 then 1 end) as over_12_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 24 then 1 end) as over_24_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 72 then 1 end) as over_72_hours
from (
select eod.industry,
       eod.company_name company,
       eod.factory_name fac_name,
       eod.dep_id dept_id,
       eod.dep_code dept_code,
       ewm.repair_time
from eam_workorder_m ewm
     left join pro_eam_org_dimension eod on ewm.department_id=eod.dep_id
where ewm.delete_flag = 0
      and ewm.work_order_status < 5 -- 状态小于5表示未完成
)x1
where 1=1
     ${if(level==1,"and industry = '"+cy+"' "," ")}
     ${if(level==2,"and company = '"+company+"' "," ")}
     ${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
     ${if(level==4,"and dept_id = '"+dept_id+"' "," ")}

```

### 设备及故障统计（机台数/故障次数）

```markdown
# 业务属性：
1.数据定义：在设备分类下设备登记的机台数量
2.分析维度：使用部门
3.数据类型：累计数据
4.数据来源：eam_workorder_m、eam_eledger_asset_card

```

&nbsp;

```markdown
with base as
    (select
        ewm.ac_code,
        eeac.asset_name,
        ewm.work_order_number,
        eod.dep_id,
        eod.dep_name,
        eod.factory_id,
        eod.factory_name as fac_name,
        eod.company_id,
        eod.company_name as company,
        eod.industry
    from eam_workorder_m ewm
        left join eam_eledger_asset_card eeac on ewm.ac_code=eeac.ac_code
    join pro_eam_org_dimension eod on ewm.department_id = eod.dep_id
    where eeac.delete_flag=0
${if(datetype==1,"and substr(ewm.creation_date, 1, 10) = '"+acc_date+"' "," ")}
${if(datetype==2,"and substr(ewm.creation_date, 1, 7) = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and substr(ewm.creation_date, 1, 4) = substr('"+acc_date+"',1,4) "," ")}
    )
select asset_name,
dep_name,
count(work_order_number) as 故障次数
from base
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(fac_name1!="","and fac_name = '"+fac_name1+"' ",if(level==3,"and fac_name = '"+fac_name+"' ",""))}
${if(level==4,"and dep_id = '"+dept_id+"' "," ")}
group by dep_name,asset_name

```

### 故障维修费用



### 截止当期月均主动维修次数

```markdown
# 业务属性：
1.数据定义：
2.指标计算逻辑：SUM（主动维修工单数量）/月份
               主动维修=计划维修按工单创建时间
3.数据来源：工单管理-计划维修
4.指标类型：复合指标
5.组织维度：电缆产业、公司、生产厂区、生产厂

```

```markdown
 with a as (
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(value2) as value2,
    case when sum(value2) = 0 then null else sum(value1)/sum(value2) end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('平均故障修复时间MTTR','平均无故障时长MTBF')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
union all 
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    max(cast(value2 as UNSIGNED)) as value2,
    case when sum(value2) = 0 then null else sum(value1)/max(cast(value2 as UNSIGNED)) end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/max(cast(value2 as UNSIGNED)) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/max(cast(value2 as UNSIGNED)) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('月均被动维修次数','月均一级保养次数','月均主动维修次数','月均委外维修次数','截止当期月均故障次数')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype!=3,
"and date_type_id = 2 and date_type >= concat(substr('"+acc_date+"',1,4),'-01') and date_type <= substr('"+acc_date+"',1,7)",
"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4)","")}
group by 1,2
union all  
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(value2) as value2,
    case when sum(value2) = 0 then null 
    when ${datetype} = 1 then sum(value1)/sum(value2)
    when ${datetype} != 1 then sum(value1)/sum(value2)/12*1.5
    end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('人均净维修时长','人均工作时长','人均被动维修时长','人均主动维修时长')
and industry = '电缆产业'
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
)

select 
    mark_name,
    type_name,
    value1,
    value2,
    占比,
    case when 同期占比 = 0 then null else (占比-同期占比)/同期占比 end as 同比,
    case when 上期占比 = 0 then null else (占比-上期占比)/上期占比 end as 环比
from a 
```

### 停机率超50%关键设备数量

```markdown
# 业务属性
1.指标定义：统计周期内停机时长占应工作时长超50%的关键数采设备的数量（台）
2.指标逻辑：应工作时长 = 统计周期结束时间 - 统计周期开始时间
          设备开机时长 = SUM(设备开机结束 - 设备开机结束时间)
          设备停机时长 = 应工作时长 - 设备开机时长
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
8.数据来源：IOT数采（dw_device_work_status_bigdata_all_time、dim_device_bigdata_min_start、yd_device_org_plane）

# BI逻辑
1. 备注：与`停机率超25%关键设备数量`指标共用BI数据集
2. 所用字段：stop50_num
3. BI SQL

```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y

```

### 当前未完成故障工单占比

```markdown
# 业务属性：
1.数据定义：当前时间内未完成故障工单总数量占当天故障工单总数的比例
2.指标计算逻辑：当前未完成故障工单占比=当前未完成故障工单总数量/当天故障工单总数
3.数据来源：eam_eledger_asset_card、eam_workorder_m

```

&nbsp;

```markdown
with base as (SELECT distinct eeac.ac_code,

eeac.use_dept,

eod.dep_name,

eod.parent_id AS fac_id,

eod.factory_name,

eod1.parent_id AS company_id,

eod1.company

FROM eam_eledger_asset_card eeac

LEFT JOIN eam_org_dimension eod ON eeac.use_dept = eod.dep_id

LEFT JOIN eam_org_dimension eod1 ON eod.parent_id = eod1.dep_id

WHERE eeac.delete_flag = 0

AND eeac.use_dept != '590566710549954560'),

undo_order_info AS (SELECT work_order_number as won1,

ac_code,

department_id,

DATE_FORMAT(creation_date, '%Y-%m-%d') AS date_type

FROM eam_workorder_m

WHERE delete_flag = 0

and work_order_status not in (5, 8, 10)

and DATE_FORMAT(creation_date, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d')),

all_order_info AS (SELECT department_id,

DATE_FORMAT(creation_date, '%Y-%m-%d') AS date_type,

count(work_order_number) as value2

FROM eam_workorder_m

WHERE delete_flag = 0

and work_order_status not in (8, 10)

and DATE_FORMAT(creation_date, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d')

group by department_id, date_type),

allData as (select '电缆产业' as industry,

t2.company_id,

t2.company,

t2.fac_id,

t2.factory_name,

t2.use_dept as dept_id,

t2.dep_name,

t1.date_type,

count(t1.won1) as value1, -- 未完成故障工单总数

t3.value2 -- 故障工单总数

from undo_order_info t1

left join base t2 on t1.ac_code = t2.ac_code

left join all_order_info t3 on t3.department_id = t1.department_id

where t2.use_dept != '590566710549954560'

group by t2.use_dept, t1.date_type

order by t1.date_type)

select sum(value1) as 未完成故障工单总数,

sum(value2) as 故障工单总数,

case when sum(value2) = 0 then null else sum(value1) / sum(value2) end as 占比

from allData

where 1=1

${if(level==1,"and industry = '"+cy+"' "," ")}

${if(level==2,"and company = '"+company+"' "," ")}

${if(level==3,"and factory_name = '"+fac_name+"' "," ")}

${if(level==4,"and dept_id = '"+dept_id+"' "," ")}

```

&nbsp;

&nbsp;

&nbsp;

### 二级保养次数环比



### 一级保养次数环比

```markdown
# 业务属性：
1.数据定义：
2.指标计算逻辑：
3.数据来源：

```

&nbsp;

```markdown
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(cs_value1) as cs_value1,
    sum(sq_value1) as sq_value1,
    case when sum(cs_value1) = 0 then null else (sum(value1)-sum(cs_value1)) / sum(cs_value1) end as 同比,
    case when sum(sq_value1) = 0 then null else (sum(value1)-sum(sq_value1)) / sum(sq_value1) end as 环比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2

```

### 已报修未完成超12小时

```markdown
# 业务属性：
1.数据定义：反映已报修超过12小时未完成维修的工单数量
2.指标计算逻辑：报修时间=当前时间点-故障报修时间点
3.测量方式：实时数据
4.数据记录方式：实时数据
5.分析维度：产业、公司生产厂区、使用部门
6.更新时间/频次：实时更新
7.数据来源：eam_workorder_m、pro_eam_org_dimension

```

&nbsp;

```markdown
select count(case when timestampdiff(hour,repair_time, now()) > 8 then 1 end)  as over_8_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 12 then 1 end) as over_12_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 24 then 1 end) as over_24_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 72 then 1 end) as over_72_hours
from (
select eod.industry,
       eod.company_name company,
       eod.factory_name fac_name,
       eod.dep_id dept_id,
       eod.dep_code dept_code,
       ewm.repair_time
from eam_workorder_m ewm
     left join pro_eam_org_dimension eod on ewm.department_id=eod.dep_id
where ewm.delete_flag = 0
      and ewm.work_order_status < 5 -- 状态小于5表示未完成
)x1
where 1=1
     ${if(level==1,"and industry = '"+cy+"' "," ")}
     ${if(level==2,"and company = '"+company+"' "," ")}
     ${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
     ${if(level==4,"and dept_id = '"+dept_id+"' "," ")}

```

### 设备停机占比

```markdown
# 业务属性
1.指标定义：当前时间处于关机状态的关键工序数采设备占总关键工序数采设备的比值（%）
2.指标逻辑：关机状态的关键工序数采设备 / 关键工序数采设备数量 * 100%
3.数据类型：实时数据
4.指标类型：复合指标
5.分析维度：电缆产业、公司、生产厂区、使用部门、重要设备、一般设备
6.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 实时数据 -> 数采设备运行状态分析
7. 数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_organization_v、yd_device_org_plane）

# BI逻辑
1. 备注：与`设备停机台数`、`设备运行台数`、`设备总数量`指标共用BI数据集
2. 所用字段：停机占比
3. BI SQL

```

```markdown
select  
    count(1) 连接数 ,
    count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 停机,
    sum( CASE WHEN (device_status = 2 and work_status='Y') THEN 1 ELSE 0 END ) 作业,
    sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 开机,
    sum( CASE WHEN device_status > 0 THEN 1 ELSE 0 END ) 在线,
    (count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END )) / count(1) as 停机占比
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 人均主动维修时长的同比



### 人均净维修时长同期



### 人均被动维修时长的同比



### 设备停机台数

```markdown
# 业务属性
1.指标定义：当前时间处于停机状态的关键工序数采设备的数量（台）
2.指标逻辑：关键工序设备数采实时状态为停机的设备数量
3.数据类型：实时数据
4.指标类型：原子指标
5.分析维度：电缆产业、公司、生产厂区、使用部门、重要设备、一般设备
6.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 实时数据 -> 数采设备运行状态分析
7.数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_organization_v、yd_device_org_plane）

# BI逻辑
1. 备注：与`设备停机占比`、`设备运行台数`、`设备总数量`指标共用BI数据集
2. 所用字段：停机
3. BI SQL

```

```markdown
select  
    count(1) 连接数 ,
    count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 停机,
    sum( CASE WHEN (device_status = 2 and work_status='Y') THEN 1 ELSE 0 END ) 作业,
    sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 开机,
    sum( CASE WHEN device_status > 0 THEN 1 ELSE 0 END ) 在线,
    (count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END )) / count(1) as 停机占比
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 人均被动维修时长的环比



### 二级保养



### 故障维修数



### 一级保养执行情况



### 人均被动维修时长



### 厂区保养平均执行时长

```markdown
# 业务属性：
1.数据定义：厂区内设备进行保养工作所花费的平均时间
2.指标计算逻辑：设备保养时间总和/部门保养次数
3.展示路径：
（1）移动端：设备域首页 -> 设备维修保养分析 -> 查看明细 -> 厂区保养平均执行时长
4.数据来源：yd_mkt_device_second_df、eam_eledger_asset_card

```

```markdown
 select bb.dept_name,
       '平均执行时长' dim_type_name,
       sum(bb.value1) value1
from yd_mkt_device_second_df bb
where 1=1
       and type_name = '厂区保养平均执行时长-条形图'
       ${if(level==1,"and industry = '"+cy+"' "," ")}
       ${if(level==2,"and company = '"+company+"' "," ")}
       ${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
       ${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
       ${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
       ${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
       ${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by bb.dept_name
order by value1 

```

&nbsp;

### 维修工总人数

```markdown
# 业务属性
1.数据定义：维修班组的整体人数
2.指标计算逻辑公式：维修工总人数=今日出勤人数+今日未出勤人数
3.数据类型：实时数据
4.数据记录方式：实时数据
5.分析维度：电缆产业
6.更新时间/频次：实时更新
7.指标类型：复合指标
8.数据来源：班组信息eam_eledger_team_member、人员出勤表eam_person_attendance、班组eam_eledger_team、机修班eam_maintenance_group

```

```markdown
with base as (select team_member_code
                   , eet.team_name
                   , eet.team_code
                   , emg.company
                   , company_id
                   , '电缆产业' as industry
              from eam_eledger_team_member as eetm
                       left join eam_eledger_team eet on eetm.team_id = eet.team_id
                       left join eam_maintenance_group emg on emg.team_code = eet.team_code
              where eet.team_status = 0
                )

select count(distinct base.team_member_code) as cnt
         , epa.pa_status
from base
left join eam_person_attendance epa on epa.pa_code = base.team_member_code
where delete_flag=0
and epa.pa_status = 1	
and substr(date(epa.creation_date),1,10) = curdate()	
union all 
select 
count(distinct team_member_code) as cnt,
'3' as pa_status  
from base

```

### 今日出勤人数

```markdown
1.数据定义:反映当前维修班组出勤情况
2.指标计算逻辑公式：设备管理系统中存在打卡记录即为出勤，否则为未出勤
3.数据类型：实时数据
4.数据记录方式：实时数据
5.指标类型：原子指标
6.分析维度：电缆产业
7.更新时间/频次：实时更新
8.数据来源：班组信息eam_eledger_team_member、人员出勤表eam_person_attendance、班组eam_eledger_team、机修班eam_maintenance_group 


```

&nbsp;

```markdown
with base as (select team_member_code
                   , eet.team_name
                   , eet.team_code
                   , emg.company
                   , company_id
                   , '电缆产业' as industry
              from eam_eledger_team_member as eetm
                       left join eam_eledger_team eet on eetm.team_id = eet.team_id
                       left join eam_maintenance_group emg on emg.team_code = eet.team_code
              where eet.team_status = 0
                )

select count(distinct base.team_member_code) as cnt
         , epa.pa_status
from base
left join eam_person_attendance epa on epa.pa_code = base.team_member_code
where delete_flag=0
and epa.pa_status = 1	
and substr(date(epa.creation_date),1,10) = curdate()	
union all 
select 
count(distinct team_member_code) as cnt,
'3' as pa_status  
from base

```

### 二级保养数



### 截止当期月均委外维修次数

```markdown
# 业务属性：
1.数据定义：反映当年设备发生委外维修工单的频率
2.指标计算逻辑：委外维修工单数量的总和/月份
               委外维修（按工单创建时间）
3.数据来源: 工单管理-委外维修工单eam_workorder_out_maintenance
          yd_mkt_device_first_df

```

&nbsp;

```markdown
 with a as (
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(value2) as value2,
    case when sum(value2) = 0 then null else sum(value1)/sum(value2) end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('平均故障修复时间MTTR','平均无故障时长MTBF')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
union all 
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    max(cast(value2 as UNSIGNED)) as value2,
    case when sum(value2) = 0 then null else sum(value1)/max(cast(value2 as UNSIGNED)) end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/max(cast(value2 as UNSIGNED)) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/max(cast(value2 as UNSIGNED)) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('月均被动维修次数','月均一级保养次数','月均主动维修次数','月均委外维修次数','截止当期月均故障次数')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype!=3,
"and date_type_id = 2 and date_type >= concat(substr('"+acc_date+"',1,4),'-01') and date_type <= substr('"+acc_date+"',1,7)",
"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4)","")}
group by 1,2
union all  
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(value2) as value2,
    case when sum(value2) = 0 then null 
    when ${datetype} = 1 then sum(value1)/sum(value2)
    when ${datetype} != 1 then sum(value1)/sum(value2)/12*1.5
    end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('人均净维修时长','人均工作时长','人均被动维修时长','人均主动维修时长')
and industry = '电缆产业'
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
)

select 
    mark_name,
    type_name,
    value1,
    value2,
    占比,
    case when 同期占比 = 0 then null else (占比-同期占比)/同期占比 end as 同比,
    case when 上期占比 = 0 then null else (占比-上期占比)/上期占比 end as 环比
from a 

```

&nbsp;

&nbsp;

### 一级保养工单数量

```markdown
# 业务属性：
1.数据定义:
2.指标逻辑：一级保养工单数量=SUM（一级保养工单数量）
           已完成：取工单状态为已完成的数据
           待验收：取工单状态为待验收的数据
3.数据类型：实时数据
4.组织维度：电缆产业、公司、生产厂区、生产厂
5.分析维度：工单状态（已完成、待验收）
6.数据来源：一级保养-一级保养记录
```

&nbsp;

```markdown
-- 部门级保养工单指标

with total as (select coalesce(count(ews.work_order_number), 0) as '保养工单总数'

, eod.name

, eod.dep_id

from eam_workorder_slave ews

left join eam_org_dimension eod on ews.department_id = eod.dep_id

where 1 = 1

and ews.work_order_type in (3, 7)

and eod.name not RLIKE '物流|造粒'

and delete_flag = 0

and substr(ews.plan_begin_time, 1, 7) = '2024-09'

group by eod.name),

wc_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单完成总数'

, eod2.name

, eod2.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

where ews2.work_order_type = 3

and work_order_status in (3,4,5,6)

and delete_flag=0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod2.name, eod2.dep_id),

yj_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单总数'

, eod2.name

, eod2.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

where ews2.work_order_type = 3

and delete_flag=0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod2.name, eod2.dep_id),

aa as (select

'4' as type

,保养工单总数

,一级保养工单总数

,一级保养工单完成总数

,tt.dep_id

,tt.name

from total as tt

left join yj_count yc on tt.dep_id=yc.dep_id

left join wc_count wc on tt.dep_id=wc.dep_id

union all -- 厂区级保养工单指标

(with total as (select coalesce(count(ews.work_order_number), 0) as '保养工单总数'

, eod3.name

, eod3.dep_id

from eam_workorder_slave ews

left join eam_org_dimension eod on ews.department_id = eod.dep_id

left join eam_org_dimension eod3 on eod.parent_id=eod3.dep_id

where 1 = 1

and ews.work_order_type in (3, 7)

and eod.name not RLIKE '物流|造粒'

and delete_flag = 0

# and substr(ews.plan_begin_time, 1, 10) = '2024-09-28'

group by eod3.name, eod3.dep_id),

wc_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单完成总数'

, eod4.name

, eod4.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod4 on eod2.parent_id=eod4.dep_id

where ews2.work_order_type = 3

and work_order_status in (3,4,5,6)

and delete_flag = 0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod4.name, eod4.dep_id),

yj_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单总数'

, eod5.name

, eod5.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod5 on eod2.parent_id=eod5.dep_id

where ews2.work_order_type = 3

and delete_flag=0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod5.name, eod5.dep_id)

select '3' as type

, 保养工单总数

, 一级保养工单总数

, 一级保养工单完成总数

, tt.dep_id

, tt.name

from total as tt

left join yj_count yc on tt.dep_id = yc.dep_id

left join wc_count wc on tt.dep_id = wc.dep_id)

union all -- 公司级保养工单指标

(

(with total as (select coalesce(count(ews.work_order_number), 0) as '保养工单总数'

, eod6.name

, eod6.dep_id

from eam_workorder_slave ews

left join eam_org_dimension eod on ews.department_id = eod.dep_id

left join eam_org_dimension eod3 on eod.parent_id=eod3.dep_id

left join eam_org_dimension eod6 on eod3.parent_id=eod6.dep_id

where 1 = 1

and ews.work_order_type in (3, 7)

and eod.name not RLIKE '物流|造粒'

and delete_flag = 0

# and substr(ews.plan_begin_time, 1, 10) = '2024-09-28'

group by eod6.name, eod6.dep_id),

wc_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单完成总数'

, eod7.name

, eod7.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod4 on eod2.parent_id=eod4.dep_id

left join eam_org_dimension eod7 on eod4.parent_id=eod7.dep_id

where ews2.work_order_type = 3

and work_order_status in (3,4,5,6)

and delete_flag = 0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod7.name, eod7.dep_id),

yj_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单总数'

, eod8.name

, eod8.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod5 on eod2.parent_id=eod5.dep_id

left join eam_org_dimension eod8 on eod8.dep_id=eod5.parent_id

where ews2.work_order_type = 3

and delete_flag = 0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod8.name, eod8.dep_id)

select '2' as type

, 保养工单总数

, 一级保养工单总数

, 一级保养工单完成总数

, tt.dep_id

, tt.name

from total as tt

left join yj_count yc on tt.dep_id = yc.dep_id

left join wc_count wc on tt.dep_id = wc.dep_id)

)

)

select

sum(保养工单总数) as 保养工单总数,

sum(一级保养工单总数) as 一级保养工单总数,

sum(一级保养工单完成总数) as 一级保养工单完成总数

from aa

where 1=1

${switch(level,'1',"and type = '2'",

'2',"and type = '2' and name = '"+company+"' ",

'3',"and type = '3' and name = '"+fac_name+"' ",

'4',"and type = '4' and dep_id = '"+dept_id+"' ")}
```

&nbsp;

&nbsp;

### 停机率超50%关键设备数量的环比

```markdown
# 业务属性
1.指标定义：本期停机率超50%关键设备数量与上期停机率超50%关键设备数量相比的变化幅度（%）
2.指标逻辑：(本期停机率超50%关键设备数量 - 上期停机率超50%关键设备数量) / 上期停机率超50%关键设备数量 * 100%
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
8.数据来源：IOT数采（dw_device_work_status_bigdata_all_time、dim_device_bigdata_min_start、yd_device_org_plane）

# BI逻辑
1. 备注：与`停机率超25%关键设备数量`指标共用BI数据集
2. 所用字段：停机50数量环比
3. BI SQL
```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y

```

### 人均工作时长环比



### 备件消耗总费用



### 计划维修



### 计划维修费用



### 当前故障设备数量

&nbsp;

```markdown
 # 业务属性：
1.数据定义：反映当前时间点存在报障未维修完成的设备数量
2.指标计算逻辑：统计设备管理系统中存在未完成故障工单的设备数量
3.指标类型：复合指标
4.分析维度：电缆产业、公司、生产厂区、使用部门
5.测量方式：实时数据
6.数据记录方式：实时数据
7.更新时间/频次：实时更新
8.数据来源：设备台账eam_eledger_asset_card
9.展示路径：
（1）移动端：设备域首页 -> 设备故障情况分析 -> 当前故障设备数量

```

&nbsp;

```markup
with x as (

select sum(cnt1) as 运行数量,

sum(cnt2) as 停机数量,

sum(cnt3) as 闲置数量,

sum(cnt) as 设备总数,

(sum(cnt1)+sum(cnt2)) as IOT设备总数,

case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt1)/(sum(cnt1)+sum(cnt2)) else 0 end as 运行占比,

case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt2)/(sum(cnt1)+sum(cnt2)) else 0 end as 停机占比,

case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt3)/(sum(cnt1)+sum(cnt2)) else 0 end as 闲置占比

from (

select

sum(case when bq.run_status = 10 and bq.ac_asset_status not in (20) then 1 else 0 end) as cnt1,

sum(case when bq.run_status = 30 and bq.ac_asset_status not in (20) then 1 else 0 end) as cnt2,

sum(case when bq.ac_asset_status = 40 then 1 else 0 end) as cnt3,

count(1) as cnt

from (

select

eeac.ac_code,

eeac.use_dept as dept_id,

eod.dep_name,

eod.factory_id as fac_id,

eod.factory_name as fac_name,

eod.company_id as company_id,

eod.company_name as company,

eeac.run_status,

eeac.ac_asset_status, -- '管理状态 EAM_ASSET_GL_STATUS 在用 (10)报废 (20)处置(30)闲置 (40)报废留用 (50)试运行 (60)'

date(last_update_date) as dd

from eam_eledger_asset_card eeac

left join pro_eam_org_dimension eod on eeac.use_dept = eod.dep_id

where eeac.delete_flag = 0

and use_dept != '590566710549954560' -- 剔除采供中心电动液压车

) as bq

where 1=1

${if(level=1,"and 1=1 "," ")}

${if(level=2,"and company = '"+company+"' "," ")}

${if(level=3,"and fac_name = '"+fac_name+"' "," ")}

${if(level=4,"and dept_id = '"+dept_id+"' "," ")}

)aa

),

y as (

select count(distinct ac_code) as 故障机台数

from (

select

x1.ac_code,

x1.department_id as dept_id,

x2.dep_name,

x2.factory_id as fac_id,

x2.factory_name as fac_name,

x2.company_id as company_id,

x2.company_name as company

from eam_workorder_m x1

join pro_eam_org_dimension x2 on x1.department_id=x2.dep_id

where substr(x1.creation_date,1,10) = curdate()

) as bq

where 1=1

${if(level=1,"and 1=1 "," ")}

${if(level=2,"and company = '"+company+"' "," ")}

${if(level=3,"and fac_name = '"+fac_name+"' "," ")}

${if(level=4,"and dept_id = '"+dept_id+"' "," ")}

)

select x.运行数量,

x.停机数量,

x.IOT设备总数,

x.设备总数,

x.运行占比,

x.停机占比,

x.闲置占比,

y.故障机台数,

case when x.设备总数!=0 then y.故障机台数/x.设备总数 else 0 end as 故障占比

from x left join y on 1=1

```

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

### 计划维修数



### 二级保养执行情况



### 平均维修耗时统计

```markdown
 # 业务属性：
1.数据定义：统计设备从故障到修复所需平均时间
2.指标计算逻辑：维修时间/故障次数
           维修时间 = 维修结束时间-维修开始时间
3.数据类型：累计数据
4.指标类型：复合指标
5.展示路径：
   （1）PC端：设备域PC端首页 -> 设备故障情况分析 -> 查看明细 -> 平均维修耗时统计
   （2）手机端：设备域手机端首页 -> 设备故障情况分析 -> 查看明细 -> 平均维修耗时统计
6.数据来源：yd_mkt_device_first_df 

```

```markup
select 
dept_name,
sum(value1) as value1,
sum(value2) as value2,
case when sum(value2) = 0 then null else round(sum(value1)/sum(value2),0) end as 占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and mark_name = '设备故障情况分析'
and type_name = '平均故障修复时间MTTR'
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1

```

### 人均净维修时长上期



### 停机设备总数

```markdown
# 业务属性
1.指标定义：当前时间状态为停机的关键数采设备的数量（台）
2.数据类型：实时数据
3.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 数采设备运行状态分析 -> 查看明细 -> 重要设备、一般设备停机占比分析
4.数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_oraganization_v、yd_device_org_plane）

 
# BI逻辑
1. 所用字段：重要设备、一般设备、其他设备停机数量之和
2. BI SQL

```

```markdown
select  
    '重要设备停机占比' as type,
    sum(case when td.ac_position = 'A' then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 
union all 
select  
    '一般设备停机占比' as type,
    sum(case when td.ac_position = 'B' then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 
union all 
select  
    '其他设备停机占比' as type,
    sum(case when td.ac_position is null then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 维修备件消耗费用



### 今日出勤率

```markdown
# 业务属性
1.数据定义：反映当前维修班组的出勤情况
2.指标逻辑计算公式：设备管理系统中存在打卡记录即为出勤，否则为未出勤
                   维修工总人数=今日出勤人数+今日未出勤人数
                   出勤率=今日出勤人数/维修工总人数*100%
3.数据类型：实时数据
4.数据记录方式:实时数据
5.指标类型：复合指标
6.分析维度：电缆产业
7.更新时间/频次：实时更新
8.数据来源：班组信息eam_eledger_team_member、人员出勤表eam_person_attendance

```

### 人均工作时长同比



### 人均净维修时长

```markdown
# 业务属性:

单位：小时（日维度）、天（月维度）、月（年维度）

指标类型：复合指标

组织维度：/

时间维度：日、月、年

分析维度：班组、班组人员、维修分类（主动维修、被动维修）

指标逻辑：

计算公式：SUM（净维修时长）/总人数净维修时长=验收完成操作时间-暂挂时间-开始维修时间主动维修：取计划维修工单被动维修：故障维修、委外维修工单按维修完成工单

数据来源：

工单管理-故障工单

工单管理-计划维修工单

```

### 重要设备平均开机时长

```markdown
# 业务属性
1.指标定义：统计周期内关键工序数采设备的平均开机时长，日/月/年维度单位分别为小时、天、天
2.指标逻辑：SUM（关键工序数采设备开机时长）/ 关键工序数采设备台数
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.分析维度：设备重要性（重要设备）
8.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
9.数据来源：IOT数采（yd_device_org_plane、dim_device_bigdata_min_start、dw_device_work_status_bigdata_all_time）

# BI逻辑
1. 备注：与`设备平均开机时长`指标共用BI数据集
2. 所用字段：avg_imp_open_stay
3. BI SQL
```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y

```

### 停机率超25%关键设备数量的环比

```markdown
# 业务属性
1.指标定义：本期停机率超25%关键设备数量与上期停机率超25%关键设备数量相比的变化幅度（%）
2.指标逻辑：(本期停机率超25%关键设备数量 - 上期停机率超25%关键设备数量) / 上期停机率超25%关键设备数量 * 100%
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
8.数据来源：IOT数采（dw_device_work_status_bigdata_all_time、dim_device_bigdata_min_start、yd_device_org_plane）

# BI逻辑
1. 备注：与`停机率超50%关键设备数量`指标共用BI数据集
2. 所用字段：停机25数量环比
3. BI SQL
```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y
```

### 停机率超50%关键设备数量的同比

```markdown
# 业务属性
1.指标定义：本期停机率超50%关键设备数量与同期停机率超50%关键设备数量相比的变化幅度（%）
2.指标逻辑：(本期停机率超50%关键设备数量 - 同期停机率超50%关键设备数量) / 同期停机率超50%关键设备数量 * 100%
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
8.数据来源：IOT数采（dw_device_work_status_bigdata_all_time、dim_device_bigdata_min_start、yd_device_org_plane）

# BI逻辑
1. 备注：与`停机率超50%关键设备数量`指标共用BI数据集
2. 所用字段：停机50数量同比
3. BI SQL
```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y
```

### 二级保养次数同比



### 按停机时长排序

```markdown
# 业务属性 
1.数据描述：统计周期内数采设备开机时长、关机时长的明细数据
2.数据类型：累计数据
3.数据排序：按停机时长（stop_time）倒序排序
4.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析 -> 明细数据 -> 停机设备详情
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析 -> 明细数据 -> 停机设备详情
5.数据来源：IOT数采
           yd_device_org_plane、yd_eam_device_info、
           dim_device_bigdata_min_start、dw_device_work_status_bigdata_all_time

# BI逻辑
1. 备注：与按`开机率排序`指标共用bi数据集，仅排序字段不同
2. 所用字段：
   公司（厂区）- ORG
   使用部门 - USE_DEPT_NAME
   设备分类 - DEVICE_CLASS
   设备名称 - AC_NAME
   规格型号 - AG_STANDARD
   停机时长（h）- STOP_TIME
   开机率 - OPEN_RATE
   设备重要性 - DEVICE_IMPORTANT
3. BI SQL

```

```markdown
SELECT 
    company_name || '（' || factory_name || '）' as org, --公司
    factory_name,
    use_dept_name,
    device_id, --设备编号（生产域）
    ac_code, --设备编号（设备域）
    ac_name, --设备名称
    ag_standard,--规格型号
    device_class, --设备分类
    device_important, --设备重要性
    case when nvl(all_time,0)=0 then null 
         else round(greatest(all_time - open_stay,0), 2) end as stop_time, --停机时长
    case when nvl(all_time,0)=0 then null 
         else round(least(open_stay / all_time, 1),4) end as open_rate --开机率
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       c.ac_code,
       c.asset_alias as ac_name,
       case when c.ac_position='A' then '重要设备'
            else '一般设备' end as device_important,
       c.asset_name AS device_class,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       b.ag_standard,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td.all_time as cs_all_time, --应工作时长
       td.all_time as sq_all_time --应工作时长
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join yd_eam_device_info c 
        on b.ac_code = c.ac_code
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
order by decode(factory_name,'远东',1,'新远东',2,'复合',3,'新材料厂',4,'安缆',5,'远东电气',6,'远东通讯',7,'远东电缆（宜宾）',8,'远东海缆',9),
case when factory_name = '远东' then decode(use_dept_name,'电力电缆厂',1,'特种电缆厂',2,'高端电缆厂',3,'老远东盘具厂',4,'物流服务部',5,'老远东物流服务部',6)
when factory_name = '新远东' then decode(use_dept_name,'超高压电缆厂',1,'高压电缆厂',2,'中压电缆厂',3,'低压电缆厂',4,'海洋电缆厂',5,'新远东盘具厂',6,'生产服务部',7,'设备能源部',8,'质量服务部',9,'新远东物流服务部',10)
when factory_name = '复合' then decode(use_dept_name,'复合导线厂',1,'智能电缆厂',2,'复合盘具厂',3)
when factory_name = '新材料厂' then decode(use_dept_name,'新材料厂',1)
when factory_name = '安缆' then decode(use_dept_name,'中压电缆厂',1,'低压电缆厂',2,'特种电缆厂',3,'造粒厂',4)
when factory_name = '远东电气' then decode(use_dept_name,'电气电缆厂',1,'远东电气X',2,'新能源汽车线厂',3)
when factory_name = '远东通讯' then decode(use_dept_name,'光缆厂（1期）',1,'光棒光纤厂（2期）',2,'安环生产管服中心',3,'设备能源部',4)
when factory_name = '远东电缆（宜宾）' then decode(use_dept_name,'智能防火电缆厂',1,'智能低压电缆厂',2)
end
${if(datamark2==1,",stop_time desc",",open_rate")}

```

### 二级保养次数

```markdown
# 业务属性：

```

### 已完成一级保养工单数量

```markdown
# 业务属性：
1.数据定义：反映截止当前时间点已完成的一级保养工单总数
2.指标逻辑：已完成一级保养工单数量=∑（已完成一级保养工单总数）
3.数据类型：实时数据
4.分析维度：产业、公司、生产厂厂区、使用部门
5.更新时间/频次：实时更新
6.数据来源：计划保养表eam_workorder_slave、设备域组织架构eam_org_dimension

```

&nbsp;

```markdown
 -- 部门级保养工单指标

with total as (select coalesce(count(ews.work_order_number), 0) as '保养工单总数'

, eod.name

, eod.dep_id

from eam_workorder_slave ews

left join eam_org_dimension eod on ews.department_id = eod.dep_id

where 1 = 1

and ews.work_order_type in (3, 7)

and eod.name not RLIKE '物流|造粒'

and delete_flag = 0

and substr(ews.plan_begin_time, 1, 7) = '2024-09'

group by eod.name),

wc_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单完成总数'

, eod2.name

, eod2.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

where ews2.work_order_type = 3

and work_order_status in (3,4,5,6)

and delete_flag=0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod2.name, eod2.dep_id),

yj_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单总数'

, eod2.name

, eod2.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

where ews2.work_order_type = 3

and delete_flag=0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod2.name, eod2.dep_id),

aa as (select

'4' as type

,保养工单总数

,一级保养工单总数

,一级保养工单完成总数

,tt.dep_id

,tt.name

from total as tt

left join yj_count yc on tt.dep_id=yc.dep_id

left join wc_count wc on tt.dep_id=wc.dep_id

union all -- 厂区级保养工单指标

(with total as (select coalesce(count(ews.work_order_number), 0) as '保养工单总数'

, eod3.name

, eod3.dep_id

from eam_workorder_slave ews

left join eam_org_dimension eod on ews.department_id = eod.dep_id

left join eam_org_dimension eod3 on eod.parent_id=eod3.dep_id

where 1 = 1

and ews.work_order_type in (3, 7)

and eod.name not RLIKE '物流|造粒'

and delete_flag = 0

# and substr(ews.plan_begin_time, 1, 10) = '2024-09-28'

group by eod3.name, eod3.dep_id),

wc_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单完成总数'

, eod4.name

, eod4.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod4 on eod2.parent_id=eod4.dep_id

where ews2.work_order_type = 3

and work_order_status in (3,4,5,6)

and delete_flag = 0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod4.name, eod4.dep_id),

yj_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单总数'

, eod5.name

, eod5.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod5 on eod2.parent_id=eod5.dep_id

where ews2.work_order_type = 3

and delete_flag=0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod5.name, eod5.dep_id)

select '3' as type

, 保养工单总数

, 一级保养工单总数

, 一级保养工单完成总数

, tt.dep_id

, tt.name

from total as tt

left join yj_count yc on tt.dep_id = yc.dep_id

left join wc_count wc on tt.dep_id = wc.dep_id)

union all -- 公司级保养工单指标

(

(with total as (select coalesce(count(ews.work_order_number), 0) as '保养工单总数'

, eod6.name

, eod6.dep_id

from eam_workorder_slave ews

left join eam_org_dimension eod on ews.department_id = eod.dep_id

left join eam_org_dimension eod3 on eod.parent_id=eod3.dep_id

left join eam_org_dimension eod6 on eod3.parent_id=eod6.dep_id

where 1 = 1

and ews.work_order_type in (3, 7)

and eod.name not RLIKE '物流|造粒'

and delete_flag = 0

# and substr(ews.plan_begin_time, 1, 10) = '2024-09-28'

group by eod6.name, eod6.dep_id),

wc_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单完成总数'

, eod7.name

, eod7.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod4 on eod2.parent_id=eod4.dep_id

left join eam_org_dimension eod7 on eod4.parent_id=eod7.dep_id

where ews2.work_order_type = 3

and work_order_status in (3,4,5,6)

and delete_flag = 0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod7.name, eod7.dep_id),

yj_count as (select COALESCE(count(ews2.work_order_number), 0) as '一级保养工单总数'

, eod8.name

, eod8.dep_id

from eam_org_dimension eod2

left join eam_workorder_slave ews2 on ews2.department_id = eod2.dep_id

left join eam_org_dimension eod5 on eod2.parent_id=eod5.dep_id

left join eam_org_dimension eod8 on eod8.dep_id=eod5.parent_id

where ews2.work_order_type = 3

and delete_flag = 0

# and substr(ews2.actual_begin_time, 1, 10) = '2024-09-28'

group by eod8.name, eod8.dep_id)

select '2' as type

, 保养工单总数

, 一级保养工单总数

, 一级保养工单完成总数

, tt.dep_id

, tt.name

from total as tt

left join yj_count yc on tt.dep_id = yc.dep_id

left join wc_count wc on tt.dep_id = wc.dep_id)

)

)

select

sum(保养工单总数) as 保养工单总数,

sum(一级保养工单总数) as 一级保养工单总数,

sum(一级保养工单完成总数) as 一级保养工单完成总数

from aa

where 1=1

${switch(level,'1',"and type = '2'",

'2',"and type = '2' and name = '"+company+"' ",

'3',"and type = '3' and name = '"+fac_name+"' ",

'4',"and type = '4' and dep_id = '"+dept_id+"' ")}

```

&nbsp;

&nbsp;

&nbsp;

### 技改中备件消耗费用



### 停机率超25%关键设备数量的同比

```markdown
# 业务属性
1.指标定义：本期停机率超25%关键设备数量与同期停机率超25%关键设备数量相比的变化幅度（%）
2.指标逻辑：(本期停机率超25%关键设备数量 - 同期停机率超25%关键设备数量) / 同期停机率超25%关键设备数量 * 100%
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
8.数据来源：IOT数采（dw_device_work_status_bigdata_all_time、dim_device_bigdata_min_start、yd_device_org_plane）

# BI逻辑
1. 备注：与`停机率超50%关键设备数量`指标共用BI数据集
2. 所用字段：停机25数量同比
3. BI SQL
```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y

```

### 按开机率排序

```markdown
# 业务属性
1.数据描述：统计周期内数采设备开机时长、关机时长的明细数据
2.数据类型：累计数据
3.数据排序：按开机率（open_rate）正序排序
4.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析 -> 明细数据 -> 停机设备详情
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析 -> 明细数据 -> 停机设备详情
5.数据来源：IOT数采
           yd_device_org_plane、yd_eam_device_info、
           dim_device_bigdata_min_start、dw_device_work_status_bigdata_all_time

# BI逻辑
1. 备注：与按`停机时长排序`指标共用bi数据集，仅排序字段不同
2. 所用字段：
   公司（厂区）- ORG
   使用部门 - USE_DEPT_NAME
   设备分类 - DEVICE_CLASS
   设备名称 - AC_NAME
   规格型号 - AG_STANDARD
   停机时长（h）- STOP_TIME
   开机率 - OPEN_RATE
   设备重要性 - DEVICE_IMPORTANT
3. BI SQL

```

```markdown
SELECT 
    company_name || '（' || factory_name || '）' as org, --公司
    factory_name,
    use_dept_name,
    device_id, --设备编号（生产域）
    ac_code, --设备编号（设备域）
    ac_name, --设备名称
    ag_standard,--规格型号
    device_class, --设备分类
    device_important, --设备重要性
    case when nvl(all_time,0)=0 then null 
         else round(greatest(all_time - open_stay,0), 2) end as stop_time, --停机时长
    case when nvl(all_time,0)=0 then null 
         else round(least(open_stay / all_time, 1),4) end as open_rate --开机率
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       c.ac_code,
       c.asset_alias as ac_name,
       case when c.ac_position='A' then '重要设备'
            else '一般设备' end as device_important,
       c.asset_name AS device_class,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       b.ag_standard,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td.all_time as cs_all_time, --应工作时长
       td.all_time as sq_all_time --应工作时长
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join yd_eam_device_info c 
        on b.ac_code = c.ac_code
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
order by decode(factory_name,'远东',1,'新远东',2,'复合',3,'新材料厂',4,'安缆',5,'远东电气',6,'远东通讯',7,'远东电缆（宜宾）',8,'远东海缆',9),
case when factory_name = '远东' then decode(use_dept_name,'电力电缆厂',1,'特种电缆厂',2,'高端电缆厂',3,'老远东盘具厂',4,'物流服务部',5,'老远东物流服务部',6)
when factory_name = '新远东' then decode(use_dept_name,'超高压电缆厂',1,'高压电缆厂',2,'中压电缆厂',3,'低压电缆厂',4,'海洋电缆厂',5,'新远东盘具厂',6,'生产服务部',7,'设备能源部',8,'质量服务部',9,'新远东物流服务部',10)
when factory_name = '复合' then decode(use_dept_name,'复合导线厂',1,'智能电缆厂',2,'复合盘具厂',3)
when factory_name = '新材料厂' then decode(use_dept_name,'新材料厂',1)
when factory_name = '安缆' then decode(use_dept_name,'中压电缆厂',1,'低压电缆厂',2,'特种电缆厂',3,'造粒厂',4)
when factory_name = '远东电气' then decode(use_dept_name,'电气电缆厂',1,'远东电气X',2,'新能源汽车线厂',3)
when factory_name = '远东通讯' then decode(use_dept_name,'光缆厂（1期）',1,'光棒光纤厂（2期）',2,'安环生产管服中心',3,'设备能源部',4)
when factory_name = '远东电缆（宜宾）' then decode(use_dept_name,'智能防火电缆厂',1,'智能低压电缆厂',2)
end
${if(datamark2==1,",stop_time desc",",open_rate")}

```

### 截止当期月均一级保养次数

```markdown
# 业务属性：
1.数据定义：截止当期月均一级保养次数反映当年发生保养的频率
2.指标计算逻辑：∑（一次保养工单数量）/月份
3.数据来源：一级保养-一级保养记录
4.指标类型：复合指标
5.组织维度：电缆产业、公司、生产厂区、生产厂
6.时间维度：日、月、年

```

&nbsp;

```markdown
with a as (
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	sum(value2) as value2,
	case when sum(value2) = 0 then null else sum(value1)/sum(value2) end as 占比,
	case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
	case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('平均故障修复时间MTTR','平均无故障时长MTBF')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
union all 
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	max(cast(value2 as UNSIGNED)) as value2,
	case when sum(value2) = 0 then null else sum(value1)/max(cast(value2 as UNSIGNED)) end as 占比,
	case when sum(cs_value2) = 0 then null else sum(cs_value1)/max(cast(value2 as UNSIGNED)) end as 同期占比,
	case when sum(sq_value2) = 0 then null else sum(sq_value1)/max(cast(value2 as UNSIGNED)) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('月均被动维修次数','月均一级保养次数','月均主动维修次数','月均委外维修次数','截止当期月均故障次数')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype!=3,
"and date_type_id = 2 and date_type >= concat(substr('"+acc_date+"',1,4),'-01') and date_type <= substr('"+acc_date+"',1,7)",
"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4)","")}
group by 1,2
union all  
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	sum(value2) as value2,
	case when sum(value2) = 0 then null 
	when ${datetype} = 1 then sum(value1)/sum(value2)
	when ${datetype} != 1 then sum(value1)/sum(value2)/12*1.5
	end as 占比,
	case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
	case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('人均净维修时长','人均工作时长','人均被动维修时长','人均主动维修时长')
and industry = '电缆产业'
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
)

select 
	mark_name,
	type_name,
	value1,
	value2,
	占比,
	case when 同期占比 = 0 then null else (占比-同期占比)/同期占比 end as 同比,
	case when 上期占比 = 0 then null else (占比-上期占比)/上期占比 end as 环比
from a 
```

### 故障次数

```markdown
 # 业务属性：
1.数据定义：设备发生故障的次数
2.指标计算逻辑：统计故障工单表中工单状态的次数（排除工单状态为关闭的）
3.数据类型：累计数据
4.指标类型：
5.展示路径：
6.数据来源：yd_mkt_device_first_df 

```

```markup
select 
dept_name,
sum(value1) as value1,
sum(value2) as value2,
case when sum(value2) = 0 then null else round(sum(value1)/sum(value2),0) end as 占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and mark_name = '设备故障情况分析'
and type_name = '平均故障修复时间MTTR'
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1

```

### 设备平均开机时长

```markdown
# 业务属性
1.指标定义：统计周期内数采设备的平均开机时长，日/月/年维度单位分别为小时、天、天
2.指标逻辑：SUM（数采设备开机时长）/ 数采设备台数
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.分析维度：设备重要性（重要设备）
8.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
9.数据来源：IOT数采（yd_device_org_plane、dim_device_bigdata_min_start、dw_device_work_status_bigdata_all_time）

# BI逻辑
1. 所用字段：avg_open_stay
2. BI SQL
```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y

```

### 当期故障总次数的环比

```markdown
# 业务属性：
1.数据定义：指的是将当期的故障总次数与上一期（即上一个月）的故障总次数进行比较
2.指标计算逻辑公式：
3.测量方式：日、月、年
4.分析维度：设备重要性（一般、重要）、设备分类、故障次数、故障原因
5.数据类型：累计数据
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.数据来源：故障工单表eam_workorder_m
            工单管理-故障工单           
           工单管理-委外维修工单eam_workorder_out_maintenance

```

&nbsp;

```markdown
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(cs_value1) as cs_value1,
    sum(sq_value1) as sq_value1,
    case when sum(cs_value1) = 0 then null else (sum(value1)-sum(cs_value1)) / sum(cs_value1) end as 同比,
    case when sum(sq_value1) = 0 then null else (sum(value1)-sum(sq_value1)) / sum(sq_value1) end as 环比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
    ${if(level==1,"and industry = '"+cy+"' "," ")}
    ${if(level==2,"and company = '"+company+"' "," ")}
    ${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
    ${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
    ${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
    ${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
    ${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2

```

&nbsp;

&nbsp;

### 重要设备停机占比

```markdown
# 业务属性
1.指标定义：停机的关键数采设备中，类型为"重要"的设备所占的比例（100%）
2.指标逻辑：类型为重要的且是停机的关键数采设备数量 / 停机的关键数采设备数量 * 100%
3.数据类型：实时数据
4.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 数采设备运行状态分析 -> 查看明细 -> 重要设备、一般设备停机占比分析
5.数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_oraganization_v、yd_device_org_plane）

 
# BI逻辑
1. 所用字段：重要设备停机数量 / 总停机数量
2. BI SQL

```

```markdown
select  
    '重要设备停机占比' as type,
    sum(case when td.ac_position = 'A' then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 
union all 
select  
    '一般设备停机占比' as type,
    sum(case when td.ac_position = 'B' then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 
union all 
select  
    '其他设备停机占比' as type,
    sum(case when td.ac_position is null then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 一级保养次数

```markdown
# 业务属性：
1.数据定义：统计每日设备开机前进行的例行检查保养次数
2.指标计算逻辑：d
3.数据类型：yd_mkt_device_first_df

```

```markdown
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(cs_value1) as cs_value1,
    sum(sq_value1) as sq_value1,
    case when sum(cs_value1) = 0 then null else (sum(value1)-sum(cs_value1)) / sum(cs_value1) end as 同比,
    case when sum(sq_value1) = 0 then null else (sum(value1)-sum(sq_value1)) / sum(sq_value1) end as 环比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2

```

### 当期故障总次数的同比

```markdown
业务属性：
1.数据定义：指的是将当期的故障总次数与上一年同期的故障总次数进行比较
2.指标计算逻辑公式：
3.测量方式：日、月、年
4.分析维度：设备重要性（一般、重要）、设备分类、故障次数、故障原因
5.数据类型：累计数据
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.数据来源：故障工单表eam_workorder_m
            工单管理-故障工单           
           工单管理-委外维修工单eam_workorder_out_maintenance

```

&nbsp;

```markdown
select 
	mark_name,
	type_name,
	sum(value1) as value1,
	sum(cs_value1) as cs_value1,
	sum(sq_value1) as sq_value1,
	case when sum(cs_value1) = 0 then null else (sum(value1)-sum(cs_value1)) / sum(cs_value1) end as 同比,
	case when sum(sq_value1) = 0 then null else (sum(value1)-sum(sq_value1)) / sum(sq_value1) end as 环比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
	${if(level==1,"and industry = '"+cy+"' "," ")}
	${if(level==2,"and company = '"+company+"' "," ")}
	${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
	${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
	${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
	${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
	${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
```

### 人均工作时长

```markdown
# 业务属性：
1.数据定义：在一定时间段内，维修工平均每天的工作时长
2.指标类型：复合指标
3.数据类型：日、月、年
4.数据记录方式：日
5.分析维度：电缆产业、维修班组、被动维修、主动维修
6.更新时间/频次：每日8:00
7.指标计算逻辑公式：人均工作时长=∑（下午刷卡时间-上午刷卡时间）/维修工总人数
8.数据来源：维修状态看板

```

### 停机率超25%关键设备数量

```markdown
# 业务属性
1.指标定义：统计周期内停机时长占应工作时长超25%的关键数采设备的数量（台）
2.指标逻辑：应工作时长 = 统计周期结束时间 - 统计周期开始时间
          设备开机时长 = SUM(设备开机结束 - 设备开机结束时间)
          设备停机时长 = 应工作时长 - 设备开机时长
3.时间维度：日、月、年
4.数据类型：累计数据
5.指标类型：复合指标
6.组织维度：电缆产业、公司、生产厂区、生产厂
7.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 累计数据 -> 数采设备运行状态分析
8.数据来源：IOT数采（dw_device_work_status_bigdata_all_time、dim_device_bigdata_min_start、yd_device_org_plane）

# BI逻辑
1. 备注：与`停机率超50%关键设备数量`指标共用BI数据集
2. 所用字段：stop25_num
3. BI SQL

```

```markdown
select
avg_open_stay, --平均开机时长
imp_open_stay/imp_device_cnt as avg_imp_open_stay,--重要设备平均开机时长
case when avg_cs_open_stay = 0 then null else (avg_open_stay-avg_cs_open_stay) / avg_cs_open_stay end as 开机时长同比,
case when avg_sq_open_stay = 0 then null else (avg_open_stay-avg_sq_open_stay) / avg_sq_open_stay end as 开机时长环比,
use_rate, --开机率
case when cs_use_rate = 0 then null else (use_rate-cs_use_rate) / cs_use_rate end as 开机率同比,
case when sq_use_rate = 0 then null else (use_rate-sq_use_rate) /sq_use_rate end as 开机率环比,
stop25_num, --停机率超25%的设备数量
case when cs_stop25_num = 0 then null else (stop25_num-cs_stop25_num) / cs_stop25_num end as 停机25数量同比,
case when sq_stop25_num = 0 then null else (stop25_num-sq_stop25_num) / sq_stop25_num end as 停机25数量环比,
stop50_num, --停机率超25%的设备数量
case when cs_stop50_num = 0 then null else (stop50_num-cs_stop50_num) / cs_stop50_num end as 停机50数量同比,
case when sq_stop50_num = 0 then null else (stop50_num-sq_stop50_num) / sq_stop50_num end as 停机50数量环比
from
(
SELECT 
    sum(xx.open_stay) as open_stay,--开机时长
    sum(case when xx.device_type='关键设备' then xx.open_stay else 0 end) as imp_open_stay,--重要设备开机时长
    sum(case when xx.device_type='关键设备' then 1 else 0 end) as imp_device_cnt,--重要设备数量
    sum(case when xx.all_time <= 0 then 0
          else xx.all_time end) as all_time, --应工作时长
    sum(case when nvl(xx.cs_all_time,0) <= 0 then 0
          else xx.cs_all_time end) as cs_all_time,--同期应工作时长
    sum(case when nvl(xx.sq_all_time,0) <= 0 then 0
          else xx.sq_all_time end) as sq_all_time,--上期应工作时长
    nvl(avg(xx.open_stay),0) as avg_open_stay,--平均开机时长
    nvl(avg(xx.cs_open_stay),0) as avg_cs_open_stay,--同期平均开机时长
    nvl(avg(xx.sq_open_stay),0) as avg_sq_open_stay,--上期平均开机时长
    case when sum(xx.all_time) <= 0 then 0
         when nvl(sum(xx.open_stay),0)=0 then 0
         when sum(xx.open_stay) >= sum(xx.all_time) then 1
         else sum(xx.open_stay) / sum(xx.all_time) end as use_rate, --开机率
    case when sum(nvl(xx.cs_all_time,0)) <= 0 then 0
         when nvl(sum(xx.cs_open_stay),0)=0 then 0
         when sum(xx.cs_open_stay) >= sum(xx.cs_all_time) then 1
         else sum(xx.cs_open_stay) / sum(xx.cs_all_time) end as cs_use_rate, --同期开机率
    case when sum(nvl(xx.sq_all_time,0)) <= 0 then 0
         when nvl(sum(xx.sq_open_stay),0)=0 then 0
         when sum(xx.sq_open_stay) >= sum(xx.sq_all_time) then 1
         else sum(xx.sq_open_stay) / sum(xx.sq_all_time) end as sq_use_rate, --上期开机率
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as stop25_num, --停机率超25%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop25_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.75 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop25_num,
    sum(case when xx.all_time=0 then 0 when xx.open_stay / xx.all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as stop50_num, --停机率超50%的关键设备数量
    sum(case when xx.cs_all_time=0 then 0 when xx.cs_open_stay / xx.cs_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as cs_stop50_num,
    sum(case when xx.sq_all_time=0 then 0 when xx.sq_open_stay / xx.sq_all_time < 0.5 and xx.device_type='关键设备' then 1 else 0 end) as sq_stop50_num
FROM
--每个设备在所选时间段内的开机时长 
(
SELECT 
       '电缆产业' as industry,
       a.device_id,
       nvl(a.device_type, 'xx') as device_type,
       b.company_name,
       b.factory_name,
       b.use_dept as dept_id,
       b.use_dept_name,
       nvl(td.open_stay,0) as open_stay,
       nvl(td_cs.open_stay,0) as cs_open_stay,
       nvl(td_sq.open_stay,0) as sq_open_stay,
       td.all_time, --应工作时长
       td_cs.all_time as cs_all_time, --应工作时长同期
       td_sq.all_time as sq_all_time --应工作时长上期
FROM dim_device_bigdata_min_start a
inner join  yd_device_org_plane  b  
        on a.device_id=nvl(b.mes_code, 'xx')
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and work_day =  '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and substr(work_day, 1, 7) =  substr('"+acc_date+"', 1, 7)   ","")}
                    ${if(datetype == 3," and substr(work_day, 1, 4) =  substr('"+acc_date+"', 1, 4)   ","")}
              group by a.device_id 
              ) td on a.device_id=td.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_cs on a.device_id=td_cs.device_id
left join (
              select
                  a.device_id,
                  (case when '${datetype}' = 1  then sum(nvl(open_stay,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(open_stay,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(open_stay,0))/24
                       else 0 end) open_stay,
                  (case when '${datetype}' = 1  then sum(nvl(all_time,0))      --选日，计算小时
                        when '${datetype}' = 2  then sum(nvl(all_time,0))/24   --选月或年，计算天
                        when '${datetype}' = 3  then sum(nvl(all_time,0))/24
                       else 0 end) all_time
              from dw_device_work_status_bigdata_all_time a  
              where 1=1
                    ${if(datetype == 1," and to_char(to_date(work_day,'yyyy-MM-dd')+1, 'yyyy-MM-dd') = '"+acc_date+"' "," ")}
                    ${if(datetype == 2," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 1), 'yyyy-MM') = substr('"+acc_date+"', 1, 7) ","")}
                    ${if(datetype == 3," and to_char(add_months(to_date(work_day,'yyyy-MM-dd'), 12), 'yyyy') = substr('"+acc_date+"', 1, 4) ","")}
              group by a.device_id
              ) td_sq on a.device_id=td_sq.device_id
--where nvl(a.device_type, 'xx')='关键设备'
) xx
where 1=1
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company_name = '"+company+"' "," ")}
${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
) y

```

### 台账登记设备总数量

```markdown
# 业务属性
1.数据定义：反映当前时间点设备管理系统设备台账中登记的设备总数
2.单位：台
3.指标类型：原子指标
4.分析维度：电缆产业、公司、生产厂区、使用部门
5.数据类型：实时数据
6.更新时间/频次：实时更新
7.指标计算逻辑公式：统计设备管理系统登记的设备总数量
8.数据来源：设备台账

```

```markdown
with x as (
select sum(cnt1) as 运行数量,
       sum(cnt2) as 停机数量,
       sum(cnt3) as 闲置数量,
       sum(cnt) as 设备总数,
       (sum(cnt1)+sum(cnt2)) as IOT设备总数,
       case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt1)/(sum(cnt1)+sum(cnt2)) else 0 end as 运行占比,
       case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt2)/(sum(cnt1)+sum(cnt2)) else 0 end as 停机占比,
       case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt3)/(sum(cnt1)+sum(cnt2)) else 0 end as 闲置占比
from (
        select 
               sum(case when bq.run_status = 10 and bq.ac_asset_status not in (20) then 1 else 0 end) as cnt1,
               sum(case when bq.run_status = 30 and bq.ac_asset_status not in (20) then 1 else 0 end) as cnt2,
               sum(case when bq.ac_asset_status = 40 then 1 else 0 end) as cnt3,
               count(1) as cnt
        from (
            select 
                eeac.ac_code,
                eeac.use_dept as dept_id,
                eod.dep_name,
                eod.factory_id as fac_id,
                eod.factory_name as fac_name,
                eod.company_id as company_id,
                eod.company_name as company,
                eeac.run_status,
                eeac.ac_asset_status, -- '管理状态 EAM_ASSET_GL_STATUS 在用 (10)报废 (20)处置(30)闲置 (40)报废留用 (50)试运行 (60)'
                date(last_update_date) as dd
            from eam_eledger_asset_card eeac
                 left join pro_eam_org_dimension eod on eeac.use_dept = eod.dep_id
            where eeac.delete_flag = 0
                 and use_dept != '590566710549954560' -- 剔除采供中心电动液压车
             ) as bq
        where 1=1
               ${if(level=1,"and 1=1 "," ")}
               ${if(level=2,"and company = '"+company+"' "," ")}
               ${if(level=3,"and fac_name = '"+fac_name+"' "," ")}
               ${if(level=4,"and dept_id = '"+dept_id+"' "," ")}
)aa
),
y as (
select count(distinct ac_code) as 故障机台数
from (
      select
          x1.ac_code,
          x1.department_id as dept_id,
          x2.dep_name,
          x2.factory_id as fac_id,
          x2.factory_name as fac_name,
          x2.company_id as company_id,
          x2.company_name as company
      from eam_workorder_m x1
           join pro_eam_org_dimension x2 on x1.department_id=x2.dep_id
      where substr(x1.creation_date,1,10) = curdate()
     ) as bq
where 1=1
       ${if(level=1,"and 1=1 "," ")}
       ${if(level=2,"and company = '"+company+"' "," ")}
       ${if(level=3,"and fac_name = '"+fac_name+"' "," ")}
       ${if(level=4,"and dept_id = '"+dept_id+"' "," ")}
)
select x.运行数量,
       x.停机数量,
       x.IOT设备总数,
       x.设备总数,
       x.运行占比,
       x.停机占比,
       x.闲置占比,
       y.故障机台数,
       case when x.设备总数!=0 then y.故障机台数/x.设备总数 else 0 end as 故障占比
from x left join y on 1=1

```

### 二级保养工单数量

```markdown
# 业务属性：
1.数据定义：
2.指标计算逻辑:二级保养工单数量=SUM（二级保养工单数量）
           已执行：取工单状态为已执行的数据
           待执行：取工单状态为待执行的数据
3.指标类型：复合指标
4.组织维度：电缆产业、公司、生产厂区、生产厂
5.时间维度：日、月、年
6.数据来源：一级保养-一级保养记录

```

&nbsp;

### 计划维修费用



### 已报修未完成超72小时

```markdown
# 业务属性：
1.数据定义：反映已报修超过12小时未完成维修的工单数量
2.指标计算逻辑：报修时间=当前时间点-故障报修时间点
3.测量方式：实时数据
4.数据记录方式：实时数据
5.分析维度：产业、公司生产厂区、使用部门
6.更新时间/频次：实时更新
7.数据来源：eam_workorder_m、pro_eam_org_dimension

```

&nbsp;

```markdown
select count(case when timestampdiff(hour,repair_time, now()) > 8 then 1 end)  as over_8_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 12 then 1 end) as over_12_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 24 then 1 end) as over_24_hours,
       count(case when timestampdiff(hour,repair_time, now()) > 72 then 1 end) as over_72_hours
from (
select eod.industry,
       eod.company_name company,
       eod.factory_name fac_name,
       eod.dep_id dept_id,
       eod.dep_code dept_code,
       ewm.repair_time
from eam_workorder_m ewm
     left join pro_eam_org_dimension eod on ewm.department_id=eod.dep_id
where ewm.delete_flag = 0
      and ewm.work_order_status < 5 -- 状态小于5表示未完成
)x1
where 1=1
     ${if(level==1,"and industry = '"+cy+"' "," ")}
     ${if(level==2,"and company = '"+company+"' "," ")}
     ${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
     ${if(level==4,"and dept_id = '"+dept_id+"' "," ")}

```

### 维修耗时



### 人均主动维修时长的环比



### 一般设备停机占比

```markdown
# 业务属性
1.指标定义：停机的关键数采设备中，类型为"一般"的设备所占的比例（100%）
2.指标逻辑：类型为一般的且是停机的关键数采设备数量 / 停机的关键数采设备数量 * 100%
3.数据类型：实时数据
4.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 数采设备运行状态分析 -> 查看明细 -> 重要设备、一般设备停机占比分析
5.数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_oraganization_v、yd_device_org_plane）

 
# BI逻辑
1. 所用字段：一般设备停机数量 / 总停机数量
2. BI SQL

```

```markdown
select  
    '重要设备停机占比' as type,
    sum(case when td.ac_position = 'A' then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 
union all 
select  
    '一般设备停机占比' as type,
    sum(case when td.ac_position = 'B' then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 
union all 
select  
    '其他设备停机占比' as type,
    sum(case when td.ac_position is null then 1 else 0 end) as cnt
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
and (device_status != 2 or device_status is null)
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 一级保养次数同比

```markdown
# 业务属性：
1.数据定义：

```

&nbsp;

```markdown
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(cs_value1) as cs_value1,
    sum(sq_value1) as sq_value1,
    case when sum(cs_value1) = 0 then null else (sum(value1)-sum(cs_value1)) / sum(cs_value1) end as 同比,
    case when sum(sq_value1) = 0 then null else (sum(value1)-sum(sq_value1)) / sum(sq_value1) end as 环比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2

```

### 当前处理工单数量

```markdown
# 业务属性:
1.数据定义：反映当前时间点未完成的故障维修、计划维修、二级保养工单总数
2.指标计算逻辑：统计设备管理系统中故障维修、计划维修、二级保养工单的工单数量
3.测量方式：实时数据
4.数据记录方式：实时数据
5.分析维度：产业、公司、生产厂区、使用部门
6.更新时间/频次:实时更新
7.数据来源：eam_workorder_slave、eam_workorder_m

```

&nbsp;

```markdown
with base as (
select '计划维修'            as repair_type,
        ews.work_order_number,
        ews.actual_begin_time as '开始时间',
        eod1.parent_id        as company_id,
        eod1.company,
        '电缆产业' as industry
 from eam_workorder_slave ews
          left join eam_org_dimension eod on ews.department_id = eod.dep_id
          left join eam_org_dimension eod1 on eod.parent_id = eod1.dep_id
 where ews.delete_flag = 0
 union all
 SELECT '故障维修'        as repair_type,
        ewm.work_order_number,
        ewm.creation_date as '开始时间',
        eod1.parent_id    as company_id,
        eod1.company,
        '电缆产业' as industry
 FROM eam_workorder_m ewm
          left join eam_org_dimension eod on ewm.department_id = eod.dep_id
          left join eam_org_dimension eod1 on eod.parent_id = eod1.dep_id
 where ewm.delete_flag = 0)
 
select count(base.work_order_number) as cnt
from base
where substr(开始时间,1,10) = CURRENT_DATE
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and repair_type = '"+fac_name+"' "," ")}
${if(level==4,"and repair_type = '"+dept_id+"' "," ")}

```

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

&nbsp;

### 设备总数量

```markdown
# 业务属性
1.指标定义：关键工序数采设备的数量（台）
2.指标逻辑：select count(1) from dim_device_bigdata where mark like '%关键设备%'
3.数据类型：实时数据
4.指标类型：原子指标
5.分析维度：电缆产业、公司、生产厂区、使用部门、重要设备、一般设备
6.展示路径：
   （1）PC端：设备域PC端首页 -> 数采设备运行状态分析
   （2）手机端：设备域手机端首页 -> 实时数据 -> 数采设备运行状态分析
7.数据来源：IOT数采（dim_device_bigdata、dw_device_status_bigdata、dim_organization_v、yd_device_org_plane）

# BI逻辑
1. 备注：与`设备停机台数`、`设备停机占比`、`设备运行台数`指标共用BI数据集
2. 所用字段：连接数
3. BI SQL
```

```markdown
select  
    count(1) 连接数 ,
    count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 停机,
    sum( CASE WHEN (device_status = 2 and work_status='Y') THEN 1 ELSE 0 END ) 作业,
    sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END ) 开机,
    sum( CASE WHEN device_status > 0 THEN 1 ELSE 0 END ) 在线,
    (count(1)-sum( CASE WHEN device_status = 2 THEN 1 ELSE 0 END )) / count(1) as 停机占比
FROM dim_device_bigdata ta
left  join 
(select  
  DEVICE_ID,
  DEVICE_STATUS,
  work_status
from dw_device_status_bigdata  
where to_char(dt,'yyyy-MM-dd') = to_char(CURRENT_DATE,'yyyy-MM-dd')  ) tb on ta.device_id = tb.device_id
left  join 
(select distinct group_name,org_name,corp_name,fac_name,fac_code from DIM_ORGANIZATION_V ) tc on  ta.L4_CODE = tc.FAC_CODE 
LEFT join  yd_device_org_plane td on ta.device_id=nvl(td.mes_code, 'xx')
where ta.mark like '%关键设备%' 
${if(level==1," and  tc.group_name = '"+cy+"' and  tc.org_name != '电气'"," ")}
${if(level==2," and  tc.org_name = '"+company+"'   ","  ")}
${if(level==3," and  td.factory_name = '"+fac_name+"' ","   ")}
${if(level==4," and  td.use_dept = '"+dept_code+"'"," ")} 

```

### 截止当期月均被动维修次数

```markdown
# 业务属性：
1.数据定义：反映当年设备发生被动维修的频率
2.指标计算逻辑：被动维修工单数量的总和/月份
               被动维修=故障维修+委外维修（按工单创建时间）
3.数据来源: 工单管理-故障工单eam_workorder_m
           工单管理-委外维修工单eam_workorder_out_maintenance
          yd_mkt_device_first_df

```

&nbsp;

```markdown
with a as (
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(value2) as value2,
    case when sum(value2) = 0 then null else sum(value1)/sum(value2) end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('平均故障修复时间MTTR','平均无故障时长MTBF')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
union all 
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    max(cast(value2 as UNSIGNED)) as value2,
    case when sum(value2) = 0 then null else sum(value1)/max(cast(value2 as UNSIGNED)) end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/max(cast(value2 as UNSIGNED)) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/max(cast(value2 as UNSIGNED)) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('月均被动维修次数','月均一级保养次数','月均主动维修次数','月均委外维修次数','截止当期月均故障次数')
${if(level==1,"and industry = '"+cy+"' "," ")}
${if(level==2,"and company = '"+company+"' "," ")}
${if(level==3,"and fac_name = '"+fac_name+"' "," ")}
${if(level==4,"and dept_code = '"+dept_id+"' "," ")}
${if(datetype!=3,
"and date_type_id = 2 and date_type >= concat(substr('"+acc_date+"',1,4),'-01') and date_type <= substr('"+acc_date+"',1,7)",
"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4)","")}
group by 1,2
union all  
select 
    mark_name,
    type_name,
    sum(value1) as value1,
    sum(value2) as value2,
    case when sum(value2) = 0 then null 
    when ${datetype} = 1 then sum(value1)/sum(value2)
    when ${datetype} != 1 then sum(value1)/sum(value2)/12*1.5
    end as 占比,
    case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,
    case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比
from yd_mkt_device_first_df 
where plate_name = '设备域首页'
and type_name in ('人均净维修时长','人均工作时长','人均被动维修时长','人均主动维修时长')
and industry = '电缆产业'
${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}
${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}
${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}
group by 1,2
)

select 
    mark_name,
    type_name,
    value1,
    value2,
    占比,
    case when 同期占比 = 0 then null else (占比-同期占比)/同期占比 end as 同比,
    case when 上期占比 = 0 then null else (占比-上期占比)/上期占比 end as 环比
from a 

```

&nbsp;

### 当前设备故障占比

```markdown
# 业务属性：
1.数据定义：截止当前时间设备发生故障的台数占设备总台数的比例
2.指标逻辑计算公式：故障台数/设备总数
3.指标类型：复合指标
4.分析维度：电缆产业、公司、生产厂区、使用部门
5.测量方式：实时数据
6.数据记录方式：实时数据
7.更新时间/频次：实时更新
8.数据来源：设备台账eam_eledger_asset_card
9.展示路径：
（1）移动端：设备域首页 -> 设备故障情况分析 -> 当前故障设备数量占比

```

&nbsp;

```markdown
with x as (
select sum(cnt1) as 运行数量,
       sum(cnt2) as 停机数量,
       sum(cnt3) as 闲置数量,
       sum(cnt) as 设备总数,
       (sum(cnt1)+sum(cnt2)) as IOT设备总数,
       case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt1)/(sum(cnt1)+sum(cnt2)) else 0 end as 运行占比,
       case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt2)/(sum(cnt1)+sum(cnt2)) else 0 end as 停机占比,
       case when (sum(cnt1)+sum(cnt2))!=0 then sum(cnt3)/(sum(cnt1)+sum(cnt2)) else 0 end as 闲置占比
from (
        select 
               sum(case when bq.run_status = 10 and bq.ac_asset_status not in (20) then 1 else 0 end) as cnt1,
               sum(case when bq.run_status = 30 and bq.ac_asset_status not in (20) then 1 else 0 end) as cnt2,
               sum(case when bq.ac_asset_status = 40 then 1 else 0 end) as cnt3,
               count(1) as cnt
        from (
            select 
                eeac.ac_code,
                eeac.use_dept as dept_id,
                eod.dep_name,
                eod.factory_id as fac_id,
                eod.factory_name as fac_name,
                eod.company_id as company_id,
                eod.company_name as company,
                eeac.run_status,
                eeac.ac_asset_status, -- '管理状态 EAM_ASSET_GL_STATUS 在用 (10)报废 (20)处置(30)闲置 (40)报废留用 (50)试运行 (60)'
                date(last_update_date) as dd
            from eam_eledger_asset_card eeac
                 left join pro_eam_org_dimension eod on eeac.use_dept = eod.dep_id
            where eeac.delete_flag = 0
                 and use_dept != '590566710549954560' -- 剔除采供中心电动液压车
             ) as bq
        where 1=1
               ${if(level=1,"and 1=1 "," ")}
               ${if(level=2,"and company = '"+company+"' "," ")}
               ${if(level=3,"and fac_name = '"+fac_name+"' "," ")}
               ${if(level=4,"and dept_id = '"+dept_id+"' "," ")}
)aa
),
y as (
select count(distinct ac_code) as 故障机台数
from (
      select
          x1.ac_code,
          x1.department_id as dept_id,
          x2.dep_name,
          x2.factory_id as fac_id,
          x2.factory_name as fac_name,
          x2.company_id as company_id,
          x2.company_name as company
      from eam_workorder_m x1
           join pro_eam_org_dimension x2 on x1.department_id=x2.dep_id
      where substr(x1.creation_date,1,10) = curdate()
     ) as bq
where 1=1
       ${if(level=1,"and 1=1 "," ")}
       ${if(level=2,"and company = '"+company+"' "," ")}
       ${if(level=3,"and fac_name = '"+fac_name+"' "," ")}
       ${if(level=4,"and dept_id = '"+dept_id+"' "," ")}
)
select x.运行数量,
       x.停机数量,
       x.IOT设备总数,
       x.设备总数,
       x.运行占比,
       x.停机占比,
       x.闲置占比,
       y.故障机台数,
       case when x.设备总数!=0 then y.故障机台数/x.设备总数 else 0 end as 故障占比
from x left join y on 1=1

```

### 人均主动维修时长



### 截止当期月均故障次数

&nbsp;

```markdown
# 业务属性：
1.数据定义：截止当期月均故障次数反映当年设备发生故障频率
2.指标计算逻辑公式：截止当期月均故障次数=∑（截止当期故障总次数）/月份
3.测量方式：日、月、年
4.数据记录方式：日、月
5.分析维度：产业、公司、生产厂区、使用部门
6.更新时间/频次：每日8:00
7.数据来源：故障工单表

```

&nbsp;

```markup
with a as (

select

mark_name,

type_name,

sum(value1) as value1,

sum(value2) as value2,

case when sum(value2) = 0 then null else sum(value1)/sum(value2) end as 占比,

case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,

case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比

from yd_mkt_device_first_df

where plate_name = '设备域首页'

and type_name in ('平均故障修复时间MTTR','平均无故障时长MTBF')

${if(level==1,"and industry = '"+cy+"' "," ")}

${if(level==2,"and company = '"+company+"' "," ")}

${if(level==3,"and fac_name = '"+fac_name+"' "," ")}

${if(level==4,"and dept_code = '"+dept_id+"' "," ")}

${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}

${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}

${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}

group by 1,2

union all

select

mark_name,

type_name,

sum(value1) as value1,

max(cast(value2 as UNSIGNED)) as value2,

case when sum(value2) = 0 then null else sum(value1)/max(cast(value2 as UNSIGNED)) end as 占比,

case when sum(cs_value2) = 0 then null else sum(cs_value1)/max(cast(value2 as UNSIGNED)) end as 同期占比,

case when sum(sq_value2) = 0 then null else sum(sq_value1)/max(cast(value2 as UNSIGNED)) end as 上期占比

from yd_mkt_device_first_df

where plate_name = '设备域首页'

and type_name in ('月均被动维修次数','月均一级保养次数','月均主动维修次数','月均委外维修次数','截止当期月均故障次数')

${if(level==1,"and industry = '"+cy+"' "," ")}

${if(level==2,"and company = '"+company+"' "," ")}

${if(level==3,"and fac_name = '"+fac_name+"' "," ")}

${if(level==4,"and dept_code = '"+dept_id+"' "," ")}

${if(datetype!=3,

"and date_type_id = 2 and date_type >= concat(substr('"+acc_date+"',1,4),'-01') and date_type <= substr('"+acc_date+"',1,7)",

"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4)","")}

group by 1,2

union all

select

mark_name,

type_name,

sum(value1) as value1,

sum(value2) as value2,

case when sum(value2) = 0 then null

when ${datetype} = 1 then sum(value1)/sum(value2)

when ${datetype} != 1 then sum(value1)/sum(value2)/12*1.5

end as 占比,

case when sum(cs_value2) = 0 then null else sum(cs_value1)/sum(cs_value2) end as 同期占比,

case when sum(sq_value2) = 0 then null else sum(sq_value1)/sum(sq_value2) end as 上期占比

from yd_mkt_device_first_df

where plate_name = '设备域首页'

and type_name in ('人均净维修时长','人均工作时长','人均被动维修时长','人均主动维修时长')

and industry = '电缆产业'

${if(datetype==1,"and date_type_id = 1 and date_type = '"+acc_date+"' "," ")}

${if(datetype==2,"and date_type_id = 2 and date_type = substr('"+acc_date+"',1,7) "," ")}

${if(datetype==3,"and date_type_id = 3 and date_type = substr('"+acc_date+"',1,4) "," ")}

group by 1,2

)

select

mark_name,

type_name,

value1,

value2,

占比,

case when 同期占比 = 0 then null else (占比-同期占比)/同期占比 end as 同比,

case when 上期占比 = 0 then null else (占比-上期占比)/上期占比 end as 环比

from a

```

### 今日未出勤人数

```markdown
# 业务属性：
1.数据定义:反映当前维修班组出勤情况
2.指标计算逻辑公式：设备管理系统中存在打卡记录即为出勤，否则为未出勤
3.数据类型：实时数据
4.数据记录方式：实时数据
5.指标类型：原子指标
6.分析维度：电缆产业
7.更新时间/频次：实时更新
8.数据来源：班组信息eam_eledger_team_member、人员出勤表eam_person_attendance、班组eam_eledger_team、机修班eam_maintenance_group 


```

&nbsp;

```markdown
with base as (select team_member_code
                   , eet.team_name
                   , eet.team_code
                   , emg.company
                   , company_id
                   , '电缆产业' as industry
              from eam_eledger_team_member as eetm
                       left join eam_eledger_team eet on eetm.team_id = eet.team_id
                       left join eam_maintenance_group emg on emg.team_code = eet.team_code
              where eet.team_status = 0
                )

select count(distinct base.team_member_code) as cnt
         , epa.pa_status
from base
left join eam_person_attendance epa on epa.pa_code = base.team_member_code
where delete_flag=0   ##删除标识 0表示未删除  1表示删除
and epa.pa_status = 2  ##当前状态 1表示出勤 2表示未出勤	
and substr(date(epa.creation_date),1,10) = curdate()	
union all 
select 
count(distinct team_member_code) as cnt,
'3' as pa_status  
from base

```

### 当前未完成故障工单总数量

```markdown
# 业务属性：
1.数据定义：反映当前时间点未完成维修的故障工单总数
2.指标计算逻辑：
3.数据类型：实时数据

```

&nbsp;

```markdown
 with base as (SELECT distinct eeac.ac_code,
                              eeac.use_dept,
                              eod.dep_name,
                              eod.parent_id  AS fac_id,
                              eod.factory_name,
                              eod1.parent_id AS company_id,
                              eod1.company
              FROM eam_eledger_asset_card eeac
                       LEFT JOIN eam_org_dimension eod ON eeac.use_dept = eod.dep_id
                       LEFT JOIN eam_org_dimension eod1 ON eod.parent_id = eod1.dep_id
              WHERE eeac.delete_flag = 0
                AND eeac.use_dept != '590566710549954560'),
     undo_order_info AS (SELECT work_order_number                      as won1,
                                ac_code,
                                department_id,
                                DATE_FORMAT(creation_date, '%Y-%m-%d') AS date_type
                         FROM eam_workorder_m
                         WHERE delete_flag = 0
                           and work_order_status not in (5, 8, 10)
                           and DATE_FORMAT(creation_date, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d')),

     all_order_info AS (SELECT department_id,
                               DATE_FORMAT(creation_date, '%Y-%m-%d') AS date_type,
                               count(work_order_number)               as value2
                        FROM eam_workorder_m
                        WHERE delete_flag = 0
                          and work_order_status not in (8, 10)
                          and DATE_FORMAT(creation_date, '%Y-%m-%d') = DATE_FORMAT(now(), '%Y-%m-%d')
                        group by department_id, date_type),

     allData as (select '电缆产业' as industry,
                        t2.company_id,
                        t2.company,
                        t2.fac_id,
                        t2.factory_name,
                        t2.use_dept as dept_id,
                        t2.dep_name,
                        t1.date_type,
                        count(t1.won1) as value1, -- 未完成故障工单总数
                        t3.value2                 -- 故障工单总数
                 from undo_order_info t1
                          left join base t2 on t1.ac_code = t2.ac_code
                          left join all_order_info t3 on t3.department_id = t1.department_id
                 where t2.use_dept != '590566710549954560'
                 group by t2.use_dept, t1.date_type
                 order by t1.date_type)

select sum(value1) as 未完成故障工单总数,
sum(value2) as 故障工单总数,
case when sum(value2) = 0 then null else sum(value1) / sum(value2) end as 占比
from allData
where 1=1
     ${if(level==1,"and industry = '"+cy+"' "," ")}
     ${if(level==2,"and company = '"+company+"' "," ")}
     ${if(level==3,"and factory_name = '"+fac_name+"' "," ")}
     ${if(level==4,"and dept_id = '"+dept_id+"' "," ")}
     
```

&nbsp;

&nbsp;

&nbsp;

with base as (SELECT distinct eeac.ac\_code,  
eeac.use\_dept,  
eod.dep\_name,  
eod.parent\_id AS fac\_id,  
eod.factory\_name,  
eod1.parent\_id AS company\_id,  
eod1.company  
FROM eam\_eledger\_asset\_card eeac  
LEFT JOIN eam\_org\_dimension eod ON eeac.use\_dept = eod.dep\_id  
LEFT JOIN eam\_org\_dimension eod1 ON eod.parent\_id = eod1.dep\_id  
WHERE eeac.delete\_flag = 0  
AND eeac.use\_dept != '590566710549954560'),  
undo\_order\_info AS (SELECT work\_order\_number as won1,  
ac\_code,  
department\_id,  
DATE\_FORMAT(creation\_date, '%Y-%m-%d') AS date\_type  
FROM eam\_workorder\_m  
WHERE delete\_flag = 0  
and work\_order\_status not in (5, 8, 10)  
and DATE\_FORMAT(creation\_date, '%Y-%m-%d') = DATE\_FORMAT(now(), '%Y-%m-%d')),

all\_order\_info AS (SELECT department\_id,  
DATE\_FORMAT(creation\_date, '%Y-%m-%d') AS date\_type,  
count(work\_order\_number) as value2  
FROM eam\_workorder\_m  
WHERE delete\_flag = 0  
and work\_order\_status not in (8, 10)  
and DATE\_FORMAT(creation\_date, '%Y-%m-%d') = DATE\_FORMAT(now(), '%Y-%m-%d')  
group by department\_id, date\_type),

allData as (select '电缆产业' as industry,  
t2.company\_id,  
t2.company,  
t2.fac\_id,  
t2.factory\_name,  
t2.use\_dept as dept\_id,  
t2.dep\_name,  
t1.date\_type,  
count(t1.won1) as value1, -- 未完成故障工单总数  
t3.value2 -- 故障工单总数  
from undo\_order\_info t1  
left join base t2 on t1.ac\_code = t2.ac\_code  
left join all\_order\_info t3 on t3.department\_id = t1.department\_id  
where t2.use\_dept != '590566710549954560'  
group by t2.use\_dept, t1.date\_type  
order by t1.date\_type)

select sum(value1) as 未完成故障工单总数,  
sum(value2) as 故障工单总数,  
case when sum(value2) = 0 then null else sum(value1) / sum(value2) end as 占比  
from allData  
where 1=1  
${if(level==1,"and industry = '"+cy+"' "," ")}  
${if(level==2,"and company = '"+company+"' "," ")}  
${if(level==3,"and factory\_name = '"+fac\_name+"' "," ")}  
${if(level==4,"and dept\_id = '"+dept\_id+"' "," ")}

### 故障维修




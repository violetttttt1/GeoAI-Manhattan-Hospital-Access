# 数据、研究区与电梯模型检查（checks_data）

覆盖：7 份数据的体检、研究区计数、车站表与电梯模型（串并联、补值）、148 St 搜索、设备清单对照、14 个站的建模修复。 节号在本文件内重新编排；原文件保存在 `archive/checks_original.md`，文末有新旧节号对照。所有数字均为初步结果。

---

*（原章：数据体检 checks.md）*

体检日期：2026-11-11。只做完整性与键匹配检查，未做任何分析。原始文件在 `raw/` 下，每份数据集一个独立目录。

## 1. 数据集概览

| 数据集 | 来源 / ID | 本地文件 | 行数 | 最新日期 |
|---|---|---|---|---|
| 电梯可用率 | data.ny.gov `rc78-7x78` | `raw/elevator_availability/` | 83,776 | Month = 2026-09-01（2015-01 起，共 141 个月） |
| 电梯资产清单 | data.ny.gov `94fv-bak7` | `raw/elevator_inventory/` | 759 | 无观测日期；`Latest Installation Date` 最大 2026-10-24 |
| MTA 车站 | data.ny.gov `39hk-dx4f` | `raw/mta_stations/` | 496 | 无日期列 |
| GTFS（地铁） | rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip | `raw/gtfs/` | stops 1,488 / trips 20,310 / routes 29 / transfers 613 / calendar 3 | calendar 有效期 2026-11-01 ~ 2027-05-15 |
| DOT Pedestrian Ramp Locations | data.cityofnewyork.us `ufzp-rrqu` | `raw/ped_ramp_locations/` | 217,679 | `GeoCyclora` 最大 2020-01-29（范围 2017-03-27 ~ 2020-01-29）；Socrata 元数据更新于 2022-05-09 |
| Pedestrian Ramp – Program Progress | data.cityofnewyork.us `e7gc-ub6z` | `raw/ramp_program_progress/` | 187,749 | `Construction_End_Date` 最大 2026-10-26（仅 60,510 行非空，最早 2003-03-22） |
| MBPO Pedestrian Ramp Report | data.cityofnewyork.us `8kic-uvpz` | `raw/mbpo_ramp_report/` | 277 | 无日期列；Socrata 元数据更新于 2021-08-10 |

注：行数均为下载 CSV 的实际行数，与 Socrata `count(*)` 一致（GTFS 除外，GTFS 没有此接口）。

## 2. 列名

**电梯可用率（23 列）**：Month, Borough, Equipment Type, Equipment Code, Managed By, Total Outages, Scheduled Outages, Unscheduled Outages, Entrapments, Time Since Major Improvement, AM Peak Availability, AM Peak Hours Available, AM Peak Total Hours, PM Peak Availability, PM Peak Hours Available, PM Peak Total Hours, 24-Hour Availability, 24-Hour Hours Available, 24-Hour Total Hours, Station Name, Station MRN, Station Complex Name, Station Complex MRN

**电梯资产清单（44 列）**：Equipment Code, Elevator or Escalator, Asset Class, Station MRN, Station Name, Station Description, Station Complex MRN, Station Complex Description, Subway Line, Borough, X Coordinate, Y Coordinate, Original Installation Date, Latest Installation Date, Service Status Code, Service Status, Service Life, NYCT Owned, Maintained By, Installer, Revenue Machine, ADA Compliant, Street Access, Exposed to Weather, Escalator Rise, Elevator Rise, Elevator Capacity, Elevator Loading Class, Elevator Number of Landings, Escalator Number of Steps, Escalator Step Width, Elevator Direction Serviced, Elevator Order, Elevator Mezzanine 1 Access, Elevator Mezzanine 2 Access, Elevator Platform Access, Notes, Redundant Elevator, Redundant Elevator Street Access, Redundant Elevator Mezzanine Access, Redundant Elevator Access Between Mezzanines, Redundant Elevator Platform Access, Alternative Route, Georeference

**MTA 车站（19 列）**：GTFS Stop ID, Station ID, Complex ID, Division, Line, Stop Name, Borough, CBD, Daytime Routes, Structure, GTFS Latitude, GTFS Longitude, North Direction Label, South Direction Label, ADA, ADA Northbound, ADA Southbound, ADA Notes, Georeference

**GTFS**
- stops：stop_id, stop_name, stop_lat, stop_lon, location_type, parent_station
- trips：route_id, trip_id, service_id, trip_headsign, direction_id, shape_id
- routes：route_id, agency_id, route_short_name, route_long_name, route_desc, route_type, route_url, route_color, route_text_color, route_sort_order
- calendar：service_id, monday…sunday, start_date, end_date
- transfers：from_stop_id, to_stop_id, transfer_type, min_transfer_time
- 另含 agency / calendar_dates / feed_info / shapes / stop_times，本次未逐一计行

**Ramp Locations（24 列）**：the_geom, CornerID, RampID, Ramp_OnStreet, GeoCyclora, Borough, StName1, StName2, CURB_REVEAL, RAMP_RUNNING_SLOPE_TOTAL, DWS_CONDITIONS, GUTTER_SLOPE, LND_WIDTH, LND_LENGTH, LND_CROSS_SLOPE, COUNTER_SLOPE, RAMP_WIDTH, RAMP_RIGHT_FLARE, RAMP_LEFT_FLARE, RAMP_LENGTH, RAMP_CROSS_SLOPE, PONDING, OBSTACLES_RAMP, OBSTACLES_LANDING

**Program Progress（9 列）**：the_geom, OBJECTID, CornerID, Street_Name1, Street_Name2, Borough, Construction_Type, Construction_End_Date, Construction_Status_Value

**MBPO Ramp Report（24 列）**：Station, Street 1, Street 2, Curb Cut, Center Cut, No Curb Cut, Ramp ID (No Id means a part of center cut), Compliant, Slope (1":12" or less), Slope Non-Comp, Ramp Width (36" or more), Width Non-Comp, Lip or Bump (1/4" or less), Lip Non-Comp, Crumbling Concrete?, Crumbling Non-Comp, Led to Pot Hole?, Pot Hole Non-Comp, Detectable warnings?, Warnings Non-Comp, Object barriers ?, Objects Non-Comp, Barriers above?, Ramp looks relatively "new"?

## 3. 电梯编号（Equipment Code）匹配率

可用率表与资产清单都含电梯和扶梯，下面按 `Equipment Type` / `Elevator or Escalator` = Elevator 过滤。

| 检查 | 结果 |
|---|---|
| 可用率表中不同的电梯编号数 | 419 |
| 资产清单中的电梯编号数 | 482（无重复） |
| 可用率 → 清单匹配率 | **419 / 419 = 100%** |
| 清单 → 可用率匹配率 | **419 / 482 = 86.9%** |
| 可用率最新月份（2026-09）的 419 个电梯 → 清单 | 100% |
| 电梯 + 扶梯合并后（可用率 701 个、清单 759 个）的交集 | 696 个 |

**清单里有、可用率表里没有的 63 个电梯：**
- 状态：53 个 Installed-Functioning-In Service，5 个 Installed-Non Functioning-Out of Service，4 个 Installed-Functioning-Out of Service，1 个 Removed
- 23 个的 Station MRN / Complex MRN 为空
- 归属：22 个非 NYCT 所有；维护方 NYCT 38、Private Contractor 14、LIRR 8、Third-Party 3
- 其中 22 个编号以 `X` 结尾
- 原因未核实。从归属和维护方看，疑似有一部分不属于 NYCT 地铁运营的统计口径，待确认

**编号格式提醒：** 编号带 `X` 后缀（如 `EL200X`），清单里 73 个电梯带 X，可用率表有 6,236 行带 X。若去掉 X 再比较，交集反而从 419 降到 417，说明 X 是编号的一部分，**不要去掉**。

## 4. 车站 / 综合体键匹配率

| 检查 | 结果 |
|---|---|
| 可用率 Complex MRN → MTA 车站 `Complex ID` | 152 / 152 = 100% |
| 清单 Complex MRN → MTA 车站 `Complex ID` | 158 / 158 = 100% |
| 同一电梯编号，两表 Complex MRN 一致 | 100%（419 个） |
| 同一电梯编号，两表 Station MRN 一致（原始字符串） | 84.2%（66 个不一致） |
| 同上，**去掉前导零后** | **100%** |
| Station MRN（去前导零）→ MTA 车站 `Station ID` | 可用率 185/185，清单 191/191 |
| MTA 车站 `GTFS Stop ID` → GTFS stops | 100%（496 个 = GTFS 的 496 个 parent station） |
| 清单 Station MRN → MTA 车站 `GTFS Stop ID` | 49 / 191（两者不是同一套编号，不能直接连） |

**关键发现：** 清单的 Station MRN 有 91 行带前导零（`012`），可用率表和车站表没有（`12`）。直接做字符串 join 会漏掉约 16% 的电梯。join 前必须统一，如 `lstrip("0")`。

车站表 496 行里 `ADA=1` 的有 166 行。其中 155 行所在综合体在清单里有电梯，11 行没有（原因未核实）。

## 5. 坡道表键匹配率

| 检查 | 结果 |
|---|---|
| Ramp Locations：RampID | 217,679 个，全部唯一，无空值 |
| Ramp Locations：CornerID | 134,127 个不同值，重复 83,552 行（一个路口多个坡道，属预期） |
| Program Progress：CornerID | 187,749 个，全部唯一 |
| Ramp Locations CornerID → Program Progress | 134,108 / 134,127 = 99.99% |
| Program Progress 中被 Ramp Locations 覆盖的 CornerID | 134,108 / 187,749 = 71.4%（其余路口没有 2017–2020 的普查记录） |
| MBPO Ramp ID → Ramp Locations `RampID` | 198 / 199 = 99.5% |
| MBPO Ramp ID → 任一表的 `CornerID` | 0（编号体系不同，必须用 RampID，不能用 CornerID） |

## 6. 其他需要留意的问题

1. **清单坐标列标签反了：** `X Coordinate` 的取值是 40.53–40.90（纬度），`Y Coordinate` 是 -74.x（经度）。使用前需对调，或改用 `Georeference`。
2. **电梯与坡道没有共同的键：** 两组数据之间没有直接的 ID 对应，只能靠空间位置关联（车站坐标 ↔ 坡道 `the_geom`）。
3. **Ramp Locations 较旧：** 数据实际采集期是 2017–2020，元数据最后更新是 2022-05。Program Progress 到 2026-11 还在更新。两者时间口径不同。
4. **Program Progress 的状态分布：** Planned Construction 61,183；Constructed 55,120；Not Required 25,411；Not Assigned 25,204；Complex Planned 16,288；Complex Constructed 4,543。`Construction_End_Date` 只有 32% 非空。
5. **MBPO 报告只有 277 行：** 属于局部（地铁站周边）抽样，不是全市普查，且 Ramp ID 缺失的行是中心切口（Center Cut）的一部分。
6. **GTFS calendar 是当前有效期的班表，** 与可用率的历史月度数据不在同一时间维度。

## 7. 未做的事

- 未检查各表内部的缺失值比例、异常值或重复记录（除上面提到的以外）
- 未核实第 3 节 63 个未匹配电梯的具体原因
- 未做任何统计分析

---

*（原章：第二轮检查：研究区内的缺口与合规情况）*

只做计数检查，不建模、不做推断。

## 8. 研究区定义（后面所有计数共用）

研究区 = **曼哈顿 110 St 以北** ∪ **三家医院各 400 米范围**，并要求数据的 Borough 字段是曼哈顿。

| 项目 | 做法 |
|---|---|
| 110 St 边界线 | 用坡道表中 81 个 110 St / Central Park North 路口的坐标拟合出一条直线（走向 -29°，残差标准差 8 m），线以北算"以北"。起初用 1 号线和 6 号线两个 110 St 站的连线，但 2/3 号线 110 St 站离线 104 m，所以换成了坡道拟合线。两种线在坡道上相差 46 个，电梯上无差别 |
| 边界上的坡道 | 110 St 本街两侧路口的坡道，北侧算入、南侧不算 |
| 医院坐标 | 用 OpenStreetMap Nominatim 按地址地理编码：Harlem Hospital（506 Lenox Ave）40.8147, -73.9393；NYP/Columbia Irving Medical Center（622 W 168th St）40.8410, -73.9407；Mount Sinai Morningside（1111 Amsterdam Ave）40.8052, -73.9614 |
| 400 米 | 每家医院取**单个坐标点**，直线距离 400 m。实际院区是一片楼群，尤其 Columbia 院区很大，若用建筑轮廓做缓冲，范围会更大、计数会略增 |
| 医院缓冲的作用 | 三家医院都在 110 St 以北，缓冲只会在 Mount Sinai Morningside（113 St）南侧多出一点：电梯 +0、坡道 +10、MBPO +0 |

## 9. 研究区电梯里，多少个在可用率表里没有记录

电梯 = 资产清单中 `Elevator or Escalator = Elevator`，坐标用清单里的 X/Y（对调后当作纬度/经度）。

| 指标 | 数值 |
|---|---|
| 清单中曼哈顿电梯 | 221 |
| 研究区内电梯 | **48** |
| 其中在可用率表有记录（任意月份） | 37 |
| **其中没有任何记录** | **11（22.9%）** |
| 其中最新月份（2026-09）没记录 | 11（同一批，不是只缺最近一个月） |

11 个无记录电梯的构成：
- **6 个**（EL147、EL150、EL151、EL152、EL153、EL155）：清单里没有车站名和 Station MRN，状态是 In Service，NYCT 所有和维护。研究区内 6 个缺车站编号的电梯全在这里，所以可能是清单里车站信息缺失造成了接不上，原因未核实
- **3 个**（EL166X、EL167X、EL169X）：137 St-City College 站，Private Contractor 维护，非 NYCT 所有，状态 Installed-Functioning-Out of Service
- **EL520**：137 St-City College 站，Third-Party Contractor 维护
- **EL156**：Dyckman St 站，NYCT 维护，In Service

医院 400 m 内的电梯：Harlem Hospital 2 个，NYP/Columbia 7 个，Mount Sinai Morningside 0 个，三者都含在上面的 48 个里；这 9 个的缺失情况没有单独拆。离 110 St 线最近的电梯在 1.15 km 外，所以边界定义对电梯结果没有影响。

明细在 [study_area_elevators.csv](../data/clean/study_area_elevators.csv)。

## 10. 研究区坡道里，多少个在 Program Progress 有完工日期

坡道 = Ramp Locations 的一行（一个坡道），按 `CornerID` 连到 Program Progress（Progress 里 CornerID 唯一，连接不会产生重复行）。Progress 的完工日期是路口级的，同一路口的多个坡道共享一个日期。

| 指标 | 坡道数 | 占研究区坡道 |
|---|---|---|
| 研究区坡道 | **6,647**（对应 3,874 个路口） | 100% |
| Progress 里没有对应路口 | 1 | |
| **有完工日期** | **2,011** | 30.3% |
| 其中 **2020 年 2 月 1 日及以后完工** | **1,429** | 21.5%（占有日期的 71.1%） |
| 其中 2020 年 1 月完工 | 58 | |
| 其中 2020 年 1 月之前完工 | 524 | |

"2020 年 1 月之后"我按 ≥ 2020-02-01 算（不含 1 月）。若把 1 月也算进去，是 1,487。若以 Ramp Locations 的采集截止日 2020-01-29 为界，是 1,437。

按路口计：3,874 个路口里有完工日期的 1,150 个，其中 2020-02 及以后的 818 个。

完工日期按年分布（坡道数）：2014–2016 共 20；2017 71；2018 214；2019 219；2020 448；2021 121；2022 102；2023 69；2024 413；2025 91；2026 243。

需要注意的地方：
- 有完工日期的 2,011 个坡道中，状态是 Constructed 1,834、Complex Constructed 116，但有 **61 个**状态却是 Complex Planned Construction（35）、Planned Construction（25）、Not Assigned（1），即有日期的并不都是"已建成"
- Ramp Locations 是 2017–2020 年采集的，2020-02 以后完工的坡道，其测量数据反映的是**完工前**的状态
- 从 Progress 一侧数，研究区有 4,766 个路口（其中 3,874 个在 Ramp Locations 里，另 892 个没有普查记录），其中有完工日期 1,250 个，2020-02 及以后 907 个

## 11. MBPO 报告：能判断合规的行数、合格数、落在研究区的数

"能判断合规" = `Compliant` 为 true 或 false。"合格" = `Compliant = true`。

| 指标 | 行数 |
|---|---|
| MBPO 总行数 | 277 |
| **能判断合规** | **248** |
| 其中 **合格（true）** | **14**（占可判断的 5.6%） |
| 其中不合格（false） | 234 |
| 不能判断（Compliant 为空） | 29 |

29 个不能判断的行全部是 Center Cut = YES 且没有 Ramp ID 的行，Compliant 一栏留空。

**落在研究区的行数：**

| 口径 | 研究区行数 | 可判断 | 合格 |
|---|---|---|---|
| **按 Ramp ID 连到坡道坐标** | **48** | 48 | **3** |
| 按车站名（125 St、135 St、168 St、175 St、207 St、Dyckman St） | 53 | 50 | 3 |

- 277 行里有 Ramp ID 的 199 行，其中 198 行能连到 Ramp Locations 坐标（1 行 ID 找不到）。其余 78 行没有 Ramp ID，没法按坐标定位
- 两个口径差 5 行：135 St 3 行和 168 St 1 行没有 Ramp ID（按车站名算入），168 St 另有 1 行的 Ramp ID 连到了坐标在 40.55°N 的坡道（位于 Staten Island），**看起来是 ID 填错**，按坐标口径被排除在外，按车站名口径算入
- 研究区内的 3 个合格行：207 St 站 2 个，Dyckman St 站 1 个
- 其他 22 个站（含 66 St-Lincoln Center、72 St Broadway、Chambers St、Roosevelt Island 4 个整站都没有 Ramp ID）按车站名都在 110 St 以南，不在研究区

## 12. MTA 车站表的 ADA 车站数（按区），与 MTA 官网对照

**车站表（`39hk-dx4f`，2026-11-11 更新）**，每行是一个车站在某条线上的记录，共 496 行：

| 区 | ADA=1（完全无障碍） | ADA=2（仅单向） | 合计 ADA 行 | ADA=0 |
|---|---|---|---|---|
| 曼哈顿 (M) | 65 | 5 | 70 | 83 |
| 布鲁克林 (Bk) | 44 | 2 | 46 | 123 |
| 皇后区 (Q) | 28 | 1 | 29 | 54 |
| 布朗克斯 (Bx) | 23 | 0 | 23 | 47 |
| 史坦顿岛 (SI) | 6 | 0 | 6 | 15 |
| **合计** | **166** | **8** | **174** | **322** |

**MTA 官网（mta.info/accessibility/stations，页面标注 Updated Oct 12, 2026）**，"Quick Reference Station List"，我解析了页面 HTML：

| 区 | 官网条目 | 其中仅单向 | 按名称去重 | 车站表按 Complex ID 去重 |
|---|---|---|---|---|
| 曼哈顿 | 58 | 5 | 50 | 50 |
| 布鲁克林 | 39 | 2 | 36 | 38 |
| 皇后区 | 26 | 1 | 26 | 25 |
| 布朗克斯 | 21 | 0 | 21 | 21 |
| 史坦顿岛铁路 | 6 | 0 | 6 | 6 |
| **合计** | **150** | **8** | **139** | **140** |

**结论：**
1. **原始数字对不上，但原因是统计单位不同。** 官网是 150 个"站名 + 线路"条目，车站表是 174 个车站-线路行。官网把同一站的多条线合成一条（如 Times Sq-42 St 一条对车站表 4 行）
2. **逐条核对没发现无障碍状态的矛盾：** 官网每个条目都能在车站表找到 ADA 行，车站表的 174 个 ADA 行都能对应到官网条目。Times Sq-42 St、West 4 St-Washington Sq、Park Place 三个条目因站名缩写不同需要手工对应（车站表写作 Times Sq / W 4 St-Wash Sq / Park Pl）
3. **单向无障碍完全一致：** 官网 8 个"仅上城/下城/某方向"条目（曼哈顿 28 St、49 St、50 St、86 St、Spring St；布鲁克林 Hoyt St、Wilson Av；皇后区 Court Sq-23 St）与车站表的 8 个 ADA=2 对上，方向也一致
4. **按线路区分的情况也一致：** 官网说 Union Sq 只有 L/N/Q/R/W 无障碍、4/5/6 不是；Canal St 只有 6 号线；168 St 只有 A/C。车站表对应行分别是 1/1/0、1/0、1/0
5. **反向检查：** 官网说无障碍的条目，在车站表里没有一个对应线路被标成 ADA=0。唯一的提示是 Pelham Pkwy，实为两个不同的站（官网指 White Plains Rd 线 2/5，Dyre Av 线的 5 号线 Pelham Pkwy 本来就不无障碍），不算差异
6. **去重口径下仍有小差异：** 布鲁克林车站表 38 vs 官网 36，皇后区 25 vs 26。我没有逐条查清，可能是综合体合并方式不同。每个条目都有对应行，所以不是漏站
7. 官网 Rockaway Park-Beach 116 St 的"rush hours only"说明指 S 线只在高峰运行，不是无障碍状态，车站表该站为 ADA=1，不构成差异

**局限：** 官网列表是我从网页 HTML 解析的，不是官方数据下载；官网页面日期（2026-10-12）比车站表（2026-11-11）早一个月。官网只覆盖地铁和史坦顿岛铁路。

## 13. 本轮产生的文件

- [study_area_elevators.csv](../data/clean/study_area_elevators.csv)：研究区内 48 个电梯的明细

---

*（原章：第三轮：研究区 ADA 车站信息表）*

## 14. 本轮产出

| 文件 | 内容 |
|---|---|
| [station_table.csv](../data/clean/station_table.csv) | **主表**，每个研究区 ADA 车站一行，共 10 行、30 列 |
| [elevator_detail.csv](../data/clean/elevator_detail.csv) | 逐电梯明细（研究区 48 个电梯 + 所关联的电梯），含 12 个月 24 小时/早高峰/晚高峰可用率、停运次数、是否进入概率模型及原因 |
| [elevators_assigned_by_coordinates.csv](../data/clean/elevators_assigned_by_coordinates.csv) | 缺车站信息的 6 个电梯按坐标归站的结果，**供你检查** |
| [hospitals_map.png](../outputs/hospitals_map.png) | 三家医院坐标与 400 m 圈、110 St 边界线、研究区、10 个 ADA 车站 |

目录里另外还有 `fetch_live_outages.py`、`live_fetch.out`、`live_log.csv`，不是我创建的，我没有碰。

## 15. 哪些车站入表

研究区内共 35 个车站行，ADA 车站（ADA=1 或 2）**10 个**，全部是 ADA=1，且 `ADA Northbound` 和 `ADA Southbound` 都是 1，没有仅单向的。两家医院的 400 m 圈内各含一个车站（168 St A/C 在 NYP/Columbia 圈内，135 St 2/3 在 Harlem Hospital 圈内），但这两站本来就在 110 St 以北，医院缓冲没有新增车站。Mount Sinai Morningside 圈内没有 ADA 车站。

入表车站：Inwood-207 St (A)、Dyckman St (1)、181 St (A)、175 St (A)、168 St (A C)、Harlem-148 St (3)、137 St-City College (1)、135 St (2 3)、125 St (A C B D)、125 St (4 5 6)。

## 16. 电梯怎么对应到车站

- **对应键：** 资产清单的 `Station MRN`（去掉前导零）= 车站表的 `Station ID`。第 4 节已验证这两个编号一致。
- 对应到这 10 站的电梯共 **27** 部，**其中 23 部进入概率模型**。
- 距离核对：进入模型的电梯到所属车站坐标最远 212 m（181 St 的 EL517/EL518），中位 73 m。唯一超过 400 m 的是 137 St 的 EL166X/167X/169X（446 m），这三部不进模型（见第 19 节）。
- 清单里的车站名和车站表对得上（如 `125ST-8AV-A/B/C/D` ↔ 125 St A C B D）。

### 缺车站信息的 6 个电梯（请你检查）

按坐标找最近车站（用车站表的 GTFS 坐标，直线距离）。明细在 `elevators_assigned_by_coordinates.csv`。

| 电梯 | 清单备注 | 最近车站（距离） | 次近 | 最近的 ADA 车站（距离） |
|---|---|---|---|---|
| EL147 | Relay Building A | 207 St 1 号线（202 m） | Inwood-207 St A（473 m） | Inwood-207 St（473 m） |
| EL150 | Passenger Elevator At 207Th Street Yard | 215 St 1 号线（213 m） | Inwood-207 St A（320 m） | Inwood-207 St（320 m） |
| EL151 | Freight Elevator At 207Th Street Yard | 215 St 1 号线（233 m） | Inwood-207 St A（576 m） | Inwood-207 St（576 m） |
| EL152 | Freight Elevator At 207Th Street Yard | 215 St 1 号线（144 m） | Inwood-207 St A（388 m） | Inwood-207 St（388 m） |
| EL153 | Freight Elevator At 207Th Street Yard | 215 St 1 号线（156 m） | Inwood-207 St A（356 m） | Inwood-207 St（356 m） |
| EL155 | Freight Elevator At 207Th Street Yard | 215 St 1 号线（265 m） | Inwood-207 St A（378 m） | Inwood-207 St（378 m） |

**需要你注意的三点：**
1. 6 个电梯按最近车站归类，会落到 215 St（5 个）和 207 St（1 个）这两个 **1 号线非 ADA 车站**，不在 ADA 车站表里，所以没有出现在 station_table.csv 的任何一行。
2. 距离都在 144–576 m，而同表中站内电梯到车站的中位距离是 73 m。从备注看，它们是 **207 St 车辆段的货梯/客梯和一栋继电器楼**，不是站内通道。我认为即使强行归到最近的 ADA 站（Inwood-207 St），也不该纳入该站的无障碍通道概率。
3. 另外这 6 个在可用率表里也没有记录。因此我没有把它们放进任何站的概率计算，只在 Inwood-207 St 那一行的 `review_note` 里提示了。如果你要把它们算进去，请告诉我归哪个站、当串联还是并联。

## 17. 可用率口径

| 项目 | 做法 |
|---|---|
| 时间窗口 | 最近 12 个月：2025-10 至 2026-09（数据最新月为 2026-09） |
| 平均可用率 | 按小时加权：窗口内 `24-Hour Hours Available` 之和 ÷ `24-Hour Total Hours` 之和。`Total Hours = 0` 的月份（共 215 行）不参与 |
| 计划外停运次数 | 窗口内 `Unscheduled Outages` 之和 |
| 另存字段 | 早高峰、晚高峰可用率和总停运次数在 elevator_detail.csv 里，没有进入概率计算 |
| 数据完整度 | 窗口内有数据的 419 个电梯里 397 个满 12 个月。进入模型的电梯中，EL519（137 St）只有 5 个月，EL144（125 St A/C/B/D）只有 9 个月，已在 `review_note` 里标出，它们的停运次数也只覆盖这些月份 |

## 18. 没有可用率记录的电梯：不补 100%

- 没有任何可用率记录的电梯，`elevator_avail_status` 标为 **未知**，可用率和停运次数列也写 `未知`，不是 1 也不是 0。
- 整站概率给两个版本，**只对没有记录的电梯补值**，有记录的电梯一律用自己的实测值：
  - `station_prob_mean_fill`：用研究区平均值 **0.9787** 补（研究区 37 个有记录电梯的 12 个月可用率的简单平均）
  - `station_prob_low_fill`：用偏低值 **0.9636** 补（同一批 37 个电梯的第 10 百分位）
- 参考分布：37 个有记录电梯的最小值 0.9490，中位数 0.9807。如果你想用更悲观的值（如最小值），告诉我就行。
- **补值只影响一个站：** 进入模型的 23 个电梯里，只有 EL520（137 St 南向）没有记录。所以两列只在 137 St 不同（0.9502 vs 0.9356），其余站两列相同。
- 这两个补值是情景假设，不是估计。没有记录的电梯可能和有记录的系统性不同（比如私人承包商维护、非 NYCT 所有），补值没法反映这一点。

## 19. 串联并联怎么算

**结构来源：** 资产清单每个电梯有这些字段：是否通街面（`Street Access`）、是否到夹层 1/夹层 2（`Elevator Mezzanine 1/2 Access`）、是否到站台（`Elevator Platform Access`）、服务方向（`Elevator Direction Serviced`：Both/Northbound/Southbound）。我把每个电梯当作连接它所停靠楼层的"边"，建成"街面 → 夹层 → 北向/南向站台"的连通图。

**整站可用概率** = 街面入口到**所有 ADA 方向**站台都能走通的概率。因为这 10 站都是双向 ADA，所以北向和南向站台都要通。电梯相互独立，对电梯的开/关状态做精确枚举（每站最多 5 个电梯），这样串联（必经）、并联（任一即可）、以及共享的电梯（如 168 St 的 EL139 同时在南北两条路径上）都能正确处理，不会重复计算。

**每站的结构和结果**（路径列在 station_table.csv 的 `access_paths`，`+` 表示串联，`|` 表示并联）：

| 车站 | 路径结构 | 概率（均值补 / 偏低补） | 备注 |
|---|---|---|---|
| Inwood-207 St (A) | EL148 → EL149 串联 | 0.9748 / 0.9748 | |
| Dyckman St (1) | 南向 EL178；北向 EL178 + EL179 串联 | 0.9695 / 0.9695 | EL156 未纳入（见下） |
| 181 St (A) | EL117、118、119 三选一 → 北向 EL517 / 南向 EL518 | 0.9847 / 0.9847 | 入口为推断（见下） |
| 175 St (A) | EL123 → EL124 串联 | 0.9868 / 0.9868 | |
| 168 St (A C) | EL139 → 北向 EL140 / 南向 EL141 | 0.9470 / 0.9470 | 三部全串联（共享 EL139），本批最低 |
| Harlem-148 St (3) | — | **空（无法计算）** | 清单里没有电梯 |
| 137 St-City College (1) | 北向 EL519，南向 EL520，两个都要通 | 0.9502 / 0.9356 | EL520 无记录，EL519 只有 5 个月数据 |
| 135 St (2 3) | 北向 EL180，南向 EL181，两个都要通 | 0.9580 / 0.9580 | |
| 125 St (A C B D) | EL142 → 北向 EL144 / 南向 EL143 | 0.9662 / 0.9662 | EL144 只有 9 个月数据 |
| 125 St (4 5 6) | EL125 → EL126 串联 | 0.9526 / 0.9526 | |

**这些结果的局限：**
1. **独立性假设：** 假设各电梯故障互不相关。同一站的电梯可能受同一事件影响（停电、施工、同一承包商），实际整站概率可能偏高估。
2. **口径是 24 小时：** 可用率是全天平均，含计划内停运，不等于通勤时段的可用性。
3. **只算电梯：** 没有考虑闸机、坡道、站台间隙等其他无障碍环节，也没有考虑替代路线（清单里的 `Alternative Route` 是文字说明，没有量化）。
4. **可用率 ≠ 使用者的体验：** 概率是"某一随机时刻整站步行可达"的概率，不是"一次出行成功的概率"。

## 20. 需要你复核的地方

表里 `needs_review = 是` 的有 6 站，原因如下：

| 车站 | 问题 | 我的处理 |
|---|---|---|
| **Harlem-148 St** | 资产清单中没有任何电梯对应该站，周边 500 m 内也没有清单电梯。是数据缺口，不是"没电梯" | 概率留空，不补值 |
| **181 St (A)** | 清单里没有任何电梯通街面。备注显示 EL117–119 是"上层夹层到下层夹层"，上层夹层在 184 St & Ft Washington Av 地面入口 | 把入口设为夹层 2（M2，对应上层夹层），是推断，不是清单直接给的 |
| **Dyckman St (1)** | EL156 关联到该站，但备注是"Freight Elevator At Dyckman Street/ Sub. Station"（变电站货梯），没有层级字段 | 未纳入概率 |
| **137 St-City College** | EL166X、EL167X、EL169X 关联到该站，状态是 Out of Service，私人承包商维护，无层级字段，坐标离车站 446 m | 未纳入概率；EL520 无可用率记录，用补值 |
| **Inwood-207 St (A)** | 车辆段 6 个电梯离它最近（见第 16 节） | 未纳入概率 |
| **125 St (A C B D)** | EL144 窗口内只有 9 个月数据 | 照常计算，仅提示 |

## 21. 地图

[hospitals_map.png](../outputs/hospitals_map.png)：橙色为 110 St 以北的曼哈顿陆地（含 Randalls Island 和 Marble Hill，因为行政上属曼哈顿），虚线为拟合出的 110 St 线，红色十字为三家医院，圆为 400 m 范围，绿色三角为 10 个 ADA 车站。底图边界来自 NYC Open Data 的 Borough Boundaries（下载在 `raw/borough_boundaries/`）。三家医院的圆在地图上都完整可见，其中 Mount Sinai Morningside 的圆跨过 110 St 线。

**地图上看到的一点：** 研究区里 Randalls Island 也被算进了"110 St 以北的曼哈顿"，这个岛上目前没有 ADA 车站，对本轮的表没有影响。

---

*（原章：第四轮：148 St 电梯搜索、医院周边 ADA 车站、NYP/Columbia 30 分钟等时圈）*

## 22. 148 St（Harlem-148 St）的电梯：所有数据里都找不到

车站表里该站是 `Station ID = 436`、GTFS 站点 `301`、线路 3 号线、ADA=1。我用这几个键加上"148 / Harlem"文字在每份数据里搜了一遍。

| 数据 | 搜索范围 | 结果 |
|---|---|---|
| 资产清单（759 行） | 车站名、Station MRN、Complex MRN 等 44 列全文 | **没有电梯**。Station MRN 或 Complex MRN 等于 436 的行数为 0，车站名里也没有 148 St / Harlem |
| 可用率表（83,776 行） | 车站名、综合体名、设备编号、Station MRN、Complex MRN | **没有**。0 行。该线其余站（135 St、3 Av-149 St 等 9 个 LWP 站）都有 |
| 实时 Equipment 清单（707 个设备：430 电梯 + 277 扶梯） | 车站名、GTFS 站点 ID（301）、MRN（436）、Complex ID（436）、服务说明、相邻 ADA 站 | **没有**。`elevatorsgtfsstopid=301`、`elevatormrn=436`、`stationcomplexid=436` 都是 0 行 |
| 实时当前停运清单（182 条） | 车站名、设备、服务说明 | **没有** |
| 站点设施数据集（71,290 行，2026-05 至 2026-10） | 车站 MRN 436 | 该站有闸机、倒计时牌、求助点、OMNY 售卖机和 **ADA 无障碍闸机的进站和出站各 1 个**，但 `ELEVATOR` 类设施数是 **0**（同期 135 St 2/3 有 2 个，Dyckman St 有 3 个） |
| 站点入口数据集（2,120 行） | Station ID 436 | 只有 **1 个入口，类型是 Station House**，没有 Elevator 类型的入口（135 St 2/3 的入口里有 2 个 Elevator） |
| 以坐标搜（第三轮已做） | 清单电梯到该站 500 m 内 | 0 个 |

**文字里提到 148 St 的地方（不是 148 St 的电梯）：** 清单和实时清单里，135 St 的 EL180/EL181 的"替代路线"文字写着：电梯故障时可乘 3 号线上行到 Harlem-148 St，再换乘下行 3 号线回 135 St。这说明 MTA 把 148 St 当作无障碍乘客可以使用的站，但没有给它登记任何电梯。另外 135 St 电梯在实时清单里的"北侧下一个 ADA 站"只列了 2 号线的 `434, 2`（3 Av-149 St），没有列 3 号线的 148 St。

**能得出的结论：** 找不到 148 St 的电梯，各来源口径一致。结合"有 ADA 无障碍闸机、只有一个车站大厅入口、没有 Elevator 类设施"，数据**与**"该站无需电梯就能无台阶进入"一致，但我无法仅凭数据证明这一点，也没有核实现场。如果该站其实是靠电梯到站台，那这些数据集全部漏登了。

新下载的文件：`raw/live_equipment/`（`equipments.json`、`outages.json`，取自 MTA 公开接口 `api-endpoint.mta.info/Dataservice/mtagtfsfeeds/`，2026-11-11 下载）、`raw/mta_entrances/`（`i9wp-a4ja`）、`raw/mta_amenities/`（`6yjv-fk7g`）。你的实时轮询程序现在放在 `<LIVE_DIR>/`，我只读了它的目录列表和脚本开头，用来确认接口地址，没有改动，也没有用里面的数据，实时清单是我自己重新下载的。

## 23. 三家医院 400 m 内的 ADA 车站，以及最近的 ADA 车站

ADA 车站 = 车站表 ADA 为 1 或 2，全市共 174 个（不限研究区）。距离是医院点到车站 GTFS 坐标的直线距离。括号里是到该站最近入口的直线距离（入口数据集）。明细在 [hospital_ada_stations.csv](../outputs/hospital_ada_stations.csv)。

| 医院 | 400 m 内的 ADA 车站 | 最近的 ADA 车站及直线距离 |
|---|---|---|
| Harlem Hospital | **1 个**：135 St（2 3），136 m（入口 118 m） | 135 St（2 3），136 m。第二近 Harlem-148 St（3），1,047 m |
| NYP/Columbia Irving Medical Center | **1 个**：168 St（A C），100 m（入口 110 m） | 168 St（A C），100 m。第二近 175 St（A），718 m |
| Mount Sinai Morningside | **0 个** | 125 St（A C B D），**1,003 m**（入口 935 m）。第二近 96 St（1 2 3），1,559 m |

补充：
- NYP/Columbia 400 m 内另有一个非 ADA 车站 168 St-Washington Hts（1 号线，通过 A/C 站的非 ADA 电梯连接，见第 16 节的备注）
- Mount Sinai Morningside 400 m 内唯一的地铁站是 116 St-Columbia University（1 号线），**不是 ADA 站**
- 单点假设：每家医院只取一个点，实际院区更大，所以"400 m 内"的结果对医院用地边界敏感。尤其 Columbia 院区较大，如果以院区边缘算，可能有更多站落入

---

*（原章：第六轮：设备清单的 ADA 核对与车站状态时间序列）*

## 24. 设备清单（`nyct_ene_equipments.json`）里的 ADA 字段

研究区 48 个电梯里 38 个能在设备清单里找到（其余 10 个不在清单里，见第 23 节）。这 38 个的 `ADA` 字段：**Y 23 个，N 15 个**。

**ADA = N 的 15 个电梯**（清单 ADA = N，资产清单 `ADA Compliant` 也是 NO，两边一致）：

| 车站（清单里的站名，线） | 电梯 |
|---|---|
| 181 St（1 号线） | EL107、EL108、EL109、EL110（"mezzanine to bridge"） |
| 168 St-Washington Hts（1 号线） | EL111、EL112、EL113、EL114（"transfer mezzanine to overpass for 1 train"） |
| 190 St（A 线） | EL115、EL116、EL120 |
| 191 St（1 号线） | EL103、EL104、EL105、EL106 |

**是否被算进 `station_table` 的概率：全部没有。** `elevator_detail.csv` 里这 15 个的 `in_probability_model` 都是 False，原因是"车站不在 ADA 车站表中"：它们所在的车站（1 号线的 181 St、168 St、191 St，以及 190 St）本身不是 ADA 车站，不在 station_table 的 10 个车站里。

**反方向：** station_table 的 `access_paths` 里共 23 个电梯，**全部在设备清单里能找到，且 ADA 全是 Y**，没有 ADA = N 的电梯混进概率。这 23 个正是上面 38 个里 ADA=Y 的 23 个。

注意同名但不同站：station_table 里的 **181 St（A 线）** 与上表的 **181 St（1 号线）** 是两个不同的车站，别混了。

## 25. 181 St（A）入口推断与清单对照：一致，但仍是推断

之前的推断：EL117–119 连"上层夹层"和"下层夹层"，街面入口接上层夹层；EL517/518 连夹层到站台。对照结果：

| 证据 | 内容 | 是否一致 |
|---|---|---|
| 设备清单 `serving` | EL117/118/119：Upper mezzanine (**184 St & Ft Washington Av**) to lower mezzanine，双向；EL517：Mezzanine to platform for Inwood-207 St-bound；EL518：Mezzanine to platform for Downtown and Brooklyn-bound | 一致：上层夹层的位置就写成街道路口，EL117–119 在上层与下层之间，EL517/518 才到站台 |
| 设备清单 `redundant` | EL117/118/119 = 1，EL517/518 = 0 | 一致：三个并联可互相替代，两个站台电梯各自唯一 |
| 设备清单 `alternativeroute` | EL117–119："Use an adjacent elevator."；EL517/518 的替代路线写"在站台时坐车去相邻站换乘" | 一致 |
| 资产清单字段 | EL117–119：Street Access = NO，Mezzanine 1 = +，Mezzanine 2 = +，Platform = -；EL517/518：Street = NO，Mezz 1 = +，Platform = + | 一致：EL117–119 连两层夹层，EL517/518 连下层夹层与站台，没有一个电梯标"街面" |
| 坐标（资产清单 X/Y 对调后） | EL117–119 在约 40.8528°N，距车站点 136–153 m 偏北；EL517/518 在 40.8498°N，距车站点 212 m 偏南 | 一致：184 St 在 181 St 以北，上层夹层电梯在北，站台电梯在南 |

**未被清单直接证实的部分：** 设备清单和资产清单都没有任何电梯标为"街面入口"，"街面进入上层夹层"这一步仍是根据 `serving` 里的 "184 St & Ft Washington Av" 推出来的，不是字段直接给的。`nextadanorth` / `nextadasouth` 在这些电梯上是空的，帮不上忙。结论：**没有发现与推断矛盾的地方，但这一点只算"与清单一致"，不算"被清单确认"。**

---

*（原章：第七轮：Harlem-148 St 标记与"预计恢复时间已过"）*

## 26. Harlem-148 St 标成"无电梯依赖"

- `station_table.csv` 新增一列 `elevator_dependency`：Harlem-148 St 为"无电梯依赖（未现场核实）"，其余 9 站为"有"。
- Harlem-148 St 的 `station_prob_mean_fill` 和 `station_prob_low_fill` 都改成 **1**（原来是空）。`fill_mean_used`、`fill_low_used` 保持原值，它们是研究区通用的补值参考，对这一站没有实际作用。
- `review_note` 已写明依据：MTA 站点设施数据集里该站有 ADA 无障碍闸机（进站、出站各 1 个）但 `ELEVATOR` 类设施数是 0，站点入口数据集里只有 1 个 Station House 入口，资产清单、可用率表、实时设备清单里都没有该站电梯（详见上面"148 St 的电梯：所有数据里都找不到"一节）。**这只是数据推断，没有现场核实**；如果该站实际靠电梯到站台，这一站的 1 就偏乐观。`needs_review` 仍保持"是"。
- `station_status_timeseries.csv` 里 Harlem-148 St 的 `available` 现在是 **1**（原来留空），`elevator_dependency` 列同样标注，不受电梯停运影响。
- 原文件已备份：`station_table.pre_harlem.csv`、`station_status_timeseries.pre_v2.csv`。时间序列因为加了列，已用全部 6 份快照重新生成，除 Harlem-148 St 和新增列之外，其余内容与旧版相同。

---

*（原章：第十一轮：14 个建不了模型的站、修复后的 Monte Carlo、最终汇总）*

写之前我再确认过 checks.md 自上一章追加后没有被改动（1503 行）。只追加，节号延续上一章，从 **57** 起。

| 文件 | 内容 |
|---|---|
| [final_summary.csv](../outputs/final_summary.csv) | 最终汇总表，每家医院一行，列名里带单位、方向和时间口径 |
| [final_summary.md](final_summary.md) | 一页说明 |
| [station_model_fixes.csv](../data/clean/station_model_fixes.csv) | 16 个站的调查和处理记录（14 个原来建不了的 + 2 个被纠正的）：原来的状态和原因、处理、修复前后的通路 |
| [mc_manhattan_summary_fixed.csv](../outputs/mc_manhattan_summary_fixed.csv)、[mc_manhattan_single_failure_fixed.csv](../outputs/mc_manhattan_single_failure_fixed.csv) | 修复后的 Monte Carlo 汇总和单点故障（旧结果 `mc_manhattan_*.csv` 保留，不覆盖） |

## 27. 那 14 个站为什么建不了电梯模型，哪些能补上

**原因分两类：** 6 个站在资产清单里**该站名下没有电梯**；8 个站有电梯，但字段不全（没有服务方向或夹层到站台的连接），建不出"街面—夹层—站台"的通路。

**我用什么补：** MTA 实时设备清单（`nyct_ene_equipments.json`，2026-11-11 下载，在"148 St 电梯搜索"一章里下载，在 `raw/live_equipment/`）。它给每部电梯写了服务说明（`serving`、`shortdescription`）、服务的线路（`linesservedbyelevator`）和所属站点（`elevatorsgtfsstopid`，同一部电梯可属于多个站点）。**判定标准：** 说明足以确定电梯连接哪些层（街面/夹层/哪个方向的站台），且电梯所属站点 ID 与目标站一致，就补；说明缺失或含糊，就不补。方向对应：上行/uptown = 北向站台（PN），下行/downtown = 南向站台（PS）。这一对应在 1/2/3、2/5、4、B/D、N/Q/R/W 这些干线上符合 GTFS 惯例，我没有逐线核实。

| 站（线路） | 区 | 原来为什么建不了 | 在数据里发现了什么 | 处理 | 采用的通路（电梯编号；+ 串联，\| 并联） |
|---|---|---|---|---|---|
| 72 St（1/2/3） | 曼哈顿 | 电梯有街面标记但没有服务方向 | 实时清单：EL239 "Street to Northbound platform"，EL240 "Street to Southbound platform" | **已补** | 北向 EL239；南向 EL240 |
| 96 St（1/2/3） | 曼哈顿 | 同上 | EL146 "Street to uptown platform"，EL145 "Street to downtown platform" | **已补** | 北向 EL146；南向 EL145 |
| 49 St（N/R/W） | 曼哈顿 | 1 部电梯无方向 | EL268X "Street to uptown platform"；该站 ADA = 2，仅上城方向 | **已补** | 仅北向 EL268X |
| 149 St-Hostos（2/5） | 布朗克斯 | 清单里该站名下没有电梯 | 电梯登记在同综合体的 4 号线站（Station MRN 390）名下；实时清单显示 EL100–EL102 同时服务站点 222 和 415、线路 2/4/5 | **已补** | 北向 EL100+EL101；南向 EL100+EL102 |
| 161 St-Yankee Stadium（4） | 布朗克斯 | 清单里该站名下没有电梯 | 电梯登记在 B/D 站（MRN 219）名下；EL131 街面到夹层，EL132 夹层到北向 4 站台，EL133 夹层到南向 4 站台 | **已补** | 北向 EL131+EL132；南向 EL131+EL133 |
| Times Sq-42 St（1/2/3） | 曼哈顿 | 电梯字段缺方向 | 综合体内：EL231X（42 St & 7 Av）、EL619（43 St & Broadway）都是"街面到夹层，服务所有线路双向"；EL233 夹层到上行 1/2/3，EL232 夹层到下行 1/2/3 和 7 | **已补** | 北向（EL231X \| EL619）+EL233；南向（EL231X \| EL619）+EL232 |
| Times Sq-42 St（7） | 曼哈顿 | 清单里该站名下只有扶梯 | EL232 到 7 号线站台 | **已补**（假设 7 号线站台两个方向共用 EL232） | 两个方向都是（EL231X \| EL619）+EL232 |
| Times Sq-42 St（N/Q/R/W） | 曼哈顿 | 夹层到站台的路径缺失 | EL230 夹层到上行 N/Q/R/W，EL229 夹层到下行 N/Q/R/W | **已补** | 北向（EL231X \| EL619）+EL230；南向（EL231X \| EL619）+EL229 |
| 59 St-Columbus Circle（1） | 曼哈顿 | 清单里该站名下没有电梯 | 电梯登记在 A/C/B/D 站（MRN 161）名下。EL280 街面到上行 1 站台，EL276X 街面到夹层，EL278 夹层到上行 A/B/C/D，EL279 上行 1 站台与上行 A/B/C/D 站台相连，EL277 和 EL622 夹层到下行站台 | **已补**（其中 1 条备选路径是推断） | 北向 EL280 \| EL276X+EL278+EL279（后者为推断）；南向 EL276X+EL277 \| EL276X+EL622 |
| **纠正：161 St（B/D）** | 布朗克斯 | 原来已建模，但混入了 EL132、EL133 | 这两部的服务线路是 **4 号线**，被我当成了 B/D 站台电梯的并联备份 | **已纠正** | 北向 EL131+EL135；南向 EL131+EL134（原来多了 EL132、EL133 作备选） |
| **纠正：59 St-Columbus Circle（A/C/B/D）** | 曼哈顿 | 原来已建模，但街面入口 EL276X 因字段缺失没有进模型 | 站台电梯 EL278、EL279、EL280 被当成互相独立的备份，偏乐观 | **已纠正** | 北向 EL276X+EL278 \| EL279+EL280（后者为推断）；南向 EL276X+EL277 \| EL276X+EL622 |
| Times Sq-42 St（S） | 曼哈顿 | 清单里该站名下没有电梯 | 实时清单只有综合体共用的入口电梯（线路列表里含 S），没有任何电梯到 S 站台 | **补不了** | S 站台的电梯连接在数据里没有说（也可能无需电梯，但数据不说） |
| 42 St-Port Authority（A/C/E） | 曼哈顿 | 清单里的电梯没有可用的站台字段 | EL291X 街面到中间平台，EL290X 平台到夹层，EL288X/EL289X 汽车总站到夹层，都是"A/C/E 双向" | **补不了** | 没有描述夹层到 A/C/E 站台的电梯，街面到站台的链条不完整 |
| 51 St（6） | 曼哈顿 | 夹层到站台的路径缺失 | 描述的是上行和下行 6 站台之间的地下通道（EL201、EL202）和街面到夹层（EL203X） | **补不了** | 夹层如何到各 6 站台没有说清，通道描述含糊 |
| W 4 St-Wash Sq（A/C/E） | 曼哈顿 | 街面入口到站台字段缺失 | EL334/EL335 连接 A/C/E 站台与换乘夹层和 B/D/F/M；EL333 "街面到上层站台层" | **补不了** | 街面电梯到哪一层的 A/C/E 站台含糊 |
| Harlem-148 St（3） | 曼哈顿 | 清单里没有电梯 | 在资产清单、可用率表、实时设备清单、站点设施数据集、入口数据集里都没有电梯（148 St 搜索一章） | **补不了，也没有可补的** | 沿用此前标记："无电梯依赖"（**未现场核实**） |

**结果：9 个补上，2 个旧模型被纠正，5 个补不了。** 能建电梯模型的站从 45 个增加到 **54 个**，电梯从 128 部增加到 **132 部**。没有可用率记录的电梯仍是 **EL132、EL133、EL520**（沿用均值补 0.9787 和偏低补 0.9636 两种处理）。补完后，新用到的每部电梯都核对过：按实时清单的站点 ID，确实属于对应的站。

**到达的 ADA 站里能被扰动的比例**（情景④，30 分钟内到达的 ADA 站记录）：

| 医院 / 方向 | 到达的 ADA 站 | 被扰动 | 比例（之前） | 其中曼哈顿的站 | 被扰动 | 比例（之前） |
|---|---|---|---|---|---|---|
| Harlem 反向 | 40 | 36 | **90%**（70%） | 26 | 22 | 85%（62%） |
| Harlem 正向 | 40 | 37 | **92%**（70%） | 32 | 29 | 91%（69%） |
| NYP/Columbia 反向 | 39 | 35 | **90%**（72%） | 32 | 28 | 88%（72%） |
| NYP/Columbia 正向 | 22 | 20 | **91%**（73%） | 17 | 15 | 88%（71%） |
| Mount Sinai 反向 | 15 | 14 | **93%**（67%） | 13 | 12 | 92%（69%） |
| Mount Sinai 正向 | 10 | 10 | **100%**（70%） | 9 | 9 | 100%（67%） |

---

## 附：新旧节号对照

| 新节号 | 原章 | 原节号 | 标题 |
|---|---|---|---|
| 1 | 数据体检 checks.md | 1 | 数据集概览 |
| 2 | 数据体检 checks.md | 2 | 列名 |
| 3 | 数据体检 checks.md | 3 | 电梯编号（Equipment Code）匹配率 |
| 4 | 数据体检 checks.md | 4 | 车站 / 综合体键匹配率 |
| 5 | 数据体检 checks.md | 5 | 坡道表键匹配率 |
| 6 | 数据体检 checks.md | 6 | 其他需要留意的问题 |
| 7 | 数据体检 checks.md | 7 | 未做的事 |
| 8 | 第二轮检查：研究区内的缺口与合规情况 | 8 | 研究区定义（后面所有计数共用） |
| 9 | 第二轮检查：研究区内的缺口与合规情况 | 9 | 研究区电梯里，多少个在可用率表里没有记录 |
| 10 | 第二轮检查：研究区内的缺口与合规情况 | 10 | 研究区坡道里，多少个在 Program Progress 有完工日期 |
| 11 | 第二轮检查：研究区内的缺口与合规情况 | 11 | MBPO 报告：能判断合规的行数、合格数、落在研究区的数 |
| 12 | 第二轮检查：研究区内的缺口与合规情况 | 12 | MTA 车站表的 ADA 车站数（按区），与 MTA 官网对照 |
| 13 | 第二轮检查：研究区内的缺口与合规情况 | 13 | 本轮产生的文件 |
| 14 | 第三轮：研究区 ADA 车站信息表 | 14 | 本轮产出 |
| 15 | 第三轮：研究区 ADA 车站信息表 | 15 | 哪些车站入表 |
| 16 | 第三轮：研究区 ADA 车站信息表 | 16 | 电梯怎么对应到车站 |
| 17 | 第三轮：研究区 ADA 车站信息表 | 17 | 可用率口径 |
| 18 | 第三轮：研究区 ADA 车站信息表 | 18 | 没有可用率记录的电梯：不补 100% |
| 19 | 第三轮：研究区 ADA 车站信息表 | 19 | 串联并联怎么算 |
| 20 | 第三轮：研究区 ADA 车站信息表 | 20 | 需要你复核的地方 |
| 21 | 第三轮：研究区 ADA 车站信息表 | 21 | 地图 |
| 22 | 第四轮：148 St 电梯搜索、医院周边 ADA 车站、NYP/Columbia 30 分钟等时圈 | 22 | 148 St（Harlem-148 St）的电梯：所有数据里都找不到 |
| 23 | 第四轮：148 St 电梯搜索、医院周边 ADA 车站、NYP/Columbia 30 分钟等时圈 | 23 | 三家医院 400 m 内的 ADA 车站，以及最近的 ADA 车站 |
| 24 | 第六轮：设备清单的 ADA 核对与车站状态时间序列 | 30 | 设备清单（`nyct_ene_equipments.json`）里的 ADA 字段 |
| 25 | 第六轮：设备清单的 ADA 核对与车站状态时间序列 | 31 | 181 St（A）入口推断与清单对照：一致，但仍是推断 |
| 26 | 第七轮：Harlem-148 St 标记与"预计恢复时间已过" | 34 | Harlem-148 St 标成"无电梯依赖" |
| 27 | 第十一轮：14 个建不了模型的站、修复后的 Monte Carlo、最终汇总 | 57 | 那 14 个站为什么建不了电梯模型，哪些能补上 |

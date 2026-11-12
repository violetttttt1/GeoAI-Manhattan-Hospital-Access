# 实时停运数据检查（checks_live）

覆盖：实时停运抓取的检查、日志字段、车站状态时间序列、预计恢复时间。抓取程序见 `live/`。 节号在本文件内重新编排；原文件保存在 `archive/checks_original.md`，文末有新旧节号对照。所有数字均为初步结果。

---

*（原章：第四轮：实时停运数据检查）*

只做检查，不做分析。采集脚本和数据现在在 `~/geoai-live/`（脚本、`live_log.csv`、`raw/live_outages/`），不在本目录，原因是 launchd 读不了 `~/Desktop`。本目录的 `LIVE_OUTAGES_MOVED.txt` 有说明。docs/checks_data.md 第 14 节里“`fetch_live_outages.py` 等不是我创建的”现在已过时：它们是后来创建的，并已搬走。

接口：`nyct%2Fnyct_ene.json`（当前停运）和 `nyct%2Fnyct_ene_equipments.json`（设备清单），都不需要 key（无 key 请求返回 200）。

## 1. 最新快照的字段

文件：`outages_20261111T192728Z.json`（抓取时间 2026-11-11 19:27:28 UTC），一个 JSON 数组，**182 行**，每行 12 个字段，每个字段 182 行都有值：

| 字段 | 含义（按取值推断） |
|---|---|
| station | 站名 |
| borough | 区（本份快照中**全为空字符串**） |
| trainno | 线路 |
| equipment | 设备编号（如 EL124），与研究区文件的 `Equipment Code` 同一套 |
| equipmenttype | EL（电梯）158 行 / ES（扶梯）24 行 |
| serving | 该设备连接的楼层说明 |
| ADA | Y/N |
| outagedate | 停运开始时间，字符串 `MM/DD/YYYY hh:mm:ss AM/PM` |
| estimatedreturntoservice | 预计恢复时间，同格式 |
| reason | 原因（如 Planned Work、Inspection、Maintenance、Under Investigation） |
| isupcomingoutage | Y/N |
| ismaintenanceoutage | Y/N |

示例（第一行）：

```json
{"station": "175 St", "borough": "", "trainno": "A", "equipment": "EL124",
 "equipmenttype": "EL", "serving": "Mezzanine to platform for service in both directions.",
 "ADA": "Y", "outagedate": "12/16/2026 10:00:00 PM",
 "estimatedreturntoservice": "12/17/2026 06:00:00 AM", "reason": "Planned Work",
 "isupcomingoutage": "Y", "ismaintenanceoutage": "N"}
```

**需要注意的三点：**
1. **182 行不是 182 个设备。** 同一设备可有多行（EL123 两行，EL786 三行等），不同设备编号只有 **132 个**（其中电梯 108 个）。
2. **`isupcomingoutage = Y` 的有 140 行，N 只有 42 行。** Y 是“预定的、还没开始的停运”（例如上面示例的开始时间是 2026-12-16，晚于抓取时间）。所以 `live_log.csv` 里的 `outage_count`（= 数组行数，182）**包含未来的计划停运**，不等于“此刻有多少设备停着”。这一点我之前汇报“有 179 条停运”时没有说清。`ismaintenanceoutage` 182 行全是 N。
3. 时间字段是不带时区的字符串，时区未核实（推测是纽约当地时间）。

## 2. 实时数据与 `study_area_elevators.csv` 按设备编号匹配

研究区 48 个电梯，编号列 `Equipment Code`，实时数据中的编号列 `equipment`（设备清单中是 `equipmentno`）。编号直接比较，没有去 X 后缀。

| 检查 | 结果 |
|---|---|
| 设备清单（707 个设备：430 电梯 + 277 扶梯）里能找到的研究区电梯 | **38 / 48 = 79.2%** |
| 研究区 37 个**有**可用率记录的电梯 → 设备清单 | 37 / 37 = 100% |
| 实时停运中的设备编号（全部 5 份快照合计 132 个）→ 设备清单 | 132 / 132 = 100% |
| 研究区 48 个电梯 → 最新快照（出现在停运/预定停运列表里） | **8 / 48 = 16.7%**（EL123、EL124、EL142、EL143、EL144、EL179、EL517、EL518） |
| 最新快照 132 个设备 → 研究区 | 8 / 132 = 6.1% |

“匹配率”有两种读法，上面都列了：**编号体系是否对得上**（设备清单 79.2%，其中缺的 10 个正是下面单独列出的 11 个中的 10 个）；**研究区电梯有没有出现在停运列表里**（8 个）。后一个数只反映“停运列表里有谁”，不是匹配失败。

这 8 个里，最新快照中只有 **EL123（175 St）一条是 N（正在停运，Under Investigation）**，其余全是 Y（预定停运）。这里只是核对，没有做更多解读。

## 3. 研究区里 11 个没有可用率记录的电梯，在实时数据里有没有

11 个：EL147、EL150、EL151、EL152、EL153、EL155、EL156、EL166X、EL167X、EL169X、EL520（docs/checks_data.md 第 9 节）。

| 电梯 | 在设备清单（`equipments.json`）里 | 在实时停运中出现（5 份快照） |
|---|---|---|
| EL147、EL150、EL151、EL152、EL153、EL155 | 否 | 否 |
| EL156 | 否 | 否 |
| EL166X、EL167X、EL169X | 否 | 否 |
| EL520 | **是** | 否 |

结论：**11 个在实时停运数据里一次都没出现**（0 / 5 份快照）。设备清单里能找到的只有 EL520。

注意不要把“没出现”当成“没有故障”：停运接口只列正在或即将停运的设备，没出现只说明这 5 份快照里它们没被列出。且这 11 个里有 10 个根本不在 MTA 的设备清单里，也就是 MTA 的实时系统可能压根不监控它们，原因未核实。EL520 在清单里但没有历史可用率，也没有出现在停运中。

## 4. 抓取份数与空档

时间范围：2026-11-11 19:06:17 ~ 19:27:28 UTC（检查时）。

| 项目 | 数值 |
|---|---|
| 停运快照文件 | **5 份** |
| `live_log.csv` 行数 | 5，全部 success = 1，没有失败记录 |
| 设备清单文件 | 1 份（19:06:12，只抓一次） |
| 文件数与日志行数 | 一致 |

相邻两次的间隔（秒）：

| 时刻（UTC） | 间隔 | 说明 |
|---|---|---|
| 19:06:17 → 19:09:33 | 196 | 手动启动的第一个进程运行期间 |
| 19:09:33 → 19:15:56 | 383 | 中间我停掉进程、试 launchd、再重启进程 |
| 19:15:56 → 19:17:26 | 90 | 搬家过程中进程切换，间隔短于 10 分钟 |
| 19:17:26 → 19:27:28 | 602 | launchd 正常运行，10 分钟节奏 |

- **没有空档**：没有超过 10 分钟（600 秒）一次的间隔，最长 602 秒（含请求耗时）。
- **前 3 个间隔比 10 分钟短**，是调试时多次重启进程造成的，不是漏抓，只是节奏不均匀。从 19:17:26 起已是稳定的 10 分钟一次。
- 上面只覆盖了 21 分钟，不足以说明长期稳定，也没有验证睡眠、断网、重启后的情形。

---

*（原章：第五轮：日志加列与实时数据小检查）*

快照：`outages_20261111T193539Z.json`（2026-11-11 19:35:39 UTC，纽约时间 14:35:39）。

## 5. `live_log.csv` 新增的列

位置 `~/geoai-live/live_log.csv`，原有 4 列顺序不变，新列加在最后：

| 列 | 含义 |
|---|---|
| `fetched_at_nyc` | 抓取时间，纽约时间（带偏移，如 `2026-11-11T14:35:39-05:00`） |
| `current_outage_devices` | 正在停运的设备数：`isupcomingoutage = N`，按 `equipment` 去重 |
| `current_nonmaint_devices` | 其中**非维护性**的设备数：同一行同时满足 `isupcomingoutage = N` 且 `ismaintenanceoutage = N`，按设备去重 |
| `distinct_devices` | 列表里所有不同的设备数（正在停运 + 预定停运） |

- 抓取失败的行，三个设备数列留空。
- 旧的 5 行是用当时保存的原始文件回填的，旧版日志备份为 `~/geoai-live/live_log.pre_v2.csv`。回填前后 `outage_count` 没变。
- 最新一行（19:35:39）：行数 182，正在停运 42，非维护性 42，不同设备 132。
- **`current_nonmaint_devices` 目前永远等于 `current_outage_devices`**：`ismaintenanceoutage` 在已抓的所有快照里全是 N，包括 `reason` 写着 "Maintenance" 的行（如 EL144、EL517、EL518）。所以这个字段看起来不能区分维护性与否，是否另有含义我没有核实。
- 脚本已改，launchd 已重启（新进程），后续每次抓取自动写新列。

## 6. 研究区在列表里的 8 个电梯

共 8 个设备、14 行（同一设备可有多条停运记录）。站名、线路来自实时数据的 `station`、`trainno`。时间是原始字符串，时区未核实。

| 设备 | 所属车站 | 预定停运（isupcomingoutage） | 维护性（ismaintenanceoutage） | 原因 | 开始 | 预计恢复 |
|---|---|---|---|---|---|---|
| EL123 | 175 St（A） | **N（正在停运）** | N | Under Investigation | 11/11/2026 01:27 PM | 11/11/2026 09:00 PM |
| EL123 | 175 St（A） | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL124 | 175 St（A） | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL142 | 125 St（A/C/B/D） | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL143 | 125 St（A/C/B/D） | Y | N | Planned Work | 12/16/2026 10:00 PM | 12/17/2026 06:00 AM |
| EL144 | 125 St（A/C/B/D） | Y | N | Maintenance | 11/11/2026 10:00 PM | 11/12/2026 06:00 AM |
| EL179 | Dyckman St（1） | Y | N | Planned Work | 11/19/2026 10:00 PM | 11/20/2026 06:00 AM |
| EL179 | Dyckman St（1） | Y | N | Inspection | 11/20/2026 10:00 PM | 11/21/2026 06:00 AM |
| EL517 | 181 St（A） | Y | N | Maintenance | 11/11/2026 10:00 PM | 11/12/2026 06:00 AM |
| EL517 | 181 St（A） | Y | N | Planned Work | 11/19/2026 10:00 PM | 11/20/2026 06:00 AM |
| EL517 | 181 St（A） | Y | N | Inspection | 11/20/2026 10:00 PM | 11/21/2026 06:00 AM |
| EL518 | 181 St（A） | Y | N | Maintenance | 11/11/2026 10:00 PM | 11/12/2026 06:00 AM |
| EL518 | 181 St（A） | Y | N | Planned Work | 11/19/2026 10:00 PM | 11/20/2026 06:00 AM |
| EL518 | 181 St（A） | Y | N | Inspection | 11/20/2026 10:00 PM | 11/21/2026 06:00 AM |

14 行里只有第一行（EL123）正在停运，其余 13 行都是预定停运。

## 7. 正在停运的设备中，ADA 为 Y 的数量

| 项目 | 数量 |
|---|---|
| 正在停运的设备（`isupcomingoutage = N`，去重） | 42 |
| 其中 `ADA = Y` | **18** |
| 其中 `ADA = N` | 24 |

拆开看：**18 个 ADA=Y 的全是电梯（EL），24 个 ADA=N 的全是扶梯（ES）**，两个字段完全对应。每个设备在所有正在停运的行里 ADA 取值一致，没有同一设备既 Y 又 N 的情况。

## 8. 日志时间戳的时区

- **`fetched_at_utc` 是 UTC。** 脚本用 `datetime.now(timezone.utc)` 生成，值带 `+00:00` 后缀；原始文件名里的时间也来自同一时刻，后缀 `Z`。
- 核对：UTC 19:35:39 对应纽约 14:35:39，偏移 -05:00，符合美东标准时间（2026 年夏令时在 11 月 1 日结束）。
- 新增的 `fetched_at_nyc` 用系统的 `America/New_York` 时区数据换算，夏令时会自动处理。
- 这只说明**我们自己记录的抓取时间**是 UTC。接口返回的 `outagedate`、`estimatedreturntoservice` 没有时区标记，是否为纽约当地时间未核实。

---

*（原章：第六轮：设备清单的 ADA 核对与车站状态时间序列）*

## 9. 车站状态时间序列：`station_status.py` 和 `station_status_timeseries.csv`

- 脚本：[station_status.py](../live/station_status.py)。读 `~/geoai-live/raw/live_outages/` 下所有快照和 `station_table.csv`，输出 [station_status_timeseries.csv](../outputs/station_status_timeseries.csv)。
- 重新运行：`python3 station_status.py`。只追加输出里还没有的快照（按 `snapshot_utc` 判断），已有行不会被改写；连续运行两次，第二次追加 0 份（已验证）。
- 列：`snapshot_utc, snapshot_nyc, station_id, gtfs_stop_id, station_name, routes, available, blocked_directions, elevators_out`。
- **规则：**
  - 电梯"在停" = 该快照里有一行 `equipment` 对得上且 `isupcomingoutage = N`。预定停运（Y）不算。
  - 车站 `access_paths` 里 `+` 是串联（都要通），`|` 是并联（任一条通即可），`PN` 和 `PS` 两个方向都要有一条完整可通的路径，车站才算可用（`available = 1`）。`blocked_directions` 写哪个方向被堵。
  - `elevators_out` 只列该车站路径里的电梯。
  - Harlem-148 St 没有电梯数据，`available` 留空，表示无法判断，不是可用也不是不可用。
- 目前 6 份快照 × 10 站 = 60 行。**每份快照里只有 175 St 是不可用（0），原因都是 EL123。** Harlem-148 St 全部留空，其余 8 站都是 1。
- 局限：
  - 这只表示"MTA 当前停运列表里有没有这个电梯"。列表之外的原因（比如设备没被监控、清单里没有）看不见。
  - 没有用 `estimatedreturntoservice` 判断"是否已过恢复时间"，快照里还列着就算在停。
  - 137 St 的 EL519/EL520 路径用的是 station_table 里的结构，EL166X、EL167X、EL169X 不在路径里。
  - 没有算概率，也没建模。

## 10. 175 St 此刻是否可用

**不可用。** 最新快照是 `outages_20261111T193539Z.json`（UTC 19:35:39，纽约 14:35:39），`station_status_timeseries.csv` 里 175 St 那一行 `available = 0`，`blocked_directions = PN;PS`，`elevators_out = EL123`。

- 175 St 的结构是 EL123 → EL124 **串联**（`PN: EL123+EL124; PS: EL123+EL124`），没有并联的替代电梯，EL123 在停，两个方向都走不通。
- EL123 在清单里的 `serving` 是"177 St & Fort Washington Ave (NE corner) to mezzanine"，也就是街面进夹层的那一部。
- 这条停运：开始 11/11/2026 01:27 PM，预计恢复 11/11/2026 09:00 PM，原因 Under Investigation，`isupcomingoutage = N`。时间字符串没有时区，是否为纽约当地时间未核实。如果是，按纽约时间当前约 14:40，预计还有大约 6 小时 20 分钟。预计恢复时间只是 MTA 的预估，不是保证。
- EL124 本身此刻不在停，只在 12/16 有一条预定停运（Y）。
- 6 份快照里 175 St 一直是不可用，所以这是持续状态，不是偶发。

---

*（原章：第七轮：Harlem-148 St 标记与"预计恢复时间已过"）*

## 11. 新增 `recovery_overdue` 列

时间序列新增两列：`recovery_overdue`（值为"预计恢复时间已过"或空）和 `overdue_elevators`（哪些电梯）。

- 规则：车站路径里某个**正在停运**的电梯，如果快照时间晚于它的 `estimatedreturntoservice`，就标记。一个电梯有多条当前停运记录时，取最晚的预计恢复时间。
- **不改变 `available`。** 标记只是提示，可用性仍然只看 `isupcomingoutage = N`。
- 接口里的时间没有时区。我按纽约当地时间解读，这一点**未核实**。
- 6 份快照里没有任何一行被标记：EL123 的预计恢复是 11/11 21:00，所有快照都早于它。
- 用假数据验证过逻辑：EL123 预计恢复 21:00 纽约时间，快照在 20:59 不标记，在 21:01 标记，且 `available` 仍是 0。
- 脚本 `station_status.py` 已同步更新，新快照进来时重新运行即可。

---

## 附：新旧节号对照

| 新节号 | 原章 | 原节号 | 标题 |
|---|---|---|---|
| 1 | 第四轮：实时停运数据检查 | 22 | 最新快照的字段 |
| 2 | 第四轮：实时停运数据检查 | 23 | 实时数据与 `study_area_elevators.csv` 按设备编号匹配 |
| 3 | 第四轮：实时停运数据检查 | 24 | 研究区里 11 个没有可用率记录的电梯，在实时数据里有没有 |
| 4 | 第四轮：实时停运数据检查 | 25 | 抓取份数与空档 |
| 5 | 第五轮：日志加列与实时数据小检查 | 26 | `live_log.csv` 新增的列 |
| 6 | 第五轮：日志加列与实时数据小检查 | 27 | 研究区在列表里的 8 个电梯 |
| 7 | 第五轮：日志加列与实时数据小检查 | 28 | 正在停运的设备中，ADA 为 Y 的数量 |
| 8 | 第五轮：日志加列与实时数据小检查 | 29 | 日志时间戳的时区 |
| 9 | 第六轮：设备清单的 ADA 核对与车站状态时间序列 | 32 | 车站状态时间序列：`station_status.py` 和 `station_status_timeseries.csv` |
| 10 | 第六轮：设备清单的 ADA 核对与车站状态时间序列 | 33 | 175 St 此刻是否可用 |
| 11 | 第七轮：Harlem-148 St 标记与"预计恢复时间已过" | 35 | 新增 `recovery_overdue` 列 |

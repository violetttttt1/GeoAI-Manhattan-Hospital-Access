# GeoAI — 曼哈顿医院无障碍可达性

## 项目目的

量化“地图上无障碍”和“现实中到得了”的差距。对象是曼哈顿岛上的三家医院：
Harlem Hospital、NYP/Columbia、Mount Sinai Morningside。先看地铁和公交，再加电梯
故障，最后加坡道（坡道是待办，见 `HANDOFF.md` 的 t1）。

核心问题：只看地图上的 ADA（无障碍）站点时能覆盖多少居民；如果电梯会随机
停运，实际能覆盖多少；以及哪一部电梯、哪一个站一停影响最大。

项目现状、初步发现、已知问题和待办见 `HANDOFF.md`；数据体检和过程记录见
`docs/checks_data.md`、`docs/checks_live.md`、`docs/checks_isochrone.md`；最终
汇总数字见 `docs/final_summary.md` 和 `outputs/final_summary.csv`。

**所有数字目前都是初步的。** 引用时请标注“初步”，不要写精确面积。

## 研究范围

- **只统计曼哈顿岛。** 居民只统计曼哈顿的 census tract，其他区不计入。等时圈
  本身可以越过河面，但居民数和面积只算曼哈顿内的部分（见 56 号脚本的裁剪）。
- 范围边界用纽约市官方曼哈顿行政区边界（陆地，不含河面；含 Marble Hill；
  罗斯福岛在内，但从未被到达）。
- **三家医院**：Harlem Hospital、NYP/Columbia、Mount Sinai Morningside。
- **30 分钟等时圈**，五个出发时刻 07:30–08:30 取平均（Monte Carlo 只用
  08:00 单一时刻，两者时间口径不同，不要直接比较绝对值）。
- **方向**：正向（从医院出发）和反向（在 08:00 前到达医院）都算过；最终
  汇总表用的是反向。
- **四个情景**：① 普通人坐地铁；② 只走 ADA 地铁站；③ 普通人地铁加公交；
  ④ ADA 地铁站加公交（所有公交车和公交站都当作可用，这是 ADA 组的上限）。
- **居民数**：ACS 2020–2024 行走困难人口，按 tract 面积比例分配到网格。

## 关键假设（先读 `HANDOFF.md` 的“已知问题”）

- 电梯故障相互独立；可用率用 12 个月 24 小时平均值；停运状态 30 分钟内不变。
- 步行速度 4.8 km/h；居民在 tract 内均匀分布；不含路缘坡道。
- 公交全部当作无障碍。
- 5 个 ADA 站没有电梯模型，当作永远可用，会高估这些站附近的覆盖概率。
  补建的 9 个站，结构来自 MTA 设备清单的文字说明，没有现场核实。
- 148 St 按“无电梯依赖”处理，没有现场核实。
- 坡道数据采集于 2017 到 2020 年，之后有改造；测量值不能直接说明是否符合 ADA。
- 实时数据里的时间没有时区标记，`ismaintenanceoutage` 字段不可用。

## 初步结果（摘自 `docs/final_summary.md`，均为初步）

ADA 组占普通人的比例（居民口径，反向，五时刻均值）：只走地铁时 NYP 约 75%、
Harlem 约 71%、Mount Sinai 约 42%；加公交后 Harlem 约 84%、NYP 约 81%、
Mount Sinai 约 69%。Harlem 和 NYP 的先后不稳定，Mount Sinai 最低。

Monte Carlo（情景④，1000 次，08:00 单一时刻）：第 5 百分位相对基线，NYP
约 70%，Harlem 约 90%，Mount Sinai 约 94%。单点依赖最大的是 NYP 的
168 St（A/C），一停损失约 43% 居民，取决于一部电梯 EL139；Harlem 的
135 St（2/3）损失约 32%。

## 文件夹说明

```
GeoAI/
├── README.md            本文件
├── HANDOFF.md           项目现状、初步发现、已知问题、待办、规则
├── requirements.txt     第三方依赖（见“环境安装”）
├── .gitignore           排除 raw/、data/cache/、archive/、zip、含 key 的文件等
├── checks.md            旧的体检记录原文（已拆成 docs/ 下的三份，见 archive/）
├── station_status.py    根目录留存的副本（live/ 里也有一份，见下）
├── station_table.csv / station_status_timeseries.csv / elevator_detail.csv
│                        根目录留存的副本，与 data/clean/ 里的一致
├── docs/                文档
│   ├── checks_data.md       数据体检（27 节）
│   ├── checks_live.md       实时抓取体检（11 节）
│   ├── checks_isochrone.md  等时圈与 Monte Carlo 记录（31 节）
│   └── final_summary.md     最终汇总表与读法
├── raw/                 原始下载数据（不进分享包，见“raw 数据重新下载”）
│                        14 个子目录：borough_boundaries、census、elevator_availability、
│                        elevator_inventory、gtfs、gtfs_bus、live_equipment、
│                        mbpo_ramp_report、mta_amenities、mta_entrances、mta_stations、
│                        nyc_centerline、ped_ramp_locations、ramp_program_progress
├── data/
│   ├── clean/           清洗后、冻结的表（不要改；要改就新建，见“规则”）
│   │                    station_table.csv、elevator_detail.csv、
│   │                    study_area_elevators.csv、elevators_assigned_by_coordinates.csv、
│   │                    station_model_fixes.csv、mc_station_model.csv、
│   │                    mc_elevator_station_map.csv
│   └── cache/           脚本跑出来的中间文件（pickle 等，可重新生成，不进分享包）
│                        另有 data/cache/rebuilt/：重建的 clean 表副本，
│                        绝不直接覆盖 data/clean/
├── scripts/             全部分析脚本（51 个，见“脚本与运行顺序”）
├── outputs/             地图（PNG）和汇总表（CSV）
├── live/                实时抓取的副本：抓取脚本、启动配置模板、station_status.py
└── archive/             备份与调试材料，不进分享包
                         checks_original.md、.pre_* 备份文件、
                         scripts_original_verbatim/（55 个脚本的原样副本）、
                         scripts_debug/（调试脚本）、scripts_superseded/（被取代的脚本）、
                         refactor_paths.py、split_checks.py、verify_scripts.py
```

`raw/` 目录保持原位不动。根目录的 `checks.md`、`station_status.py`、
`station_table.csv`、`station_status_timeseries.csv`、`elevator_detail.csv`
是整理时特意保留的副本（其中后 4 个是复制，原件仍在根目录）。

## 环境安装

- Python 3.13（结果是在 3.13.9 上跑出来的）。
- 只装五个第三方库，其余都是标准库：

```bash
pip install -r requirements.txt
```

`requirements.txt`：pandas 2.2.3、numpy 2.3.5、scipy 1.16.3、
matplotlib 3.10.6、Pillow 12.0.0。

## 怎么跑

在项目根目录（也就是 `scripts/` 的上一级）运行：

```bash
python scripts/01_download_raw.py --list   # 先看 raw 数据清单（可选）
python scripts/10_check_profile.py
python scripts/11_check_id_match.py
# ……按编号顺序往下跑，见下表
```

- 脚本按编号顺序跑，`lib_*.py` 和 `_paths.py` 不直接运行，它们是被其他脚本
  `exec` / `import` 加载的共享代码。
- 所有路径都走 `scripts/_paths.py`：`R` = `raw/`、`O` = `data/clean/`（已冻结
  的表）或 `outputs/`（其他输出）、`S` = `data/cache/`、`REB` =
  `data/cache/rebuilt/`。脚本里没有写死的绝对路径。
- 想对着一份临时副本跑（不碰原项目），设环境变量 `GEOAI_ROOT` 指向那份
  副本的根目录，例如 `GEOAI_ROOT=/tmp/geoai-copy python scripts/54_....py`。
- 65 号和 69 号脚本用多进程，各约 5 分钟；其他脚本大多在 1 分钟内。
- 有 4 个脚本是按当时即席运行的命令重建的，不是当时实际跑的原脚本，文件头
  里写明了：`31_bus_windows.py`、`55_iso_time_average_summary.py`、
  `57_manhattan_clip_tables.py`、`66_mc_station_model_table.py`，以及新写的
  `01_download_raw.py` 和 `81_add_pct_columns.py`。

### 脚本与运行顺序

“输出”一栏只写主要输出；标“只打印”的脚本不写文件，结果打在终端上。

| 脚本 | 做什么 | 主要输入 | 主要输出 |
|---|---|---|---|
| `01_download_raw.py` | 下载全部 15 份原始数据（新写，见“raw 数据重新下载”） | 各来源网址 | `raw/`（约 800 MB） |
| `10_check_profile.py` | 体检原始数据：行列、日期范围（打印） | `raw/` 各表 | 只打印 |
| `11_check_id_match.py` | 核对各表之间的站点/设备 ID 是否对得上（打印） | `raw/` 各表 | 只打印 |
| `12_check_station_id_zero_pad.py` | 核对 Station MRN 去掉前导 0 后在各表是否一致（打印） | 可用率表、设备清单、站点表 | 只打印 |
| `13_ada_official_list_parse.py` | 解析 MTA 官网无障碍站点页 | `data/cache/mta_acc.html` | `data/cache/official_ada.csv` |
| `14_ada_official_list_match.py` | 官网无障碍站点表与站点表按名字+线路匹配（打印） | `official_ada.csv`、站点表 | 只打印 |
| `15_search_148st.py` | 在各表里搜 148 St / Harlem 相关记录（打印） | `raw/` 各表 | 只打印 |
| `20_study_area_counts.py` | 划研究区：110 St 以北 + 三家医院周边 400 m，统计区内电梯、坡道 | `raw/` 各表 | 只打印 |
| `21_study_area_line_fit.py` | 用坡道拐角点拟合 110 St 分界线（打印） | 坡道位置表 | 只打印 |
| `22_study_area_mbpo_stations.py` | 按医院分区统计坡道与 MBPO 站点（打印） | 坡道位置表、站点表 | 只打印 |
| `23_station_table.py` | 建研究区站点表与逐电梯明细 | 站点表、设备清单、可用率表 | `data/clean/station_table.csv`、`elevator_detail.csv`、`study_area_elevators.csv`、`elevators_assigned_by_coordinates.csv`（经 `data/cache/rebuilt/` 中转） |
| `24_hospital_ada_stations.py` | 三家医院附近的 ADA 站（按直线距离） | 站点表、出入口表 | `outputs/hospital_ada_stations.csv` |
| `25_hospitals_map.py` | 三家医院与研究区地图 | 行政区边界 GeoJSON | `outputs/hospitals_map.png` |
| `30_street_graph.py` | 用 NYC Street Centerline 建步行路网图 | `raw/nyc_centerline/` | `data/cache/graph.pkl` |
| `31_bus_windows.py` | 建公交时刻表窗口（重建，见文件头） | `raw/gtfs_bus/`（曼哈顿、布朗克斯、MTA Bus） | `data/cache/bus_8.pkl`、`bus_12.pkl`、`bus_avg.pkl`、`bus_rev.pkl`、`bus_rev5.pkl` |
| `40_iso_nyp_subway_run.py` | NYP 出发（正向）地铁等时圈，30 分钟 | 路网图、地铁 GTFS | `data/cache/iso_res.pkl` |
| `41_iso_nyp_subway_area.py` | NYP 地铁等时圈的面积与居民统计 | `iso_res.pkl` | `outputs/nyp_isochrone_summary.csv`、`data/cache/iso_masks.pkl` |
| `42_iso_nyp_subway_map.py` | NYP 地铁等时圈地图 | `iso_res.pkl`、`iso_masks.pkl` | `outputs/nyp_isochrone_30min.png` |
| `43_iso_nyp_bus_run.py` | NYP 地铁+公交：08:00/12:00 × 用不用公交 × 只走 ADA 站 | 路网图、地铁+公交 GTFS | `data/cache/iso2_res.pkl` |
| `44_iso_nyp_bus_area.py` | NYP 地铁+公交的面积与居民统计 | `iso2_res.pkl` | `outputs/nyp_isochrone_bus_summary.csv`、`data/cache/iso2_masks.pkl` |
| `45_iso_nyp_bus_map.py` | NYP 地铁+公交四情景地图 | `iso2_masks.pkl`、汇总表 | `outputs/nyp_isochrone_bus_4scenarios.png` |
| `50_iso_hospitals_run.py` | 三家医院等时圈：正向 08:00/12:00、反向 08:00 | 路网图、地铁+公交 GTFS | `data/cache/iso3_res.pkl` |
| `51_iso_hospitals_area.py` | 三家医院等时圈的面积与居民统计 | `iso3_res.pkl` | `outputs/hospital_isochrone_summary.csv`、`data/cache/iso3_masks.pkl` |
| `52_iso_hospitals_map.py` | 三家医院四情景地图 | `iso3_masks.pkl`、汇总表 | `outputs/isochrone_harlem_4scenarios.png`、`isochrone_nyp_columbia_4scenarios.png`、`isochrone_mt_sinai_morningside_4scenarios.png` |
| `53_iso_reverse_validate.py` | 反向等时圈抽查验证（打印） | `iso3_res.pkl` | 只打印 |
| `54_iso_time_average_runs.py` | 三家医院 × 4 情景 × 5 个出发时刻（07:30–08:30），反向 | 路网图、地铁+公交 GTFS | `outputs/hospital_isochrone_timeavg_runs.csv` |
| `55_iso_time_average_summary.py` | 五时刻的均值/标准差/最小/最大/变异系数（重建，见文件头） | `hospital_isochrone_timeavg_runs.csv` | `outputs/hospital_isochrone_timeavg_summary.csv` |
| `56_manhattan_clip_runs.py` | 同 54，但只统计曼哈顿内的居民与面积 | 路网图、地铁+公交 GTFS | `outputs/manhattan_clip_runs.csv` |
| `57_manhattan_clip_tables.py` | 裁剪前后对照表与 ADA 占比、公交增益（重建，见文件头） | `manhattan_clip_runs.csv` | `outputs/manhattan_clip_comparison.csv`、`manhattan_clip_ratios.csv` |
| `60_mc_first_run.py` | 情景④ Monte Carlo 第一轮：1000 次，随机种子 20261111，08:00 单一时刻 | 电梯模型、人口密度网格 | `outputs/mc_scenario4_summary.csv`、`mc_single_failure.csv`、`data/cache/mc_counts.pkl` |
| `61_mc_selfcheck.py` | Monte Carlo 自检：抽样频率 vs 解析概率（打印） | 电梯模型 | 只打印 |
| `62_mc_threshold_noise.py` | 覆盖概率 90% 阈值附近的抽样噪声检查（打印） | `mc_counts.pkl`、`mc_scenario4_summary.csv` | 只打印 |
| `63_mc_coverage_maps.py` | Monte Carlo 覆盖概率地图 | 电梯模型、1000 次抽样 | `outputs/mc_scenario4_coverage_forward.png`、`mc_scenario4_coverage_reverse.png` |
| `64_mc_expanded_model_build.py` | 扩展电梯模型：从 10 站扩到 59 站（先在原 10 站上验证通过） | 站点表、设备清单、可用率表 | `data/cache/mc2_model.pkl` |
| `65_mc_expanded_run.py` | 扩展模型 Monte Carlo：1000 次（多进程，约 5 分钟） | `mc2_model.pkl` | `outputs/mc_manhattan_summary.csv`、`mc_manhattan_single_failure.csv` |
| `66_mc_station_model_table.py` | 把模型导出成表（重建，见文件头） | `mc2_model.pkl`、`mc3_model.pkl` | `data/cache/rebuilt/mc_station_model.csv`、`mc_elevator_station_map.csv`（另有一份已放入 `data/clean/`，供 80 号使用） |
| `67_mc_tables.py` | 把 Monte Carlo 结果整理成表格（打印 + 写表） | `mc_manhattan_summary.csv` 等 | `data/cache/tbl_*.md` |
| `68_mc_station_fixes.py` | 修正电梯模型：补建 9 个站，纠正 2 个旧模型 | `mc2_model.pkl`、可用率表 | `data/cache/mc3_model.pkl`、`data/clean/station_model_fixes.csv` |
| `69_mc_fixed_run.py` | 修正后模型 Monte Carlo：1000 次（多进程，约 5 分钟） | `mc3_model.pkl` | `outputs/mc_manhattan_summary_fixed.csv`、`mc_manhattan_single_failure_fixed.csv` |
| `70_mc_fix_compare.py` | 修正前后对照（打印） | 修正前后的汇总表 | 只打印 |
| `80_final_summary.py` | 最终汇总：三家医院 × 4 情景 + Monte Carlo | 裁剪对照表、修正后 MC 表、单点失效表 | `outputs/final_summary.csv`、`docs/final_summary.md` |
| `81_add_pct_columns.py` | 在 MC 汇总表里加两列：均值与第 5 百分位相对各自基线的百分比（基线 = 同一医院、同一方向、同一出发时刻、同一情景） | `mc_manhattan_summary_fixed.csv` | `outputs/mc_manhattan_summary_fixed_with_pct.csv`（原文件不动） |
| `_paths.py` | 全部脚本共用的路径 helper（不直接运行） | — | — |
| `lib_iso_core.py` | 地铁等时圈共享代码（路网 + 地铁 GTFS） | — | 供 40–42、44、51 调用 |
| `lib_iso2_core.py` | 地铁+公交等时圈共享代码 | — | 供 43–45 调用 |
| `lib_iso3_core.py` | 三家医院等时圈共享代码 | — | 供 50–54 调用 |
| `lib_iso4_grid.py` | 10 m 网格与 tract 人口密度 | — | 供 54、62 调用 |
| `lib_clip_core.py` | 曼哈顿裁剪共享代码 | — | 供 56、64、65、69 调用 |
| `lib_mc_core.py` | Monte Carlo 共享代码（10 站模型） | — | 供 60–63 调用 |
| `lib_mc2_model.py` | 扩展电梯模型 builder | — | 供 64–65、68–69 调用 |
| `lib_bus_load.py` | 公交 GTFS 加载 | — | 供 31、43、50 调用 |

## raw 数据重新下载

```bash
python scripts/01_download_raw.py --list    # 看清单：数据集、大小、目标路径
python scripts/01_download_raw.py --check   # 只检查每个网址是否可达，不下载
python scripts/01_download_raw.py --only mta_stations,elevator_inventory
python scripts/01_download_raw.py           # 全部，约 800 MB（主要是公交 GTFS，约 560 MB）
```

15 份数据（`--list` 会列出全部）：电梯可用率、电梯设备清单、地铁站点表、
地铁 GTFS、公交 GTFS（曼哈顿、布朗克斯、布鲁克林、皇后区、史丹顿岛、MTA Bus
公司）、人行道坡道位置、坡道工程进度、MBPO 坡道报告、行政区边界、MTA 实时
设备与停运快照、地铁出入口、地铁站设施、NYC 街道中心线、ACS 2020–2024
B18105 表 + 2020 年 tract 边界、MTA 官网无障碍站点页（存到 `data/cache/`，
不在 `raw/` 里）。

**重新下载后不会和原来完全一致的数据**：

- `live_equipment`：2026-11-11 当天抓的 MTA 实时快照，无法重现。
- 电梯可用率、设备清单、站点表、出入口、站设施：MTA 的滚动更新表。
- 地铁/公交 GTFS：MTA 发布新时刻表就会换文件（这里用的公交时刻表有效期
  为 2026-10-12 至 2027-01-02）。
- MTA 官网无障碍站点页：当时版本日期为 2026-10-12。
- 行政区/tract 边界、街道中心线、ACS 文件、坡道表是静态或变化很慢的来源，
  重新下载后应基本一致。

另外，桌面上的 `GeoAI_raw.zip`（182.6 MB）就是 `raw/` 的压缩包：解压到项目
根目录就会得到 `raw/`，不用重新下载。

## 实时抓取（`live/`）

- `live/fetch_live_outages.py`：每 10 分钟查一次 MTA 电梯/扶梯实时停运接口。
  每次成功抓取：原始响应原样存到 `raw/live_outages/outages_<UTC 时间>.json`，
  并在 `live_log.csv` 里追加一行（UTC 时间、是否成功、条数、错误、纽约时间、
  设备数）。失败会记日志，60 秒后重试；401/403 会直接停掉脚本。
- `live/station_status.py`：用实时数据算各站状态。实时目录由环境变量
  `GEOAI_LIVE_DIR` 指定，默认用项目里的 `live/`。
- `live/com.geoai.liveoutages.plist.template`：macOS launchd 启动配置模板，
  把里面的 `<PYTHON>`、`<LIVE_DIR>`、`<LOG_DIR>` 换成自己机器上的实际路径再用。
- 原来的 `~/geoai-live` 不要动：抓取进程在组长电脑上跑，周六上午分享快照。
  `live/` 里的只是副本和模板。
- 可选的 API key 从环境变量 `MTA_API_KEY` 读（请求头 `x-api-key`），不要写进
  文件里；到目前为止不需要 key。

## 给后来者的规则

- **不要修改已有脚本和 `data/clean/` 里的文件。** 要改就新建，文件名以任务
  编号开头，比如 `t1_`。
- 结果写在 `docs/checks_t1.md` 这样的文件里，**不写人名**。
- 数字都先标“初步”，别写精确面积。
- 新数据、新中间文件先放 `data/cache/`；只有确认冻结的表才进 `data/clean/`。
- 敏感信息（人名、邮箱、`/Users/` 开头的路径、API key、密码、token）不要
  写进要分享的文件里。

## 验证状态（2026-11-11 记录）

46 个脚本中有 32 个已逐个重跑并与原输出逐字节比对通过，0 失败；其余 14 个
（54 号及以后）当时还在后台跑。重跑是在临时项目副本里做的，没有改动原项目。
超过 10 分钟的脚本标为“未验证”。

## 已知问题

见 `HANDOFF.md` 的“已知问题，请先读”一节：5 个站没有电梯模型、补建的 9 个
站未经现场核实、161 St（B/D）几部电梯可用率只有约 50% 且原因未核实、坡道
数据老、实时数据无时区标记，等等。动手做 t1–t6 之前请先读那一节。

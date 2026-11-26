# 上游源文件对照表

`mods.toml` 的 `[upstream] local_roots = ["F:/games/MO2data/MYSSE/mods"]` 下手工核对的结果。
路径 = MO2 目录 + 文件，相对 `local_roots`；URL 直连，走 `127.0.0.1:7890` 代理；
指向 `.bsa` 时按条目的 `source` 路径从包内取（`check_upstream.py` 调 BSArch 解包）。
同一模组有多个源文件就多行；`mods.toml` 的 78 个 dir、107 个条目全部覆盖。
校对日期：2026-11-26。

## 已写入 `upstream`（91 条）

| 我们的 dir | 源文件（相对 `local_roots`） |
| --- | --- |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/Dawnguard_EN.txt` |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/Dragonborn_EN.txt` |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/Hearthfire_EN.txt` |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/SkyrimSE_EN.txt` |
| `menu_translation/achievement-injector` | `Achievement Injector/interface/translations/AchievementInjector_english.txt` |
| `menu_translation/bfco-ng` | `BFCO NG/SKSE/Plugins/BFCO NG/Language.json` |
| `menu_translation/classic-sprinting-redone` | `Classic Sprinting Redone (SKSE64)/interface/translations/ClassicSprintingRedone_ENGLISH.txt` |
| `menu_translation/cold-breath-ng` | `Cold Breath NG/SKSE/Plugins/ColdBreathNG_Translation.ini` |
| `menu_translation/dfg` | `Dynamic Forms Generator - DFG/Viny Mods/Dynamic Forms Generator/Language.json` |
| `menu_translation/dialogue-history` | `Dialogue History/interface/translations/DialogueHistory_ENGLISH.txt` |
| `menu_translation/dmenu` | `dMenu NG/SKSE/Plugins/dMenu/translations.txt` |
| `menu_translation/dmk` | `Directional Movement Keys - DMK/Viny Mods/DMK/Language.json` |
| `menu_translation/dodge-for-all` | `Dodge for all/SKSE/Plugins/Stats Tracker/Localization/DodgeAll.json` |
| `menu_translation/dodge-for-all` | `Dodge for all/Viny Mods/Dodge for all/Language.json` |
| `menu_translation/edf` | `Easy Distribution Framework - EDF/Viny Mods/EDF/Language.json` |
| `menu_translation/fitting-room` | `Fitting Room - ESO Style Transmog/interface/translations/Fitting Room_ENGLISH.txt` |
| `menu_translation/fuck` | `Fuzz's Legally Intelligible Core Kit/Interface/Translations/FUCK_ENGLISH.txt` |
| `menu_translation/fuck-qty` | `Selling of Stacks or Singles/Interface/Translations/FUCK-QTY_ENGLISH.txt` |
| `menu_translation/fuck-race` | `Racemenu Enhancer/Interface/Translations/FUCK-RACE_ENGLISH.txt` |
| `menu_translation/hand-guard` | `Hand Guard - Hand and Arm Clipping Fix for SexLab and OStim/SKSE/Plugins/SLHandGuardStrings_EN.json` |
| `menu_translation/hmdp` | `How many days passed - HMDP/SKSE/Plugins/Stats Tracker/Localization/HMDP.json` |
| `menu_translation/horsepower` | `HorsePower - Modernized Horse Riding/Interface/Translations/HorsePower_English.txt` |
| `menu_translation/hud-ng` | `HUD NG/SKSE/Plugins/HudNG/Translations/english.json` |
| `menu_translation/input-manager` | `Input Manager/Viny Mods/Input Manager/Language.json` |
| `menu_translation/journal-redesigned` | `Quest Journal Overhaul - Entire Journal Redesigned/interface/translations/Journal Redesigned_english.txt` |
| `menu_translation/just-a-block` | `Just a block/SKSE/Plugins/JusBlock_Language.json` |
| `menu_translation/kill-feed` | `Kill Feed/interface/translations/KillFeed_ENGLISH.txt` |
| `menu_translation/legendary-map-comap` | `Legendary Map - CoMAP Support and Some Improvements/interface/translations/Legendary Map_english.txt` |
| `menu_translation/load-time-profiler` | `Load Time Profiler/SKSE/Plugins/LoadTimeProfiler/Localization.json` |
| `menu_translation/log-watcher` | `Log Watcher - Real-time Analysis of SKSE Logs/SKSE/Plugins/LogWatcher/Translation/LogWatcherTranslation.json` |
| `menu_translation/map-menu-redesigned` | `Map Menu Redesigned/interface/translations/MapMenuRedesigned_english.txt` |
| `menu_translation/mcm-memory` | `MCM Memory - Settings Backup and Restore/SKSE/Plugins/MCMMemory/Translation/Translation.json` |
| `menu_translation/more-hud` | `moreHUD SE/AHZmoreHUD.bsa` |
| `menu_translation/more-ragdoll` | `More Ragdoll Control/Viny Mods/More Ragdoll/Language.json` |
| `menu_translation/my-precious` | `My Precious...es - Multiple Rings SKSE/interface/translations/MyPreciouses_ENGLISH.txt` |
| `menu_translation/my-precious` | `MyPreciouses - MCM Addon/MCM/Config/MyPreciouses/config.json` |
| `menu_translation/notification-tweaks` | `Notification Tweaks/interface/translations/NotificationTweaks_ENGLISH.txt` |
| `menu_translation/npc-senses` | `NPC Senses/Viny Mods/NPC Senses/Language.json` |
| `menu_translation/npc-stats-editor` | `NPC Stats Editor/Viny Mods/NPC Stats Editor/Language.json` |
| `menu_translation/nve` | `NPC Visual Editor - NVE/Viny Mods/NPC Visual/Language.json` |
| `menu_translation/obody-ng` | `OBody Next Generation/interface/translations/OBody_ENGLISH.txt` |
| `menu_translation/orbit-menu-ng` | `https://raw.githubusercontent.com/Abi822/Orbit-Menu-NG/main/lang/Orbit%20Menu%20Translation%20Example.json` |
| `menu_translation/ostim` | `OStim Standalone - Advanced Adult Animation Framework/interface/translations/OStim_ENGLISH.txt` |
| `menu_translation/parry-for-all` | `Parry for all/SKSE/Plugins/Stats Tracker/Localization/ParryAll.json` |
| `menu_translation/parry-for-all` | `Parry for all/Viny Mods/Parry for all/Language.json` |
| `menu_translation/pickup-radius` | `Pick Up Radius SKSE/SKSE/Plugins/PickUpRadiusSKSE_Translation.ini` |
| `menu_translation/quick-commands` | `Quick Commands/Viny Mods/Console Commands/Language.json` |
| `menu_translation/quick-item-transfer` | `Quick Item Transfer/interface/translations/Quick Item Transfer_english.txt` |
| `menu_translation/quicklootie` | `QuickLoot IE - A QuickLoot EE Fork/interface/translations/QuickLootIE_english.txt` |
| `menu_translation/reticle-arcs` | `Reticle Arcs/SKSE/Plugins/ReticleArcs/Translation.ini` |
| `menu_translation/riverwood-has-walls` | `Riverwood Has Walls - A Full Overhaul/interface/translations/Riverwood Has Walls_english.txt` |
| `menu_translation/show-player-in-inventory` | `Show Player In Inventory/Interface/Translations/ShowPlayerInInventory_ENGLISH.txt` |
| `menu_translation/skse-menu-framework` | `SKSE Menu Framework/SKSE/Plugins/SKSEMenuFrameworkStrings_EN.json` |
| `menu_translation/skyparkour` | `SkyParkour v3 - Procedural Parkour and Climbing Framework (SPPF)/interface/translations/SkyParkour_English.txt` |
| `menu_translation/skyprompt` | `SkyPrompt/interface/translations/SkyPrompt_ENGLISH.txt` |
| `menu_translation/start-menu-redesigned` | `Start Menu Redesigned/interface/translations/StartMenuRedesigned_english.txt` |
| `menu_translation/stats-tracker` | `Stats Tracker Menu - STM/SKSE/Plugins/Stats Tracker/Localization/STM_Localization.json` |
| `menu_translation/svg-and-png-icon-injector` | `SVG and PNG Icon Injector/SKSE/Plugins/Translations/PNGIconInjector_en.txt` |
| `menu_translation/tdm` | `True Directional Movement - Modernized Third Person Gameplay/interface/translations/TrueDirectionalMovement_english.txt` |
| `menu_translation/time-control` | `Time Control/Viny Mods/Time Control/Language.json` |
| `menu_translation/time-is-ticking` | `Time is Ticking/Viny Mods/Time is Ticking/Localization/en.json` |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/SKSE/Plugins/Stats Tracker/Localization/TrickDeath.json` |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/Viny Mods/Trick Death/Language.json` |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/Viny Mods/Trick Death/Localization/DeathMessages.json` |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/Viny Mods/Trick Death/Localization/en.json` |
| `other_translation/custom-markers` | `Custom Markers - Map - Mini Radar - Beacons/SKSE/Plugins/Translations/CustomMarkers_en.txt` |
| `other_translation/eslifer` | `https://raw.githubusercontent.com/MaskPlague/ESLifier/main/eslifier_translation.ts` |
| `other_translation/modex` | `Modex - A Mod Explorer Menu (AddItemMenu)/Interface/Modex/language/english.json` |
| `other_translation/music-conductor` | `Music Conductor/SKSE/Plugins/translations/MusicConductor_en.txt` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/AlchemyActivator.esp/SKMJPerk_dakalchemy.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Dynamic Activation Key - Addons Collection.esp/SKMJPerk_dakaddons.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/EatFromFlora.esp/SKMJPerk_eatfromflora.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Growl - Werebeasts of Skyrim.esp/SKMJPerk_growl.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Home Cloud Storage.esp/SKMJPerk_dakcloud.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Press E To Heal Followers.esp/SKMJPerk_etoheal.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Simple Hunting Overhaul.esp/SKMJPerk_simple hunting overhaul.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Take A Nap.esp/SKMJPerk_takeanap.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Take A Peek - New Stealth Mechanic.esp/SKMJPerk_takeapeekdsd.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/VampireFeedingTweaks.esp/SKMJPerk_vft.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/firstpersoninteractions.esp/SKMJPerk_fpinonaddon.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/immersiveinteractions.esp/SKMJPerk_immersiveinteractions.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/simplyknock.esp/SKMJPerk_skknockicon.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/skymoji.esp/SKMJPerk_skymojifurniture.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/skyrim.esm/SKMJ_skyrimvampfeed.json` |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/skyrim.esm/SKMJ_skyrimwolffeed.json` |
| `other_translation/outfit-distributor` | `Outfit Distributor SKSE/SKSE/Plugins/OutfitDist/Localization/en.json` |
| `other_translation/risas` | `Risas All In One Menu/SKSE/Plugins/RisaAllInOneMenu/Translations/en.json` |
| `other_translation/risas` | `Risas All In One Menu/SKSE/Plugins/RisaUI/Translations/en.json` |
| `other_translation/romantasy` | `Romantasy - An Elegant Romance System/Magelight/Romantasy/js/strings.js` |
| `other_translation/skyrim-party-sheet` | `Skyrim Party Sheet/SKSE/Plugins/translations/PartySheet_en.txt` |
| `other_translation/veldunui` | `Vel'dun UI/Interface/translations/skyui_se_english.txt` |

## 没有上游（16 条）

| 我们的 dir | 源文件（相对 `local_roots`） | 情况 |
| --- | --- | --- |
| `descriptionmods` | `*.ini` | 英文本就在仓库内，无上游 |
| `menu_translation/cee` | `interface/translations/Conditional Expressions_ENGLISH.txt` | 模组已删除（本机已无对应目录） |
| `menu_translation/feet-of-skyrim` | `interface/translations/FeetOfSkyrim_ENGLISH.txt` | 模组已删除（本机已无对应目录） |
| `menu_translation/hmdp` | `SKSE/Plugins/DaysPassed_Language.json` | 本机只有 `DaysPassed.dll`，无语言文件 |
| `menu_translation/inlos` | `Viny Mods/INLOS/Language.json` | 模组已删除（本机已无对应目录） |
| `menu_translation/ppa` | `SKSE/Plugins/ppa-translations/english.json` | 本机只有 `ppa-animation-tagging/*.json` |
| `menu_translation/press-f-to-pay-respects` | `SKSE/Plugins/PressFtoPayRespects_Translation.ini` | 模组已删除（本机已无对应目录） |
| `menu_translation/quick-swap` | `Viny Mods/Quick Swap/Language.json` | 模组目录已从本机移除 |
| `menu_translation/speed-of-strolling` | `interface/translations/styyx-move-speed_ENGLISH.txt` | 模组已删除（本机已无对应目录） |
| `menu_translation/swift-potion-ng` | `SKSE/Plugins/SwiftPotionNG_Translation.json` | 模组已删除（本机已无对应目录） |
| `menu_translation/unblockable-hits` | `SKSE/Plugins/Stats Tracker/Localization/UnblockableHits.json` | 模组目录已从本机移除 |
| `menu_translation/unblockable-hits` | `SKSE/Plugins/Unblock/Language.json` | 上游已取消（本地为旧版 33 键） |
| `menu_translation/undodgeable-hits` | `SKSE/Plugins/Stats Tracker/Localization/UndodgeableHits.json` | 模组目录已从本机移除 |
| `menu_translation/undodgeable-hits` | `SKSE/Plugins/Undodge/Language.json` | 上游已取消（本地为旧版 33 键） |
| `other_translation/new-skill-menu` | `Viny Mods/NSM/Localization/NSM_Language.json` | 模组已删除（本机已无对应目录） |
| `other_translation/smart-search` | `interface/translations/SmartSearch_en.ini` | 模组已删除（本机已无对应目录） |

## 校对发现

- `check_upstream.py --all --dry`：68 条一致、23 条字节有差异、0 条报错，全程约 6 秒。
- 23 条差异里 22 条只是缩进或 CRLF ↔ LF，JSON 规范化后内容完全一致（含 `my-precious` 的 `config.json`）。
- `pickup-radius`：上游多 4 个键（`ScriptedSlowdown*`、`ScriptedDelay*`），已同步并补译。
- `more-hud`：英文原件在 `moreHUD SE/AHZmoreHUD.bsa` 内，`upstream` 直接指 BSA；解包内容与仓库源字节一致。
- `oblivion-interaction-icons` 的 16 个 json 与 `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/` 下的副本字节一致，
  与 `[PATCH]Oblivion Interaction Icons` 版内容不同（本地多 `color='#989180'` 等属性），所以 `upstream` 按 Vel'dun UI 写。
- `music-conductor`：仓库布局已改为与上游一致（`SKSE/Plugins/translations/`），基线已用 `--sync --yes` 重建。

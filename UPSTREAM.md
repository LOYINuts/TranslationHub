# 上游源文件对照表

`mods.toml` 的 `[upstream] local_roots = ["F:/games/MO2data/MYSSE/mods"]` 下手工核对的结果。
`upstream` 写相对路径（MO2 目录 + 文件），按 `local_roots` 拼接；URL 直连，走 `127.0.0.1:7890` 代理。
一个（`dir`, 源文件）一行，一个模组有多个源文件就多行。校对日期：2026-11-26。

状态含义：**已写入** = `mods.toml` 已有 `upstream`；**待定** = 本机已确认路径但暂未写入；
**本机未找到** = 路径列是仓库里配置的源文件，本机没这台英文原件。

| 我们的 dir | upstream / 源文件（相对 `local_roots`） | 状态 |
| --- | --- | --- |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/Dawnguard_EN.txt` | 已写入 |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/Dragonborn_EN.txt` | 已写入 |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/Hearthfire_EN.txt` | 已写入 |
| `menu_translation/achievement-injector` | `Achievement Injector/SKSE/Plugins/AchievementsData/Localizations/SkyrimSE_EN.txt` | 已写入 |
| `menu_translation/achievement-injector` | `Achievement Injector/interface/translations/AchievementInjector_english.txt` | 已写入 |
| `menu_translation/bfco-ng` | `BFCO NG/SKSE/Plugins/BFCO NG/Language.json` | 已写入 |
| `menu_translation/classic-sprinting-redone` | `Classic Sprinting Redone (SKSE64)/interface/translations/ClassicSprintingRedone_ENGLISH.txt` | 已写入 |
| `menu_translation/cold-breath-ng` | `Cold Breath NG/SKSE/Plugins/ColdBreathNG_Translation.ini` | 已写入 |
| `menu_translation/dialogue-history` | `Dialogue History/interface/translations/DialogueHistory_ENGLISH.txt` | 已写入 |
| `menu_translation/dmenu` | `dMenu NG/SKSE/Plugins/dMenu/translations.txt` | 已写入 |
| `menu_translation/fitting-room` | `Fitting Room - ESO Style Transmog/interface/translations/Fitting Room_ENGLISH.txt` | 已写入 |
| `menu_translation/hand-guard` | `Hand Guard - Hand and Arm Clipping Fix for SexLab and OStim/SKSE/Plugins/SLHandGuardStrings_EN.json` | 已写入 |
| `menu_translation/horsepower` | `HorsePower - Modernized Horse Riding/Interface/Translations/HorsePower_English.txt` | 已写入 |
| `menu_translation/hud-ng` | `HUD NG/SKSE/Plugins/HudNG/Translations/english.json` | 已写入 |
| `menu_translation/journal-redesigned` | `Quest Journal Overhaul - Entire Journal Redesigned/interface/translations/Journal Redesigned_english.txt` | 已写入 |
| `menu_translation/just-a-block` | `Just a block/SKSE/Plugins/JusBlock_Language.json` | 已写入 |
| `menu_translation/kill-feed` | `Kill Feed/interface/translations/KillFeed_ENGLISH.txt` | 已写入 |
| `menu_translation/legendary-map-comap` | `Legendary Map - CoMAP Support and Some Improvements/interface/translations/Legendary Map_english.txt` | 已写入 |
| `menu_translation/load-time-profiler` | `Load Time Profiler/SKSE/Plugins/LoadTimeProfiler/Localization.json` | 已写入 |
| `menu_translation/log-watcher` | `Log Watcher - Real-time Analysis of SKSE Logs/SKSE/Plugins/LogWatcher/Translation/LogWatcherTranslation.json` | 已写入 |
| `menu_translation/map-menu-redesigned` | `Map Menu Redesigned/interface/translations/MapMenuRedesigned_english.txt` | 已写入 |
| `menu_translation/mcm-memory` | `MCM Memory - Settings Backup and Restore/SKSE/Plugins/MCMMemory/Translation/Translation.json` | 已写入 |
| `menu_translation/my-precious` | `My Precious...es - Multiple Rings SKSE/interface/translations/MyPreciouses_ENGLISH.txt` | 已写入 |
| `menu_translation/notification-tweaks` | `Notification Tweaks/interface/translations/NotificationTweaks_ENGLISH.txt` | 已写入 |
| `menu_translation/obody-ng` | `OBody Next Generation/interface/translations/OBody_ENGLISH.txt` | 已写入 |
| `menu_translation/orbit-menu-ng` | `https://raw.githubusercontent.com/Abi822/Orbit-Menu-NG/main/lang/Orbit%20Menu%20Translation%20Example.json` | 已写入 |
| `menu_translation/ostim` | `OStim Standalone - Advanced Adult Animation Framework/interface/translations/OStim_ENGLISH.txt` | 已写入 |
| `menu_translation/pickup-radius` | `Pick Up Radius SKSE/SKSE/Plugins/PickUpRadiusSKSE_Translation.ini` | 已写入 |
| `menu_translation/quick-item-transfer` | `Quick Item Transfer/interface/translations/Quick Item Transfer_english.txt` | 已写入 |
| `menu_translation/quicklootie` | `QuickLoot IE - A QuickLoot EE Fork/interface/translations/QuickLootIE_english.txt` | 已写入 |
| `menu_translation/reticle-arcs` | `Reticle Arcs/SKSE/Plugins/ReticleArcs/Translation.ini` | 已写入 |
| `menu_translation/riverwood-has-walls` | `Riverwood Has Walls - A Full Overhaul/interface/translations/Riverwood Has Walls_english.txt` | 已写入 |
| `menu_translation/skse-menu-framework` | `SKSE Menu Framework/SKSE/Plugins/SKSEMenuFrameworkStrings_EN.json` | 已写入 |
| `menu_translation/skyparkour` | `SkyParkour v3 - Procedural Parkour and Climbing Framework (SPPF)/interface/translations/SkyParkour_English.txt` | 已写入 |
| `menu_translation/skyprompt` | `SkyPrompt/interface/translations/SkyPrompt_ENGLISH.txt` | 已写入 |
| `menu_translation/start-menu-redesigned` | `Start Menu Redesigned/interface/translations/StartMenuRedesigned_english.txt` | 已写入 |
| `menu_translation/stats-tracker` | `Stats Tracker Menu - STM/SKSE/Plugins/Stats Tracker/Localization/STM_Localization.json` | 已写入 |
| `menu_translation/svg-and-png-icon-injector` | `SVG and PNG Icon Injector/SKSE/Plugins/Translations/PNGIconInjector_en.txt` | 已写入 |
| `menu_translation/tdm` | `True Directional Movement - Modernized Third Person Gameplay/interface/translations/TrueDirectionalMovement_english.txt` | 已写入 |
| `other_translation/custom-markers` | `Custom Markers - Map - Mini Radar - Beacons/SKSE/Plugins/Translations/CustomMarkers_en.txt` | 已写入 |
| `other_translation/eslifer` | `https://raw.githubusercontent.com/MaskPlague/ESLifier/main/eslifier_translation.ts` | 已写入 |
| `other_translation/modex` | `Modex - A Mod Explorer Menu (AddItemMenu)/Interface/Modex/language/english.json` | 已写入 |
| `other_translation/music-conductor` | `Music Conductor/SKSE/Plugins/translations/MusicConductor_en.txt` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/AlchemyActivator.esp/SKMJPerk_dakalchemy.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Dynamic Activation Key - Addons Collection.esp/SKMJPerk_dakaddons.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/EatFromFlora.esp/SKMJPerk_eatfromflora.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Growl - Werebeasts of Skyrim.esp/SKMJPerk_growl.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Home Cloud Storage.esp/SKMJPerk_dakcloud.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Press E To Heal Followers.esp/SKMJPerk_etoheal.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Simple Hunting Overhaul.esp/SKMJPerk_simple hunting overhaul.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Take A Nap.esp/SKMJPerk_takeanap.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/Take A Peek - New Stealth Mechanic.esp/SKMJPerk_takeapeekdsd.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/VampireFeedingTweaks.esp/SKMJPerk_vft.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/firstpersoninteractions.esp/SKMJPerk_fpinonaddon.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/immersiveinteractions.esp/SKMJPerk_immersiveinteractions.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/simplyknock.esp/SKMJPerk_skknockicon.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/skymoji.esp/SKMJPerk_skymojifurniture.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/skyrim.esm/SKMJ_skyrimvampfeed.json` | 已写入 |
| `other_translation/oblivion-interaction-icons` | `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/skyrim.esm/SKMJ_skyrimwolffeed.json` | 已写入 |
| `other_translation/outfit-distributor` | `Outfit Distributor SKSE/SKSE/Plugins/OutfitDist/Localization/en.json` | 已写入 |
| `other_translation/romantasy` | `Romantasy - An Elegant Romance System/Magelight/Romantasy/js/strings.js` | 已写入 |
| `other_translation/skyrim-party-sheet` | `Skyrim Party Sheet/SKSE/Plugins/translations/PartySheet_en.txt` | 已写入 |
| `menu_translation/dfg` | `Dynamic Forms Generator - DFG/Viny Mods/Dynamic Forms Generator/Language.json` | 待定 |
| `menu_translation/dmk` | `Directional Movement Keys - DMK/Viny Mods/DMK/Language.json` | 待定 |
| `menu_translation/dodge-for-all` | `Dodge for all/SKSE/Plugins/Stats Tracker/Localization/DodgeAll.json` | 待定 |
| `menu_translation/dodge-for-all` | `Dodge for all/Viny Mods/Dodge for all/Language.json` | 待定 |
| `menu_translation/edf` | `Easy Distribution Framework - EDF/Viny Mods/EDF/Language.json` | 待定 |
| `menu_translation/hmdp` | `How many days passed - HMDP/SKSE/Plugins/Stats Tracker/Localization/HMDP.json` | 待定 |
| `menu_translation/input-manager` | `Input Manager/Viny Mods/Input Manager/Language.json` | 待定 |
| `menu_translation/more-ragdoll` | `More Ragdoll Control/Viny Mods/More Ragdoll/Language.json` | 待定 |
| `menu_translation/npc-senses` | `NPC Senses/Viny Mods/NPC Senses/Language.json` | 待定 |
| `menu_translation/npc-stats-editor` | `NPC Stats Editor/Viny Mods/NPC Stats Editor/Language.json` | 待定 |
| `menu_translation/nve` | `NPC Visual Editor - NVE/Viny Mods/NPC Visual/Language.json` | 待定 |
| `menu_translation/parry-for-all` | `Parry for all/SKSE/Plugins/Stats Tracker/Localization/ParryAll.json` | 待定 |
| `menu_translation/parry-for-all` | `Parry for all/Viny Mods/Parry for all/Language.json` | 待定 |
| `menu_translation/quick-commands` | `Quick Commands/Viny Mods/Console Commands/Language.json` | 待定 |
| `menu_translation/quick-swap` | `Quick Swap/Viny Mods/Quick Swap/Language.json` | 待定 |
| `menu_translation/time-control` | `Time Control/Viny Mods/Time Control/Language.json` | 待定 |
| `menu_translation/time-is-ticking` | `Time is Ticking/Viny Mods/Time is Ticking/Localization/en.json` | 待定 |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/SKSE/Plugins/Stats Tracker/Localization/TrickDeath.json` | 待定 |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/Viny Mods/Trick Death/Language.json` | 待定 |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/Viny Mods/Trick Death/Localization/DeathMessages.json` | 待定 |
| `menu_translation/trick-death` | `Trick Death - A checkpoint and respawn system/Viny Mods/Trick Death/Localization/en.json` | 待定 |
| `menu_translation/unblockable-hits` | `Unblockable Hits/SKSE/Plugins/Stats Tracker/Localization/UnblockableHits.json` | 待定 |
| `menu_translation/undodgeable-hits` | `Undodgeable Hits/SKSE/Plugins/Stats Tracker/Localization/UndodgeableHits.json` | 待定 |
| `menu_translation/cee` | `interface/translations/Conditional Expressions_ENGLISH.txt` | 本机未找到：无对应模组目录 |
| `menu_translation/feet-of-skyrim` | `interface/translations/FeetOfSkyrim_ENGLISH.txt` | 本机未找到：无对应模组目录 |
| `menu_translation/fuck` | `interface/translations/FUCK_ENGLISH.txt` | 本机未找到：无对应模组目录 |
| `menu_translation/fuck-qty` | `interface/translations/FUCK-QTY_ENGLISH.txt` | 本机未找到：无对应模组目录 |
| `menu_translation/fuck-race` | `interface/translations/FUCK-RACE_ENGLISH.txt` | 本机未找到：无对应模组目录 |
| `menu_translation/hmdp` | `SKSE/Plugins/DaysPassed_Language.json` | 本机未找到：只有 `DaysPassed.dll` |
| `menu_translation/inlos` | `Viny Mods/INLOS/Language.json` | 本机未找到：`Viny Mods/INLOS` 不存在 |
| `menu_translation/more-hud` | `interface/translations/ahzmorehud_english.txt` | 本机未找到：`moreHUD SE` 内没有英文 txt，估计在 BSA 里 |
| `menu_translation/my-precious` | `interface/translations/config.json` | 本机未找到：同目录只有 `MyPreciouses_ENGLISH.txt` |
| `menu_translation/new-skill-menu` | `Viny Mods/NSM/Localization/NSM_Language.json` | 本机未找到：`Viny Mods/NSM` 不存在 |
| `menu_translation/ppa` | `SKSE/Plugins/ppa-translations/english.json` | 本机未找到：只有 `ppa-animation-tagging/*.json` |
| `menu_translation/press-f-to-pay-respects` | `SKSE/Plugins/PressFtoPayRespects_Translation.ini` | 本机未找到：无对应模组目录 |
| `menu_translation/show-player-in-inventory` | `interface/translations/ShowPlayerInInventory_ENGLISH.txt` | 本机未找到：未核对 |
| `menu_translation/speed-of-strolling` | `interface/translations/styyx-move-speed_ENGLISH.txt` | 本机未找到：文件不存在 |
| `menu_translation/swift-potion-ng` | `SKSE/Plugins/SwiftPotionNG_Translation.json` | 本机未找到：文件不存在 |
| `menu_translation/unblockable-hits` | `SKSE/Plugins/Unblock/Language.json` | 本机未找到：只有 BDI 的 json |
| `menu_translation/undodgeable-hits` | `SKSE/Plugins/Undodge/Language.json` | 本机未找到：只有 BDI 的 json |
| `other_translation/smart-search` | `interface/translations/SmartSearch_en.ini` | 本机未找到：无对应模组目录 |

## 校对发现

- `check_upstream.py --all --dry`：57 条一致、5 条有差异、0 条报错。
- `just-a-block`、`mcm-memory`、`log-watcher`、`bfco-ng`：整文件差异只是 CRLF ↔ LF，内容一致。
- `pickup-radius`：上游多 4 个键（`ScriptedSlowdown*`、`ScriptedDelay*`），待同步。
- `oblivion-interaction-icons` 的 16 个 json 与 `Vel'dun UI/SKSE/Plugins/DynamicStringDistributor/` 下的副本字节一致，
  与 `[PATCH]Oblivion Interaction Icons` 版内容不同（本地多 `color='#989180'` 等属性），所以 `upstream` 按 Vel'dun UI 写。
- `music-conductor`：仓库布局已改为与上游一致（`SKSE/Plugins/translations/`），基线已用 `--sync --yes` 重建。
- `unblockable-hits`、`undodgeable-hits` 另有 `SKSE/Plugins/Stats Tracker/Rules/*.json`，未纳入配置。

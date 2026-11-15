// Every word the page shows, in one table: key on the left, text on the right. To translate the page, copy this
// file, change only the text on the right of each line, keep every {place} (the page fills it with a name or a
// number), and ship the copy at the same path. Keys are dotted lower case, area first.
// A text that contains an apostrophe goes in double quotes, as settings.title does.
//
// Two keys for a word that changes with a count: ".one" for exactly one, ".many" for every other number.
// Tier names (tier.1 to tier.6) also stand in for the names the plugin sends; a deed's label can be given as
// deed.<its editor ID> (for example deed.ROM_LocationsDiscovered); without that line the plugin's own label shows.
// A key missing here shows as [key] and is logged once to the page console.
//
// t(key, values): the text with its {places} filled from values (as text; the page escapes it where it draws it).
// or(key, fallback): the table's text, or fallback (the plugin's own words) when the table has no line for the key.
// Dual-use: Node requires it for the tests.
(function () {
    'use strict';
    const table = {
        'brand.title': 'Romantasy',

        'common.companion': '同伴',
        'common.newbond': '新羁绊',
        'common.deepens': '加深羁绊',
        'common.wounds': '伤害羁绊',
        'common.favorite': '喜好',
        'common.peeve': '忌讳',
        'common.cancel': '取消',
        'common.back': '返回',

        'tier.1': '陌生人',
        'tier.2': '相识',
        'tier.3': '朋友',
        'tier.4': '知己',
        'tier.5': '恋人',
        'tier.6': '配偶',

        'roster.company': '你的队伍',
        'roster.count.one': '{count} 段羁绊',
        'roster.count.many': '{count} 段羁绊',
        'roster.following.one': '· {count} 位随行',
        'roster.following.many': '· {count} 位随行',
        'roster.find': '寻找同伴',
        'roster.find.clear': '清除',
        'roster.order.label': '排序',
        'roster.order.closest': '距离最近',
        'roster.order.name': '姓名',
        'roster.order.recent': '最近变动',
        'roster.group.following': '随行中',
        'roster.group.away': '不随行',
        'roster.row.away': '不随行',
        'roster.nobody': '没有叫这个名字的人。',
        'roster.settings': '设置',
        'roster.health': '状态：{status}',
        'roster.refresh': '刷新',
        'roster.close': '关闭',

        'dossier.following': '随行中',
        'dossier.away': '不随行',
        'dossier.edit': '编辑性格',
        'dossier.reset': '重置羁绊',
        'dossier.remove': '移除羁绊',
        'dossier.bond': '羁绊',
        'dossier.bond.of': '/ {points} 羁绊',
        'dossier.complete': '羁绊圆满',
        'dossier.until': '距 {tier} 还差 {points}',
        'dossier.gate': '{tier} 需要相处 {needed} 天（目前 {sofar} 天）',

        'mood.warm': '热络',
        'mood.warm.title': '热络：最近几天相处得很好。',
        'mood.settled': '平稳',
        'mood.settled.title': '平稳：最近没有影响羁绊的事。',
        'mood.strained': '紧张',
        'mood.strained.title': '紧张：最近几天伤了羁绊。',

        'values.title': '他们在意什么',
        'values.none.likes': '没有记录喜好。',
        'values.none.dislikes': '没有记录忌讳。',

        'recent.title': '最近变动',
        'recent.none': '最近没有变动。',
        'recent.journal': '日志',

        'persona.title': '性格',
        'persona.configured': '已配置的性格',
        'persona.configured.line': '已从 {file} 载入偏好。',
        'persona.player': '玩家创建的性格',
        'persona.player.line': '这一页属于你。它的喜好与忌讳可以重写。',
        'persona.author': '作者定义的性格',
        'persona.author.line': '由随从作者封存。Romantasy 不会改动或移除。',
        'persona.author.line.plugin': '由随从作者在 {plugin} 中封存。Romantasy 不会改动或移除。',
        'persona.managed': '受管理的性格',
        'persona.managed.line': '运行时由另一个兼容模组提供。Romantasy 视其为只读。',
        'persona.plugin': '来源插件',
        'persona.file': '配置文件',

        'miles.title': '里程碑',
        'miles.unlocks': '{tier} 解锁：',

        'empty.away': '所有羁绊同伴都不在随行。请在设置中开启“显示不随行的同伴”来查看。',
        'empty.none': '还没有任何羁绊。选择一位同伴开始。',
        'empty.settings': '设置',

        'settings.eyebrow': '封印之页',
        'settings.title': "抄写员的羽毛笔",
        'settings.favorites': '用收藏菜单打开',
        'settings.favorites.detail': '关：用左 Ctrl + R 打开。开：从收藏菜单施放 Romantasy 能力，快捷键停用。',
        'settings.gain': '“情意加深”弹窗',
        'settings.gain.detail': '当羁绊向上跨过某一阶时显示金色弹窗。',
        'settings.loss': '“情意受损”弹窗',
        'settings.loss.detail': '当羁绊跌落到某一阶以下时显示玫瑰色弹窗。',
        'settings.away': '显示不随行的同伴',
        'settings.away.detail': '即使不在随行，也把羁绊留在名册里。',
        'settings.whispers': '低语',
        'settings.whispers.detail': '同伴有所反应时，在 HUD 上显示小提示。它们不会暂停游戏。',
        'settings.contrast': '更高对比度',
        'settings.contrast.detail': '更亮的文字、实色面板与更粗的描边。',
        'settings.motion': '减少动效',
        'settings.motion.detail': '停止漂移的背景与较大的动画。',
        'settings.log': '详细日志',
        'settings.log.detail': '把每次点数变动写入 Romantasy.log。供模组作者与错误回报使用。',
        'settings.dev': '开发者工具',
        'settings.dev.detail': '显示测试工具。启用时需要输入密码。',
        'settings.skyrimnet.bridge': '把羁绊告知 SkyrimNet',
        'settings.skyrimnet.bridge.detail': "把每位同伴的羁绊加入 SkyrimNet 已知的内容，并向它报告阶位变化。",
        'settings.skyrimnet.conversation': '对话可以推动羁绊',
        'settings.skyrimnet.conversation.detail': "让 SkyrimNet 的 AI 因一句好话或重话推动几点羁绊。每天有上限。",
        'settings.ostim.moments': '共处时刻',
        'settings.ostim.moments.detail': '与同伴在 OStim 场景中独处，每天一次，会为羁绊加一点。',
        'settings.ostim.hold': '场景中保持安静',
        'settings.ostim.hold.detail': '阶位变化与低语会等到 OStim 场景结束后。',
        'settings.moment': '阶位变化的时机',
        'settings.moment.calm': '在宁静时刻',
        'settings.moment.immediate': '立即',
        'settings.moment.detail': '宁静时刻指旅店、家中、城镇里，或睡醒之后。任何变化都不会等超过一天。',
        'settings.pace': '关系推进速度',
        'settings.pace.slow': '慢热',
        'settings.pace.standard': '标准',
        'settings.pace.fast': '快速',
        'settings.pace.detail': '快速让事迹点数翻倍。慢热把点数减半，并且每升一阶都需要先相处满若干天。损失永远不受影响。',
        'settings.corner': '低语角落',
        'settings.corner.topleft': '左上',
        'settings.corner.topright': '右上',
        'settings.corner.bottomleft': '左下',
        'settings.corner.bottomright': '右下',
        'settings.size': '名册尺寸',
        'settings.size.standard': '标准',
        'settings.size.large': '大',
        'settings.size.largest': '最大',
        'settings.size.detail': '让名册里的一切都变大。',

        'dev.title': '开发者工具',
        'dev.note': '测试工具。调整点数与模拟事迹只影响正在随行的同伴。',
        'dev.bond.up': '羁绊 +500',
        'dev.bond.down': '羁绊 −500',
        'dev.sidequest': '支线任务 +1',
        'dev.murder': '谋杀 +1',
        'dev.refresh': '刷新',

        'health.title': '诊断',
        'health.ok': '一切正常。',
        'health.word.error': '问题',
        'health.word.warn': '待查',
        'health.meta.plugin': 'Romantasy',
        'health.meta.plugin.version': 'Romantasy {version}',
        'health.meta.host': 'Magelight 界面 {version}',
        'health.meta.bonds.one': '{count} 段羁绊',
        'health.meta.bonds.many': '{count} 段羁绊',

        'enroll.create.eyebrow': '新羁绊',
        'enroll.create.title': '建立一段新羁绊',
        'enroll.create.copy': '选择一位 Romantasy 还不认识的同伴，然后盖印那些加深或伤害羁绊的事迹。',
        'enroll.create.commit': '建立羁绊',
        'enroll.edit.eyebrow': '玩家创建的性格',
        'enroll.edit.title': '重写这一页',
        'enroll.edit.copy': '只有你写下的页可以重写。由随从模组提供的性格依然受保护。',
        'enroll.edit.commit': '封印性格',
        'enroll.note': '这段羁绊会与此存档一同保存。新角色开始时会有它的性格副本。',
        'enroll.sub': '每项事迹初始都是中立。把他们看重的盖上印记。',
        'enroll.hint': '在封页之前不会有任何改动。',
        'enroll.companion': '同伴',
        'enroll.notfound': '找不到该羁绊',
        'enroll.notfound.copy': '这位同伴已不在名册中。',
        'enroll.nocandidates': '目前没有可加入的同伴。先招募一位随从，再试一次。',
        'enroll.nodeeds': '没有可用的事迹。',
        'enroll.nomatch': '没有与“{query}”相符的事迹。',
        'enroll.deeds': '喜好与忌讳',
        'enroll.search': '搜索事迹',
        'enroll.category.other': '其他',
        'enroll.neutral': '中立',
        'enroll.cap.favorites': '最多三项喜好。',
        'enroll.cap.peeves': '最多三项忌讳。',
        'enroll.chips.none': '还没有盖过印。',
        'enroll.deeds.one': '{count} 项事迹',
        'enroll.deeds.many': '{count} 项事迹',

        'modal.eyebrow': '玩家创建的羁绊',
        'modal.reset.title': '重置这段羁绊？',
        'modal.reset.button': '重置羁绊',
        'modal.reset.body': "性格会保留。这位同伴的点数与最近历史只会在当前存档中重置。",
        'modal.remove.title': '移除这段羁绊？',
        'modal.remove.button': '移除羁绊',
        'modal.remove.body': '这只会从当前存档中移除这段羁绊，其他存档不受影响。由随从模组提供的性格依然受保护。',
        'modal.password.eyebrow': '受限',
        'modal.password.title': '开发者工具',
        'modal.password.note': '这些工具可以改写所有羁绊。输入密码以解锁。',
        'modal.password.field': '密码',
        'modal.password.error': '封印不认这个密码。',
        'modal.password.unlock': '解锁',

        'popup.gain': '情意加深',
        'popup.loss': '情意受损',
        'popup.unlocked': '已解锁',
        'popup.points': '{points} 点',
        'popup.next': '下一阶：{tier}',
        'popup.continue': '继续',

        'journal.title': '日志',
        'journal.opening': '正在打开日志……',
        'journal.failed': '无法打开日志。',
        'journal.empty': '这里还什么都没写。',
        'journal.since': '自第 {day} 天起 · {together}',
        'journal.together.one': '共处 {days} 天',
        'journal.together.many': '共处 {days} 天',
        'journal.milestones': '里程碑',
        'journal.milestone': '第 {day} 天 · {what}',
        'journal.began': '日志开始',
        'journal.reached': '达到 {tier}',
        'journal.fell': '跌至 {tier}',
        'journal.shared': '初次共处',
        'journal.chart': '最近六十天',
        'journal.chart.tip': '第 {day} 天：+{gained}，−{lost}',
        'journal.chart.totals': '获得 {gained} · 失去 {lost}',
        'journal.day': '第 {day} 天',
        'journal.moments': '最深刻的时刻',
        'journal.moments.gains': '加深最多',
        'journal.moments.losses': '伤害最多',
        'journal.moments.none': '还没有。',
        'journal.history': '历史',

        'legend.select': '选择',
        'legend.open': '打开',
        'legend.close': '关闭',
        'legend.back': '返回',
        'legend.scroll': '滚动',
        'legend.stamp': '盖印',
        'legend.cancel': '取消',
        'legend.confirm': '确认',
        'legend.continue': '继续',
        'legend.key.enter': '回车',
        'legend.key.esc': 'Esc',
        'legend.pad.up': '十字键 上',
        'legend.pad.down': '十字键 下',
        'legend.pad.updown': '十字键 ↑↓'
    };

    const has = key => typeof key === 'string' && Object.prototype.hasOwnProperty.call(table, key);
    const logged = {};

    // Each {place} with a value of that name in values; a place with no value stays as written. A table value that
    // is not a string (a hand edit gone wrong) is filled in its string form, never thrown on.
    function fill(text, values) {
        if (!values || typeof values !== 'object') return text;
        return String(text).replace(/\{(\w+)\}/g, (place, name) => Object.prototype.hasOwnProperty.call(values, name) ? String(values[name]) : place);
    }

    function t(key, values) {
        if (has(key)) return fill(table[key], values);
        const shown = '[' + String(key) + ']';
        if (!logged[shown]) {
            logged[shown] = true;
            if (typeof console === 'object' && console && typeof console.warn === 'function') console.warn('Romantasy: strings.js has no text for ' + shown);
        }
        return shown;
    }

    const or = (key, fallback) => has(key) ? table[key] : fallback;

    const api = { t, or, table };
    if (typeof module === 'object' && module.exports) { module.exports = api; return; }
    window.RM = window.RM || {};
    window.RM.strings = api;
})();

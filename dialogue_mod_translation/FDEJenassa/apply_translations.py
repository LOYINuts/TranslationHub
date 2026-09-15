"""Apply translations to the XML file. All translations are manually provided."""
import os
import re

XML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FDE Jenassa Part 2_20F57570.xml")

with open(XML_PATH, 'r', encoding='utf-8-sig') as f:
    content = f.read()
translations = {
    # === aaJenassaNtC (战斗触发 - Anger) ===
    "I will enjoy spilling your blood!": "我会很享受让你血流成河的！",
    "You'll cower in the shadows!": "你只配缩在阴影里发抖！",
    "Know fear, weakling!": "尝尝恐惧的滋味吧，废物！",
    "Another life to extinguish!": "又一条命，该熄灭了。",

    # === aaJenassaCtN (击杀 - Neutral) ===
    "Embrace silence.": "拥抱沉默吧。",
    "Now, you feel the cold grip of death.": "现在，你该感受到死亡冰冷的拥抱了。",

    # === aaJenassaAmorBackground3ai (东帝国公司背景) ===
    "What did the East Empire Company have to do with this?": "东帝国公司和这件事有什么关系？",
    "They were recruiting able hands to secure their business. At the time, the Empire's ships were occupied by the battles at the Abecean Sea.": "他们在招募能干的人手来保障生意。那时帝国的舰船正忙于阿碧希恩海的战事。",
    "Without the Imperials to purge them, pirates grew rampant in the far north, raiding and sinking the East Empire Company's vessels.": "没有帝国舰队清剿，海盗在极北之地越发猖獗，不断袭击和击沉东帝国公司的船只。",
    "They needed a veteran fighter who's familiar with the underworlds of both Skyrim and Morrowind, and that's where they saw the value in my service.": "他们需要一个熟悉天际和晨风两地地下世界的老兵——这就是他们看中我的地方。",
    "So they paid off my fine and purchased my freedom. Although to be more precise, I had merely exchanged the executioner's axe for a golden shackle.": "于是他们替我缴清了罚金，买来了我的自由。不过说得准确些——我只是把刽子手的斧头换成了一副金色的镣铐。",
    "An improvement, nonetheless.": "不过总归是进步了。",

    # === aaJenassaAmorBackground3ai3 ===
    "I suppose you've already fulfilled your end of the bargain.": "我猜你已经履行完你那边的协议了吧。",
    "As if it's ever so easy to shake off those goldmongers.": "好像摆脱那些财迷是那么容易的事似的。",
    "My service is still required from time to time. Usually when they need someone to get their hands dirty.": "他们时不时还需要我的服务。通常是需要有人替他们干脏活的时候。",
    "I do get paid, of course, but it's little more than pocket money.": "当然，他们确实付钱，但那点钱跟零花钱没什么两样。",
    "\"To offset the fine they've helped me pay,\" they say. Hmph.": "\"用来抵消他们帮我付的罚金。\"他们这么说。哼。",

    # === aaJenassaAmorBackground3ai3c ===
    "Does that interfere with your mercenary work with me?": "那会影响你跟着我做的雇佣工作吗？",
    "I am well-versed in the art of multi-tasking.": "我对多线操作这门艺术颇有心得。",
    "In truth, some of the bandit camps you come across just might number among my targets.": "事实上，你碰到的那些强盗营地当中，有几个可能就是我的目标。",
    "A goldmonger has no lack of enemies, after all. A bandit here, a Forsworn there... A mercenary's work is never done.": "毕竟，一个财迷从来不缺敌人。这里一个强盗，那里一个弃誓者……雇佣兵的活是干不完的。",

    # === aaJenassaAmor3CW3 (内战 - 风暴斗篷) ===
    "Do you think I made the wrong choice, helping the Stormcloaks?": "你觉得我帮风暴斗篷是选错了吗？",
    "I think it's quite obvious.": "我觉得这答案显而易见了。",
    "But whichever side you're loyal to, I am bound by my contract to fight by your side.": "但无论你效忠于哪一边，合同在身，我都会在你身边战斗。",
    "Doesn't mean I have to like what my blade is being used for.": "但这不代表我得喜欢我的剑被用来做什么。",

    # === aaJenassaAmorQTopic ===
    "I'd like to ask you something.": "我想问你点事。",

    # === aaJenassaAmor5Mercenary3 (雇佣兵哲学) ===
    "Do you like being a mercenary then?": "那你喜欢当雇佣兵吗？",
    "I appreciate the art of death, and I never resent the gold. The rest is only a means to an end.": "我欣赏死亡的艺术，也从不嫌弃金币。其余的一切只是达到目的的手段罢了。",
    "Even if there comes a day where I need not worry about food and bed, I think I might still hunt the occasional bandits, just to scratch that itch.": "就算有朝一日我不必为吃住发愁，我想我偶尔还是会去猎杀几个强盗——就为了解解痒。",

    # === aaJenassa6MarriageTaunt (婚后催促) ===
    "Come on. We still have battles to fight.": "走吧。我们还有仗要打。",
    "Let's go. There's still much to do.": "走吧。还有好多事要做。",
    "I wonder if you dreamt of me.": "我好奇你有没有梦到我。",
    "I barely got any rest at all.": "我几乎没怎么休息。",
    "Think we woke a Draugr or two while we were 'resting'?": "你说我们'休息'的时候，是不是吵醒了一两个尸鬼？",

    # === aaJenassa6IdleIdle (美景感叹) ===
    "Three Daedra above - what a sight!": "三大魔神在上——真是壮观！",
    "I didn't realize such a place existed... Yet it does.": "我不知道还有这样的地方存在……但它确实在这里。",
    "There's beauty to be appreciated everywhere.": "美丽无处不在，值得细细品味。",
    "Such views are meant for worthy eyes.": "这样的风景，就该配上有资格欣赏的眼睛。",
    "The creators of this place know their art well.": "这地方的建造者深谙他们自己的艺术。",

    # === aaJenassa8Shop0 (开店对话) ===
    "Can you tell me something about your store?": "能跟我说说你的店吗？",
    "Well - I've mostly been selling blades, arrows and traveling gear. Some I crafted, the others I bought from other artisans.": "嗯——我主要卖刀剑、箭矢和旅行装备。有些是我自己打造的，有些是从其他工匠那里买来的。",
    "There are quite a few customers who keep returning, so business is good.": "有不少回头客，所以生意还不错。",

    # === aaJenassa8Shop1 ===
    "Do you know why?": "你知道为什么吗？",
    "Let's just say my customers always get what they need in my store, as long as it concerns the art of death.": "这么说吧——只要关乎死亡的艺术，我的顾客总能在我的店里找到他们需要的东西。",
    "I spent years as a sellsword in all manners of warfare, and I know what serves me best in any situation.": "我当了多年的雇佣兵，经历过各种战事，我知道在任何情况下什么最适合自己。",
    "What I sell is not just weapon, but also decades of wisdom.": "我卖的不仅仅是武器，还有几十年的智慧。",

    # === aaJenassa8Shop2 ===
    "Do you like running a store, instead of being a sellsword?": "你喜欢开店胜过当雇佣兵吗？",
    "Well, if I could, of course I prefer making art myself.": "嗯，如果可以的话，我当然更愿意亲手创造艺术。",
    "But since you need me to stay at home, helping others make art will have to suffice.": "但既然你需要我留在家里，帮别人创造艺术也只好将就了。",

    # === aaJenassa8zExit0 ===
    "Let's talk about something else.": "我们聊点别的吧。",

    # === aaJenassa8Idle (任务评论 - 按顺序) ===
    # 安息者墓穴
    "A death cult rules this tomb. We should silence them forever.": "死灵教派统治着这座墓穴。我们应该让他们永远安静。",
    "These necromancers toy with Death... They'll soon meet that which they think they master.": "这些死灵法师在玩弄死亡……他们很快就会与自认为掌控的东西面对面了。",
    # 红卫死灵法师
    "I wonder what drove that necromancer down this path. The Redguards hate the undead even more so than my kind.": "我在想是什么驱使那个死灵法师走上这条路。红卫人比我们暗精灵更憎恨亡灵。",
    "I can understand the Redguard necromancer. She'd bring down those who watched condescendingly as her beloved died.": "我能理解那个红卫死灵法师。她要毁掉那些居高临下看着她爱人死去的人。",
    "The necromancer's vengeance might be righteous, but her means had led to nothing but death... Let's leave this tomb behind.": "死灵法师的复仇或许是正义的，但她的手段带来的只有死亡……我们离开这座墓穴吧。",
    # 乌鸦岩 - 灰烬魔怪
    "It seems the Redoran Guards are crumbling to the Ash Spawn attacks. Raven Rock won't be the first city to be buried in ash, nor will it be the last.": "看来瑞多然卫兵在灰烬魔怪的攻击下节节败退。乌鸦岩不会是第一个被灰烬掩埋的城市，也不会是最后一个。",
    "These \"Ash Spawn\" are unlike anything I've seen back on the mainland. I suspect dark arts are involved in their creation.": "这些\"灰烬魔怪\"跟我在大陆上见过的任何东西都不一样。我怀疑它们的诞生涉及黑暗法术。",
    "I've seen the Imperials use criminals and Daedra, even undead when they're desperate - but an army of ashen monsters just might be the first.": "我见过帝国在绝望时使用罪犯、魔族，甚至亡灵——但一支灰烬怪物组成的大军，还真算是头一回。",
    "I wonder what preserved the Imperial General's body. For how long he had died, he didn't look rotten at all.": "我在想是什么保存了那位帝国将军的尸体。死了那么久，他看起来竟然完全没有腐烂。",
    "Considering we just saved Raven Rock from certain destruction, the Captain should've been more generous. They make do with what they can, I suppose.": "考虑到我们刚刚拯救了乌鸦岩，让它免于毁灭，那个队长本该更慷慨一些的。不过……我想他们也只能给出这么多了。",
    # 强盗评论
    "You've done well killing that bandit back there. No one will mourn for thugs like her.": "干得漂亮，杀了那个强盗。没会人会为那种暴徒哀悼的。",
    "This crypt gives me a strange unease. The bandits aren't the only things that dwell here.": "这座墓窖让我感到一种异样的不安。住在这里的可不只有那些强盗。",
    "I would've cut down that bandit back there if it were up to me. Fools like her are just a waste of clean air.": "要是我说了算，我早就把那个强盗砍倒了。她那种蠢货简直是浪费干净的空气。",
    "I see doubt and mutiny beset these bandits. We'll be wise to use that.": "我看到疑虑和叛心困扰着这些强盗。我们最好利用这一点。",
    "I shed no tears for those bandits, but ordeals like the Pale Lady are precisely why I loathe dealing with the dead.": "我不会为那些强盗掉一滴泪，但像苍白女士这种劫难——正是我厌恶跟死人打交道的理由。",
    # 白色药瓶
    "That Altmer looks as if he'll cough his lungs out any moment. Will he even be alive to pay you when we get back?": "那个高精灵看起来随时都会把肺咳出来。等我们回去的时候，他还能活着付你钱吗？",
    "I see the White Phial is nothing but a few fragments. Well, that's not our problem - let's get back to the Altmer for our payment.": "看来白色药瓶只剩下几块碎片了。好吧，那不是我们的问题——回去找那个高精灵拿报酬吧。",
    "This Altmer is why I never take jobs from bedridden wretches. The dead pay no debts, and they know that all too well.": "这个高精灵就是为什么我从不接卧病在床的可怜虫的活。死人付不了债——他们自己最清楚这一点。",
    "I wonder if the White Phial can truly be repaired. Either way, I'll settle for the Phial or a fat purse of gold.": "我在想白色药瓶是否真的能修复。不管怎样，拿到药瓶或者一大袋金币，我都能接受。",
    "So, the White Phial is restored after all. Had the young alchemist failed to do so, I suppose this shop would need a new name.": "看来白色药瓶终究还是修复了。如果那个年轻的炼金术士失败了——我想这家店得换个名字了。",
    # 裂谷城 - 蜜酒
    "Having seen how the Rieklings stained this mead hall, I'll never trust anything brewed here - Nord reclamation or not.": "见识了那些瑞克林怎么糟蹋这个蜜酒厅之后，我绝不会相信这里酿造的任何东西——不管诺德人怎么收复都一样。",
    # The Lover - 悔恨之女
    "That woman actually believed she stood a chance. What a fool.": "那个女人居然以为自己有机会。真是个蠢货。",
    "People will say anything to excuse their failings. No matter - their payment is what counts.": "人们为了给自己的失败开脱，什么话都说得出来。无所谓——他们付的钱才是要紧的。",
    # 红鹰
    "I've heard of the Red Eagle when I fought the Forsworn. They would scream his name in battle, as if it'd give them some divine protection.": "我跟弃誓者作战时听说过红鹰。他们会在战场上尖叫他的名字，仿佛那能给他们带来某种神灵庇佑。",
    "I heard the Red Eagle fought fiercely against Nord aggression. All that zeal turned out to be for naught after all.": "我听说红鹰曾激烈抵抗诺德人的侵略。到头来，那股狂热终究成了一场空。",
    "We Dunmer have the Nerevarine. I suppose the Reachmen can have their Red Eagle.": "我们暗精灵有尼瑞瓦因。我想，是弃誓者也可以有他们的红鹰。",
    "All that's left of the Red Eagle are his sword and his title. Not his bloodline, not even his name. I suppose that's the fate of most heroes.": "红鹰留下的只有他的剑和他的名号。没有他的血脉，甚至没有他的真名。我想这就是大多数英雄的命运吧。",
    "The Red Eagle is gone, and you're free to kill Nords and Forsworn alike with his sword. I suppose that's not the legacy he hoped for.": "红鹰已经消逝了，而你可以用他的剑随意杀戮诺德人和弃誓者。我想那并不是他期望的遗产。",
    # 斯库玛贩子
    "There used to be a few Skooma cartels in Morrowind. I suppose the ash storms made for good cover for their operations.": "晨风曾经有几个斯库玛贩子集团。我猜那些灰烬风暴为他们提供了很好的掩护。",
    "I've never taken Skooma myself. The stuff is poison for the mind.": "我自己从来没碰过斯库玛。那玩意儿是毒害心智的东西。",
    "Riften will be Riften, with or without the Skooma cartel.": "裂谷城就是裂谷城，有没有斯库玛贩子都一样。",
    "I don't know if it's the wolves, the Skooma, or just the cave itself - but it stinks worse than a mine full of sulfur.": "我不知道是那些狼、斯库玛、还是洞穴本身的问题——但这里比满是硫磺的矿井还要臭。",
    "The cartel is gone, and a new one will soon swoop in and claim their place - Riften will always be Riften.": "贩子集团没了，很快就会有新的冲进来占据他们的位置——裂谷城永远都是裂谷城。",
    # 伊利亚
    "I've killed Hagravens before. Those witches always talk in honeyed lies before placing you on the altar. Let's stay guarded around this Illia.": "我以前杀过鹰身女巫。那些女巫在把你送上祭坛之前，总是用甜言蜜语撒谎。在这个伊利亚身边，我们保持警惕吧。",
    "Illia seems all innocent and trusting, but I promise you - no pure soul would call this tower her home.": "伊利亚看起来天真又信任人，但我向你保证——没有哪个纯洁的灵魂会把这座塔叫做家。",
    "At this point, Illia has killed more witches than necessary to win your trust. Either she's true to her words, or she's a better schemer than I know.": "到现在为止，伊利亚杀死的女巫已经超出了赢得你信任所需的数目。要么她是真心实意的，要么她就是我见过的最好的阴谋家。",
    "I see I misjudged Illia when I first saw her. She truly intended to do the right thing.": "看来我第一次见到伊利亚时看错她了。她确实是真心想做正确的事。",
    # 狼头骨洞 - 狼皇后
    "So, the Steward dismissed the peasant's concerns about Wolfskull Cave. Once again, it's up to us to do the dirty work.": "看来总管根本没把那农民对狼头骨洞的担忧当回事。又轮到我们来干脏活了。",
    "Do you feel it too? There's an ominous chill in these ruins, whispering of terrors from ages past.": "你也感觉到了吗？这些遗迹里有一股不祥的寒意，低语着来自远古的恐怖。",
    "Necromancers and their foul art, always the source of troubles. The peasant was right all along.": "死灵法师和他们那肮脏的法术，永远是麻烦的根源。那个农民一直是对的。",
    "So, that's what those necromancers were after - a dead Septim queen who ruled over the dead... And she is now free, all because of their folly.": "原来如此，那些死灵法师想要的是一个能统治死者的塞普汀女王亡灵……而她现在自由了，全都是因为他们的愚蠢。",
    "The Septim queen was bound to return after her escape. Living or dead, their kind are always too proud to stay silent.": "塞普汀女王逃脱后注定会回来。无论是生者还是死者，他们那种人永远骄傲到不肯沉默。",
    "Do you hear the dead's whispers? They're warning us away. Maybe it's the Septim queen's mind trick, cast out of fear.": "你听到死者的低语了吗？他们在警告我们离开。也许是塞普汀女王出于恐惧施展的思维把戏。",
    "Vampires and walking corpses. Is that all the undead queen can muster?": "吸血鬼和行尸。那个不死女王就这点能耐吗？",
    "I grew weary of the Wolf Queen's voice. The dead should stay silent... Let's make it so again.": "我已经厌倦了狼女王的声音。死者就该保持沉默……让我们让她重新闭嘴吧。",
    "The whispers have ceased. As I predicted, it was the Wolf Queen's trick. She feared us... even if she acted all mighty and terrible.": "低语声停止了。不出我所料，那是狼女王的把戏。她害怕我们……尽管她装出一副威严可怖的样子。",
    "You'd think the Steward would be more generous to the vanquishers of Solitude's worst villain. I hope the catacomb's loot was good, at least.": "你可能会以为总管会对击败孤独城最恶毒反派的人更慷慨一些。至少希望地下墓穴的战利品还不错。",
    # 墨索尔
    "A house burned right in the middle of the town, and no one does anything about it - as if it's nothing out of the ordinary.": "一座房子在镇子正中间烧毁了，却没有人采取任何行动——好像这根本不是什么异常的事。",
    "With all the terrors that lurk in the marsh, the peasants chose to fight a simple wizard, of all things. That's Skyrim for you.": "沼泽里潜伏着那么多恐怖的东西，那些农民却偏偏选择对抗一个普通的巫师。这就是天际。",
    "Playing hide and seek with a ghost is hardly a fair game - unless she wants to be found.": "跟一个鬼魂玩捉迷藏可不是什么公平的游戏——除非她想让你找到她。",
    "The truth of Morthal's terror is unveiled at last. Maybe the town can be saved after all.": "墨索尔恐怖的真相终于揭晓了。也许这座城镇终究还有救。",
    "The vampires are destroyed, but the air grows thickened with death. I wonder if we've truly quelled the evil, or only removed its competition.": "吸血鬼被消灭了，但空气中却充满了死亡的气息。我怀疑我们是真的平息了邪恶，还是只是替它清除了竞争对手。",
    # 乌鸦岩矿井
    "So I guessed correctly. A Nord ruin slumbers beneath Raven Rock's mine. Now, let's see if it's as horrifying as the East Empire Company believed.": "看来我猜对了。乌鸦岩矿井下沉睡着一座诺德遗迹。现在，让我们看看它是不是像东帝国公司认为的那样恐怖。",
    "A skeleton, dead for centuries. No doubt, that's the old Imperial's great-grandfather.": "一具死了几百年的骷髅。毫无疑问，那是那个老帝国人的曾祖父。",
    "Here we are... the true secret of Raven Rock's mine. The source of all the terror in this ruin.": "我们到了……乌鸦岩矿井真正的秘密。这座遗迹中所有恐怖的源头。",
    "It has been a remarkable journey, but I long for the blue sky already. Well, no blue sky on Solstheim, perhaps, but any sky would be an improvement.": "这段旅程确实不凡，但我已经开始渴望蓝天了。好吧，索瑟姆也许没有蓝天——但只要是天空，就已经是进步了。",
    "Finally! Breathable air without the stench of the centuries-dead.": "终于！可以呼吸的空气，没有那些陈年死尸的恶臭。",
    # 黑荆棘
    "To be so naive that he'd deal with Maven Black-Briar's failure of an offspring? Maybe Louis deserves to eat his loss.": "居然天真到去跟玛雯·黑荆棘那个废物后代做交易？也许路易斯活该吃这个亏。",
    "If I ever had a son like Sibbi Black-Briar, I'd put him on a boat to Atmora and never look back.": "如果我有个儿子像西比·黑荆棘那样，我会把他扔上去阿特莫拉的船，再也不回头。",
    "I almost pity Maven Black-Briar. For all her power and schemes, she stands to lose her empire to an offspring like Sibbi.": "我几乎有点同情玛雯·黑荆棘了。尽管她权势滔天、善于谋划，却可能把帝国输给西比这样的后代。",
    "Good move telling that Breton's scheme to Maven Black-Briar. She would've found out anyway... No reason to put ourselves at risk for a corpse.": "把那个布莱顿人的阴谋告诉玛雯·黑荆棘，这步棋走得好。她迟早会发现的……没理由为一个死人把自己置于危险之中。",
    "All this drama over a horse, and it's not even that handsome a steed. What a disappointment.": "这么多破事就为了一匹马，而且那匹坐骑也算不上多好看。真让人失望。",
    # 黎明守卫
    "Bear hunting isn't what I expected to be a vampire hunter's task.": "猎熊可不是我预想中吸血鬼猎人的工作。",
    "I suggest we simply head to the nearest Dwemer ruin for her gyro. No point wasting time on a wild chase amidst all this mud.": "我建议我们直接去最近的锻莫遗迹找她的陀螺仪。在这片烂泥地里瞎追纯粹浪费时间。",
    "So, we have ourselves a Dwemer expert. Slaughtering vampires with their steel just might elevate my art.": "看来我们找到了一位锻莫专家。用他们的钢铁屠杀吸血鬼——或许能提升我的艺术境界。",
    "Seems to me Isran never even liked these 'old friends' of his. Such unifying force he'll make for.": "在我看来，伊斯朗从来就不喜欢他自己的这些\"老朋友\"。他可真能团结人啊。",
    "I wonder what this Florentius is capable of. Priest of Arkay? What is he going to do - exorcise the vampires? Or pray for their souls?": "我在想这个弗洛伦修斯有什么本事。阿凯的祭司？他打算做什么——给吸血鬼驱魔？还是为他们的灵魂祈祷？",
    "Does Florentius... 'talk' to his god? Now I see why the people had that hesitant tone when they asked you to find him.": "弗洛伦修斯……会跟他的神\"说话\"？现在我明白为什么那些人请你去找他的时候，语气那么犹豫了。",
    # 索瑟姆 - 塔尔莫
    "Two elves who kidnapped a blacksmith? They're either from Raven Rock or the Thalmor - and I assure you, my people have no interest in Nord armor.": "两个精灵绑架了一个铁匠？他们要么来自乌鸦岩，要么是梭默——我向你保证，我族人可对诺德盔甲没有兴趣。",
    "I thought this isle would be the last place to interest a Thalmor. Surely, there are greener pastures to conquer or plunder.": "我以为这座岛屿是梭默最不可能感兴趣的地方。肯定有更好的地方值得他们征服或掠夺吧。",
    "I wonder what magic this 'Stalhrim' contains, so powerful that it made the Thalmor come all this way from Alinor.": "我在想这\"魔冰\"里到底蕴藏着什么魔力，如此强大，竟让梭默从艾琳诺千里迢迢赶来。",
    "I never expected that we'd do business with the Thalmor, but whoever pays well, I suppose.": "我从没想过我们会跟梭默做生意，不过……谁出价高就跟谁做，我想是这样的。",
    "I've started to imagine how a Thalmor would look in Stalhrim armor. A blue Altmer would look like quite the spectacle, don't you think?": "我开始想象一个梭默穿上魔冰盔甲会是什么样子了。一个蓝皮肤的高精灵，那场景一定很壮观，你不觉得吗？",
    # 索瑟姆 - 历史学家
    "It's not my first time escorting a historian through an old ruin, though my first was inconceivably more talkative... and annoying.": "这不是我第一次护送历史学家探索古老遗迹了，不过第一个简直多得令人难以置信……而且烦人。",
    "The Empire built fortresses like this to last. Considering its age, it still holds up well.": "帝国建造的堡垒就是这样经久耐用。以它的年代来看，它仍然保存得很好。",
    "I could get used to this place. The darkness gives me a warm comfort.": "我能习惯这个地方。黑暗给我一种温暖的慰藉。",
    "With the wars and the debts, the Jarls and the generals have gradually lost control of their forts.": "由于战争和债务，领主们和将军们渐渐失去了对堡垒的控制。",
    "Imperial forts like this used to dot the landscapes of Morrowind. After the Red Year, they've mostly crumbled into dust.": "像这样的帝国堡垒曾经遍布晨风的大地。红年之后，它们大多已经化为尘土了。",
    "I once wiped out a fortress in a single night. Poisoned wine does the trick every time - that, and my silent steps.": "我曾经一夜之间灭掉了一座堡垒。毒酒每次都管用——再加上我无声的步伐。",
    # 孤独城
    "Solitude is one of the few Skyrim cities that agree with me.": "孤独城是少数几个让我觉得合拍的天际城市之一。",
    "Solitude values real art, yet it's never lacking in schemes and shadows. This just might be the perfect city for someone like me.": "孤独城珍视真正的艺术，但这里的阴谋和暗影也从来不缺。这或许正是适合我这样的人的城市。",
    "I may enjoy Nord mead, but Solitude's fine wine is unlike any other.": "我或许喜欢喝诺德蜜酒，但孤独城的精品葡萄酒别具一格。",
    # 阿达拉（长笛）
    "Adara and I used to play with the instruments at the day's end. So many fond memories we had with the flutes...": "阿达拉和我以前常在一天结束时演奏乐器。我们用那些笛子留下了那么多美好的回忆……",
    "Maybe we can play with the flute later, like I used to with Adara.": "也许我们待会可以吹吹笛子，就像我以前和阿达拉那样。",
    "One can make such great art with a flute.": "一支笛子也能创造出如此伟大的艺术。",
    # 龙
    "I wonder if the dragons feel fear. That must be the only thing they know when you devour their souls.": "我在想龙会不会感到恐惧。当你吞噬它们的灵魂时，那一定就是它们唯一能感受到的东西。",
    "I've been struck by the soul trap spell a few times. When you absorb the dragons' souls, I can only imagine they feel the agony tenfold.": "我被灵魂陷阱术击中过几次。当你吸收龙魂的时候，我只能想象它们承受的痛苦是你的十倍。",
    "So, the dragon god made you to kill his children and eat their souls? I've seen worse parents.": "所以，龙神造出你就是为了杀死他的孩子，吃掉他们的灵魂？我见过更糟的父母。",
    "If you think the dragons are irritating, then you don't know the cliff racers. Those nasty critters never have the decency to stay grounded.": "如果你觉得龙很烦人，那是你没见识过悬崖鸟。那些讨厌的东西从来不懂得待在地上。",
    "The dragons breathe magic as effortlessly as we spit. It would be wise to take precautions against their ice or fire.": "龙吐息魔法就像我们吐口水一样轻松。最好做好防范，抵御它们的冰霜或火焰。",
    # 洗澡
    "I suppose this place can't get any filthier... Bathing time can't come soon enough.": "我想这个地方不会再更脏了……真想赶紧洗个澡。",
    "The longer we stay here, the more we smell like this place's denizens. I suggest we find the nearest pond soon as we leave this accursed place.": "我们在这里待得越久，身上的味道就越像这里的居民。我建议一离开这个该死的地方就去找最近的水塘。",
    "A thorough bath always does us adventuring type wonders.": "好好洗个澡，对我们这些冒险者来说总是有奇效。",
    "Why don't we have a long, warm bath - just you and me, undisturbed by anything.": "我们何不洗个长长的热水澡——就你和我，不受任何打扰。",
    "We have a long road ahead. A quick bath in a nearby pond ought to refresh our spirits... Not to mention it'll get rid of the odor.": "前路漫漫。在附近的水塘里快速洗个澡，应该能让我们的精神振作起来……更别说还能去掉身上的臭味。",

    # === aaJenassaAmor3CW302 (内战 - 婚后) ===
    "But no matter. Soon as our contract is over, the Stormcloaks will see their patrols disappear without a trace.": "不过无所谓了。等合同一结束，风暴斗篷就会发现他们的巡逻队消失得无影无踪。",
    "I tolerate the Stormcloaks because of you, my love - but had it not been for you, I'd see their patrols slaughtered in the dark.": "我容忍风暴斗篷是因为你，我的爱人——但若不是因为你，我早就看着他们的巡逻队在暗处被屠戮殆尽了。",

    # === aaJenassa8RR020 (乌鸦岩 - 刺杀阴谋) ===
    "What do you think about Raven Rock's assassination plot?": "你对乌鸦岩的刺杀阴谋怎么看？",
    "Assassination, family feuds, backstabbing - these are all parts of a Dunmer noble's daily life.": "刺杀、家族世仇、背后捅刀——这都是暗精灵贵族日常生活的一部分。",
    "I don't know which side is more right in this situation - the Redoran or the Ulen. But knowing Morrowind, the answer is most certainly neither.": "我不知道在这种情况下哪一方更正确——是瑞多然还是乌伦。但以我对晨风的了解，答案肯定两方都不是。",
    "But no matter. Point your blade at the Ulen, and I'll wipe them out as you desire.": "不过无所谓。只要你把剑指向乌伦，我就按你的意愿把他们清除干净。",

    # === aaJenassa8RR021 ===
    "Why is neither side right?": "为什么两边都不对？",
    "The Great Houses feud over lands, gold and ancestral claims. The conflict between the Redoran and the Ulen was no different, whatever they may say.": "大家族之间的世仇无非是为了土地、金币和祖先宣称权。瑞多然和乌伦之间的冲突也不例外，不管他们怎么说。",
    "Of course, the Redoran can make all their claims about their righteous purge of House Hlaalu. The dead cannot talk back after all.": "当然，瑞多然可以大谈他们如何正义地清算了赫拉鲁家族。毕竟死人不会反驳。",

    # === aaJenassa8RR022 ===
    "It seems you're no stranger to Great House politics.": "看来你对大家族的政治并不陌生。",
    "In my childhood, I'd occasionally play the inconspicuous urchin for Great House schemers.": "小时候，我偶尔会为那些大家族阴谋家扮演不起眼的小乞丐。",
    "While I poured their Matze, those gluttonous nobles would announce their grand plot to their allies, only for me to trade it for a warm meal.": "当我在倒马泽酒的时候，那些饕餮贵族会向盟友宣布他们的宏伟计划——而我则拿这些情报换一顿热饭。",
    "It's almost pitiful how no one ever suspected a drink pourer, just because she seemed all harmless and small.": "从来没有人怀疑过一个倒酒的，就因为她看起来人畜无害、身材矮小——这几乎让人觉得可怜。",

    # === aaJenassa8RR022a ===
    "That's dishonorable.": "那可不光彩。",
    "In contrast to those who literally plotted to murder my employers for power?": "跟那些为了权力而密谋谋杀我雇主的人比起来？",
    "Honor is only a fancy garment afforded by those who live in peace.": "荣誉不过是只有生活在和平中的人才穿得起的一件华丽外衣。",

    # === aaJenassa8RR022b ===
    "A meal in exchange of political advantage? Sounds like a bargain.": "一顿饭换一个政治优势？听起来挺划算的。",
    "They needed their advantage, and I needed my belly to stop drumming. All things considered, we both got what we wanted.": "他们需要他们的优势，而我要让自己的肚子不再咕咕叫。总的来说，我们都得到了想要的。",
    "But of course, my loyalty is much more expensive than porridge and meat nowadays.": "当然，如今我的忠诚，可比一碗粥和肉贵得多了。",

    # === aaJenassa8RR022c ===
    "So you've adapted to the shadows since your childhood.": "所以你从小就已经适应了暗影。",
    "I guess this life chose me as much as I chose it.": "我想，与其说我选择了这种生活，不如说它选择了我。",

    # === aaJenassa8RR023 ===
    "Honestly, these Dunmeri intrigues are too messy for my liking.": "老实说，这些暗精灵的阴谋太混乱了，我不喜欢。",
    "And I won't blame you for it... Our society is as complex as a maze to most, with each exit leading only to another labyrinth.": "我也不会因此责怪你……我们的社会对大多数人来说就像一座迷宫，每个出口通向的只是另一座迷宫。",
    "Well, you did resolve the Silver-Blood situation in Markarth, did you not? I say this is child's play compared to that.": "嗯，你不是解决了马卡斯城银血家族的事吗？跟那件事比起来，这不过是小儿科。",

    # === aaJenassa8RR02302 ===
    "In any event, you accepted a contract from the Councilor. It's only fair that you complete his task, or let him know your wish.": "无论如何，你接受了议员的合同。完成他的任务，或者让他知道你的意愿——这才公平。",

    # === aaJenassa8RR024 ===
    "Let's find out those Ulen and finish them.": "去找到那些乌伦家族的家伙，干掉他们。",
    "As you say.": "听你的。",

    # === aaJenassa8RR021a ===
    "But the Ulen are a threat to Raven Rock's peace.": "但乌伦家族对乌鸦岩的和平构成了威胁。",
    "A threat to the Redoran's peace. Had it been the Ulen who ruled Raven Rock, the Redoran would've attempted the same.": "是对瑞多然家族的和平的威胁。如果是乌伦家族统治乌鸦岩，瑞多然也会做同样的事。",
    "Different names, same plots. Such is the long saga of my people.": "不同的名号，同样的阴谋。这就是我族人漫长的编年史。",

    # === aaJenassa8RR021b ===
    "The victor wrote the history.": "历史是胜利者书写的。",
    "And that's the truth.": "事实正是如此。",

    # === aaJenassa8WorkingFor0 ===
    "If you're employed by the East Empire Company, how can you still work for me?": "如果你受雇于东帝国公司，你怎么还能为我工作？",
    "To answer it simply, they don't require my service every moment.": "简单回答的话——他们不是时时刻刻都需要我的服务。",
    "I'm free to pursue other work while they have no need for me. The more contracts I complete, the sooner I can repay this debt.": "他们不需要我的时候，我可以自由地接其他工作。我完成的合同越多，就能越早还清这笔债。",
    "But where they need my service, I'll be obligated to abandon all other work to serve their interests. Such are the terms of their 'offer'.": "但只要他们需要我的服务，我就有义务放下所有其他工作，去为他们效劳。这就是他们那个\"提议\"的条款。",

    # === aaJenassa8WorkingFor1 ===
    "That sounds only fair.": "听起来还算公平。",
    "Fair to the Company, as always.": "对公司公平罢了，一如既往。",

    # === aaJenassa8WorkingFor2 ===
    "Do they pay you when they don't need you?": "他们不需要你的时候，也会付你钱吗？",
    "If you wouldn't pay for a mead you didn't drink, then why would they pay for a service they didn't use?": "如果你不会为没喝的蜜酒付钱，那他们为什么要为没用的服务付钱？",

    # === aaJenassa8WorkingFor3 ===
    "That sounds harsh.": "听起来真苛刻。",
    "When an Imperial sets the terms, they've already calculated all their gains and losses.": "当一个帝国人制定条款时，他们已经算清了所有的得失。",

    # === aaJenassa8WorkingFor4 (长篇对话 - Jordis/伊利亚/孩子等) ===
    "Wait, what will happen to us if they summon you now?": "等等，如果他们现在召唤你，那我们怎么办？",
    "Then I'll have no choice but to return to their service until their need for me expires. Unless you wish to come along, that is.": "那我就别无选择，只能回到他们那里去，直到他们对我的需要结束。除非你愿意一起来。",
    "If not... I suppose the least I could do is to give you a refund.": "如果不……我想我至少可以给你退款。",
    "Why are you giving me that look, Jenassa?": "你为什么那样看着我，简娜莎？",
    "It's nothing.": "没什么。",
    "No, I can tell something's on your mind. You looked just like Faida when she lost my brother.": "不，我看得出来你有心事。你刚才的样子，就像法伊达失去我哥哥时的表情。",
    "Well, I... You look like someone from my past, is all.": "嗯，我……你看起来像我过去认识的一个人，仅此而已。",
    "Ah, I'd say I could be that person, but I'm certain I'd remember you. After all, you leave quite the impression on everyone you meet.": "啊，我倒是想说我就是那个人，但我肯定我会记得你。毕竟，你给每个见过你的人都留下了深刻的印象。",
    "No, you can't possibly be her... She died thirty years ago.": "不，你不可能是她……她三十年前就死了。",
    "Jenassa, you mentioned I looked like someone from your past... who died thirty years ago? Who was that?": "简娜莎，你说我看起来像你过去认识的一个人……三十年前去世了？那是谁？",
    "She was my first love in Skyrim. The one who taught me that warmth exists even in the frozen north.": "她是我在天际的初恋。是那个教会我即使在冰封的北方也存在温暖的人。",
    "Oh. I didn't realize she was your... I mean, my condolences.": "哦。我不知道她是你的……我是说，请节哀。",
    "Thank you.": "谢谢。",
    "She was a bard - the most gifted of her class. When we were together, she'd always perform the world's most beautiful art for me.": "她是个诗人——是她那一行中最有天赋的。我们在一起的时候，她总是为我演奏这世上最美丽的艺术。",
    "Well, I'm no bard - the far opposite of one, if that's what you're asking.": "嗯，我不是诗人——如果你问的话，恰恰相反。",
    "It's fine. I have found an artist just as great as she was.": "没关系。我已经找到了一个和她一样伟大的艺术家。",
    "And I'm not asking you to be one. We are each who we are... to presume otherwise brings nothing but sorrow.": "而且我并不是要求你成为一个诗人。我们各自做自己……以为别人应该是什么样子，只会带来痛苦。",
    "So, Jenassa - what's with your obsession over 'art'?": "那么，简娜莎——你对'艺术'的执着是怎么回事？",
    "The world would be a colorless place without it, no?": "没有艺术，这世界会变得毫无色彩，不是吗？",
    "Yeah. But from the sound of it, the only color of your art is bloody red!": "是啊。但听你这么说，你的艺术唯一的颜色就是血红色吧！",
    "Well, we each have our preferences. Some play their lutes... while I stick to my sword.": "嗯，我们各有各的偏好。有些人弹他们的鲁特琴……而我坚守我的剑。",
    "But what is your art, Jordis - if you have one?": "但你的艺术是什么呢，乔迪斯——如果你有的话？",
    "Well, not singing or dancing, that's for sure.": "嗯，肯定不是唱歌也不是跳舞。",
    "You look happy, Jenassa.": "你看起来很幸福，简娜莎。",
    "All because of your Thane.": "全是因为你的领主。",
    "You didn't look like the type to settle down... But it suits you. Now it's as if I'm seeing my brother and Faida again, ever the joyful couple.": "你看起来不像会安稳下来的人……但这样很适合你。现在我仿佛又看到了我的哥哥和法伊达，永远幸福的一对。",
    "Seeing people from your past, Jordis?": "看到了你过去认识的人，乔迪斯？",
    "Yeah. You got me!": "是啊。被你发现了！",
    "Tell me something about your mother, Illia.": "跟我说说你母亲的事吧，伊利亚。",
    "Why? I didn't realize you cared.": "为什么？我没意识到你竟然关心。",
    "My own mother died to save me from the An-Xileel... Were I in your place, I could never bring myself to hurt her... Let alone kill her.": "我自己的母亲为了从安-希雷尔手中救我而牺牲……如果我是你，我永远无法说服自己去伤害她……更别说杀了她了。",
    "You were lucky to have your mother then, Jenassa.": "那你那时很幸运，还能有你的母亲，简娜莎。",
    "Maybe at one point, mine would've made the same sacrifice. But after years of corruption, I doubt she still loved anything besides power.": "也许在某一刻，我的母亲也曾愿意做出同样的牺牲。但经过多年的堕落，我怀疑除了权力，她已不再爱任何东西。",
    "Was that why you struck her down?": "这就是你打倒她的原因吗？",
    "I don't know. At that point, all I knew was that I must stop the coven and their human sacrifice.": "我不知道。那一刻，我只知道自己必须阻止那个女巫团和他们的人祭。",
    "Maybe I would've chosen differently had my mother shown a bit more warmth. But then, she wouldn't be that power-mad Hag we slew.": "如果我母亲表现出哪怕一丝温情，也许我会做出不同的选择。但那样的话，她就不会是那个我们杀死的、权力疯狂的妖婆了。",
    "Tell me something about Morrowind, Jenassa.": "跟我说说晨风的事吧，简娜莎。",
    "You'll have to be more specific with your question.": "你得问得更具体一点。",
    "Well, specific... how?": "嗯，具体……怎么个具体法？",
    "Morrowind is a big place. Dozens of cities, hundreds of species, with five noble houses each trying to kill the others every day.": "晨风是个很大的地方。几十座城市，数百个物种，五个贵族家族每天都在互相残杀。",
    "I didn't know what to ask, because I knew nothing at all about the world outside the Tower. But you just gave me something to work with... Thanks.": "我不知道该问什么，因为我对塔楼以外的世界一无所知。但你刚刚给了我一些可以了解的东西……谢谢。",
    "Honestly, why don't you just go read a book? Surely, the witches taught you to read?": "老实说，你为什么不直接去读本书呢？那些女巫总该教过你识字吧？",
    "Illia - I noticed your disgust when I prayed to the Three earlier.": "伊利亚——我注意到你刚才在我向三神祈祷时露出了厌恶的表情。",
    "You were praying to the Daedra.": "你在向迪德拉祈祷。",
    "Who I worship is my business. Why don't you mind your sorceries, witch?": "我信仰谁是我的事。你管好你的巫术就行了，女巫。",
    "I was doing exactly that - until you had to bring it up.": "我正是在这么做——直到你非要把这事提出来。",
    "Good. Then we understand each other.": "很好。那我们互相理解了。",

    # === aaJenassa8MS060 (狼头骨洞 - 主线任务) ===
    "What do you think about Wolfskull Cave?": "你怎么看狼头骨洞这件事？",
    "I think the Steward is a fool to dismiss that villager's warning - but at least, he has half the wisdom to hire professionals to investigate.": "我觉得总管是个傻瓜，居然无视那个村民的警告——但至少他还有一半的智慧，知道雇专业人士来调查。",
    "I just hope he pays well.": "我只希望他付的钱够多。",

    # === aaJenassa8MS061 ===
    "It's not about the money for me. It's about saving people.": "对我来说不是钱的问题。是为了救人。",
    "A thousand people would fight for a thousand reasons. In the end, the only thing that matters is the job gets done.": "一千个人会为了一千个理由而战。归根结底，唯一重要的是活儿干完了。",

    # === aaJenassa8MS062 ===
    "Why wouldn't the Steward pay well?": "总管怎么会不给足够的钱？",
    "Solitude is the pearl of the north, so I don't doubt that its coffer has more than enough for two hired blades.": "孤独城是北方的明珠，所以我不怀疑它的金库足够付两个雇佣兵的钱。",
    "But the Steward sees Wolfskull Cave's rumors as a farce. That's why he didn't even care to send reinforcements.": "但总管把狼头骨洞的传闻当作一场闹剧。这就是为什么他连派援军都不肯。",
    "A small pouch for our time, that's the payment he expects to afford.": "给我们一小袋钱打发时间——这就是他打算付的报酬。",

    # === aaJenassa8MS063 ===
    "With the war going on, Solitude really can't afford to investigate mere rumors.": "仗还在打，孤独城真的抽不出人手去调查区区谣言。",
    "Isn't that the most convenient excuse everyone uses these days.": "这难道不是如今每个人都在用的最方便的借口吗？",
    "A farm was raided by bandits? The soldiers are off at the war camp. The city's water needs to be sanitized? The gold is all in the war chest.": "农场被强盗洗劫了？士兵们都在前线军营。城市的水需要净化了？金币全在军需箱里。",
    "Maybe the Jarls are more interested in painting the map than governing their people.": "也许领主们更热衷于在地图上涂抹疆域，而不是治理他们的子民。",

    # === aaJenassa8MS064 ===
    "The Steward should've done more to help his people.": "总管本该为他的子民做更多的事。",
    "The Nords are all about their honor, and nothing's more honorable than killing others on the battlefield.": "诺德人满脑子都是荣誉，而没有什么比在战场上杀人更荣誉的了。",
    "Where's the honor in keeping some peasants happy?": "让几个农民过上好日子，荣誉又在哪里？",

    # === aaJenassa8MS06302 ===
    "Let's go.": "走吧。",
    "Either way, the Steward's thoughts are of little consequence to us. We'll just keep doing what we always do best.": "不管怎样，总管的看法对我们来说无关紧要。我们只管继续做我们最擅长的事。",

    # === aaJenassa8MS064a ===
    "Falk Firebeard doesn't seem like a warmonger to me.": "法尔克·火胡在我看来不像个好战分子。",
    "Yet those around him are all sounding the war drums. Even if the Steward wanted to care, the warmongers wouldn't have permitted him.": "可他身边的人都在敲响战鼓。就算总管想关心，好战分子也不会允许他这么做。",

    # === aaJenassa8MS064b ===
    "Enough with your cynicism. I'll hear no more of it.": "够了，你的愤世嫉俗。我不想再听了。",
    "Maybe don't ask for my thoughts next time, then.": "那你下次就别问我意见好了。",

    # === aaJenassa8MS064c ===
    "And you care about the peasants?": "那你在乎那些农民吗？",
    "Obviously no. I merely made an observation after spending decades on this land.": "显然不在乎。我只是在这片土地上待了几十年后，做了一个观察而已。",

    # === aaJenassa8MS064d ===
    "They're all short-sighted fools.": "他们全是目光短浅的蠢货。",
    "If they see any further beyond the glory at hand, it would be a betrayal of their proud heritage, no?": "如果他们能看到眼前的荣耀之外的东西，那岂不是背叛了他们引以为傲的传统，不是吗？",

    # === aaJenassa8MS070 (灯塔) ===
    "What do you think about Solitude's lighthouse?": "你怎么看孤独城的灯塔这件事？",
    "You mean the Argonian pirate's 'proposition'.": "你是说那个亚龙人海盗的\"提议\"。",
    "I don't know why you're even considering to entertain him. If I know pirates, they're never going to share their spoil.": "我不知道你为什么还在考虑跟他周旋。以我对海盗的了解，他们从来不会分享战利品。",

    # === aaJenassa8MS0702 ===
    "Besides - should an East Empire Company vessel be wrecked after this, then the situation with my debtor will become most... peculiar.": "再说——如果之后有东帝国公司的船在这里遇难，那我跟债主之间的关系就会变得很……微妙。",
    "Besides - should an East Empire Company vessel be wrecked after this, then we'll earn the ire of Cyrodiil's greatest power.": "再说——如果之后有东帝国公司的船在这里遇难，那我们就会惹来赛洛迪尔最强大的势力的怒火。",
    "I may no longer be chained to them, but their eyes are always present in Haafingar. Many more like me are still at their disposal.": "我或许已经不再被他们束缚，但他们的眼线无处不在——在哈芬加尔。还有很多像我一样的人仍受他们支配。",
    "The Legion may fight honorably... but the Company does not.": "军团或许会光明正大地战斗……但公司不会。",

    # 重复的 (268, 269 are duplicates of 265, 267) - skip them in dict since they'll be matched by original text

    # === aaJenassa8MS071 ===
    "Don't worry, I'll ignore the Argonian pirate.": "别担心，我不会理那个亚龙人海盗的。",
    "Your wisdom is greater than you realized.": "你的智慧比你自以为的还要大。",

    # === aaJenassa8MS072 ===
    "I'm interested to see this through.": "我想把这件事看到底。",

    # === aaJenassa8MS073 ===
    "That pirate is a fool. All he spouts is rot.": "那个海盗是个蠢货。他满嘴喷粪。",
    "Well. Now that you mention it... What kind of criminal would recruit an accomplice on the street?": "好吧。既然你提到了……什么样的罪犯会在大街上招募同伙？",
    "Only the foolish or the careless, I'd imagine - and neither make for good schemers.": "我想只有愚蠢或者粗心大意的人才干得出来——而这两者都成不了好的阴谋家。",

    # === aaJenassa8MS074 ===
    "There are riches awaiting us in this job. We just have to go and grab it.": "这活儿里有财富等着我们。我们只管去拿就是了。",

    # === aatherewillcome ===
    "There will come a day your curiosity leads us to safe havens and good fortune, but I see that day is still far away.": "总有一天，你的好奇心会带我们去往安全的避风港和好运——但在我看来，那一天还远着呢。",

    # === aaJenassa8MS140 (墨索尔) ===
    "What do you think about Morthal?": "你怎么看墨索尔？",
    "Normally, I appreciate silence and solitude - but in Morthal, even the silence grows suffocating.": "通常来说，我喜欢安静和独处——但在墨索尔，连安静都变得令人窒息。",
    "A house was burnt down and a family ruined, yet the suspect still walks freely under the sun, and the town goes about its business as usual.": "一座房子被烧毁了，一个家庭被毁了，然而嫌疑人仍在光天化日之下自由行走，镇上的生活一切照旧。",
    "It's as if that's the norm here. Still, indifferent... and dead.": "仿佛这就是这里的常态。死寂，冷漠……了无生气。",

    # === aaJenassa8MS141 ===
    "I intend to unravel the mystery here.": "我打算揭开这里的谜团。",
    "Unravel the mystery, or upset the design of the forces that be?": "揭开谜团，还是打乱当权者的布局？",

    # === aaJenassa8MS142 ===
    "Maybe we should get away while we can.": "也许我们应该趁还来得及的时候离开。",
    "Wise caution can often be confused with cowardice.": "明智的谨慎常常会被误认为是怯懦。",
    "In my view, there's no point saving a place that doesn't care to be saved.": "在我看来，拯救一个不在乎自己是否得救的地方，毫无意义。",
    "Let's go then. I can hardly wait to breathe freely again.": "那我们走吧。我迫不及待想再次自由地呼吸了。",

    # === aaJenassa8MS143 ===
    "The burnt family demands justice.": "那个被烧毁的家庭需要正义。",
    "I see your point. It may not save a soul... but the dead will find some small comfort if we avenge them.": "我明白你的意思。这或许救不了任何人……但如果我们为他们复仇，死者也能得到些许安慰。",

    # === aaJenassa8MS14102 ===
    "I don't know what we expect to find in this town, or what yet awaits us in the marsh.": "我不知道我们期望在这座镇上找到什么，又或者沼泽里还有什么在等着我们。",
    "But if Death is looming over Morthal, then I say we feed it what it desires - the blood of those responsible for the terror.": "但如果死神正在墨索尔上空徘徊——那我说，我们就喂给它想要的东西——那些对这起恐怖事件负责的人的血。",

    # === aaJenassa8RR030 (乌鸦岩矿井秘密) ===
    "What do you think about Raven Rock Mine's secrets?": "你怎么看乌鸦岩矿井的秘密？",
    "Knowing how the East Empire Company operates, it wouldn't surprise me that they've concealed secrets beneath the mine.": "以我对东帝国公司运作方式的了解，他们在矿井下藏了秘密，我一点也不惊讶。",
    "It exists to generate wealth for the noble houses. Everything else is expendable for that goal.": "矿井的存在就是为了给贵族家族创造财富。除此之外的一切，为了这个目标都是可以牺牲的。",
    "For them to shut down the mine, I see two explanations - one, they stood to gain much from what lied beneath, so they kept it sealed for themselves.": "他们关闭矿井，在我看来有两种解释——第一，他们能从下面的东西中获得巨大利益，所以将其封存起来留给自己。",
    "And two, they stood to lose much more if they let the mine be. That means whatever they'd hidden beneath... is best left forgotten.": "第二，如果继续开采矿井，他们可能会损失更多。也就是说，他们藏在下面的不管是什么……最好就此遗忘。",

    # === aaJenassa8RR031 ===
    "What do you think they've hidden down there?": "你觉得他们在下面藏了什么？",
    "I doubt even the Vici themselves knew, let alone a mere sellsword they employed.": "我怀疑连维西家族自己都不清楚，更别提他们雇用的区区一个佣兵了。",
    "I honestly don't know.": "老实说，我不知道。",

    # === aaJenassa8RR03102 ===
    "If I were to entertain a guess, it'd either be a Nordic ruin, full of undead longing for flesh - or a Dwemer ruin, with their steels of death.": "如果让我猜的话，要么是一座诺德遗迹，里面满是渴望血肉的亡灵——要么是一座锻莫遗迹，充满他们那致命的钢铁。",
    "The Company might not care much for things besides profit, but it still operated under the Emperor's grace.": "公司除了利润之外或许不怎么关心别的事，但它毕竟是在皇帝的恩典下运作的。",
    "Should an army of undead swarm the town, the Emperor - and by extension, the Company - would have much to answer for.": "如果一支亡灵大军涌向镇上，皇帝——连带着公司——将难辞其咎。",

    # === aaJenassa8RR032 ===
    "Do you think we should leave the mine alone then?": "那你觉得我们应该别碰那个矿井吗？",
    "I believe we should delve deeper and see what the Company has hidden.": "我认为我们应该深入下去，看看公司到底藏了什么。",
    "Where there are risks, there are opportunities. Whatever secret lies below, it is worth protecting to the Company.": "哪里有风险，哪里就有机会。不管下面藏着什么秘密，它对公司来说一定值得守护。",
    "That either means it can make us rich, or it can change the world.": "那要么意味着它能让我们发财，要么意味着它能改变世界。",

    # === aaJenassa8RR033 ===
    "Let's go.": "走吧。",
    "The East Empire Company's secrets await.": "东帝国公司的秘密在等着我们。",

    # === aaJenassa8Betray0 ===
    "If someone pays you to, would you ever betray your patron?": "如果有人出钱，你会背叛你的雇主吗？",
    "I suppose this question arose from my profession.": "我想这个问题是源于我的职业吧。",
    "Who put such thoughts in you? I suppose it's that sorry failure Lydia.": "是谁让你有这种想法的？我猜是那个可怜的失败者莱迪亚。",

    # === aaJenassa8Betray02 ===
    "I may work for gold, but I will never sully my art by betraying those who afforded it.": "我或许为金币而工作，但我绝不会用背叛来玷污我的艺术——尤其不会背叛那些出钱让我施展艺术的人。",

    # === aaJenassa8Betray03 ===
    "Learn to appreciate my art, unless you want this fear to come true... when our contract expires.": "学着欣赏我的艺术吧——除非你想让这个恐惧成真……等我们的合同到期的时候。",
    "After all the time we've spent together, I thought you had started to appreciate my art. I guess I was wrong.": "一起经历了这么多，我以为你已经开始欣赏我的艺术了。看来我错了。",

    # === aaJenassa8Betray1 ===
    "I'm sorry, Jenassa. I didn't mean that.": "对不起，简娜莎。我不是那个意思。",
    "Very well. Let's put those thoughts behind us for good.": "很好。让我们把这些想法彻底抛在脑后吧。",

    # === aaJenassa8Betray2 ===
    "Don't the Dunmer like treachery?": "暗精灵不是喜欢背信弃义吗？",
    "Against enemies, not those whose coin feeds me.": "是对敌人，不是对那些用钱养活我的人。",
    "Why don't you stay silent for a while, until you've grown a mind of your own, at least.": "你为什么不先安静一会儿——至少等到你有了自己的脑子再说。",

    # === aaJenassa8Betray3 ===
    "We'll see.": "走着瞧吧。",
    "I guess we will.": "我想我们会的。",

    # === aaJenassa8Betray4 ===
    "Don't bring Lydia into this.": "别把莱迪亚扯进来。",
    "So it's your own thought, then. Very well... I see now how you truly look at me.": "所以这是你自己的看法了。很好……我现在知道你真正是怎么看我的了。",

    # === aaJenassa8SV010 (历史学家) ===
    "It's not your first time escorting a historian?": "这不是你第一次护送历史学家了吧？",
    "The first time I took on such a contract, it was in another Nord ruin. I reckon it was even bigger than this one.": "我第一次接这种合同，是在另一座诺德遗迹里。我估计那座比这个还要大。",
    "Supposedly, that ruin was built above an ancient Falmer burial ground, which the Nords defiled and destroyed during their conquests.": "据说那座遗迹建在一处古老的雪精灵墓地上方，诺德人在征战期间亵渎并摧毁了它。",
    "This historian believed the Falmer ghosts had possessed the Draugr there, and intended to prove it.": "那个历史学家相信雪精灵的鬼魂附身了那里的尸鬼，并打算证明这一点。",

    # === aaJenassa8SV011 ===
    "Was that historian an elf?": "那个历史学家是精灵吗？",
    "He was a full-blooded Nord. Dressed like one, drank like one, even breathed like one.": "他是个纯血诺德人。穿得像诺德人，喝得像诺德人，连呼吸都像诺德人。",
    "Only thing that was different? He claimed his 28th great-grandmother was the last Falmeri princess, which made him the true heir to their legacy.": "唯一不同的地方？他声称他的第28代曾祖母是最后一位雪精灵公主，这让他成为了雪精灵遗产的真正继承人。",

    # === aaJenassa8SV012 ===
    "What happened in that ruin?": "那座遗迹里发生了什么？",
    "What happened was that he kept yapping about the ancient Falmer and their glory, how the Nords' revenge for Saarthal was too harsh, and so on.": "事实是，他一直在喋喋不休地谈论古老的雪精灵和他们的荣耀，诺德人对萨瑟尔的复仇太过分了，诸如此类。",
    "After a certain point, I simply stopped paying attention. He gave the ruin many more pieces of his mind, no doubt.": "到了一定时候，我就干脆不再听了。他肯定对那座遗迹发表了很多高见。",

    # === aaJenassa8SV012a ===
    "I thought you'd agree with him.": "我以为你会同意他的看法。",
    "Because I'm an elf?": "因为我是个精灵？",
    "We Dunmer hardly even care about our own brethren, until the circumstances drive us to band together.": "我们暗精灵连自己的同胞都几乎不怎么关心——除非形势迫使我们必须团结一致。",
    "All I can say is that the Falmer got their fate, and history is already written.": "我只能说，雪精灵得到了他们的命运，而历史已经写就。",

    # === aaJenassa8SV012b ===
    "What a fool. The Falmer are gone, only the monsters are left.": "真是个傻瓜。雪精灵已经消失了，只剩下那些怪物了。",
    "My thought exactly. But why should an artist argue with her patron?": "我也是这么想的。但一个艺术家为什么要跟她的赞助人争论呢？",

    # === aaJenassa8SV012c ===
    "Did the historian get what he was looking for in the Nord ruin?": "那个历史学家在诺德遗迹里找到他想要的东西了吗？",
    "Apparently no. There were plenty of Draugr... but besides a Wispmother and a few dozens of her spawn, we found no trace of the Falmer.": "显然没有。那里有很多尸鬼……但除了一个雾母和她的几十个后代，我们没有发现任何雪精灵的痕迹。",
    "He was devastated, but no matter. All I cared was getting my hard-earned pay.": "他崩溃了，不过无所谓。我只在乎拿到我辛苦挣来的报酬。",

    # === aaJenassa8SV013 ===
    "Do you think Tharstan is better than him?": "你觉得萨斯顿比他好吗？",
    "Tharstan's talkative, sure... but at least he also tries to be helpful.": "萨斯顿确实话多……但至少他也尽力提供帮助。",
    "As far as historians go, he might make for the best patron of his kind.": "就历史学家而言，他可能是这类人里最好的雇主了。",
    # 孩子对话
    "I was once like you, young one.": "我曾经也像你一样，小家伙。",
    "Once like me?": "曾经像我一样？",
    "After my parents died... the Argonians took my village and drove me to the cities.": "我父母死后……亚龙人占领了我的村庄，把我赶到了城市里。",
    "I did all sorts of things to survive, even begged... like you.": "我做过各种各样的事来活下去，甚至乞讨过……就像你一样。",
    "But you are now a strong lady.": "但你如今已经是一位坚强的女士了。",
    "Because I never gave up the fight, little one. And neither should you.": "因为我从未放弃过抗争，小家伙。你也不应该放弃。",
    "My lady... would you like a flower?": "女士……你想要一朵花吗？",
    "I don't need a flower. But... fine. I'll have one.": "我不需要花。但……好吧。我拿一朵吧。",
    "You look like someone I knew. Have I seen your mother before?": "你看起来像我认识的一个人。我以前见过你母亲吗？",
    "My mama, she... she died long ago. I don't know much about her.": "我妈妈，她……她很久以前就去世了。我不太了解她。",
    "I think I remember her. She was an alchemist, often went gathering ingredients near Kynesgrove.": "我想我记得她。她是个炼金术士，经常去凯恩之林附近采集材料。",
    "Did she pick flowers like me? Can you... tell me more about her? Please?": "她也像我一样采花吗？你能……多告诉我一些关于她的事吗？求你了？",
    "Maybe one day, little one. For now, we have a journey to pursue.": "也许有一天吧，小家伙。但现在，我们还有旅途要赶。",

    # === aaJenassa6BanterControl ===
    "Child Banter Control": "孩童闲聊控制",
}

# Apply translations
def apply_translations(content, trans_map):
    updated_count = 0
    for original, translation in trans_map.items():
        # Escape XML special chars for the replacement
        translation_escaped = translation.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Pattern to find: <ESP>...<ORIGINAL>original</ORIGINAL>...<TRADUIT />... or <TRADUIT></TRADUIT>
        # We need to find the specific ESP block and update it
        pattern = r'(<ESP>(?:(?!<ESP>).)*?<ORIGINAL>' + re.escape(original) + r'</ORIGINAL>.*?</ESP>)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            # Try with lenient regex 
            pattern2 = r'(<ISP' if not match else None
            continue
        
        block = match.group(1)
        new_block = block
        
        # Replace <TRADUIT /> or <TRADUIT></TRADUIT> with <TRADUIT>translation</TRADUIT>
        new_block = re.sub(r'<TRADUIT\s*/>', f'<TRADUIT>{translation_escaped}</TRADUIT>', new_block)
        new_block = re.sub(r'<TRADUIT>\s*</TRADUIT>', f'<TRADUIT>{translation_escaped}</TRADUIT>', new_block)
        
        # Change STATUS from 0 to 90
        new_block = new_block.replace('<STATUS>0</STATUS>', '<STATUS>90</STATUS>')
        
        if new_block != block:
            content = content.replace(block, new_block, 1)
            updated_count += 1
    
    return content, updated_count

content, count = apply_translations(content, translations)

# Check for duplicates in the map (same original text appearing multiple times)
from collections import Counter
orig_counts = Counter(translations.keys())
dupes = {k: v for k, v in orig_counts.items() if v > 1}
if dupes:
    print(f"WARNING: Duplicate keys in translations: {dupes}")

print(f"Updated {count} entries")
print(f"Total translations provided: {len(translations)}")

with open(XML_PATH, 'w', encoding='utf-8-sig') as f:
    f.write(content)
print("Done!")

import os
import re

XML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FDE Jenassa Part 2_20F57570.xml")

with open(XML_PATH, 'r', encoding='utf-8-sig') as f:
    content = f.read()
translations = {
    # ========== aaJenassa8Idle (任务评论) ==========

    # --- 斯库玛贩子 ---
    "There used to be a few Skooma cartels in Morrowind. I suppose the ash storms made for good cover for their operations.":
        "晨风以前也有几个斯库玛贩子团伙。我猜那些灰烬风暴正好帮他们打了掩护。",

    "I've never taken Skooma myself. The stuff is poison for the mind.":
        "我自己从不碰斯库玛。那东西就是心智的毒药。",

    "Riften will be Riften, with or without the Skooma cartel.":
        "裂谷城就那样，有没有斯库玛贩子都一样。",

    "I don't know if it's the wolves, the Skooma, or just the cave itself - but it stinks worse than a mine full of sulfur.":
        "我不知道是那些狼、那些斯库玛、还是这洞本身——反正比硫磺矿还臭。",

    "The cartel is gone, and a new one will soon swoop in and claim their place - Riften will always be Riften.":
        "贩子没了，很快又有新的扑进来占了他们的窝——裂谷城永远是裂谷城。",

    # --- 伊利亚 ---
    "I've killed Hagravens before. Those witches always talk in honeyed lies before placing you on the altar. Let's stay guarded around this Illia.":
        "我以前杀过鹰身女巫。那些巫婆嘴上说得好听，回头就把你送上祭坛。对这个伊利亚，咱们还是留个心眼。",

    "Illia seems all innocent and trusting, but I promise you - no pure soul would call this tower her home.":
        "伊利亚看着天真又信任人，但我跟你保证——没有一个干净的灵魂会把这座塔叫作自己的家。",

    "At this point, Illia has killed more witches than necessary to win your trust. Either she's true to her words, or she's a better schemer than I know.":
        "到了这一步，伊利亚杀的女巫已经远远超过赢取你信任所需了。要么她说的句句属实——要么她就是我见过最会演戏的。",

    "I see I misjudged Illia when I first saw her. She truly intended to do the right thing.":
        "看来我第一眼见到伊利亚时看走眼了。她是真心想做正确的事。",

    # --- 狼头骨洞 / 狼女王 ---
    "So, the Steward dismissed the peasant's concerns about Wolfskull Cave. Once again, it's up to us to do the dirty work.":
        "所以，总管根本没把那农民对狼头骨洞的担忧当回事。又轮到我们来干脏活了。",

    "Do you feel it too? There's an ominous chill in these ruins, whispering of terrors from ages past.":
        "你也感觉到了吧？这遗迹里有股不祥的寒意，低语着来自远古的恐惧。",

    "Necromancers and their foul art, always the source of troubles. The peasant was right all along.":
        "死灵法师和他们那肮脏的勾当，永远是祸根。那个农民一直是对的。",

    "So, that's what those necromancers were after - a dead Septim queen who ruled over the dead... And she is now free, all because of their folly.":
        "原来如此，那些死灵法师想要的是——一个死了的塞普汀女王，一个统治死者的女王……就因为他们愚蠢，现在她自由了。",

    "The Septim queen was bound to return after her escape. Living or dead, their kind are always too proud to stay silent.":
        "塞普汀女王逃出来之后必然会卷土重来。不管活的死的，他们那种人永远骄傲到不肯闭嘴。",

    "Do you hear the dead's whispers? They're warning us away. Maybe it's the Septim queen's mind trick, cast out of fear.":
        "你听到死者的低语了吗？他们在警告我们离开。也许是塞普汀女王出于恐惧施展的把戏。",

    "Vampires and walking corpses. Is that all the undead queen can muster?":
        "吸血鬼和行尸。那个不死女王就拿得出这点东西？",

    "I grew weary of the Wolf Queen's voice. The dead should stay silent... Let's make it so again.":
        "我听够了狼女王的声音。死者就该沉默……让我们让她重新闭嘴吧。",

    "The whispers have ceased. As I predicted, it was the Wolf Queen's trick. She feared us... even if she acted all mighty and terrible.":
        "低语声停了。不出我所料，是狼女王的把戏。她怕我们……尽管她装得一副不可一世的样子。",

    "You'd think the Steward would be more generous to the vanquishers of Solitude's worst villain. I hope the catacomb's loot was good, at least.":
        "你可能会觉得，总管对消灭了孤独城最凶恶反派的功臣，会出手大方些。至少希望地下墓穴里的战利品还不错。",

    # --- 墨索尔 ---
    "A house burned right in the middle of the town, and no one does anything about it - as if it's nothing out of the ordinary.":
        "镇子正中央一座房子烧了，没一个人管——好像这根本不算什么怪事。",

    "With all the terrors that lurk in the marsh, the peasants chose to fight a simple wizard, of all things. That's Skyrim for you.":
        "沼泽里藏着那么多可怕的东西，结果那些农民偏偏挑一个普普通通的巫师来对付。这就是天际。",

    "Playing hide and seek with a ghost is hardly a fair game - unless she wants to be found.":
        "跟一个鬼魂玩捉迷藏，这游戏本来就不公平——除非她自己想让你找到。",

    "The truth of Morthal's terror is unveiled at last. Maybe the town can be saved after all.":
        "墨索尔恐怖的真相终于揭开了。也许这镇子还有救。",

    "The vampires are destroyed, but the air grows thickened with death. I wonder if we've truly quelled the evil, or only removed its competition.":
        "吸血鬼被灭了，但空气里的死气越来越重。我在想——我们是真的平息了邪恶，还是只是替它清掉了竞争对手。",

    # --- 乌鸦岩矿井 ---
    "So I guessed correctly. A Nord ruin slumbers beneath Raven Rock's mine. Now, let's see if it's as horrifying as the East Empire Company believed.":
        "果然让我猜中了。乌鸦岩矿井下面沉睡着一座诺德遗迹。现在，让我们看看它是不是真像东帝国公司以为的那么可怕。",

    "A skeleton, dead for centuries. No doubt, that's the old Imperial's great-grandfather.":
        "一具死了几百年的骷髅。没跑，就是那个老帝国人的曾祖父。",

    "Here we are... the true secret of Raven Rock's mine. The source of all the terror in this ruin.":
        "到了……乌鸦岩矿井真正的秘密。这座遗迹里所有恐惧的源头。",

    "It has been a remarkable journey, but I long for the blue sky already. Well, no blue sky on Solstheim, perhaps, but any sky would be an improvement.":
        "这趟旅程确实不一般，但我已经开始想念蓝天了。好吧，索瑟姆也许没有蓝天——但只要是天空，就是种改善。",

    "Finally! Breathable air without the stench of the centuries-dead.":
        "终于！能喘口气了，没有那些陈年尸臭。",

    # --- 黑荆棘 ---
    "To be so naive that he'd deal with Maven Black-Briar's failure of an offspring? Maybe Louis deserves to eat his loss.":
        "天真到去跟玛雯·黑荆棘那个废物儿子做交易？路易斯亏了也是活该。",

    "If I ever had a son like Sibbi Black-Briar, I'd put him on a boat to Atmora and never look back.":
        "要是我有个儿子像西比·黑荆棘那样——我直接把他扔上去阿特莫拉的船，头也不回。",

    "I almost pity Maven Black-Briar. For all her power and schemes, she stands to lose her empire to an offspring like Sibbi.":
        "我几乎有点可怜玛雯·黑荆棘了。她费尽心机爬到今天，结果自己的帝国可能毁在西比这种后代手里。",

    "Good move telling that Breton's scheme to Maven Black-Briar. She would've found out anyway... No reason to put ourselves at risk for a corpse.":
        "把那个布莱顿人的阴谋告诉玛雯·黑荆棘——这步走得对。她迟早也会发现的……没必要为一具死尸把我们自己搭进去。",

    "All this drama over a horse, and it's not even that handsome a steed. What a disappointment.":
        "闹出这么多破事就为一匹马，而且那匹马也算不上多好看。真让人失望。",

    # --- 黎明守卫 ---
    "Bear hunting isn't what I expected to be a vampire hunter's task.":
        "猎熊可不是我预想中吸血鬼猎人该干的活。",

    "I suggest we simply head to the nearest Dwemer ruin for her gyro. No point wasting time on a wild chase amidst all this mud.":
        "我建议我们直接去最近的锻莫遗迹找她的陀螺仪。在这片烂泥地里瞎追纯属浪费时间。",

    "So, we have ourselves a Dwemer expert. Slaughtering vampires with their steel just might elevate my art.":
        "看来我们找到了一位锻莫专家。用他们的钢铁来屠杀吸血鬼——说不定能提升我的艺术。",

    "Seems to me Isran never even liked these 'old friends' of his. Such unifying force he'll make for.":
        "我看伊斯朗压根就不喜欢他这些'老友'。他可真能团结人啊。",

    "I wonder what this Florentius is capable of. Priest of Arkay? What is he going to do - exorcise the vampires? Or pray for their souls?":
        "我倒想知道这个弗洛伦修斯有多大本事。阿凯的祭司？他打算怎么着——给吸血鬼驱魔？还是为他们的灵魂祈祷？",

    "Does Florentius... 'talk' to his god? Now I see why the people had that hesitant tone when they asked you to find him.":
        "弗洛伦修斯……能跟他的神'说话'？现在我明白那些人请你去找他的时候，为什么语气那么犹豫了。",

    # --- 梭默 / 魔冰 ---
    "Two elves who kidnapped a blacksmith? They're either from Raven Rock or the Thalmor - and I assure you, my people have no interest in Nord armor.":
        "两个精灵绑架了一个铁匠？要么是乌鸦岩来的，要么是梭默——我跟你保证，我族人对诺德盔甲可没兴趣。",

    "I thought this isle would be the last place to interest a Thalmor. Surely, there are greener pastures to conquer or plunder.":
        "我以为这座岛是梭默最不可能感兴趣的地方。肯定有更好的地方值得他们征服或掠夺吧。",

    "I wonder what magic this 'Stalhrim' contains, so powerful that it made the Thalmor come all this way from Alinor.":
        "我在想这'魔冰'里到底有什么魔力，能让梭默从艾琳诺千里迢迢赶来。",

    "I never expected that we'd do business with the Thalmor, but whoever pays well, I suppose.":
        "我没想到有一天我们居然会和梭默做交易——不过，谁出价高就跟谁做，我想是这样。",

    "I've started to imagine how a Thalmor would look in Stalhrim armor. A blue Altmer would look like quite the spectacle, don't you think?":
        "我开始想象一个梭默穿上魔冰盔甲会是什么样子了。蓝皮肤的高精灵——那场面一定很壮观，你不觉得吗？",

    # --- 历史学家 / 帝国堡垒 ---
    "It's not my first time escorting a historian through an old ruin, though my first was inconceivably more talkative... and annoying.":
        "这不是我第一次护送历史学家逛遗迹了。不过上一个话多得吓人……而且烦人。",

    "The Empire built fortresses like this to last. Considering its age, it still holds up well.":
        "帝国建的堡垒就是结实。以它的岁数来说，居然还这么完好。",

    "I could get used to this place. The darkness gives me a warm comfort.":
        "我能习惯这个地方。黑暗让我感到温暖又安心。",

    "With the wars and the debts, the Jarls and the generals have gradually lost control of their forts.":
        "仗打得多了，债欠得多了，领主和将军们慢慢就管不住自己的堡垒了。",

    "Imperial forts like this used to dot the landscapes of Morrowind. After the Red Year, they've mostly crumbled into dust.":
        "像这样的帝国堡垒，曾经遍布晨风的土地。红年之后，它们大多已经化为尘土了。",

    "I once wiped out a fortress in a single night. Poisoned wine does the trick every time - that, and my silent steps.":
        "我曾经一夜之间屠了一座堡垒。毒酒——每次都管用，再加上我没声的脚步。",

    # --- 孤独城 ---
    "Solitude is one of the few Skyrim cities that agree with me.":
        "孤独城是少数几个让我觉得合拍的天际城市。",

    "Solitude values real art, yet it's never lacking in schemes and shadows. This just might be the perfect city for someone like me.":
        "孤独城珍视真正的艺术——但这里的阴谋和暗影也从来不缺。这也许正是适合我这种人待的地方。",

    "I may enjoy Nord mead, but Solitude's fine wine is unlike any other.":
        "我确实喜欢喝诺德蜜酒，但孤独城的葡萄酒，别处喝不到那个味。",

    # --- 阿达拉 / 长笛 ---
    "Adara and I used to play with the instruments at the day's end. So many fond memories we had with the flutes...":
        "阿达拉和我以前常在一天结束时演奏乐器。那些笛子——那么多美好的回忆……",

    "Maybe we can play with the flute later, like I used to with Adara.":
        "也许我们待会可以吹吹笛子，就像我以前和阿达拉那样。",

    "One can make such great art with a flute.":
        "一支笛子也能创造出如此伟大的艺术。",

    # --- 龙 ---
    "I wonder if the dragons feel fear. That must be the only thing they know when you devour their souls.":
        "我在想龙会不会感受到恐惧。当你吞噬它们灵魂的时候，它们唯一能感受到的，大概就是那个了。",

    "I've been struck by the soul trap spell a few times. When you absorb the dragons' souls, I can only imagine they feel the agony tenfold.":
        "我被灵魂陷阱命中过几次。你吸收龙魂的时候，我只能想象——它们的痛苦是你的十倍。",

    "So, the dragon god made you to kill his children and eat their souls? I've seen worse parents.":
        "所以，龙神造你出来，就是为了杀他的孩子、吃他们的灵魂？我见过更差劲的父母。",

    "If you think the dragons are irritating, then you don't know the cliff racers. Those nasty critters never have the decency to stay grounded.":
        "如果你觉得龙很烦，那你还没见识过悬崖鸟。那种恶心的东西从来不肯老老实实待在地上。",

    "The dragons breathe magic as effortlessly as we spit. It would be wise to take precautions against their ice or fire.":
        "龙吐息就像我们吐口水一样轻松。最好提前做好准备，防着它们的冰和火。",

    # --- 洗澡 ---
    "I suppose this place can't get any filthier... Bathing time can't come soon enough.":
        "我想这地方已经脏到头了……真想赶紧洗个澡。",

    "The longer we stay here, the more we smell like this place's denizens. I suggest we find the nearest pond soon as we leave this accursed place.":
        "我们在这待得越久，身上就越像这里的住户。我建议一离开这个鬼地方就去找最近的水塘。",

    "A thorough bath always does us adventuring type wonders.":
        "好好洗个澡，对我们这些成天在外跑的人来说，总有奇效。",

    "Why don't we have a long, warm bath - just you and me, undisturbed by anything.":
        "我们何不好好洗个热水澡——就你和我，谁也别来打扰。",

    "We have a long road ahead. A quick bath in a nearby pond ought to refresh our spirits... Not to mention it'll get rid of the odor.":
        "前路还长。在附近池塘里冲个凉，应该能让我们精神起来……更别提把身上的味去掉。",

    # === aaJenassa8WorkingFor0 (东帝国公司雇佣关系) ===
    "If you're employed by the East Empire Company, how can you still work for me?":
        "你既然受雇于东帝国公司，怎么还能为我工作？",

    "To answer it simply, they don't require my service every moment.":
        "简单说——他们不是时时刻刻都需要我。",

    "I'm free to pursue other work while they have no need for me. The more contracts I complete, the sooner I can repay this debt.":
        "他们用不着我的时候，我可以自由接别的活。我完成的合同越多，就能越早还清这笔债。",

    "But where they need my service, I'll be obligated to abandon all other work to serve their interests. Such are the terms of their 'offer'.":
        "但只要他们需要我，我就有义务放下所有其他工作，为他们办事。这就是他们那个'提议'的条款。",

    # === aaJenassa8WorkingFor1 ===
    "That sounds only fair.":
        "听起来还算公平。",

    "Fair to the Company, as always.":
        "对公司公平罢了——一向如此。",

    # === aaJenassa8WorkingFor2 ===
    "Do they pay you when they don't need you?":
        "他们不用你的时候，也付你钱吗？",

    "If you wouldn't pay for a mead you didn't drink, then why would they pay for a service they didn't use?":
        "你不会为没喝的蜜酒付钱——那他们为什么要为没用的服务付钱？",

    # === aaJenassa8WorkingFor3 ===
    "That sounds harsh.":
        "听起来真够苛刻的。",

    "When an Imperial sets the terms, they've already calculated all their gains and losses.":
        "帝国人定条件的时候，早就把自己的得失都算得一清二楚了。",

    # === aaJenassa8WorkingFor4 (长篇对话 - 乔丹/Jordis/伊利亚) ===
    "Wait, what will happen to us if they summon you now?":
        "等等，要是他们现在把你召回去，我们怎么办？",

    "Then I'll have no choice but to return to their service until their need for me expires. Unless you wish to come along, that is.":
        "那我就只能回去，直到他们不再需要我为止。当然——除非你愿意一起来。",

    "If not... I suppose the least I could do is to give you a refund.":
        "如果不来的话……我想我至少还能把钱退给你。",

    "Why are you giving me that look, Jenassa?":
        "你为什么那样看着我，简娜莎？",

    "It's nothing.":
        "没什么。",

    "No, I can tell something's on your mind. You looked just like Faida when she lost my brother.":
        "不，我看得出来你有心事。你刚才的表情，就像法伊达失去我哥哥时那样。",

    "Well, I... You look like someone from my past, is all.":
        "嗯，我……你看起来像我过去认识的一个人，就这个。",

    "Ah, I'd say I could be that person, but I'm certain I'd remember you. After all, you leave quite the impression on everyone you meet.":
        "啊，我倒想说我可能就是那个人——但我肯定我会记得你。毕竟，你给每个见过你的人都留下了深刻的印象。",

    "No, you can't possibly be her... She died thirty years ago.":
        "不，你不可能是她……她三十年前就死了。",

    "Jenassa, you mentioned I looked like someone from your past... who died thirty years ago? Who was that?":
        "简娜莎，你说我看起来像你过去认识的一个人……三十年前就死了？那是谁？",

    "She was my first love in Skyrim. The one who taught me that warmth exists even in the frozen north.":
        "她是我在天际的第一个爱人。是她教会我——即使在冰封的北方，也有温暖存在。",

    "Oh. I didn't realize she was your... I mean, my condolences.":
        "哦。我不知道她是你……我是说，请节哀。",

    "Thank you.":
        "谢谢。",

    "She was a bard - the most gifted of her class. When we were together, she'd always perform the world's most beautiful art for me.":
        "她是个诗人——那是她那一行里最有天分的人。我们在一起的时候，她总是为我演奏这世上最美的艺术。",

    "Well, I'm no bard - the far opposite of one, if that's what you're asking.":
        "嗯，我不是什么诗人——恰恰相反，如果你问的是这个。",

    "It's fine. I have found an artist just as great as she was.":
        "没关系。我已经找到了一个和她一样了不起的艺术家。",

    "And I'm not asking you to be one. We are each who we are... to presume otherwise brings nothing but sorrow.":
        "我也没有要求你成为那样的人。我们各自做自己就好……以为别人应该是什么样子，只会带来痛苦。",

    "So, Jenassa - what's with your obsession over 'art'?":
        "那么，简娜莎——你为什么对'艺术'这么执着？",

    "The world would be a colorless place without it, no?":
        "没有艺术，这世界就失去色彩了，不是吗？",

    "Yeah. But from the sound of it, the only color of your art is bloody red!":
        "是啊。但听你这么说，你的艺术唯一的颜色——就是血红色吧！",

    "Well, we each have our preferences. Some play their lutes... while I stick to my sword.":
        "好吧，我们各有各的喜好。有人弹鲁特琴……而我坚守我的剑。",

    "But what is your art, Jordis - if you have one?":
        "那你的艺术是什么，乔迪斯——如果你有的话？",

    "Well, not singing or dancing, that's for sure.":
        "嗯，反正不是唱歌也不是跳舞，这个可以肯定。",

    "You look happy, Jenassa.":
        "你看起来很幸福，简娜莎。",

    "All because of your Thane.":
        "全都是因为你的领主。",

    "You didn't look like the type to settle down... But it suits you. Now it's as if I'm seeing my brother and Faida again, ever the joyful couple.":
        "你看起来不像那种会安定下来的人……但这很适合你。现在我仿佛又看到了我哥哥和法伊达，永远那么幸福的一对。",

    "Seeing people from your past, Jordis?":
        "看到了过去认识的人，乔迪斯？",

    "Yeah. You got me!":
        "是啊。被你看穿了！",

    "Tell me something about your mother, Illia.":
        "跟我说说你母亲的事吧，伊利亚。",

    "Why? I didn't realize you cared.":
        "为什么？我不知道你居然还关心这个。",

    "My own mother died to save me from the An-Xileel... Were I in your place, I could never bring myself to hurt her... Let alone kill her.":
        "我自己的母亲为了从安-希雷尔手下救我而死的……如果我是你，我绝对下不了手伤害她……更别说杀了她。",

    "You were lucky to have your mother then, Jenassa.":
        "那你那时候很幸运，还能有你的母亲，简娜莎。",

    "Maybe at one point, mine would've made the same sacrifice. But after years of corruption, I doubt she still loved anything besides power.":
        "也许曾经，我的母亲也愿意做出同样的牺牲。但经过这么多年的堕落，我怀疑她除了权力，已经不再爱任何东西了。",

    "Was that why you struck her down?":
        "所以那就是你打倒她的原因？",

    "I don't know. At that point, all I knew was that I must stop the coven and their human sacrifice.":
        "我不知道。那一刻，我只知道我必须阻止那个女巫团和他们的人祭。",

    "Maybe I would've chosen differently had my mother shown a bit more warmth. But then, she wouldn't be that power-mad Hag we slew.":
        "如果我母亲曾表现出哪怕一丝温情，也许我会做出不同的选择。但那样的话——她就不会是那个我们杀死的、被权力冲昏了头的妖婆了。",

    "Tell me something about Morrowind, Jenassa.":
        "跟我说说晨风的事吧，简娜莎。",

    "You'll have to be more specific with your question.":
        "你得问得再具体一点。",

    "Well, specific... how?":
        "嗯，具体……怎么个具体法？",

    "Morrowind is a big place. Dozens of cities, hundreds of species, with five noble houses each trying to kill the others every day.":
        "晨风是个很大的地方。几十座城市，数百个物种，五个贵族家族天天都在互相残杀。",

    "I didn't know what to ask, because I knew nothing at all about the world outside the Tower. But you just gave me something to work with... Thanks.":
        "我不知道该问什么，因为塔外面的世界我什么都不知道。但你刚才给了我一些能了解的东西……谢谢。",

    "Honestly, why don't you just go read a book? Surely, the witches taught you to read?":
        "说实话，你干嘛不自己去读本书呢？那些女巫总该教过你认字吧？",

    "Illia - I noticed your disgust when I prayed to the Three earlier.":
        "伊利亚——我注意到了，刚才我向三神祈祷时，你露出了厌恶的表情。",

    "You were praying to the Daedra.":
        "你在向迪德拉祈祷。",

    "Who I worship is my business. Why don't you mind your sorceries, witch?":
        "我信仰谁是我的事。你管好你的巫术就行了，女巫。",

    "I was doing exactly that - until you had to bring it up.":
        "我正是在这么做——直到你非要把这事挑明。",

    "Good. Then we understand each other.":
        "很好。那我们互相理解了。",

    # === aaJenassa8MS060 (狼头骨洞) ===
    "What do you think about Wolfskull Cave?":
        "你怎么看狼头骨洞？",

    "I think the Steward is a fool to dismiss that villager's warning - but at least, he has half the wisdom to hire professionals to investigate.":
        "我觉得总管是个蠢货，根本没把那个村民的警告当回事——但至少他还有一半脑子，知道雇专业人士来调查。",

    "I just hope he pays well.":
        "我只希望他出手够大方。",

    # === aaJenassa8MS061 ===
    "It's not about the money for me. It's about saving people.":
        "对我来说不是钱的问题。是要救人。",

    "A thousand people would fight for a thousand reasons. In the end, the only thing that matters is the job gets done.":
        "一千个人会为一千种理由而战。到头来，唯一重要的——是活儿干完了。",

    # === aaJenassa8MS062 ===
    "Why wouldn't the Steward pay well?":
        "总管怎么会不肯出够钱？",

    "Solitude is the pearl of the north, so I don't doubt that its coffer has more than enough for two hired blades.":
        "孤独城是北方的明珠，我一点也不怀疑它的金库够付两个佣兵。",

    "But the Steward sees Wolfskull Cave's rumors as a farce. That's why he didn't even care to send reinforcements.":
        "但总管把狼头骨洞的传闻当成一场闹剧。所以他连派援军都不上心。",

    "A small pouch for our time, that's the payment he expects to afford.":
        "一小袋金币打发我们的时间——那就是他打算付的报酬。",

    # === aaJenassa8MS063 ===
    "With the war going on, Solitude really can't afford to investigate mere rumors.":
        "仗还在打呢，孤独城确实抽不出人去调查区区谣言。",

    "Isn't that the most convenient excuse everyone uses these days.":
        "这难道不是如今每个人都用的最顺手的借口吗？",

    "A farm was raided by bandits? The soldiers are off at the war camp. The city's water needs to be sanitized? The gold is all in the war chest.":
        "农场被强盗洗劫了？——士兵们都在前线营地呢。城里的水需要净化了？——金币全在军需箱里呢。",

    "Maybe the Jarls are more interested in painting the map than governing their people.":
        "也许领主们更热衷于在地图上涂抹疆域，而不是好好治理他们的子民。",

    # === aaJenassa8MS064 ===
    "The Steward should've done more to help his people.":
        "总管本该为他的子民做更多事的。",

    "The Nords are all about their honor, and nothing's more honorable than killing others on the battlefield.":
        "诺德人满嘴都是荣誉，而没有什么比在战场上杀敌更荣誉的了。",

    "Where's the honor in keeping some peasants happy?":
        "让几个农民过上好日子——荣誉又在哪里？",

    # === aaJenassa8MS06302 ===
    "Let's go.":
        "走吧。",

    "Either way, the Steward's thoughts are of little consequence to us. We'll just keep doing what we always do best.":
        "不管怎样，总管怎么想对我们来说无关紧要。我们只管继续做我们最擅长的事。",

    # === aaJenassa8MS064a ===
    "Falk Firebeard doesn't seem like a warmonger to me.":
        "法尔克·火胡在我眼里不像个好战分子。",

    "Yet those around him are all sounding the war drums. Even if the Steward wanted to care, the warmongers wouldn't have permitted him.":
        "可围着他的人全都在敲战鼓。就算总管想关心——好战分子也不会允许他。",

    # === aaJenassa8MS064b ===
    "Enough with your cynicism. I'll hear no more of it.":
        "够了，你的愤世嫉俗我听够了。",

    "Maybe don't ask for my thoughts next time, then.":
        "那你下次就别问我的看法。",

    # === aaJenassa8MS064c ===
    "And you care about the peasants?":
        "那你在乎那些农民吗？",

    "Obviously no. I merely made an observation after spending decades on this land.":
        "显然不在乎。我只不过在这片土地上待了几十年，随口说了一句观察罢了。",

    # === aaJenassa8MS064d ===
    "They're all short-sighted fools.":
        "全都是目光短浅的蠢货。",

    "If they see any further beyond the glory at hand, it would be a betrayal of their proud heritage, no?":
        "要是他们能看到眼前的荣耀之外的东西——那岂不是背叛了他们引以为傲的传统，你说是不是？",

    # === aaJenassa8MS070 (灯塔) ===
    "What do you think about Solitude's lighthouse?":
        "你怎么看孤独城的灯塔那件事？",

    "You mean the Argonian pirate's 'proposition'.":
        "你是说那个亚龙人海盗的'提议'吧。",

    "I don't know why you're even considering to entertain him. If I know pirates, they're never going to share their spoil.":
        "我不明白你为什么还在考虑跟他周旋。以我对海盗的了解——他们绝不会把战利品分给别人。",

    # === aaJenassa8MS0702 ===
    "Besides - should an East Empire Company vessel be wrecked after this, then the situation with my debtor will become most... peculiar.":
        "再说——要是之后有东帝国公司的船在这里遇难——那我跟债主之间的事可就变得……微妙了。",

    "Besides - should an East Empire Company vessel be wrecked after this, then we'll earn the ire of Cyrodiil's greatest power.":
        "再说——要是之后有东帝国公司的船在这里遇难——那我们就会招来赛洛迪尔最强大的势力的怒火。",

    "I may no longer be chained to them, but their eyes are always present in Haafingar. Many more like me are still at their disposal.":
        "我或许已经不再被他们拴着了，但在哈芬加尔，他们的眼线无处不在。还有很多像我一样的人——仍然受他们支配。",

    "The Legion may fight honorably... but the Company does not.":
        "军团也许会光明正大地战斗……但公司不会。",

    # === aaJenassa8MS071 ===
    "Don't worry, I'll ignore the Argonian pirate.":
        "放心吧，我不会理那个亚龙人海盗的。",

    "Your wisdom is greater than you realized.":
        "你的智慧比你自己以为的还要大。",

    # === aaJenassa8MS072 ===
    "I'm interested to see this through.":
        "我想把这件事看到底。",

    # === aaJenassa8MS073 ===
    "That pirate is a fool. All he spouts is rot.":
        "那个海盗就是个蠢货。从他那张嘴里吐不出象牙。",

    "Well. Now that you mention it... What kind of criminal would recruit an accomplice on the street?":
        "好吧。既然你提到了……什么罪犯会在大街上招募同伙？",

    "Only the foolish or the careless, I'd imagine - and neither make for good schemers.":
        "我想只有傻子或者粗心鬼才干得出来——而这两样人都成不了好的阴谋家。",

    # === aaJenassa8MS074 ===
    "There are riches awaiting us in this job. We just have to go and grab it.":
        "这活儿里有财宝等着我们。去拿就是了。",

    # === aatherewillcome ===
    "There will come a day your curiosity leads us to safe havens and good fortune, but I see that day is still far away.":
        "总有一天，你的好奇心会带我们去到安全的避风港和好运——但在我看来，那一天还早着呢。",

    # === aaJenassa8MS140 (墨索尔) ===
    "What do you think about Morthal?":
        "你怎么看墨索尔？",

    "Normally, I appreciate silence and solitude - but in Morthal, even the silence grows suffocating.":
        "通常来说，我喜欢安静和独处——但在墨索尔，连安静都压得人喘不过气。",

    "A house was burnt down and a family ruined, yet the suspect still walks freely under the sun, and the town goes about its business as usual.":
        "房子烧了，家毁了——嫌疑人却还在光天化日之下自由走动，镇上的人也照常过他们的日子。",

    "It's as if that's the norm here. Still, indifferent... and dead.":
        "好像这就是这里的常态似的。死寂，冷漠……没有一点生气。",

    # === aaJenassa8MS141 ===
    "I intend to unravel the mystery here.":
        "我打算揭开这里的谜团。",

    "Unravel the mystery, or upset the design of the forces that be?":
        "揭开谜团，还是搅乱当权者的布局？",

    # === aaJenassa8MS142 ===
    "Maybe we should get away while we can.":
        "也许趁还来得及，我们该走。",

    "Wise caution can often be confused with cowardice.":
        "明智的谨慎常常被人误认为是懦弱。",

    "In my view, there's no point saving a place that doesn't care to be saved.":
        "依我看，拯救一个不在乎自己有没有救的地方——毫无意义。",

    "Let's go then. I can hardly wait to breathe freely again.":
        "那走吧。我快等不及想好好喘口气了。",

    # === aaJenassa8MS143 ===
    "The burnt family demands justice.":
        "那个被烧毁的家庭需要公道。",

    "I see your point. It may not save a soul... but the dead will find some small comfort if we avenge them.":
        "我明白你的意思。也许救不了谁……但如果我们替他们报了仇，死者也能得到一丝安慰吧。",

    # === aaJenassa8MS14102 ===
    "I don't know what we expect to find in this town, or what yet awaits us in the marsh.":
        "我不知道我们指望在这镇上找到什么，也不知道沼泽里还有什么在等着我们。",

    "But if Death is looming over Morthal, then I say we feed it what it desires - the blood of those responsible for the terror.":
        "但如果死神正笼罩着墨索尔——那我说，就喂给它想要的：那些对这起恐怖事件负责的人的鲜血。",

    # === aaJenassa8RR030 (乌鸦岩矿井秘密) ===
    "What do you think about Raven Rock Mine's secrets?":
        "你怎么看乌鸦岩矿井的秘密？",

    "Knowing how the East Empire Company operates, it wouldn't surprise me that they've concealed secrets beneath the mine.":
        "以我对东帝国公司行事风格的了解，他们在矿井下面藏了秘密——我一点也不意外。",

    "It exists to generate wealth for the noble houses. Everything else is expendable for that goal.":
        "这座矿井的存在就是为了给贵族家族创造财富。除此之外的一切，为了这个目标都可以牺牲。",

    "For them to shut down the mine, I see two explanations - one, they stood to gain much from what lied beneath, so they kept it sealed for themselves.":
        "他们关闭矿井，我看有两个解释——第一，下面的东西能让他们大赚一笔，所以他们把它封起来留给自己。",

    "And two, they stood to lose much more if they let the mine be. That means whatever they'd hidden beneath... is best left forgotten.":
        "第二，如果让矿井继续开下去，他们失去的会多得多。也就是说，不管他们藏在下面的是什么……最好就此遗忘。",

    # === aaJenassa8RR031 ===
    "What do you think they've hidden down there?":
        "你觉得他们下面藏了什么？",

    "I doubt even the Vici themselves knew, let alone a mere sellsword they employed.":
        "我怀疑连维西家族自己都不清楚，更别说他们雇来的卖命佣兵了。",

    "I honestly don't know.":
        "老实说，我不知道。",

    # === aaJenassa8RR03102 ===
    "If I were to entertain a guess, it'd either be a Nordic ruin, full of undead longing for flesh - or a Dwemer ruin, with their steels of death.":
        "如果非要我猜的话——要么是一座诺德遗迹，里面全是渴望血肉的亡灵——要么是一座锻莫遗迹，遍布他们那致命的钢铁。",

    "The Company might not care much for things besides profit, but it still operated under the Emperor's grace.":
        "公司除了利润之外或许不关心别的——但它终究是在皇帝的恩典下运作的。",

    "Should an army of undead swarm the town, the Emperor - and by extension, the Company - would have much to answer for.":
        "如果一支亡灵大军涌向城镇，皇帝——连带着公司——都难逃其咎。",

    # === aaJenassa8RR032 ===
    "Do you think we should leave the mine alone then?":
        "那你是觉得我们不该管这个矿井？",

    "I believe we should delve deeper and see what the Company has hidden.":
        "我认为我们应该深入下去，看看公司到底藏了什么。",

    "Where there are risks, there are opportunities. Whatever secret lies below, it is worth protecting to the Company.":
        "哪里有风险，哪里就有机会。不管下面藏着什么秘密——那东西值得公司如此守护。",

    "That either means it can make us rich, or it can change the world.":
        "那要么意味着它能让我们发财，要么意味着它能改变世界。",

    # === aaJenassa8RR033 ===
    "Let's go.":
        "走吧。",

    "The East Empire Company's secrets await.":
        "东帝国公司的秘密在等着我们。",

    # === aaJenassa8Betray0 ===
    "If someone pays you to, would you ever betray your patron?":
        "如果有人出钱，你会背叛你的雇主吗？",

    "I suppose this question arose from my profession.":
        "我想这个问题是冲着我的职业来的吧。",

    "Who put such thoughts in you? I suppose it's that sorry failure Lydia.":
        "谁让你有这种想法的？我猜是那个可怜的废物莱迪亚吧。",

    # === aaJenassa8Betray02 ===
    "I may work for gold, but I will never sully my art by betraying those who afforded it.":
        "我或许为金币而工作——但我绝不会用背叛来玷污我的艺术，背叛那些花钱让我施展艺术的人。",

    # === aaJenassa8Betray03 ===
    "Learn to appreciate my art, unless you want this fear to come true... when our contract expires.":
        "学着欣赏我的艺术吧——除非你想让这个担心成真……等我们的合同到期的时候。",

    "After all the time we've spent together, I thought you had started to appreciate my art. I guess I was wrong.":
        "一起经历了这么多，我以为你已经学会欣赏我的艺术了。看来是我错了。",

    # === aaJenassa8Betray1 ===
    "I'm sorry, Jenassa. I didn't mean that.":
        "对不起，简娜莎。我不是那个意思。",

    "Very well. Let's put those thoughts behind us for good.":
        "很好。那就把这些想法彻底扔到脑后吧。",

    # === aaJenassa8Betray2 ===
    "Don't the Dunmer like treachery?":
        "暗精灵不是最喜欢背信弃义吗？",

    "Against enemies, not those whose coin feeds me.":
        "是对敌人——不是对那些用钱养活我的人。",

    "Why don't you stay silent for a while, until you've grown a mind of your own, at least.":
        "你不如先安静一会儿——至少等你自己长了脑子再开口。",

    # === aaJenassa8Betray3 ===
    "We'll see.":
        "走着瞧吧。",

    "I guess we will.":
        "看来也只能这样了。",

    # === aaJenassa8Betray4 ===
    "Don't bring Lydia into this.":
        "别把莱迪亚扯进来。",

    "So it's your own thought, then. Very well... I see now how you truly look at me.":
        "所以，这是你自己的看法了。很好……我现在知道你真正是怎么看我的了。",

    # === aaJenassa8SV010 (历史学家) ===
    "It's not your first time escorting a historian?":
        "你不是第一次护送历史学家了吧？",

    "The first time I took on such a contract, it was in another Nord ruin. I reckon it was even bigger than this one.":
        "我第一次接这种活，是在另一座诺德遗迹里。我估摸着比这座还要大。",

    "Supposedly, that ruin was built above an ancient Falmer burial ground, which the Nords defiled and destroyed during their conquests.":
        "据说那座遗迹建在一处古老的雪精灵墓地上方——诺德人在征服途中把它玷污并摧毁了。",

    "This historian believed the Falmer ghosts had possessed the Draugr there, and intended to prove it.":
        "那个历史学家相信雪精灵的鬼魂附在了那里的尸鬼身上，打算以此证明自己的理论。",

    # === aaJenassa8SV011 ===
    "Was that historian an elf?":
        "那个历史学家是精灵？",

    "He was a full-blooded Nord. Dressed like one, drank like one, even breathed like one.":
        "纯血的诺德人。穿得像诺德人，喝得像诺德人，连喘气都像诺德人。",

    "Only thing that was different? He claimed his 28th great-grandmother was the last Falmeri princess, which made him the true heir to their legacy.":
        "唯一不一样的地方？他声称他的第28代曾祖母是最后一位雪精灵公主——所以他才是雪精灵遗产的真正继承人。",

    # === aaJenassa8SV012 ===
    "What happened in that ruin?":
        "那座遗迹里后来怎么了？",

    "What happened was that he kept yapping about the ancient Falmer and their glory, how the Nords' revenge for Saarthal was too harsh, and so on.":
        "后来啊——他一直在喋喋不休地讲古老的雪精灵和他们的辉煌，说什么诺德人对萨瑟尔的报复太过分了，诸如此类。",

    "After a certain point, I simply stopped paying attention. He gave the ruin many more pieces of his mind, no doubt.":
        "到后来，我就干脆不听了。他肯定对那座遗迹发表了很多高论。",

    # === aaJenassa8SV012a ===
    "I thought you'd agree with him.":
        "我以为你会同意他的说法。",

    "Because I'm an elf?":
        "就因为我是精灵？",

    "We Dunmer hardly even care about our own brethren, until the circumstances drive us to band together.":
        "我们暗精灵连自己的同胞都几乎不怎么放在心上——除非情况逼得我们必须团结。",

    "All I can say is that the Falmer got their fate, and history is already written.":
        "我只能说——雪精灵得到了他们应得的命运，而历史已经写就。",

    # === aaJenassa8SV012b ===
    "What a fool. The Falmer are gone, only the monsters are left.":
        "真是个蠢货。雪精灵早就没了，只剩下那些怪物了。",

    "My thought exactly. But why should an artist argue with her patron?":
        "我也是这么想的。不过——一个艺术家何必跟出钱的人争辩呢？",

    # === aaJenassa8SV012c ===
    "Did the historian get what he was looking for in the Nord ruin?":
        "那个历史学家在诺德遗迹里找到他想要的东西了吗？",

    "Apparently no. There were plenty of Draugr... but besides a Wispmother and a few dozens of her spawn, we found no trace of the Falmer.":
        "显然没有。里面尸鬼倒是不少……但除了一个雾母和她的几十个崽子，雪精灵的踪迹我们半点也没找到。",

    "He was devastated, but no matter. All I cared was getting my hard-earned pay.":
        "他整个人都垮了，不过无所谓。我只在乎拿到我辛苦挣来的报酬。",

    # === aaJenassa8SV013 ===
    "Do you think Tharstan is better than him?":
        "你觉得萨斯顿比他强吗？",

    "Tharstan's talkative, sure... but at least he also tries to be helpful.":
        "萨斯顿确实话多……但他至少还会帮忙。",

    "As far as historians go, he might make for the best patron of his kind.":
        "就历史学家来说，他可能算是这类人里最好的雇主了。",

    # --- 孩子对话 ---
    "I was once like you, young one.":
        "我也曾和你一样，小家伙。",

    "Once like me?":
        "也曾和我一样？",

    "After my parents died... the Argonians took my village and drove me to the cities.":
        "我父母死后……亚龙人占领了我的村子，把我赶到了城里。",

    "I did all sorts of things to survive, even begged... like you.":
        "我做过各种各样的事来活下去——甚至讨过饭……就像你一样。",

    "But you are now a strong lady.":
        "可你现在是一位坚强的女士了。",

    "Because I never gave up the fight, little one. And neither should you.":
        "因为我从未放弃过——小家伙。你也不该放弃。",

    "My lady... would you like a flower?":
        "这位女士……您想要一朵花吗？",

    "I don't need a flower. But... fine. I'll have one.":
        "我不需要花。不过……好吧。我拿一朵。",

    "You look like someone I knew. Have I seen your mother before?":
        "你看起来像我认识的一个人。我以前见过你母亲吗？",

    "My mama, she... she died long ago. I don't know much about her.":
        "我妈妈，她……她很久以前就去世了。我不太了解她。",

    "I think I remember her. She was an alchemist, often went gathering ingredients near Kynesgrove.":
        "我想我记得她。她是个炼金术士，经常去凯恩之林附近采集材料。",

    "Did she pick flowers like me? Can you... tell me more about her? Please?":
        "她也像我一样采花吗？你能……多告诉我一些关于她的事吗？求你了？",

    "Maybe one day, little one. For now, we have a journey to pursue.":
        "也许有一天吧，小家伙。但现在，我们还有路要赶。",

    # === aaJenassa6BanterControl ===
    "Child Banter Control":
        "孩童闲聊控制",
}

# Apply translations
def apply_translations(content, trans_map):
    updated_count = 0
    for original, translation in trans_map.items():
        translation_escaped = translation.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Build regex to find the ESP block with this original and STATUS=0
        escaped_orig = re.escape(original)
        # Find the block
        pattern = r'(<ESP>(?:(?!<ESP>).)*?<ORIGINAL>' + escaped_orig + r'</ORIGINAL>.*?</ESP>)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print(f"NOT FOUND: {original[:60]}...")
            continue
        
        block = match.group(1)
        
        # Check if STATUS is 0 and TRADUIT is empty
        if '<STATUS>0</STATUS>' not in block:
            # Already processed
            continue
        
        new_block = block
        
        # Replace <TRADUIT /> or <TRADUIT></TRADUIT>
        if re.search(r'<TRADUIT\s*/>', new_block):
            new_block = re.sub(r'<TRADUIT\s*/>', f'<TRADUIT>{translation_escaped}</TRADUIT>', new_block)
        elif re.search(r'<TRADUIT>\s*</TRADUIT>', new_block):
            new_block = re.sub(r'<TRADUIT>\s*</TRADUIT>', f'<TRADUIT>{translation_escaped}</TRADUIT>', new_block)
        
        # Change STATUS
        new_block = new_block.replace('<STATUS>0</STATUS>', '<STATUS>90</STATUS>')
        
        if new_block != block:
            content = content.replace(block, new_block, 1)
            updated_count += 1
    
    return content, updated_count

print(f"Translations provided: {len(translations)}")
content, count = apply_translations(content, translations)
print(f"Updated: {count}")

# Check for duplicates (same original text appearing twice)
from collections import Counter
orig_list = list(translations.keys())
dupes = [k for k, v in Counter(orig_list).items() if v > 1]
if dupes:
    print(f"WARNING: Duplicate keys: {dupes}")

# Check remaining STATUS=0
remaining = re.findall(r'<STATUS>0</STATUS>', content)
print(f"Remaining STATUS=0: {len(remaining)}")
with open(XML_PATH, 'w', encoding='utf-8-sig') as f:
    f.write(content)
print("Done!")

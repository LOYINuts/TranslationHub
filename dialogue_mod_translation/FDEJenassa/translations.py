"""Helper script to apply translations to the XML file."""
import os
import re

XML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FDE Jenassa Part 2_20F57570.xml")

with open(XML_PATH, 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Translation mapping: original English → Chinese translation
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
    '"To offset the fine they've helped me pay," they say. Hmph.': '"用来抵消他们帮我付的罚金。"他们这么说。哼。',
    
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
    "Let's talk about something else.": "我们聊点别的吧。",: 

# We'll fill this in as we go

def apply_translations(content, trans_map):
    """Replace <TRADUIT /> with <TRADUIT>translation</TRADUIT> and set STATUS to 90."""
    # Find all ESP blocks
    pattern = r'(<ESP>.*?</ESP>)'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    updated_count = 0
    for m in matches:
        block = m.group(1)
        original_match = re.search(r'<ORIGINAL>(.*?)</ORIGINAL>', block)
        if not original_match:
            continue
        original = original_match.group(1)
        
        if original in trans_map:
            translation = trans_map[original]
            translation_escaped = translation.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Replace <TRADUIT /> with <TRADUIT>translation</TRADUIT>
            new_block = re.sub(
                r'<TRADUIT\s*/>',
                f'<TRADUIT>{translation_escaped}</TRADUIT>',
                block
            )
            
            # Change STATUS from 0 to 90
            new_block = new_block.replace('<STATUS>0</STATUS>', '<STATUS>90</STATUS>')
            
            # Also handle case where <TRADUIT></TRADUIT> exists but empty
            new_block = re.sub(
                r'<TRADUIT>\s*</TRADUIT>',
                f'<TRADUIT>{translation_escaped}</TRADUIT>',
                new_block
            )
            
            if new_block != block:
                content = content.replace(block, new_block, 1)
                updated_count += 1
    
    return content, updated_count

# After filling translations, call:
# content, count = apply_translations(content, translations)
# print(f"Updated {count} entries")
# with open(XML_PATH, 'w', encoding='utf-8-sig') as f:
#     f.write(content)

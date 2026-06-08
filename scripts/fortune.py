"""
每日运势生成器
按日期 seed 抽签，结果在同一天内稳定不变；改 pool 即可扩容。
"""

import datetime
import os
import random
import re
import sys

# ──────────────── 抽签池 ────────────────

YI = [
    "补觉", "关电脑", "假装在思考", "点外卖", "把手机调静音",
    "买杯奶茶", "理直气壮地摸鱼", "回老消息", "整理一下桌面",
    "听听老歌", "去阳台发呆", "重启自己", "对镜子比心",
    "晒太阳", "把待办清单撕了", "拒绝一件事", "和朋友吹水",
    "深呼吸 3 次", "把昨天的衣服叠了", "翻翻相册", "改个签名",
    "给自己买一朵花", "学一句新方言", "记录一件小事", "早点下班",
    "今天不内耗", "犒劳自己一顿", "把待回复的 +1", "睁眼说瞎话",
    "做饭只放盐", "把闹钟往后拨 15 分钟",
]

JI = [
    "早起", "接需求", "承诺 deadline", "回工作群", "改文档",
    "开摄像头开会", "和甲方掰扯", "上称", "翻聊天记录", "查工资条",
    "刷购物 App", "看大盘", "立 flag", "回复'好的收到'",
    "假装在加班", "假装在学习", "向上汇报", "向下传达",
    "和算法工程师讲道理", "和产品经理讲需求", "和设计师争 1 像素",
    "开始一个新项目", "重构祖传代码", "在群里发'？'",
    "在飞书上@所有人", "对着空气发火", "陷入内耗", "看天气预报",
    "测 MBTI", "复盘", "查蚂蚁森林能量",
]

COLORS = [
    "薄荷绿", "鲁邦红", "克莱因蓝", "莫兰迪灰", "祖母绿",
    "椰奶白", "罗兰紫", "胭脂粉", "黛烟黑", "鎏金黄",
    "雾霾蓝", "牛油果绿", "焦糖棕", "葡萄紫", "暮山紫",
    "玻璃苣蓝", "梨果黄", "海盐青", "千禧粉", "墨松绿",
]

STARS = [
    "水星与摸鱼座合相", "天枢星照命宫，主小确幸",
    "今日土星逆行，慎言慎行（建议装哑）", "金牛座食日，宜囤零食",
    "玄武七宿明朗，宜出门觅食", "月亮入梦境宫，午睡有奇效",
    "天狼星与床头柜形成 90° 夹角", "紫微帝座位移 0.3°，影响微弱",
    "占星 App 已闪退，全凭本心", "今日无主星，自由发挥",
    "破军入财宫，红包雨提示已开启", "天王星跑偏，今日宜任性",
    "金星与你的工位呈钝角，建议挪一下椅子",
    "白虎七宿动，谨防被点名", "南斗六星齐明，宜偷得浮生半日闲",
]

XINFA = [
    "重启大法", "明天再说", "已读乱回", "装作没看见",
    "假装在忙", "甩锅大法", "拖到自动消失", "睡一觉就好",
    "买它", "撤回再说", "退出重进", "顺其自然",
    "假装这是 feature", "再等等看", "深呼吸三次",
    "把锅扣给上下游", "鞠躬道歉但不改", "立刻请假",
]

QIAN_TITLE = [
    "云开雾散", "山重水复", "柳暗花明", "守得云开",
    "因祸得福", "塞翁失马", "苦尽甘来", "时来运转",
    "贵人相助", "好梦成真", "天降甘霖", "雨过天晴",
    "一鸣惊人", "潜龙在渊", "鸿运当头",
]

QIAN_BODY = [
    [
        "虽前路雾沉沉，但抬头",
        "忽见一抹微光——",
        "那不是晨曦，",
        "那是有人给你发了红包。",
        "宜：收下，并装作不在意。",
    ],
    [
        "今日有人会对你说",
        "「在吗，有点事」——",
        "请深呼吸，",
        "并将手机倒扣于桌面。",
        "宜：装失联，留得青山在。",
    ],
    [
        "推开窗，看见的不是远方，",
        "是隔壁阿姨在晾被子。",
        "意外的烟火气，",
        "正是今日最大的彩头。",
        "宜：去楼下走两圈。",
    ],
    [
        "命格中有一杯热饮，",
        "今日定会被打翻。",
        "莫慌——",
        "翻的是焦虑，不是杯子。",
        "宜：续上第二杯。",
    ],
    [
        "凡事不必太较真，",
        "你较真的事，",
        "在三天后的你眼里，",
        "都像别人家的笑话。",
        "宜：少 emo，多吃饭。",
    ],
    [
        "今夜会有一条好消息，",
        "藏在第 47 条未读里。",
        "翻牌它，",
        "也许是平台优惠券，",
        "也许是你妈让你早点睡。",
        "宜：都接住。",
    ],
    [
        "出门记得抬头看天，",
        "云的形状，",
        "今天专门为你而设。",
        "宜：拍下来，",
        "九宫格里只发一张。",
    ],
    [
        "心里那件搁置已久的小事，",
        "今天用三分钟就能解决。",
        "怪只怪——",
        "你拖了三十天。",
        "宜：立刻去做。",
    ],
    [
        "命里缺什么不重要，",
        "重要的是你今天",
        "想吃什么。",
        "宜：跟着馋虫走。",
    ],
    [
        "运势这种东西，",
        "信则有，不信则也有。",
        "今日宜：",
        "假装自己运势爆棚，",
        "结果通常真的不错。",
    ],
]

STARFIELD_TEMPLATES = [
    [
        "   ✦  ·   *      .   ·    ✦   ",
        " ·     .     ✦       .        ",
        "   ✦       .    ✦  *    .     ",
        "       ✧   ·       ·       ✦  ",
        "   .       ·  ✦      ✧      . ",
        " ✦     .   ✧    ·     ✦       ",
        "      *    ·  ✦       .   ✧   ",
    ],
    [
        "  *    ·    ✦     ✧   ·    *  ",
        "    ✧      ·     .       ✦    ",
        "  ·   ✦    *       ·   .      ",
        "       ·    ✧   ·     ✦       ",
        " ✦    .       *      ✧     ·  ",
        "    .    ·     ✦       *      ",
        "  ✧     *    ·    ✧    .   ✦  ",
    ],
    [
        "    ·   ☄    ·    ✦     ·    ",
        " ✦     .     ·    *      ✧    ",
        "    ✧    ·       ✦     ·      ",
        " ·    ✦      ✧        *    .  ",
        "    .      *     ·      ✦     ",
        " ✧      ·    ✦   .       ·    ",
        "    *       ·       ✧   ✦     ",
    ],
]

# ──────────────── 抽签 ────────────────


def draw(today: datetime.date) -> dict:
    seed = int(today.strftime("%Y%m%d"))
    rng = random.Random(seed)

    yi = rng.sample(YI, 3)
    ji = rng.sample(JI, 3)
    color = rng.choice(COLORS)
    lucky_num = rng.randint(0, 99)
    bug_count = round(rng.uniform(0.5, 9.99), 2)
    xinfa = rng.choice(XINFA)
    star = rng.choice(STARS)
    qian_title = rng.choice(QIAN_TITLE)
    qian_body = rng.choice(QIAN_BODY)
    starfield = rng.choice(STARFIELD_TEMPLATES)

    return dict(
        date=today.strftime("%Y / %m / %d"),
        star=star,
        yi=yi,
        ji=ji,
        color=color,
        lucky_num=lucky_num,
        bug_count=bug_count,
        xinfa=xinfa,
        qian_title=qian_title,
        qian_body=qian_body,
        starfield=starfield,
    )


# ──────────────── 渲染 ────────────────


def render(d: dict) -> str:
    yi_lines = "\n".join(f"      · {y}" for y in d["yi"])
    ji_lines = "\n".join(f"      · {j}" for j in d["ji"])
    qian_lines = "\n".join(f"  {line}" for line in d["qian_body"])
    starfield = "\n".join(d["starfield"])

    left = f"""```text
╔══════════════════════════════════╗
║  🎴  KuaiYu's Daily Oracle       ║
╠══════════════════════════════════╣

  日期：{d['date']}
  星象：{d['star']}

  ✅ 今日宜
{yi_lines}

  ❌ 今日忌
{ji_lines}

  🎨 幸运色   : {d['color']}
  🔢 幸运数   : {d['lucky_num']}
  🐛 bug 预测 : {d['bug_count']} 个
  💡 解咒心法 : 「{d['xinfa']}」

╚══════════════════════════════════╝
```"""

    right = f"""```text
{starfield}

         ｢ 卦象解读 ｣

  签曰：「{d['qian_title']}」

{qian_lines}
```"""

    return f"""<!-- FORTUNE_START -->
<table>
<tr>
<td valign="top" width="50%">

{left}

</td>
<td valign="top" width="50%">

{right}

</td>
</tr>
</table>
<!-- FORTUNE_END -->"""


# ──────────────── 写回 README ────────────────


def update_readme(readme_path: str, block: str) -> bool:
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"<!-- FORTUNE_START -->.*?<!-- FORTUNE_END -->",
        re.DOTALL,
    )
    if not pattern.search(content):
        print("ERROR: 未找到 FORTUNE_START / FORTUNE_END 标记", file=sys.stderr)
        sys.exit(1)

    new_content = pattern.sub(block, content)
    if new_content == content:
        return False

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    # GitHub Actions 跑在 UTC，转成北京时间出"今日"
    now_utc = datetime.datetime.utcnow()
    today_cst = (now_utc + datetime.timedelta(hours=8)).date()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(repo_root, "README.md")

    d = draw(today_cst)
    block = render(d)
    changed = update_readme(readme_path, block)

    print(f"日期 {today_cst}  签：{d['qian_title']}  幸运色：{d['color']}")
    print("README 已更新" if changed else "README 无变化")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
时序图：简历投递匹配时序图
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'sequence')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(14, 12))
ax.set_xlim(0, 14)
ax.set_ylim(0, 12)
ax.axis('off')

ax.text(7, 11.5, '简历投递与智能匹配时序图', fontsize=18, fontweight='bold', ha='center')

# 对象框
objects = [
    (2, '求职者', '#E3F2FD', '#1976D2'),
    (5, 'Web前端', '#F3E5F5', '#7B1FA2'),
    (8, 'Flask后端', '#FFF9C4', '#F9A825'),
    (11, '数据库', '#E0F7FA', '#00838F'),
]

lifelines_height = 9

for x, name, fc, ec in objects:
    # 对象头
    box = FancyBboxPatch((x - 0.8, lifelines_height), 1.6, 0.6,
                        boxstyle="round,pad=0.05",
                        facecolor=fc, edgecolor=ec, linewidth=2)
    ax.add_patch(box)
    ax.text(x, lifelines_height + 0.3, name, fontsize=11, fontweight='bold',
            ha='center', va='center')

    # 虚线
    ax.plot([x, x], [0.5, lifelines_height], color='#9E9E9E',
            linestyle='--', linewidth=1.5)

# 消息箭头
messages = [
    (2, 8, 5, '1. 提交投递请求', 'black'),
    (5, 8, 8, '2. 验证用户权限', 'black'),
    (8, 8, 11, '3. 查询简历/岗位', 'black'),
    (11, 7, 8, '4. 返回数据', 'black'),
    (8, 7, 5, '5. 调用匹配算法', '#7B1FA2'),
    (5, 5, 2, '6. 返回匹配分数', 'black'),
    (2, 3, 5, '7. 展示匹配结果', 'black'),
    (5, 3, 8, '8. 保存投递记录', '#F9A825'),
    (8, 3, 11, '9. 写入数据库', 'black'),
    (11, 1.5, 8, '10. 确认保存', 'black'),
    (8, 1.5, 5, '11. 返回成功', 'black'),
    (5, 1.5, 2, '12. 显示成功消息', '#4CAF50'),
]

for i, (x1, y1, x2, text, color) in enumerate(messages):
    if x1 == x2:
        # 同步返回
        ax.plot([x1, x1], [y1, y1 - 0.5], color=color, linewidth=2)
    else:
        # 箭头消息
        ax.annotate('', xy=(x2, y1 - 0.4), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color=color, lw=2))
        # 消息标签
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y1 + 0.15, text, fontsize=9, ha='center',
               color=color, fontweight='bold')

# 激活框
for x in [5, 8, 11]:
    rect = plt.Rectangle((x - 0.3, 1), 0.6, 7.5, linewidth=1,
                         edgecolor='#9E9E9E', facecolor='#F5F5F5', alpha=0.3)
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'matching_sequence.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 简历投递匹配时序图已生成')
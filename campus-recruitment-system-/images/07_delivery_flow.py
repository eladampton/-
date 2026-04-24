# -*- coding: utf-8 -*-
"""
投递匹配流程图
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'flow')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(14, 12))
ax.set_xlim(0, 14)
ax.set_ylim(0, 12)
ax.axis('off')

ax.text(7, 11.5, '简历投递与智能匹配流程图', fontsize=18, fontweight='bold', ha='center')

# 左侧：HR操作
hr_box = FancyBboxPatch((0.5, 7), 3.5, 3.5, boxstyle="round,pad=0.1",
                        facecolor='#E3F2FD', edgecolor='#1565C0', linewidth=2)
ax.add_patch(hr_box)
ax.text(2.25, 10.2, 'HR模块', fontsize=12, fontweight='bold', ha='center')
hr_steps = ['发布岗位', '查看投递', '筛选简历', '更新状态']
for i, step in enumerate(hr_steps):
    box = FancyBboxPatch((0.8, 9 - i * 0.7), 2.9, 0.5, boxstyle="round,pad=0.05",
                        facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=1)
    ax.add_patch(box)
    ax.text(2.25, 9.25 - i * 0.7, step, fontsize=9, ha='center', va='center')

# 中间：投递管理
delivery_box = FancyBboxPatch((4.5, 6), 5, 2, boxstyle="round,pad=0.1",
                               facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=2)
ax.add_patch(delivery_box)
ax.text(7, 7.7, '投递管理', fontsize=12, fontweight='bold', ha='center')
ax.text(7, 7.3, '1. 用户选择简历', fontsize=9, ha='center')
ax.text(7, 7, '2. 提交到目标岗位', fontsize=9, ha='center')
ax.text(7, 6.6, '3. 创建投递记录', fontsize=9, ha='center')

# 右侧：求职者操作
seeker_box = FancyBboxPatch((10, 7), 3.5, 3.5, boxstyle="round,pad=0.1",
                           facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2)
ax.add_patch(seeker_box)
ax.text(11.75, 10.2, '求职者模块', fontsize=12, fontweight='bold', ha='center')
seeker_steps = ['创建简历', '浏览岗位', '投递简历', '查看结果']
for i, step in enumerate(seeker_steps):
    box = FancyBboxPatch((10.3, 9 - i * 0.7), 2.9, 0.5, boxstyle="round,pad=0.05",
                        facecolor='#C8E6C9', edgecolor='#388E3C', linewidth=1)
    ax.add_patch(box)
    ax.text(11.75, 9.25 - i * 0.7, step, fontsize=9, ha='center', va='center')

# 连接箭头
ax.annotate('', xy=(4.5, 8), xytext=(2, 9),
           arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))
ax.annotate('', xy=(9.5, 8), xytext=(12, 9),
           arrowprops=dict(arrowstyle='->', color='#388E3C', lw=2))

# 智能匹配算法
match_box = FancyBboxPatch((4, 3.5), 6, 2, boxstyle="round,pad=0.1",
                          facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2)
ax.add_patch(match_box)
ax.text(7, 5.2, '智能匹配算法引擎', fontsize=12, fontweight='bold', ha='center')
ax.text(7, 4.8, '输入: 简历文本 + 岗位要求', fontsize=9, ha='center')
ax.text(7, 4.5, '处理: TF-IDF + 余弦相似度', fontsize=9, ha='center')
ax.text(7, 4.2, '输出: 匹配分数 + 详细报告', fontsize=9, ha='center')

ax.annotate('', xy=(7, 6), xytext=(7, 6.5),
           arrowprops=dict(arrowstyle='->', color='#F9A825', lw=2))

# 输出结果
result_box = FancyBboxPatch((4, 0.8), 6, 2, boxstyle="round,pad=0.1",
                            facecolor='#E0F7FA', edgecolor='#00838F', linewidth=2)
ax.add_patch(result_box)
ax.text(7, 2.5, '匹配结果展示', fontsize=12, fontweight='bold', ha='center')

result_items = [
    (4.3, '综合匹配分数 (0-100分)'),
    (5.3, '各维度分数 (学历/技能/薪资)'),
    (6.3, '匹配优势列表'),
    (7.3, '不匹配项提示'),
    (8.3, '求职建议'),
]

for i, (x, text) in enumerate(result_items):
    box = FancyBboxPatch((x - 0.5, 1.1), 1.5, 0.4, boxstyle="round,pad=0.02",
                        facecolor='#B2EBF2', edgecolor='#00838F', linewidth=1)
    ax.add_patch(box)
    ax.text(x + 0.25, 1.3, str(i+1), fontsize=8, ha='center', fontweight='bold')
    ax.text(x + 0.25, 1.7, text, fontsize=7, ha='center')

ax.annotate('', xy=(7, 2.2), xytext=(7, 3.5),
           arrowprops=dict(arrowstyle='->', color='#00838F', lw=2))

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'delivery_matching_flow.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 投递匹配流程图已生成')
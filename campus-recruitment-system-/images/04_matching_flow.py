# -*- coding: utf-8 -*-
"""
智能匹配算法流程图
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'algorithm')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(14, 16))
ax.set_xlim(0, 14)
ax.set_ylim(0, 16)
ax.axis('off')

ax.text(7, 15.5, '智能匹配算法流程图', fontsize=20, fontweight='bold', ha='center')

# 开始
start = FancyBboxPatch((5, 14.5), 4, 0.8, boxstyle="round,pad=0.1",
                       facecolor='#4CAF50', edgecolor='#2E7D32', linewidth=2)
ax.add_patch(start)
ax.text(7, 14.9, '开始', fontsize=12, fontweight='bold', ha='center', color='white')

# 输入简历和岗位
inputs = [
    (2, 13, '输入简历文本', 'resume_text'),
    (8, 13, '输入岗位要求', 'job_requirements'),
]

for x, y, text, _ in inputs:
    box = FancyBboxPatch((x, y), 4, 0.8, boxstyle="round,pad=0.05",
                         facecolor='#2196F3', edgecolor='#1565C0', linewidth=2)
    ax.add_patch(box)
    ax.text(x + 2, y + 0.4, text, fontsize=11, fontweight='bold', ha='center', color='white')

ax.annotate('', xy=(4, 14.5), xytext=(6, 14.9),
           arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))
ax.annotate('', xy=(8, 14.5), xytext=(6, 14.9),
           arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))

# 步骤框
steps = [
    (7, 12, '#FF9800', '1. 文本预处理\n(分词、去停用词)'),
    (7, 10, '#9C27B0', '2. TF-IDF特征提取\n(向量化文本)'),
    (7, 8, '#E91E63', '3. 计算余弦相似度\n(向量相似度)'),
    (7, 6, '#00BCD4', '4. 多维度评分\n(学历/技能/薪资)'),
    (7, 4, '#4CAF50', '5. 加权求和\n(计算最终分数)'),
]

for x, y, fc, text in steps:
    box = FancyBboxPatch((x - 3, y - 0.7), 6, 1.4, boxstyle="round,pad=0.1",
                        facecolor=fc, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(x, y, text, fontsize=11, fontweight='bold', ha='center', va='center', color='white')

# 连接线
for i in range(len(steps) - 1):
    ax.annotate('', xy=(7, steps[i][1] - 1.4), xytext=(7, steps[i][1] - 0.7),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))

# 输出结果
output = FancyBboxPatch((4, 2), 6, 1.2, boxstyle="round,pad=0.1",
                       facecolor='#607D8B', edgecolor='#37474F', linewidth=2)
ax.add_patch(output)
ax.text(7, 2.7, '输出匹配结果', fontsize=12, fontweight='bold', ha='center', color='white')
ax.text(7, 2.3, '• 综合匹配分数 (0-100分)', fontsize=9, ha='center', color='white')
ax.text(7, 2.0, '• 匹配详情 (优势/劣势)', fontsize=9, ha='center', color='white')

ax.annotate('', xy=(7, 3.2), xytext=(7, 3.3),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))

# 公式框
formula_box = FancyBboxPatch((0.5, 0.3), 5, 1.2, boxstyle="round,pad=0.1",
                             facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=1)
ax.add_patch(formula_box)
ax.text(3, 1.1, '余弦相似度公式:', fontsize=9, fontweight='bold')
ax.text(3, 0.7, 'cos(θ) = A·B / (|A||B|)', fontsize=10, ha='center')

# 权重说明
weight_box = FancyBboxPatch((8.5, 0.3), 5, 1.2, boxstyle="round,pad=0.1",
                            facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=1)
ax.add_patch(weight_box)
ax.text(11, 1.1, '权重配置:', fontsize=9, fontweight='bold')
ax.text(11, 0.7, '学历30% 技能40% 薪资30%', fontsize=10, ha='center')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'matching_algorithm.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 智能匹配算法流程图已生成')
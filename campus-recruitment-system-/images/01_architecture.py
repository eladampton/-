# -*- coding: utf-8 -*-
"""
系统架构图
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'architecture')
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# 标题
ax.text(7, 9.5, '校招简历智能匹配系统架构图', fontsize=20, fontweight='bold',
        ha='center', va='center')

# 用户层
user_layer = FancyBboxPatch((0.5, 7), 4, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
ax.add_patch(user_layer)
ax.text(2.5, 7.9, '用户层', fontsize=12, fontweight='bold', ha='center')

# 用户类型
users = ['求职者', 'HR', '管理员']
for i, user in enumerate(users):
    rect = FancyBboxPatch((0.8 + i * 1.2, 7.2), 1, 0.5, boxstyle="round,pad=0.05",
                          facecolor='#BBDEFB', edgecolor='#1976D2', linewidth=1)
    ax.add_patch(rect)
    ax.text(1.3 + i * 1.2, 7.45, user, fontsize=9, ha='center', va='center')

# Web层
web_layer = FancyBboxPatch((4.5, 7), 5, 1.5, boxstyle="round,pad=0.1",
                           facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2)
ax.add_patch(web_layer)
ax.text(7, 7.9, 'Web表现层', fontsize=12, fontweight='bold', ha='center')

web_items = ['Bootstrap 5', 'Jinja2模板', '响应式布局']
for i, item in enumerate(web_items):
    rect = FancyBboxPatch((4.8 + i * 1.6, 7.2), 1.4, 0.5, boxstyle="round,pad=0.05",
                          facecolor='#C8E6C9', edgecolor='#388E3C', linewidth=1)
    ax.add_patch(rect)
    ax.text(5 + i * 1.6, 7.45, item, fontsize=8, ha='center', va='center')

# Flask层
flask_layer = FancyBboxPatch((0.5, 5), 4, 1.5, boxstyle="round,pad=0.1",
                              facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=2)
ax.add_patch(flask_layer)
ax.text(2.5, 5.9, 'Flask框架层', fontsize=12, fontweight='bold', ha='center')

flask_items = ['路由分发', '会话管理', '权限控制', '模板渲染']
for i, item in enumerate(flask_items):
    rect = FancyBboxPatch((0.8 + i * 0.95, 5.2), 0.85, 0.4, boxstyle="round,pad=0.05",
                          facecolor='#FFE0B2', edgecolor='#F57C00', linewidth=1)
    ax.add_patch(rect)
    ax.text(0.85 + i * 0.95, 5.4, item, fontsize=7, ha='center', va='center')

# 服务层
service_layer = FancyBboxPatch((4.5, 5), 5, 1.5, boxstyle="round,pad=0.1",
                               facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2)
ax.add_patch(service_layer)
ax.text(7, 5.9, '业务逻辑层', fontsize=12, fontweight='bold', ha='center')

service_items = ['简历解析', '智能匹配', '投递管理', '用户管理']
for i, item in enumerate(service_items):
    rect = FancyBboxPatch((4.8 + i * 1.2, 5.2), 1.1, 0.4, boxstyle="round,pad=0.05",
                          facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=1)
    ax.add_patch(rect)
    ax.text(4.85 + i * 1.2, 5.4, item, fontsize=7, ha='center', va='center')

# TF-IDF算法层
algo_layer = FancyBboxPatch((9.5, 5), 4, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#FCE4EC', edgecolor='#C2185B', linewidth=2)
ax.add_patch(algo_layer)
ax.text(11.5, 5.9, '智能匹配算法层', fontsize=12, fontweight='bold', ha='center')

algo_items = ['TF-IDF', '余弦相似度', '权重计算']
for i, item in enumerate(algo_items):
    rect = FancyBboxPatch((9.8 + i * 1.2, 5.2), 1.1, 0.4, boxstyle="round,pad=0.05",
                          facecolor='#F8BBD0', edgecolor='#C2185B', linewidth=1)
    ax.add_patch(rect)
    ax.text(9.85 + i * 1.2, 5.4, item, fontsize=7, ha='center', va='center')

# 数据层
data_layer = FancyBboxPatch((4.5, 2.5), 5, 2, boxstyle="round,pad=0.1",
                            facecolor='#E0F7FA', edgecolor='#0097A7', linewidth=2)
ax.add_patch(data_layer)
ax.text(7, 4.1, '数据持久层', fontsize=12, fontweight='bold', ha='center')

data_items = [
    ('MySQL', '用户表', '简历表', '岗位表', '投递表'),
    ('文件存储', '简历文件', '头像上传', '', '')
]
for i, (title, *items) in enumerate(data_items):
    ax.text(5.5, 3.7 - i * 0.7, title, fontsize=9, fontweight='bold')
    for j, item in enumerate(items[:3]):
        rect = FancyBboxPatch((6.5 + j * 1, 3.4 - i * 0.7), 0.9, 0.35, boxstyle="round,pad=0.02",
                              facecolor='#B2EBF2', edgecolor='#0097A7', linewidth=1)
        ax.add_patch(rect)
        ax.text(6.55 + j * 1, 3.55 - i * 0.7, item, fontsize=7, ha='center', va='center')

# 箭头 - 用户到Web
ax.annotate('', xy=(4.5, 7.75), xytext=(4.5, 8.5),
            arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))

# 箭头 - Web到Flask
ax.annotate('', xy=(2.5, 6.5), xytext=(4.5, 7),
            arrowprops=dict(arrowstyle='->', color='#F57C00', lw=2))

# 箭头 - Flask到服务层
ax.annotate('', xy=(4.5, 6.5), xytext=(4.5, 5.75),
            arrowprops=dict(arrowstyle='->', color='#388E3C', lw=2))

# 箭头 - 服务层到算法层
ax.annotate('', xy=(9.5, 5.75), xytext=(9, 5.75),
            arrowprops=dict(arrowstyle='->', color='#C2185B', lw=2))

# 箭头 - 服务层到数据层
ax.annotate('', xy=(7, 4.5), xytext=(7, 5),
            arrowprops=dict(arrowstyle='->', color='#0097A7', lw=2))

# 图例
legend_items = [
    ('#E3F2FD', '#1976D2', '用户层'),
    ('#E8F5E9', '#388E3C', 'Web层'),
    ('#FFF3E0', '#F57C00', 'Flask层'),
    ('#F3E5F5', '#7B1FA2', '业务层'),
    ('#FCE4EC', '#C2185B', '算法层'),
    ('#E0F7FA', '#0097A7', '数据层'),
]

for i, (fc, ec, label) in enumerate(legend_items):
    rect = FancyBboxPatch((0.5 + i * 2.3, 1), 0.5, 0.4, boxstyle="round,pad=0.02",
                         facecolor=fc, edgecolor=ec, linewidth=1)
    ax.add_patch(rect)
    ax.text(1.3 + i * 2.3, 1.2, label, fontsize=8)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'system_architecture.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 系统架构图已生成')
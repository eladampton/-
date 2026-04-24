# -*- coding: utf-8 -*-
"""
系统功能模块图
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'architecture')
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

# 标题
ax.text(8, 11.5, '系统功能模块图', fontsize=22, fontweight='bold', ha='center', va='center')

# 中心 - 简历智能匹配系统
center = FancyBboxPatch((5.5, 5), 5, 1.5, boxstyle="round,pad=0.15",
                        facecolor='#1A237E', edgecolor='#0D47A1', linewidth=3)
ax.add_patch(center)
ax.text(8, 5.85, '简历智能匹配系统', fontsize=14, fontweight='bold',
        ha='center', va='center', color='white')

# 四个主模块
modules = [
    (1.5, 8, '#2196F3', '#1565C0', '用户管理模块', ['用户注册', '用户登录', '权限管理', '密码修改']),
    (10.5, 8, '#4CAF50', '#2E7D32', '岗位管理模块', ['发布岗位', '编辑岗位', '岗位下架', '投递查看']),
    (1.5, 2.5, '#FF9800', '#E65100', '简历管理模块', ['创建简历', '上传简历', '简历解析', '简历编辑']),
    (10.5, 2.5, '#9C27B0', '#6A1B9A', '智能匹配模块', ['TF-IDF提取', '余弦相似度', '分数计算', '结果展示']),
]

for x, y, fc, ec, title, items in modules:
    # 模块框
    module_box = FancyBboxPatch((x, y), 4, 2.5, boxstyle="round,pad=0.1",
                               facecolor=fc, edgecolor=ec, linewidth=2)
    ax.add_patch(module_box)
    ax.text(x + 2, y + 2.1, title, fontsize=11, fontweight='bold',
            ha='center', va='center', color='white')

    # 子项
    for i, item in enumerate(items):
        rect = FancyBboxPatch((x + 0.3, y + 0.1 + i * 0.55), 3.4, 0.45, boxstyle="round,pad=0.05",
                              facecolor='white', edgecolor=ec, linewidth=1, alpha=0.9)
        ax.add_patch(rect)
        ax.text(x + 2, y + 0.35 + i * 0.55, item, fontsize=9, ha='center', va='center')

    # 连接线
    if x < 8:
        ax.plot([x + 4, x + 5.5], [y + 1.25, 5.75], color=ec, linewidth=2)
        ax.annotate('', xy=(x + 4, y + 1.25), xytext=(x + 5.5, 5.75),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=2))
    else:
        ax.plot([x, x + 5.5], [y + 1.25, 5.75], color=ec, linewidth=2)
        ax.annotate('', xy=(x, y + 1.25), xytext=(x + 5.5, 5.75),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=2))

# 底部数据存储模块
db_box = FancyBboxPatch((5.5, 0.5), 5, 1.5, boxstyle="round,pad=0.1",
                         facecolor='#00BCD4', edgecolor='#00838F', linewidth=2)
ax.add_patch(db_box)
ax.text(8, 1.4, '数据存储层', fontsize=12, fontweight='bold',
        ha='center', va='center', color='white')

db_items = ['MySQL数据库', '文件存储']
for i, item in enumerate(db_items):
    rect = FancyBboxPatch((6 + i * 2.3, 0.7), 2, 0.5, boxstyle="round,pad=0.05",
                          facecolor='white', edgecolor='#00838F', linewidth=1)
    ax.add_patch(rect)
    ax.text(7 + i * 2.3, 0.95, item, fontsize=9, ha='center', va='center')

# 连接到中心
ax.annotate('', xy=(6.5, 5), xytext=(6.5, 2),
            arrowprops=dict(arrowstyle='<->', color='#00838F', lw=2))
ax.annotate('', xy=(9.5, 5), xytext=(9.5, 2),
            arrowprops=dict(arrowstyle='<->', color='#00838F', lw=2))

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'function_modules.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 功能模块图已生成')
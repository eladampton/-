# -*- coding: utf-8 -*-
"""
数据库ER图
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'database')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 16)
ax.set_ylim(0, 12)
ax.axis('off')

ax.text(8, 11.5, '数据库ER图', fontsize=22, fontweight='bold', ha='center')

# 用户表
user_box = FancyBboxPatch((1, 9), 3.5, 2, boxstyle="round,pad=0.1",
                          facecolor='#FFCDD2', edgecolor='#C62828', linewidth=2)
ax.add_patch(user_box)
ax.text(2.75, 10.6, '用户表 users', fontsize=11, fontweight='bold', ha='center')
ax.text(1.2, 10.3, 'id (PK) 用户名 密码', fontsize=8)
ax.text(1.2, 10.0, '姓名 角色 邮箱', fontsize=8)
ax.text(1.2, 9.7, '手机 公司 创建时间', fontsize=8)

# 简历表
resume_box = FancyBboxPatch((5.5, 9), 3.5, 2, boxstyle="round,pad=0.1",
                            facecolor='#C8E6C9', edgecolor='#2E7D32', linewidth=2)
ax.add_patch(resume_box)
ax.text(7.25, 10.6, '简历表 resumes', fontsize=11, fontweight='bold', ha='center')
ax.text(5.7, 10.3, 'id (PK) user_id (FK)', fontsize=8)
ax.text(5.7, 10.0, '姓名 学校 专业', fontsize=8)
ax.text(5.7, 9.7, '学历 技能 状态', fontsize=8)

# 岗位表
job_box = FancyBboxPatch((10, 9), 3.5, 2, boxstyle="round,pad=0.1",
                         facecolor='#BBDEFB', edgecolor='#1565C0', linewidth=2)
ax.add_patch(job_box)
ax.text(11.75, 10.6, '岗位表 jobs', fontsize=11, fontweight='bold', ha='center')
ax.text(10.2, 10.3, 'id (PK) hr_id (FK)', fontsize=8)
ax.text(10.2, 10.0, '岗位名 城市 薪资', fontsize=8)
ax.text(10.2, 9.7, '学历要求 技能要求', fontsize=8)

# 投递表
delivery_box = FancyBboxPatch((3, 5), 4, 2, boxstyle="round,pad=0.1",
                              facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=2)
ax.add_patch(delivery_box)
ax.text(5, 6.6, '投递表 deliveries', fontsize=11, fontweight='bold', ha='center')
ax.text(3.2, 6.3, 'id (PK) user_id (FK)', fontsize=8)
ax.text(3.2, 6.0, 'job_id (FK) resume_id (FK)', fontsize=8)
ax.text(3.2, 5.7, '匹配分数 状态 投递时间', fontsize=8)

# 匹配结果表
match_box = FancyBboxPatch((8, 5), 4, 2, boxstyle="round,pad=0.1",
                          facecolor='#E1BEE7', edgecolor='#7B1FA2', linewidth=2)
ax.add_patch(match_box)
ax.text(10, 6.6, '匹配结果表', fontsize=11, fontweight='bold', ha='center')
ax.text(8.2, 6.3, 'id (PK) resume_id (FK)', fontsize=8)
ax.text(8.2, 6.0, 'job_id (FK) 最终分数', fontsize=8)
ax.text(8.2, 5.7, 'TF-IDF分 匹配详情', fontsize=8)

# 收藏表
fav_box = FancyBboxPatch((3, 1.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                         facecolor='#FFCCBC', edgecolor='#D84315', linewidth=2)
ax.add_patch(fav_box)
ax.text(4.75, 2.7, '收藏表 favorites', fontsize=10, fontweight='bold', ha='center')
ax.text(3.2, 2.4, 'id (PK) user_id (FK) job_id (FK)', fontsize=8)

# 浏览记录表
browse_box = FancyBboxPatch((8, 1.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                            facecolor='#B2EBF2', edgecolor='#00838F', linewidth=2)
ax.add_patch(browse_box)
ax.text(9.75, 2.7, '浏览记录表', fontsize=10, fontweight='bold', ha='center')
ax.text(8.2, 2.4, 'id (PK) user_id (FK) job_id (FK)', fontsize=8)

# 关系线
# User -> Resume
ax.annotate('', xy=(5.5, 9.8), xytext=(4.5, 9.8),
           arrowprops=dict(arrowstyle='->', color='#C62828', lw=2))
ax.text(4.8, 10.1, '1:N', fontsize=9, color='#C62828')

# User -> Job
ax.annotate('', xy=(10, 9.8), xytext=(4.5, 10.5),
           arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))
ax.text(7, 10.8, '1:N', fontsize=9, color='#1565C0')

# User -> Delivery
ax.annotate('', xy=(4, 7), xytext=(3, 9),
           arrowprops=dict(arrowstyle='->', color='#C62828', lw=2))

# Resume -> Delivery
ax.annotate('', xy=(5, 6.5), xytext=(7, 9),
           arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2))

# Job -> Delivery
ax.annotate('', xy=(7, 6.5), xytext=(10, 9),
           arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))

# Delivery -> Match
ax.annotate('', xy=(8, 6), xytext=(7, 6),
           arrowprops=dict(arrowstyle='->', color='#F9A825', lw=2))

# User -> Favorite
ax.annotate('', xy=(4, 3), xytext=(3, 9),
           arrowprops=dict(arrowstyle='->', color='#D84315', lw=2))

# Job -> Favorite
ax.annotate('', xy=(6.5, 2.7), xytext=(11, 9.5),
           arrowprops=dict(arrowstyle='->', color='#D84315', lw=2))

# User -> BrowseHistory
ax.annotate('', xy=(9, 3), xytext=(4, 9),
           arrowprops=dict(arrowstyle='->', color='#00838F', lw=2))

# Job -> BrowseHistory
ax.annotate('', xy=(10.5, 2.7), xytext=(12, 9),
           arrowprops=dict(arrowstyle='->', color='#00838F', lw=2))

# 图例
ax.text(1, 0.5, 'PK: 主键  FK: 外键  1:N: 一对多关系', fontsize=9, style='italic')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'database_er.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 数据库ER图已生成')
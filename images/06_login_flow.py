# -*- coding: utf-8 -*-
"""
用户登录注册流程图
"""
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'flow')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(12, 14))
ax.set_xlim(0, 12)
ax.set_ylim(0, 14)
ax.axis('off')

ax.text(6, 13.5, '用户登录注册流程图', fontsize=18, fontweight='bold', ha='center')

# 开始
start = FancyBboxPatch((4.5, 12.5), 3, 0.7, boxstyle="round,pad=0.1",
                       facecolor='#4CAF50', edgecolor='#2E7D32', linewidth=2)
ax.add_patch(start)
ax.text(6, 12.85, '开始', fontsize=11, fontweight='bold', ha='center', color='white')

# 选择
choice = FancyBboxPatch((3, 11), 6, 1, boxstyle="round,pad=0.1",
                         facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=2)
ax.add_patch(choice)
ax.text(6, 11.5, '用户选择：登录 / 注册', fontsize=11, fontweight='bold', ha='center')

ax.annotate('', xy=(6, 12.5), xytext=(6, 12.1),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))

# 登录分支
login_box = FancyBboxPatch((0.5, 8.5), 4.5, 2, boxstyle="round,pad=0.1",
                           facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2)
ax.add_patch(login_box)
ax.text(2.75, 10.2, '登录流程', fontsize=11, fontweight='bold', ha='center')
ax.text(0.7, 9.7, '1. 输入用户名密码', fontsize=9)
ax.text(0.7, 9.3, '2. 验证用户信息', fontsize=9)
ax.text(0.7, 8.9, '3. 检查账号状态', fontsize=9)
ax.text(0.7, 8.5, '4. 登录成功/失败', fontsize=9)

# 注册分支
reg_box = FancyBboxPatch((7, 8.5), 4.5, 2, boxstyle="round,pad=0.1",
                          facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2)
ax.add_patch(reg_box)
ax.text(9.25, 10.2, '注册流程', fontsize=11, fontweight='bold', ha='center')
ax.text(7.2, 9.7, '1. 填写注册信息', fontsize=9)
ax.text(7.2, 9.3, '2. 验证信息完整性', fontsize=9)
ax.text(7.2, 8.9, '3. 检查用户名唯一', fontsize=9)
ax.text(7.2, 8.5, '4. 创建账号', fontsize=9)

# 分支箭头
ax.annotate('', xy=(0.5, 10), xytext=(4.5, 11),
           arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))
ax.annotate('', xy=(7, 10), xytext=(7.5, 11),
           arrowprops=dict(arrowstyle='->', color='#388E3C', lw=2))

# 权限分发
auth_box = FancyBboxPatch((3, 5.5), 6, 1.2, boxstyle="round,pad=0.1",
                          facecolor='#F3E5F5', edgecolor='#7B1FA2', linewidth=2)
ax.add_patch(auth_box)
ax.text(6, 6.1, '权限分发', fontsize=12, fontweight='bold', ha='center')
ax.text(6, 5.75, '根据角色进入对应模块', fontsize=10, ha='center')

# 三个角色
roles = [
    (0.5, 3.5, '#C62828', '管理员', '后台管理'),
    (4.25, 3.5, '#1565C0', '企业HR', '岗位管理'),
    (8, 3.5, '#2E7D32', '求职者', '简历投递'),
]

for x, y, fc, title, desc in roles:
    box = FancyBboxPatch((x, y), 3.5, 1.5, boxstyle="round,pad=0.1",
                        facecolor=fc, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(x + 1.75, y + 1.1, title, fontsize=11, fontweight='bold',
            ha='center', color='white')
    ax.text(x + 1.75, y + 0.6, desc, fontsize=9, ha='center', color='white')

# 连接线
ax.annotate('', xy=(2, 5), xytext=(6, 5.5),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))
ax.annotate('', xy=(4.25, 3.5), xytext=(4, 4.2),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))
ax.annotate('', xy=(4.5, 3.5), xytext=(4.5, 4.2),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))
ax.annotate('', xy=(8.25, 3.5), xytext=(6, 4.2),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))

# 结束
end = FancyBboxPatch((4.5, 1.5), 3, 0.7, boxstyle="round,pad=0.1",
                     facecolor='#607D8B', edgecolor='#37474F', linewidth=2)
ax.add_patch(end)
ax.text(6, 1.85, '进入系统', fontsize=11, fontweight='bold', ha='center', color='white')

ax.annotate('', xy=(6, 2.2), xytext=(6, 2.7),
           arrowprops=dict(arrowstyle='->', color='black', lw=2))

# 错误处理
error_box = FancyBboxPatch((0.5, 1.5), 3, 0.8, boxstyle="round,pad=0.1",
                           facecolor='#FFCDD2', edgecolor='#C62828', linewidth=2)
ax.add_patch(error_box)
ax.text(2, 1.9, '登录失败', fontsize=10, fontweight='bold', ha='center')
ax.text(2, 1.6, '错误提示', fontsize=9, ha='center')

error_box2 = FancyBboxPatch((8.5, 1.5), 3, 0.8, boxstyle="round,pad=0.1",
                            facecolor='#FFCDD2', edgecolor='#C62828', linewidth=2)
ax.add_patch(error_box2)
ax.text(10, 1.9, '注册失败', fontsize=10, fontweight='bold', ha='center')
ax.text(10, 1.6, '返回重填', fontsize=9, ha='center')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'login_flow.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] 用户登录注册流程图已生成')
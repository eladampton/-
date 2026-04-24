# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
matplotlib.rcParams['axes.unicode_minus'] = False
import numpy as np
import os

output_dir = 'images/analytics'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

colors = {
    'primary': '#1a365d',
    'secondary': '#2c5282', 
    'accent': '#3182ce',
    'success': '#38a169',
    'warning': '#d69e2e',
    'danger': '#e53e3e',
    'purple': '#805ad5',
    'cyan': '#00b5d8'
}

def save_chart(fig, filename):
    fig.tight_layout()
    fig.savefig(f'{output_dir}/{filename}', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'已生成: {filename}')

# 1. 投递趋势折线图
fig, ax = plt.subplots(figsize=(12, 6))
days = [f'第{i}天' for i in range(1, 31)]
deliveries = [45, 52, 38, 65, 78, 92, 55, 48, 72, 85, 95, 88, 102, 95, 78, 65, 72, 88, 95, 108, 
             115, 98, 85, 72, 68, 82, 95, 105, 112, 98]
ax.plot(days, deliveries, marker='o', linewidth=2, markersize=6, color=colors['primary'])
ax.fill_between(range(30), deliveries, alpha=0.3, color=colors['accent'])
ax.set_title('System Daily Delivery Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Days', fontsize=12)
ax.set_ylabel('Delivery Count', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 130)
save_chart(fig, 'delivery-trend.png')

# 2. 投递状态饼图
fig, ax = plt.subplots(figsize=(8, 8))
statuses = ['Pending Review', 'Viewed', 'Contacted', 'Not Suitable']
sizes = [35, 28, 15, 22]
color_list = [colors['primary'], colors['accent'], colors['success'], colors['danger']]
explode = (0.05, 0.02, 0.02, 0.02)
wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=statuses, colors=color_list,
                                   autopct='%1.1f%%', startangle=90, pctdistance=0.75)
for autotext in autotexts:
    autotext.set_fontsize(12)
    autotext.set_fontweight('bold')
ax.set_title('Application Status Distribution', fontsize=14, fontweight='bold')
save_chart(fig, 'application-status.png')

# 3. 岗位类别柱状图
fig, ax = plt.subplots(figsize=(10, 6))
categories = ['Software Dev', ' Product Mgr', 'Data Analyst', 'UX Design', 'Operations', 'Marketing']
counts = [420, 285, 198, 156, 312, 178]
bars = ax.bar(categories, counts, color=[colors['primary'], colors['secondary'], colors['accent'], 
                          colors['success'], colors['warning'], colors['purple']])
ax.set_title('Job Category Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Job Count', fontsize=12)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height)}',
           ha='center', va='bottom', fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
save_chart(fig, 'job-category.png')

# 4. 匹配分数分布直方图
fig, ax = plt.subplots(figsize=(10, 6))
scores = np.random.normal(75, 12, 500)
scores = scores[(scores > 30) & (scores < 100)]
ax.hist(scores, bins=20, color=colors['accent'], edgecolor='white', alpha=0.8)
ax.axvline(x=np.mean(scores), color=colors['danger'], linestyle='--', linewidth=2, label=f'Mean: {np.mean(scores):.1f}')
ax.axvline(x=np.median(scores), color=colors['success'], linestyle='--', linewidth=2, label=f'Median: {np.median(scores):.1f}')
ax.set_title('Match Score Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Match Score', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
save_chart(fig, 'score-distribution.png')

# 5. 用户增长曲线图
fig, ax = plt.subplots(figsize=(12, 6))
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
registered = [120, 185, 320, 485, 680, 890]
active = [95, 142, 265, 398, 545, 712]
ax.plot(months, registered, marker='o', linewidth=2, markersize=8, label='Registered Users', color=colors['primary'])
ax.plot(months, active, marker='s', linewidth=2, markersize=8, label='Active Users', color=colors['success'])
ax.fill_between(range(6), registered, active, alpha=0.2, color=colors['accent'])
ax.set_title('User Growth Trend', fontsize=14, fontweight='bold')
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('User Count', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)
save_chart(fig, 'user-growth.png')

# 6. 学历分布柱状图
fig, ax = plt.subplots(figsize=(8, 6))
education = ['PhD', 'Master', 'Bachelor', 'Associate', 'High School']
counts = [180, 680, 1850, 420, 70]
bars = ax.barh(education, counts, color=[colors['purple'], colors['primary'], colors['secondary'], 
                              colors['accent'], colors['warning']])
ax.set_title('Education Level Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Count', fontsize=12)
for bar, count in zip(bars, counts):
    ax.text(count + 30, bar.get_y() + bar.get_height()/2., str(count), va='center', fontsize=10)
ax.grid(True, alpha=0.3, axis='x')
save_chart(fig, 'education-distribution.png')

# 7. 城市岗位热力图数据
fig, ax = plt.subplots(figsize=(10, 8))
cities = ['Beijing', 'Shanghai', 'Shenzhen', 'Hangzhou', 'Guangzhou', 'Chengdu']
industries = ['Tech', 'Finance', 'E-commerce', 'Education', 'Consulting']
data = np.array([
    [85, 72, 68, 55, 42],
    [82, 78, 65, 48, 38],
    [88, 65, 72, 52, 35],
    [75, 58, 82, 45, 28],
    [68, 55, 58, 42, 32],
    [58, 48, 52, 38, 25]
])
im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(industries)))
ax.set_yticks(range(len(cities)))
ax.set_xticklabels(industries)
ax.set_yticklabels(cities)
for i in range(len(cities)):
    for j in range(len(industries)):
        ax.text(j, i, data[i, j], ha='center', va='center', color='white', fontweight='bold')
ax.set_title('City-Industry Job Heatmap', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax, label='Job Count')
save_chart(fig, 'city-industry-heatmap.png')

# 8. 薪资分布箱线图
fig, ax = plt.subplots(figsize=(8, 6))
ranges = ['3k-5k', '5k-8k', '8k-12k', '12k-15k', '15k-20k', '20k+']
data = [[45, 52, 38, 42, 35, 28], [68, 72, 65, 58, 48, 42], [120, 135, 110, 95, 82, 75],
       [85, 92, 78, 68, 58, 52], [42, 48, 52, 45, 38, 35], [18, 22, 25, 28, 22, 18]]
bp = ax.boxplot(data, labels=ranges, patch_artist=True)
colors_box = [colors['accent'], colors['primary'], colors['secondary'], colors['success'], colors['warning'], colors['purple']]
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_title('Salary Distribution by Range', fontsize=14, fontweight='bold')
ax.set_xlabel('Salary Range (CNY)', fontsize=12)
ax.set_ylabel('Application Count', fontsize=12)
ax.grid(True, alpha=0.3, axis='y')
save_chart(fig, 'salary-distribution.png')

# 9. 技能词云图效果（用条形图替代）
fig, ax = plt.subplots(figsize=(12, 6))
skills = ['Python', 'Java', 'SQL', 'JavaScript', 'Machine Learning', 'Data Analysis', 'Excel', 'Linux', 'Git', 'Docker']
importance = [95, 88, 82, 78, 75, 72, 65, 58, 52, 45]
bars = ax.barh(skills, importance, color=colors['primary'])
ax.set_title('Skill Demand Ranking', fontsize=14, fontweight='bold')
ax.set_xlabel('Demand Index', fontsize=12)
for bar, imp in zip(bars, importance):
    ax.text(imp + 1, bar.get_y() + bar.get_height()/2., str(imp), va='center', fontsize=10)
ax.set_xlim(0, 110)
ax.grid(True, alpha=0.3, axis='x')
save_chart(fig, 'skill-demand.png')

# 10. 算法准确率对比
fig, ax = plt.subplots(figsize=(10, 6))
methods = ['Keyword', 'TF-IDF+Cosine', 'Word2Vec', 'BERT', 'Our Method']
precision = [62.3, 78.5, 81.2, 85.8, 89.2]
recall = [58.1, 75.2, 79.8, 83.5, 86.5]
f1 = [60.1, 76.8, 80.5, 84.6, 87.8]
x = np.arange(len(methods))
width = 0.25
ax.bar(x - width, precision, width, label='Precision', color=colors['primary'])
ax.bar(x, recall, width, label='Recall', color=colors['accent'])
ax.bar(x + width, f1, width, label='F1-Score', color=colors['success'])
ax.set_title('Algorithm Comparison', fontsize=14, fontweight='bold')
ax.set_xlabel('Method', fontsize=12)
ax.set_ylabel('Score (%)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(methods)
ax.legend()
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3, axis='y')
save_chart(fig, 'algorithm-comparison.png')

print(f'\n所有图表已生成到: {output_dir}/')
print(f'共生成 10 张图表')
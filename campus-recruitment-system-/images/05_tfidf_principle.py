# -*- coding: utf-8 -*-
"""
TF-IDF算法原理图
"""
import os
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'images', 'algorithm')
os.makedirs(OUTPUT_DIR, exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：TF-IDF公式
ax1 = axes[0]
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 8)
ax1.axis('off')

ax1.text(5, 7.5, 'TF-IDF 术语权重计算', fontsize=16, fontweight='bold', ha='center')

# TF公式
ax1.text(2, 6, '词频 TF (Term Frequency)', fontsize=12, fontweight='bold', color='#1976D2')
ax1.text(2, 5.5, 'TF(t) = 词t在文档中出现的次数 / 文档总词数', fontsize=10)

# IDF公式
ax1.text(2, 4.2, '逆文档频率 IDF (Inverse Document Frequency)', fontsize=12, fontweight='bold', color='#388E3C')
ax1.text(2, 3.7, 'IDF(t) = log(总文档数 / 包含词t的文档数)', fontsize=10)

# TF-IDF公式
ax1.text(2, 2.2, 'TF-IDF权重', fontsize=12, fontweight='bold', color='#C62828')
ax1.text(2, 1.7, 'TF-IDF(t) = TF(t) × IDF(t)', fontsize=10)

# 示例
ax1.text(7, 6, '示例:', fontsize=11, fontweight='bold')
example_text = """文档1: "Python编程开发"
文档2: "Java编程开发"
文档3: "Python数据分析" """
ax1.text(7, 5, example_text, fontsize=9, va='top', family='monospace')

ax1.text(7, 3, '"Python"在各文档中:', fontsize=10)
ax1.text(7, 2.5, 'TF-IDF(文档1) = 0.5 × 0.477 = 0.239', fontsize=9, family='monospace')
ax1.text(7, 2, 'TF-IDF(文档3) = 0.5 × 0.477 = 0.239', fontsize=9, family='monospace')

# 右图：向量空间模型
ax2 = axes[1]
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 8)
ax2.axis('off')

ax2.text(5, 7.5, '余弦相似度计算', fontsize=16, fontweight='bold', ha='center')

# 公式
formula = r'$cos(\theta) = \frac{A \cdot B}{|A| \times |B|} = \frac{\sum_{i=1}^{n} A_i \times B_i}{\sqrt{\sum A_i^2} \times \sqrt{\sum B_i^2}}$'
ax2.text(5, 6.5, formula, fontsize=14, ha='center')

# 示例向量
ax2.text(2, 5, '简历向量 A = [0.8, 0.6, 0.3, 0.5]', fontsize=10, family='monospace')
ax2.text(2, 4.5, '岗位向量 B = [0.7, 0.8, 0.4, 0.6]', fontsize=10, family='monospace')

ax2.text(2, 3.5, '计算过程:', fontsize=11, fontweight='bold')
ax2.text(2, 3, '• 点积: 0.8×0.7 + 0.6×0.8 + 0.3×0.4 + 0.5×0.6 = 1.24', fontsize=9)
ax2.text(2, 2.5, '• 模A: √(0.64+0.36+0.09+0.25) = 1.36', fontsize=9)
ax2.text(2, 2, '• 模B: √(0.49+0.64+0.16+0.36) = 1.36', fontsize=9)
ax2.text(2, 1.5, '• 相似度: 1.24/(1.36×1.36) = 0.67', fontsize=9, color='#C62828', fontweight='bold')

ax2.text(7, 5, '相似度范围: 0~1', fontsize=10, fontweight='bold')
ax2.text(7, 4, '1.0 = 完全匹配', fontsize=9, color='#4CAF50')
ax2.text(7, 3.5, '0.8+ = 高度匹配', fontsize=9, color='#4CAF50')
ax2.text(7, 3, '0.6+ = 中等匹配', fontsize=9, color='#FF9800')
ax2.text(7, 2.5, '0.0 = 完全不匹配', fontsize=9, color='#F44336')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'tfidf_principle.png'), dpi=150, bbox_inches='tight')
plt.close()
print('[OK] TF-IDF算法原理图已生成')
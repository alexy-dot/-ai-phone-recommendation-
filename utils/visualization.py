#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化工具
生成雷达图、对比图表等可视化内容
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from typing import List, Dict, Tuple
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class PhoneVisualizer:
    """手机参数可视化工具"""
    
    def __init__(self):
        self.dimensions = ['性能', '拍照', '续航', '便携', '价格', '外观']
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    def create_radar_chart(self, phones: List[Dict], save_path: str = None) -> str:
        """创建雷达图对比"""
        if len(phones) > 6:
            phones = phones[:6]  # 限制最多6款手机
        
        # 准备数据
        angles = np.linspace(0, 2 * np.pi, len(self.dimensions), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(projection='polar'))
        
        for i, phone in enumerate(phones):
            # 获取各维度分数
            scores = [
                phone.get('performance_score', 0.5),
                phone.get('camera_score', 0.5),
                phone.get('battery_score', 0.5),
                phone.get('portability_score', 0.5),
                phone.get('price_score', 0.5),
                phone.get('appearance_score', 0.5)
            ]
            scores += scores[:1]  # 闭合图形
            
            # 绘制雷达图
            ax.plot(angles, scores, 'o-', linewidth=2, 
                   label=phone['name'], color=self.colors[i % len(self.colors)])
            ax.fill(angles, scores, alpha=0.25, color=self.colors[i % len(self.colors)])
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.dimensions)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        
        # 添加标题和图例
        plt.title('手机参数雷达图对比', size=16, pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def create_comparison_chart(self, phones: List[Dict], save_path: str = None) -> str:
        """创建柱状图对比"""
        if len(phones) > 8:
            phones = phones[:8]  # 限制最多8款手机
        
        # 准备数据
        names = [phone['name'] for phone in phones]
        prices = [phone['price'] for phone in phones]
        performance_scores = [phone.get('performance_score', 0.5) for phone in phones]
        camera_scores = [phone.get('camera_score', 0.5) for phone in phones]
        
        # 创建子图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 价格对比
        bars1 = ax1.bar(names, prices, color='skyblue', alpha=0.7)
        ax1.set_title('价格对比', fontsize=14)
        ax1.set_ylabel('价格 (元)')
        ax1.tick_params(axis='x', rotation=45)
        
        # 在柱子上添加价格标签
        for bar, price in zip(bars1, prices):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'¥{price}', ha='center', va='bottom')
        
        # 性能对比
        x = np.arange(len(names))
        width = 0.35
        
        bars2 = ax2.bar(x - width/2, performance_scores, width, label='性能', color='lightcoral')
        bars3 = ax2.bar(x + width/2, camera_scores, width, label='拍照', color='lightgreen')
        
        ax2.set_title('性能与拍照对比', fontsize=14)
        ax2.set_ylabel('评分')
        ax2.set_xticks(x)
        ax2.set_xticklabels(names, rotation=45)
        ax2.legend()
        ax2.set_ylim(0, 1)
        
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def create_feature_comparison(self, phones: List[Dict], save_path: str = None) -> str:
        """创建特性对比表格图"""
        if len(phones) > 5:
            phones = phones[:5]  # 限制最多5款手机
        
        # 准备数据
        features = ['CPU', '内存', '存储', '屏幕', '摄像头', '电池', '重量']
        data = []
        
        for phone in phones:
            row = [
                phone.get('cpu', 'N/A'),
                f"{phone.get('ram_gb', 0)}GB",
                f"{phone.get('storage_gb', 0)}GB",
                f"{phone.get('screen_size_inch', 0)}英寸",
                f"{phone.get('camera_mp', 0)}MP",
                f"{phone.get('battery_mah', 0)}mAh",
                f"{phone.get('weight_g', 0)}g"
            ]
            data.append(row)
        
        # 创建表格
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # 创建表格
        table = ax.table(cellText=data,
                        colLabels=features,
                        rowLabels=[phone['name'] for phone in phones],
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        # 设置标题
        plt.title('手机参数详细对比', fontsize=16, pad=20)
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def create_recommendation_summary(self, recommendations: List[Dict], save_path: str = None) -> str:
        """创建推荐总结图"""
        if not recommendations:
            return ""
        
        # 准备数据
        names = [rec['name'] for rec in recommendations]
        scores = [rec['score'] for rec in recommendations]
        prices = [rec['price'] for rec in recommendations]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 匹配度对比
        bars1 = ax1.bar(names, scores, color='gold', alpha=0.7)
        ax1.set_title('推荐匹配度', fontsize=14)
        ax1.set_ylabel('匹配度')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylim(0, 1)
        
        # 在柱子上添加匹配度标签
        for bar, score in zip(bars1, scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{score:.3f}', ha='center', va='bottom')
        
        # 价格对比
        bars2 = ax2.bar(names, prices, color='lightblue', alpha=0.7)
        ax2.set_title('价格对比', fontsize=14)
        ax2.set_ylabel('价格 (元)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 在柱子上添加价格标签
        for bar, price in zip(bars2, prices):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'¥{price}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            plt.show()
            return "" 
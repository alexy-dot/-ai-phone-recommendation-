#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态雷达图生成器
根据用户关注的维度动态生成雷达图
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import os


class DynamicRadarChartGenerator:
    """动态雷达图生成器"""
    
    def __init__(self):
        # 维度名称映射
        self.dimension_labels = {
            'cpu_performance': 'CPU性能',
            'memory_capacity': '内存容量',
            'storage_speed': '存储速度',
            'gpu_performance': 'GPU性能',
            'camera_quality': '拍照质量',
            'camera_features': '拍照功能',
            'battery_capacity': '电池容量',
            'charging_speed': '充电速度',
            'screen_quality': '屏幕质量',
            'screen_size': '屏幕尺寸',
            'weight_portability': '重量便携',
            'size_portability': '尺寸便携',
            'build_quality': '做工质量',
            'design_appeal': '设计外观',
            'price_value': '性价比',
            'heat_control': '散热控制',
            'network_stability': '网络稳定',
            'software_optimization': '系统优化',
            'durability': '耐用性'
        }
        
        # 颜色配置
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                      '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
        # 图表样式配置
        self.style_config = {
            'figsize': (12, 10),
            'dpi': 300,
            'background_color': '#f8f9fa',
            'grid_color': '#e9ecef',
            'text_color': '#495057',
            'title_size': 16,
            'label_size': 12,
            'legend_size': 10
        }
    
    def generate_radar_chart(self, recommendations: List[Dict], 
                           demand_vector, 
                           output_path: str,
                           title: str = "手机性能雷达图（基于用户需求）"):
        """生成动态雷达图"""
        try:
            # 获取关注的维度
            focus_dimensions = demand_vector.focus_dimensions
            
            if not focus_dimensions:
                print("⚠️ 没有找到用户关注的维度，使用默认维度")
                focus_dimensions = ['cpu_performance', 'camera_quality', 
                                  'battery_capacity', 'price_value', 'weight_portability']
            
            # 限制维度数量，避免图表过于复杂
            if len(focus_dimensions) > 8:
                focus_dimensions = focus_dimensions[:8]
            
            # 准备数据
            angles = np.linspace(0, 2 * np.pi, len(focus_dimensions), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            # 创建图表
            fig, ax = plt.subplots(figsize=self.style_config['figsize'], 
                                 subplot_kw=dict(projection='polar'))
            
            # 设置背景色
            fig.patch.set_facecolor(self.style_config['background_color'])
            ax.set_facecolor(self.style_config['background_color'])
            
            # 为每个推荐手机绘制雷达图
            for i, rec in enumerate(recommendations[:5]):  # 最多显示5款
                phone_vector = rec['phone_vector']
                phone_name = rec['phone'].name
                scores = []
                
                for dimension in focus_dimensions:
                    score = getattr(phone_vector, dimension, 0.0)
                    scores.append(score)
                
                scores += scores[:1]  # 闭合图形
                
                # 绘制线条和填充
                color = self.colors[i % len(self.colors)]
                ax.plot(angles, scores, 'o-', linewidth=2.5, 
                       label=phone_name, color=color, markersize=6)
                ax.fill(angles, scores, alpha=0.25, color=color)
            
            # 设置标签
            ax.set_xticks(angles[:-1])
            labels = [self.dimension_labels.get(dim, dim) for dim in focus_dimensions]
            ax.set_xticklabels(labels, size=self.style_config['label_size'], 
                             color=self.style_config['text_color'])
            
            # 设置网格
            ax.grid(True, color=self.style_config['grid_color'], alpha=0.6)
            ax.set_ylim(0, 1)
            
            # 设置标题
            ax.set_title(title, size=self.style_config['title_size'], 
                        pad=20, color=self.style_config['text_color'])
            
            # 设置图例
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), 
                     fontsize=self.style_config['legend_size'])
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(output_path, dpi=self.style_config['dpi'], 
                       bbox_inches='tight', facecolor=self.style_config['background_color'])
            plt.close()
            
            print(f"✅ 雷达图已保存: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成雷达图时出错: {e}")
            return False
    
    def generate_comparison_chart(self, recommendations: List[Dict], 
                                demand_vector,
                                output_path: str):
        """生成对比图表"""
        try:
            focus_dimensions = demand_vector.focus_dimensions[:6]  # 最多6个维度
            
            if not focus_dimensions:
                focus_dimensions = ['cpu_performance', 'camera_quality', 
                                  'battery_capacity', 'price_value']
            
            # 准备数据
            phone_names = []
            dimension_scores = {dim: [] for dim in focus_dimensions}
            
            for rec in recommendations[:5]:  # 最多5款手机
                phone_names.append(rec['phone'].name)
                phone_vector = rec['phone_vector']
                
                for dimension in focus_dimensions:
                    score = getattr(phone_vector, dimension, 0.0)
                    dimension_scores[dimension].append(score)
            
            # 创建子图
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            axes = axes.flatten()
            
            # 为每个维度创建柱状图
            for i, dimension in enumerate(focus_dimensions):
                if i < len(axes):
                    ax = axes[i]
                    scores = dimension_scores[dimension]
                    
                    bars = ax.bar(phone_names, scores, 
                                color=self.colors[:len(scores)], alpha=0.7)
                    
                    ax.set_title(self.dimension_labels.get(dimension, dimension), 
                               fontsize=12, color=self.style_config['text_color'])
                    ax.set_ylabel('分数', fontsize=10)
                    ax.set_ylim(0, 1)
                    
                    # 旋转x轴标签
                    ax.tick_params(axis='x', rotation=45)
                    
                    # 在柱子上添加数值
                    for bar, score in zip(bars, scores):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                               f'{score:.2f}', ha='center', va='bottom', fontsize=9)
            
            # 隐藏多余的子图
            for i in range(len(focus_dimensions), len(axes)):
                axes[i].set_visible(False)
            
            plt.suptitle('手机性能对比图', fontsize=16, color=self.style_config['text_color'])
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(output_path, dpi=self.style_config['dpi'], 
                       bbox_inches='tight', facecolor=self.style_config['background_color'])
            plt.close()
            
            print(f"✅ 对比图已保存: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成对比图时出错: {e}")
            return False
    
    def generate_summary_chart(self, recommendations: List[Dict], 
                             demand_vector,
                             output_path: str):
        """生成推荐总结图"""
        try:
            # 创建图表
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            # 左侧：匹配分数条形图
            phone_names = []
            match_scores = []
            
            for rec in recommendations[:5]:
                phone_names.append(rec['phone'].name)
                match_scores.append(rec['match_score'])
            
            bars1 = ax1.bar(phone_names, match_scores, 
                           color=self.colors[:len(match_scores)], alpha=0.7)
            ax1.set_title('匹配分数排名', fontsize=14, color=self.style_config['text_color'])
            ax1.set_ylabel('匹配分数', fontsize=12)
            ax1.set_ylim(0, 1)
            ax1.tick_params(axis='x', rotation=45)
            
            # 在柱子上添加数值
            for bar, score in zip(bars1, match_scores):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{score:.3f}', ha='center', va='bottom', fontsize=10)
            
            # 右侧：关注维度热力图
            focus_dimensions = demand_vector.focus_dimensions[:6]
            if focus_dimensions:
                dimension_labels = [self.dimension_labels.get(dim, dim) for dim in focus_dimensions]
                
                # 准备热力图数据
                heatmap_data = []
                for rec in recommendations[:5]:
                    phone_vector = rec['phone_vector']
                    scores = [getattr(phone_vector, dim, 0.0) for dim in focus_dimensions]
                    heatmap_data.append(scores)
                
                im = ax2.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')
                ax2.set_title('关注维度性能热力图', fontsize=14, color=self.style_config['text_color'])
                ax2.set_xticks(range(len(focus_dimensions)))
                ax2.set_xticklabels(dimension_labels, rotation=45, ha='right')
                ax2.set_yticks(range(len(phone_names)))
                ax2.set_yticklabels(phone_names)
                
                # 添加颜色条
                cbar = plt.colorbar(im, ax=ax2)
                cbar.set_label('性能分数', fontsize=10)
                
                # 在热力图中添加数值
                for i in range(len(phone_names)):
                    for j in range(len(focus_dimensions)):
                        text = ax2.text(j, i, f'{heatmap_data[i][j]:.2f}',
                                       ha="center", va="center", color="black", fontsize=9)
            
            plt.suptitle('推荐结果总结', fontsize=16, color=self.style_config['text_color'])
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(output_path, dpi=self.style_config['dpi'], 
                       bbox_inches='tight', facecolor=self.style_config['background_color'])
            plt.close()
            
            print(f"✅ 总结图已保存: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成总结图时出错: {e}")
            return False
    
    def generate_all_charts(self, recommendations: List[Dict], 
                          demand_vector,
                          output_dir: str = "output") -> Dict[str, str]:
        """生成所有类型的图表"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chart_paths = {}
        
        # 生成雷达图
        radar_path = os.path.join(output_dir, f"radar_chart_{timestamp}.png")
        if self.generate_radar_chart(recommendations, demand_vector, radar_path):
            chart_paths['radar'] = radar_path
        
        # 生成对比图
        comparison_path = os.path.join(output_dir, f"comparison_chart_{timestamp}.png")
        if self.generate_comparison_chart(recommendations, demand_vector, comparison_path):
            chart_paths['comparison'] = comparison_path
        
        # 生成总结图
        summary_path = os.path.join(output_dir, f"summary_chart_{timestamp}.png")
        if self.generate_summary_chart(recommendations, demand_vector, summary_path):
            chart_paths['summary'] = summary_path
        
        return chart_paths
    
    def get_dimension_label(self, dimension: str) -> str:
        """获取维度的中文标签"""
        return self.dimension_labels.get(dimension, dimension)
    
    def set_style_config(self, **kwargs):
        """设置图表样式配置"""
        self.style_config.update(kwargs)
    
    def set_colors(self, colors: List[str]):
        """设置颜色配置"""
        self.colors = colors 
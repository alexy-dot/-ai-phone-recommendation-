#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型驱动智能推荐系统 - 主程序
完全基于大模型的智能手机推荐系统
"""

import sys
import os
import uuid
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sample_data import sample_phones, PhoneSpec
from database.database import DatabaseManager
from core.data_processor import PhoneNormalizer, NormalizedPhoneVector
from core.demand_analyzer import DemandParser, UserDemand
from core.recommendation_engine import RecommendationEngine, RecommendationResult
from services.llm_provider import LLMProvider, LLMConfig
from ai.llm_orchestrator import LLMOrchestrator, AIResponse
from utils.visualization import PhoneVisualizer

class AIDrivenPhoneRecommendationSystem:
    """大模型驱动智能推荐系统"""
    
    def __init__(self):
        # 初始化核心组件
        self.normalizer = PhoneNormalizer()
        self.demand_parser = DemandParser()
        self.recommendation_engine = RecommendationEngine()
        
        # 初始化AI组件
        self.llm_provider = LLMProvider()
        self.llm_orchestrator = LLMOrchestrator()
        
        # 初始化数据组件
        self.db_manager = DatabaseManager()
        self.visualizer = PhoneVisualizer()
        
        # 初始化数据
        self.normalized_phones = self._initialize_data()
        
        # 创建输出目录
        os.makedirs('output', exist_ok=True)
        
        # 系统统计
        self.stats = {
            'total_requests': 0,
            'llm_requests': 0,
            'clarification_requests': 0,
            'recommendation_requests': 0,
            'start_time': datetime.now()
        }
        
    def _initialize_data(self) -> List[NormalizedPhoneVector]:
        """初始化数据"""
        print("正在初始化数据...")
        
        # 检查数据库是否已有数据
        existing_phones = self.db_manager.get_all_phones()
        if existing_phones:
            print(f"从数据库加载 {len(existing_phones)} 款手机")
            phones = []
            for record in existing_phones:
                phone = PhoneSpec(
                    name=record.name,
                    cpu=record.cpu,
                    ram_gb=record.ram_gb,
                    storage_gb=record.storage_gb,
                    screen_size_inch=record.screen_size_inch,
                    camera_mp=record.camera_mp,
                    battery_mah=record.battery_mah,
                    weight_g=record.weight_g,
                    price=record.price,
                    highlights=json.loads(record.highlights),
                    rating=record.rating,
                    sales=record.sales,
                    heat_control_score=record.heat_control_score,
                    network_stability_score=record.network_stability_score
                )
                phones.append(phone)
        else:
            print("数据库为空，导入示例数据...")
            phones = sample_phones
            for phone in phones:
                self.db_manager.insert_phone(phone)
        
        # 归一化数据
        normalized_phones = []
        for phone in phones:
            normalized_phone = self.normalizer.normalize_phone(phone)
            normalized_phones.append(normalized_phone)
        
        print(f"数据初始化完成，共加载 {len(normalized_phones)} 款手机")
        return normalized_phones
    
    def start_interactive_mode(self):
        """启动大模型驱动交互模式"""
        print("=" * 60)
        print("🤖 欢迎使用大模型驱动智能推荐系统！")
        print("=" * 60)
        
        # 显示系统状态
        self._show_system_status()
        
        print("💬 您可以这样描述您的需求：")
        print("- 我想买一部拍照好的手机")
        print("- 预算3000-4000，主要玩游戏")
        print("- 需要轻薄便携的商务手机")
        print("- 续航持久的手机，价格不限")
        print("=" * 60)
        print("📝 特殊命令：")
        print("- 'quit' 或 'exit' - 退出系统")
        print("- 'clear' - 清除对话历史")
        print("- 'stats' - 查看系统统计")
        print("- 'chart' - 生成可视化图表")
        print("=" * 60)
        
        session_id = str(uuid.uuid4())
        
        while True:
            try:
                user_input = input("\n👤 您: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 感谢使用，再见！")
                    break
                
                if user_input.lower() == 'clear':
                    self.llm_orchestrator.conversation_memories[session_id] = self.llm_orchestrator.get_or_create_memory(session_id)
                    print("🧹 对话历史已清除")
                    continue
                
                if user_input.lower() == 'stats':
                    self._show_statistics()
                    continue
                
                if user_input.lower() == 'chart':
                    self._generate_charts()
                    continue
                
                if not user_input:
                    continue
                
                # 处理用户输入
                response = self._process_user_input_ai_driven(session_id, user_input)
                
                # 显示系统回复
                print(f"\n🤖 系统: {response['message']}")
                
                # 如果有澄清问题，显示它
                if response.get('clarification_question'):
                    print(f"❓ 澄清问题: {response['clarification_question']}")
                
                # 如果有推荐结果，显示详细信息
                if response.get('recommendations') and 'all_recommendations' in response['recommendations']:
                    self._display_recommendations_ai_driven(response['recommendations'])
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用，再见！")
                break
            except Exception as e:
                print(f"\n❌ 系统出现错误: {e}")
                print("请重新输入您的需求")
    
    def _process_user_input_ai_driven(self, session_id: str, user_input: str) -> Dict:
        """大模型驱动用户输入处理"""
        self.stats['total_requests'] += 1
        
        # 准备手机数据
        phone_data = []
        for phone in self.normalized_phones:
            phone_info = {
                'name': phone.name,
                'price': phone.original_data['price'],
                'cpu': phone.original_data['cpu'],
                'ram_gb': phone.original_data['ram_gb'],
                'storage_gb': phone.original_data['storage_gb'],
                'camera_mp': phone.original_data['camera_mp'],
                'battery_mah': phone.original_data['battery_mah'],
                'weight_g': phone.original_data['weight_g'],
                'rating': phone.original_data['rating'],
                'highlights': phone.original_data['highlights']
            }
            phone_data.append(phone_info)
        
        # 使用LLM编排器处理
        try:
            # 直接同步调用
            response = self.llm_orchestrator.process_user_input(
                user_input, session_id, phone_data
            )
            
            # 转换为字典格式
            result = {
                'message': response.message,
                'llm_used': True
            }
            
            if response.clarification_question:
                result['clarification_question'] = response.clarification_question
                self.stats['clarification_requests'] += 1
            
            if response.recommendations:
                result['recommendations'] = {
                    'all_recommendations': response.recommendations,
                    'total_recommendations': len(response.recommendations)
                }
                self.stats['recommendation_requests'] += 1
            
            self.stats['llm_requests'] += 1
            
            # 保存到数据库
            self.db_manager.save_recommendation_history(
                session_id, user_input, response.message,
                json.dumps(result.get('recommendations', {}))
            )
            
            return result
            
        except Exception as e:
            print(f"LLM编排器处理失败: {e}")
            # 回退到传统方法
            return self._fallback_processing(session_id, user_input)
    
    def _fallback_processing(self, session_id: str, user_input: str) -> Dict:
        """回退处理"""
        print("🔄 使用传统推荐方法")
        
        # 使用传统推荐引擎
        try:
            demand = self.demand_parser.parse_demand(user_input)
            recommendations = self.recommendation_engine.recommend(
                self.normalized_phones, demand, top_n=3
            )
            
            if recommendations:
                # 转换为字典格式
                rec_list = []
                for i, rec in enumerate(recommendations, 1):
                    rec_list.append({
                        'rank': i,
                        'name': rec.phone.name,
                        'price': rec.phone.original_data['price'],
                        'score': rec.score,
                        'reasons': rec.reasons
                    })
                
                # 使用LLM生成解释
                if self.llm_provider.is_available():
                    explanation = self.llm_provider.generate_recommendation_explanation(
                        rec_list[0]['name'],
                        rec_list[0]['reasons'],
                        user_input
                    )
                    message = f"根据您的需求，我为您推荐以下手机：\n\n{explanation}"
                else:
                    message = f"根据您的需求，我为您推荐以下手机：\n\n"
                    for rec in rec_list:
                        message += f"{rec['rank']}. {rec['name']} - ¥{rec['price']}\n"
                        message += f"   推荐理由: {', '.join(rec['reasons'])}\n\n"
                
                return {
                    'message': message,
                    'recommendations': {
                        'all_recommendations': rec_list,
                        'total_recommendations': len(rec_list)
                    },
                    'llm_used': False
                }
            else:
                return {
                    'message': "抱歉，没有找到符合您需求的手机。请尝试调整您的需求描述。",
                    'llm_used': False
                }
                
        except Exception as e:
            print(f"传统处理也失败: {e}")
            return {
                'message': "系统暂时无法处理您的请求，请稍后再试。",
                'llm_used': False
            }
    
    def _display_recommendations_ai_driven(self, recommendations_data: dict):
        """AI驱动推荐结果显示"""
        if 'message' in recommendations_data:
            print(f"\n{recommendations_data['message']}")
            return
        
        print(f"\n🎯 为您找到 {recommendations_data['total_recommendations']} 款推荐手机：")
        print("-" * 60)
        
        for rec in recommendations_data['all_recommendations']:
            print(f"🥇 第{rec['rank']}名: {rec['name']}")
            print(f"💰 价格: ¥{rec['price']}")
            print(f"📊 匹配度: {rec['score']:.3f}")
            print(f"💡 推荐理由: {', '.join(rec['reasons'])}")
            print("-" * 60)
        
        # 询问是否生成可视化图表
        print("\n📈 是否生成可视化对比图表？(y/n): ", end="")
        choice = input().strip().lower()
        if choice in ['y', 'yes', '是']:
            self._generate_recommendation_charts(recommendations_data['all_recommendations'])
    
    def _generate_recommendation_charts(self, recommendations: List[Dict]):
        """为推荐结果生成图表"""
        try:
            # 准备数据
            phones_data = []
            for rec in recommendations:
                phone_name = rec['name']
                for phone in self.normalized_phones:
                    if phone.name == phone_name:
                        phone_dict = {
                            'name': phone.name,
                            'price': phone.original_data['price'],
                            'performance_score': phone.performance_score,
                            'camera_score': phone.camera_score,
                            'battery_score': phone.battery_score,
                            'portability_score': phone.portability_score,
                            'price_score': phone.price_score,
                            'appearance_score': phone.appearance_score,
                            **phone.original_data
                        }
                        phones_data.append(phone_dict)
                        break
            
            # 生成雷达图
            radar_path = f"output/ai_recommendation_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_radar_chart(phones_data, radar_path)
            print(f"📊 雷达图已保存: {radar_path}")
            
            # 生成对比图
            comparison_path = f"output/ai_recommendation_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_comparison_chart(phones_data, comparison_path)
            print(f"📈 对比图已保存: {comparison_path}")
            
        except Exception as e:
            print(f"❌ 生成图表时出错: {e}")
    
    def _generate_charts(self):
        """生成系统图表"""
        try:
            # 获取所有手机数据
            all_phones = self.db_manager.get_all_phones()
            phones_data = []
            
            for record in all_phones:
                phone_dict = {
                    'name': record.name,
                    'price': record.price,
                    'cpu': record.cpu,
                    'ram_gb': record.ram_gb,
                    'storage_gb': record.storage_gb,
                    'screen_size_inch': record.screen_size_inch,
                    'camera_mp': record.camera_mp,
                    'battery_mah': record.battery_mah,
                    'weight_g': record.weight_g,
                    'rating': record.rating,
                    'sales': record.sales
                }
                phones_data.append(phone_dict)
            
            # 生成特性对比表
            feature_path = f"output/ai_feature_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_feature_comparison(phones_data[:5], feature_path)
            print(f"📊 特性对比表已保存: {feature_path}")
            
        except Exception as e:
            print(f"❌ 生成图表时出错: {e}")
    
    def _show_system_status(self):
        """显示系统状态"""
        print("🔧 系统状态:")
        print(f"- 🤖 LLM服务: {'✅ 可用' if self.llm_provider.is_available() else '❌ 不可用'}")
        print(f"- 🗄️ 数据库: ✅ 已连接")
        print(f"- 📊 可视化: ✅ 已就绪")
        print(f"- 🧠 AI编排器: ✅ 已就绪")
        
        # 显示数据库统计
        stats = self.db_manager.get_statistics()
        print(f"- 📱 手机数据: {stats['total_phones']} 款")
        print(f"- 💰 平均价格: ¥{stats['avg_price']:.0f}")
        print(f"- ⭐ 平均评分: {stats['avg_rating']:.1f}/5.0")
        print()
    
    def _show_statistics(self):
        """显示系统统计信息"""
        print("\n📊 系统统计信息:")
        print("-" * 40)
        print(f"🕐 运行时间: {datetime.now() - self.stats['start_time']}")
        print(f"📝 总请求数: {self.stats['total_requests']}")
        print(f"🤖 LLM请求数: {self.stats['llm_requests']}")
        print(f"❓ 澄清请求数: {self.stats['clarification_requests']}")
        print(f"🎯 推荐请求数: {self.stats['recommendation_requests']}")
        
        if self.stats['total_requests'] > 0:
            llm_rate = self.stats['llm_requests'] / self.stats['total_requests']
            print(f"🤖 LLM使用率: {llm_rate:.1%}")
        
        # 数据库统计
        db_stats = self.db_manager.get_statistics()
        print(f"📱 手机总数: {db_stats['total_phones']}")
        print(f"💰 价格范围: ¥{db_stats['min_price']} - ¥{db_stats['max_price']}")
        print(f"👥 用户会话: {db_stats['total_sessions']}")
        print("-" * 40)
    
    def run_demo(self):
        """运行AI驱动演示"""
        print("=" * 60)
        print("🤖 AI驱动演示模式 - 测试智能对话功能")
        print("=" * 60)
        
        test_cases = [
            "你好，我想买一部手机",
            "预算3000-4000，拍照优先",
            "能详细介绍一下这些手机吗？",
            "哪个性价比最高？",
            "谢谢你的推荐"
        ]
        
        session_id = str(uuid.uuid4())
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🎬 演示 {i}: {test_case}")
            response = self._process_user_input_ai_driven(session_id, test_case)
            print(f"🤖 系统回复: {response['message']}")
            print("\n" + "="*60)
            
            if i < len(test_cases):
                input("⏸️ 按回车键继续下一个演示...")
    
    def test_recommendation_ai_driven(self, test_demand: str):
        """AI驱动推荐测试"""
        print(f"🧪 测试需求: {test_demand}")
        print("-" * 40)
        
        # 使用AI驱动处理
        response = self._process_user_input_ai_driven(
            str(uuid.uuid4()), test_demand
        )
        
        print(f"🤖 系统回复: {response['message']}")
        
        if response.get('recommendations'):
            self._display_recommendations_ai_driven(response['recommendations'])

def main():
    """主函数"""
    system = AIDrivenPhoneRecommendationSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'demo':
            system.run_demo()
        elif command == 'test':
            if len(sys.argv) > 2:
                test_demand = ' '.join(sys.argv[2:])
                system.test_recommendation_ai_driven(test_demand)
            else:
                print("请提供测试需求，例如: python main_ai_driven.py test '预算3000-4000，拍照优先'")
        else:
            print("未知命令。可用命令:")
            print("  python main_ai_driven.py demo    - 运行演示")
            print("  python main_ai_driven.py test <需求> - 测试特定需求")
            print("  python main_ai_driven.py         - 启动交互模式")
    else:
        # 默认启动交互模式
        system.start_interactive_mode()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能手机/电脑参数对比与对话推荐系统 - 增强版
集成LLM、可视化、数据库等新功能
"""

import sys
import os
import uuid
import json
from typing import List, Dict, Optional
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.sample_data import sample_phones, PhoneSpec
from database.database import DatabaseManager
from core.data_processor import PhoneNormalizer, NormalizedPhoneVector
from core.demand_analyzer import DemandParser, UserDemand
from core.recommendation_engine import RecommendationEngine, RecommendationResult
from core.dialogue_controller import DialogueManager, DialogueState
from services.llm_provider import LLMProvider, LLMConfig
from utils.visualization import PhoneVisualizer

class EnhancedPhoneRecommendationSystem:
    """增强版手机推荐系统"""
    
    def __init__(self):
        # 初始化核心组件
        self.normalizer = PhoneNormalizer()
        self.demand_parser = DemandParser()
        self.recommendation_engine = RecommendationEngine()
        self.dialogue_manager = DialogueManager()
        
        # 初始化新功能组件
        self.db_manager = DatabaseManager()
        self.llm_provider = LLMProvider()
        self.visualizer = PhoneVisualizer()
        
        # 初始化数据
        self.normalized_phones = self._initialize_data()
        
        # 创建输出目录
        os.makedirs('output', exist_ok=True)
        
    def _initialize_data(self) -> List[NormalizedPhoneVector]:
        """初始化数据，将原始数据归一化并存储到数据库"""
        print("正在初始化数据...")
        
        # 检查数据库是否已有数据
        existing_phones = self.db_manager.get_all_phones()
        if existing_phones:
            print(f"从数据库加载 {len(existing_phones)} 款手机")
            # 将数据库记录转换为PhoneSpec对象
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
            # 将示例数据存储到数据库
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
        """启动增强版交互模式"""
        print("=" * 60)
        print("欢迎使用增强版智能手机推荐系统！")
        print("=" * 60)
        
        # 显示系统状态
        self._show_system_status()
        
        print("您可以描述您的需求，比如：")
        print("- 预算3000-4000，拍照优先")
        print("- 想要轻薄便携的手机")
        print("- 需要性能强劲的游戏手机")
        print("- 续航持久的商务手机")
        print("输入 'quit' 或 'exit' 退出系统")
        print("输入 'chart' 生成可视化图表")
        print("输入 'stats' 查看系统统计")
        print("=" * 60)
        
        session_id = str(uuid.uuid4())
        
        while True:
            try:
                user_input = input("\n您: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("感谢使用，再见！")
                    break
                
                if user_input.lower() == 'chart':
                    self._generate_charts()
                    continue
                
                if user_input.lower() == 'stats':
                    self._show_statistics()
                    continue
                
                if not user_input:
                    continue
                
                # 处理用户输入
                response = self._process_user_input_enhanced(session_id, user_input)
                
                # 显示系统回复
                print(f"\n系统: {response['message']}")
                
                # 如果有澄清问题，显示它
                if response.get('clarification_question'):
                    print(f"澄清问题: {response['clarification_question']}")
                
                # 如果有推荐结果，显示详细信息
                if response.get('recommendations') and 'all_recommendations' in response['recommendations']:
                    self._display_recommendations_enhanced(response['recommendations'])
                
            except KeyboardInterrupt:
                print("\n\n感谢使用，再见！")
                break
            except Exception as e:
                print(f"\n系统出现错误: {e}")
                print("请重新输入您的需求")
    
    def _process_user_input_enhanced(self, session_id: str, user_input: str) -> Dict:
        """增强版用户输入处理 - 真正使用大模型"""
        # 使用LLM理解用户意图
        if self.llm_provider.is_available():
            llm_analysis = self.llm_provider.understand_intent(user_input)
            print(f"LLM分析: {llm_analysis}")
            
            # 检查是否需要澄清
            if llm_analysis.get('clarification_needed', False):
                clarification_question = self.llm_provider.generate_clarification_question(
                    llm_analysis.get('unclear_aspect', '需求'),
                    "",
                    []
                )
                return {
                    'message': f"我理解您的需求，但还需要一些信息来为您提供更准确的推荐。{clarification_question}",
                    'clarification_question': clarification_question
                }
        
        # 构建LLM请求
        system_prompt = """你是一个专业的手机推荐助手。你需要根据用户的需求，从提供的手机数据中选择最合适的手机进行推荐。

你的任务包括：
1. 理解用户的需求和偏好
2. 分析手机的各项参数和性能
3. 根据用户需求进行匹配和推荐
4. 提供详细的推荐理由和对比分析
5. 进行自然的对话交流，回答用户的问题

请确保推荐的手机符合用户的主要需求，并提供充分的理由说明为什么这些手机是最佳选择。
请用自然、友好的语气与用户交流，像真人导购一样。"""

        # 获取手机数据
        phone_data = []
        for phone in self.normalized_phones[:10]:  # 只取前10款
            phone_info = {
                'name': phone.name,
                'price': phone.original_data['price'],
                'cpu': phone.original_data['cpu'],
                'ram_gb': phone.original_data['ram_gb'],
                'storage_gb': phone.original_data['storage_gb'],
                'camera_mp': phone.original_data['camera_mp'],
                'battery_mah': phone.original_data['battery_mah'],
                'rating': phone.original_data['rating']
            }
            phone_data.append(phone_info)
        
        # 构建完整提示词
        phone_list = "\n".join([f"{i+1}. {phone['name']} - ¥{phone['price']} - {phone['cpu']} - {phone['camera_mp']}MP - {phone['battery_mah']}mAh" 
                               for i, phone in enumerate(phone_data)])
        
        full_prompt = f"""{system_prompt}

可用手机:
{phone_list}

用户: {user_input}

助手: 请根据用户需求提供专业的手机推荐建议。如果用户需求不够明确，请友好地询问更多信息。如果可以提供推荐，请详细说明推荐理由和手机特点。请用自然、友好的语气回复，像真人导购一样。"""
        
        # 使用LLM生成回复
        if self.llm_provider.is_available():
            llm_response = self.llm_provider._make_api_request(full_prompt)
            if llm_response:
                # 检查是否需要推荐结果
                if any(keyword in user_input for keyword in ['推荐', '建议', '选择', '买', '购买', '要', '需要', '想要']):
                    # 获取推荐结果
                    try:
                        demand = self.demand_parser.parse_demand(user_input)
                        recommendations = self.recommendation_engine.recommend(
                            self.normalized_phones, demand, top_n=3
                        )
                        
                        if recommendations:
                            # 添加推荐结果到回复
                            recommendation_text = "\n\n推荐结果:\n"
                            for i, rec in enumerate(recommendations, 1):
                                recommendation_text += f"{i}. {rec.phone.name} - ¥{rec.phone.original_data['price']} - 匹配度: {rec.score:.3f}\n"
                                recommendation_text += f"   推荐理由: {', '.join(rec.reasons)}\n\n"
                            
                            llm_response += recommendation_text
                    except Exception as e:
                        print(f"获取推荐失败: {e}")
                
                # 保存到数据库
                self.db_manager.save_recommendation_history(
                    session_id, user_input, llm_response,
                    json.dumps({})
                )
                
                return {
                    'message': llm_response,
                    'llm_used': True
                }
        
        # 如果LLM不可用，使用传统方法
        print("🔄 LLM不可用，使用传统推荐方法")
        response = self.dialogue_manager.process_user_input(
            session_id, user_input, self.normalized_phones
        )
        
        # 保存到数据库
        self.db_manager.save_recommendation_history(
            session_id, user_input, response['message'],
            json.dumps(response.get('recommendations', {}))
        )
        
        response['llm_used'] = False
        return response
    
    def _display_recommendations_enhanced(self, recommendations_data: dict):
        """增强版推荐结果显示"""
        if 'message' in recommendations_data:
            print(f"\n{recommendations_data['message']}")
            return
        
        print(f"\n为您找到 {recommendations_data['total_recommendations']} 款推荐手机：")
        print("-" * 60)
        
        for rec in recommendations_data['all_recommendations']:
            print(f"第{rec['rank']}名: {rec['name']}")
            print(f"价格: ¥{rec['price']}")
            print(f"匹配度: {rec['score']:.3f}")
            print(f"推荐理由: {', '.join(rec['reasons'])}")
            print("-" * 60)
        
        # 询问是否生成可视化图表
        print("\n是否生成可视化对比图表？(y/n): ", end="")
        choice = input().strip().lower()
        if choice in ['y', 'yes', '是']:
            self._generate_recommendation_charts(recommendations_data['all_recommendations'])
    
    def _generate_recommendation_charts(self, recommendations: List[Dict]):
        """为推荐结果生成图表"""
        try:
            # 准备数据
            phones_data = []
            for rec in recommendations:
                # 从归一化数据中获取原始数据
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
            radar_path = f"output/recommendation_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_radar_chart(phones_data, radar_path)
            print(f"雷达图已保存: {radar_path}")
            
            # 生成对比图
            comparison_path = f"output/recommendation_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_comparison_chart(phones_data, comparison_path)
            print(f"对比图已保存: {comparison_path}")
            
            # 生成推荐总结图
            summary_path = f"output/recommendation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_recommendation_summary(recommendations, summary_path)
            print(f"推荐总结图已保存: {summary_path}")
            
        except Exception as e:
            print(f"生成图表时出错: {e}")
    
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
            feature_path = f"output/feature_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.visualizer.create_feature_comparison(phones_data[:5], feature_path)
            print(f"特性对比表已保存: {feature_path}")
            
        except Exception as e:
            print(f"生成图表时出错: {e}")
    
    def _show_system_status(self):
        """显示系统状态"""
        print("系统状态:")
        print(f"- LLM服务: {'可用' if self.llm_provider.is_available() else '不可用'}")
        print(f"- 数据库: 已连接")
        print(f"- 可视化: 已就绪")
        
        # 显示数据库统计
        stats = self.db_manager.get_statistics()
        print(f"- 手机数据: {stats['total_phones']} 款")
        print(f"- 平均价格: ¥{stats['avg_price']:.0f}")
        print(f"- 平均评分: {stats['avg_rating']:.1f}/5.0")
        print()
    
    def _show_statistics(self):
        """显示系统统计信息"""
        stats = self.db_manager.get_statistics()
        
        print("\n系统统计信息:")
        print("-" * 40)
        print(f"手机总数: {stats['total_phones']}")
        print(f"价格范围: ¥{stats['min_price']} - ¥{stats['max_price']}")
        print(f"平均价格: ¥{stats['avg_price']:.0f}")
        print(f"平均评分: {stats['avg_rating']:.1f}/5.0")
        print(f"用户会话: {stats['total_sessions']}")
        print("-" * 40)
    
    def run_demo(self):
        """运行增强版演示"""
        print("=" * 60)
        print("增强版演示模式 - 测试不同需求场景")
        print("=" * 60)
        
        test_cases = [
            "预算3000-4000，拍照优先",
            "想要轻薄便携的手机",
            "需要性能强劲的游戏手机",
            "续航持久的商务手机",
            "高端旗舰手机，预算不限"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n演示 {i}: {test_case}")
            self.test_recommendation_enhanced(test_case)
            print("\n" + "="*60)
            
            if i < len(test_cases):
                input("按回车键继续下一个演示...")
    
    def test_recommendation_enhanced(self, test_demand: str):
        """增强版推荐测试"""
        print(f"测试需求: {test_demand}")
        print("-" * 40)
        
        # 使用LLM分析需求
        if self.llm_provider.is_available():
            llm_analysis = self.llm_provider.understand_intent(test_demand)
            print(f"LLM分析结果: {llm_analysis}")
        
        # 解析需求
        demand = self.demand_parser.parse_demand(test_demand)
        print(f"解析结果:")
        print(f"  预算范围: {demand.budget_min}-{demand.budget_max}")
        print(f"  偏好: {demand.preferences}")
        print(f"  权重分配:")
        print(f"    性能: {demand.performance_weight:.2f}")
        print(f"    拍照: {demand.camera_weight:.2f}")
        print(f"    续航: {demand.battery_weight:.2f}")
        print(f"    便携: {demand.portability_weight:.2f}")
        print(f"    价格: {demand.price_weight:.2f}")
        print(f"    外观: {demand.appearance_weight:.2f}")
        
        # 获取推荐
        recommendations = self.recommendation_engine.recommend(
            self.normalized_phones, demand, top_n=3
        )
        
        # 显示推荐结果
        summary = self.recommendation_engine.get_recommendation_summary(recommendations)
        self._display_recommendations_enhanced(summary)

def main():
    """主函数"""
    system = EnhancedPhoneRecommendationSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'demo':
            system.run_demo()
        elif command == 'test':
            if len(sys.argv) > 2:
                test_demand = ' '.join(sys.argv[2:])
                system.test_recommendation_enhanced(test_demand)
            else:
                print("请提供测试需求，例如: python main_enhanced.py test '预算3000-4000，拍照优先'")
        else:
            print("未知命令。可用命令:")
            print("  python main_enhanced.py demo    - 运行演示")
            print("  python main_enhanced.py test <需求> - 测试特定需求")
            print("  python main_enhanced.py         - 启动交互模式")
    else:
        # 默认启动交互模式
        system.start_interactive_mode()

if __name__ == "__main__":
    main() 
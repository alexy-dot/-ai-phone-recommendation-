#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Schema的智能推荐系统 - 主程序
整合Schema抽象层、大模型和向量匹配
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
from ai.demand_schema import DemandSchemaMatcher, DemandSchema
from ai.schema_based_recommendation import SchemaBasedRecommendationEngine, SchemaRecommendationResult
from services.llm_provider import LLMProvider
from utils.visualization import PhoneVisualizer


class SchemaBasedRecommendationSystem:
    """基于Schema的智能推荐系统"""
    
    def __init__(self):
        # 初始化核心组件
        self.schema_matcher = DemandSchemaMatcher()
        self.recommendation_engine = SchemaBasedRecommendationEngine()
        self.db_manager = DatabaseManager()
        self.llm_provider = LLMProvider()
        self.visualizer = PhoneVisualizer()
        
        # 初始化数据
        self.phones = self._initialize_data()
        
        # 创建输出目录
        os.makedirs('output', exist_ok=True)
        
        # 对话历史管理
        self.conversation_histories = {}
        
        # 系统统计
        self.stats = {
            'total_requests': 0,
            'successful_recommendations': 0,
            'clarification_questions': 0,
            'average_processing_time': 0.0,
            'schema_completeness_avg': 0.0,
            'start_time': datetime.now()
        }
    
    def _initialize_data(self) -> List[PhoneSpec]:
        """初始化手机数据"""
        print("📊 正在初始化手机数据...")
        
        # 检查数据库是否已有数据
        existing_phones = self.db_manager.get_all_phones()
        if existing_phones:
            print(f"✅ 从数据库加载 {len(existing_phones)} 款手机")
            return existing_phones
        
        # 使用示例数据
        print(f"✅ 使用示例数据 {len(sample_phones)} 款手机")
        
        # 保存到数据库
        for phone in sample_phones:
            self.db_manager.save_phone(phone)
        
        return sample_phones
    
    def start_interactive_mode(self):
        """启动交互模式"""
        print("🎉 欢迎使用基于Schema的智能推荐系统！")
        print("=" * 60)
        self._show_system_status()
        print("=" * 60)
        
        session_id = str(uuid.uuid4())
        print(f"🆔 会话ID: {session_id}")
        print("\n💡 您可以这样描述您的需求：")
        print("   • 我想要拍照好的手机")
        print("   • 需要性能强劲的游戏手机")
        print("   • 预算3000-4000，轻薄便携")
        print("   • 续航持久的商务手机")
        print("   • 性价比高的手机")
        print("   • 喜欢苹果，拍照要好")
        print("   • 不要小米，预算5000左右")
        print("\n🔧 特殊命令：")
        print("   • 'quit' 或 'exit' - 退出系统")
        print("   • 'clear' - 清除对话历史")
        print("   • 'stats' - 查看系统统计")
        print("   • 'history' - 查看对话历史")
        print("   • 'help' - 查看帮助信息")
        print("   • 'schema' - 查看当前Schema")
        
        while True:
            try:
                user_input = input("\n👤 您: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 感谢使用基于Schema的智能推荐系统，再见！")
                    break
                
                if user_input.lower() == 'clear':
                    self.conversation_histories[session_id] = []
                    print("🧹 对话历史已清除")
                    continue
                
                if user_input.lower() == 'stats':
                    self._show_statistics()
                    continue
                
                if user_input.lower() == 'history':
                    self._show_conversation_history(session_id)
                    continue
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'schema':
                    self._show_current_schema(session_id)
                    continue
                
                if not user_input:
                    continue
                
                # 处理用户输入
                result = self._process_user_input(session_id, user_input)
                
                # 显示推荐结果
                self._display_recommendation_result(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 感谢使用基于Schema的智能推荐系统，再见！")
                break
            except Exception as e:
                print(f"\n❌ 系统出现错误: {e}")
                print("请重新输入您的需求")
    
    def _process_user_input(self, session_id: str, user_input: str) -> SchemaRecommendationResult:
        """处理用户输入"""
        self.stats['total_requests'] += 1
        start_time = datetime.now()
        
        print(f"\n🤖 系统: 正在分析您的需求...")
        
        # 获取对话历史
        conversation_history = self.conversation_histories.get(session_id, [])
        
        # 使用Schema推荐引擎
        result = self.recommendation_engine.recommend(
            phones=self.phones,
            user_input=user_input,
            conversation_history=conversation_history,
            top_n=5
        )
        
        # 更新对话历史
        conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        conversation_history.append({
            'role': 'assistant',
            'content': f"基于Schema推荐了{len(result.recommendations)}款手机，策略:{result.recommendation_strategy}",
            'timestamp': datetime.now().isoformat(),
            'schema': result.demand_schema.to_dict()
        })
        
        self.conversation_histories[session_id] = conversation_history
        
        # 更新统计信息
        if result.recommendations:
            self.stats['successful_recommendations'] += 1
        
        if result.clarification_questions:
            self.stats['clarification_questions'] += len(result.clarification_questions)
        
        # 更新Schema完整性平均值
        self.stats['schema_completeness_avg'] = (
            (self.stats['schema_completeness_avg'] * (self.stats['total_requests'] - 1) + 
             result.demand_schema.completeness_score) / self.stats['total_requests']
        )
        
        # 计算平均处理时间
        processing_time = (datetime.now() - start_time).total_seconds()
        total_time = (datetime.now() - self.stats['start_time']).total_seconds()
        self.stats['average_processing_time'] = total_time / self.stats['total_requests']
        
        # 保存到数据库
        self.db_manager.save_recommendation_history(
            session_id, user_input, 
            f"Schema推荐{len(result.recommendations)}款手机",
            json.dumps({
                'recommendations': [rec['phone'].name for rec in result.recommendations],
                'strategy': result.recommendation_strategy,
                'confidence_score': result.confidence_score,
                'processing_time': processing_time,
                'schema_completeness': result.demand_schema.completeness_score,
                'schema_confidence': result.demand_schema.confidence_score
            })
        )
        
        return result
    
    def _display_recommendation_result(self, result: SchemaRecommendationResult):
        """显示推荐结果"""
        print(f"\n🎯 为您找到 {len(result.recommendations)} 款推荐手机：")
        print("-" * 60)
        
        # 显示Schema分析
        schema = result.demand_schema
        print(f"📋 Schema分析:")
        print(f"   • 需求片段: {len(schema.segments)} 个")
        for i, segment in enumerate(schema.segments, 1):
            print(f"     {i}. {segment.description} (权重: {segment.weight:.2f})")
        
        print(f"   • 预算范围: {schema.budget_range if schema.budget_range else '未指定'}")
        print(f"   • 品牌偏好: {schema.brand_preferences if schema.brand_preferences else '无偏好'}")
        print(f"   • 使用场景: {', '.join(schema.usage_scenarios) if schema.usage_scenarios else '未指定'}")
        print(f"   • Schema完整性: {schema.completeness_score:.2f}")
        print(f"   • 匹配置信度: {schema.confidence_score:.2f}")
        print(f"   • 推荐策略: {result.recommendation_strategy}")
        print(f"   • 推荐置信度: {result.confidence_score:.2f}")
        
        # 显示推荐结果
        for i, rec in enumerate(result.recommendations, 1):
            phone = rec['phone']
            match_score = rec['match_score']
            match_reasons = rec.get('match_reasons', [])
            recommendation_type = rec.get('recommendation_type', '')
            
            print(f"\n🥇 第{i}名: {phone.name}")
            print(f"💰 价格: ¥{phone.price}")
            print(f"📊 匹配度: {match_score:.3f}")
            print(f"🎯 推荐类型: {recommendation_type}")
            print(f"💡 推荐理由: {', '.join(match_reasons)}")
            
            # 显示详细参数
            print(f"📱 参数: {phone.cpu} | {phone.ram_gb}GB | {phone.storage_gb}GB | {phone.camera_mp}MP | {phone.battery_mah}mAh")
        
        # 显示匹配详情
        if result.match_details:
            print(f"\n📊 匹配详情:")
            for detail in result.match_details[:3]:  # 显示前3个
                print(f"   • {detail['phone_name']}: 匹配度{detail['match_score']:.3f}, 匹配片段{detail['schema_analysis']['segments_matched']}个")
        
        # 显示澄清问题
        if result.clarification_questions:
            print(f"\n❓ 为了更好地为您推荐，请回答以下问题：")
            for i, question in enumerate(result.clarification_questions, 1):
                print(f"   {i}. {question}")
        
        # 显示下一步建议
        if result.next_steps:
            print(f"\n🔄 下一步建议：")
            for step in result.next_steps:
                print(f"   • {step}")
        
        # 显示处理时间
        print(f"\n⏱️ 处理时间: {result.confidence_score:.2f}秒")
    
    def _show_system_status(self):
        """显示系统状态"""
        print("📊 系统状态:")
        print(f"   • 手机数据: {len(self.phones)} 款")
        print(f"   • LLM服务: {'✅ 可用' if self.llm_provider.is_available() else '❌ 不可用'}")
        print(f"   • 数据库: {'✅ 已连接' if self.db_manager else '❌ 未连接'}")
        print(f"   • 平均价格: ¥{sum(p.price for p in self.phones) / len(self.phones):.0f}")
        print(f"   • 价格范围: ¥{min(p.price for p in self.phones)} - ¥{max(p.price for p in self.phones)}")
        print(f"   • Schema系统: ✅ 已启用")
        print(f"   • 向量匹配: 🔄 待集成embedding模型")
    
    def _show_statistics(self):
        """显示系统统计"""
        print("\n📈 系统统计:")
        print(f"   • 总请求数: {self.stats['total_requests']}")
        print(f"   • 成功推荐: {self.stats['successful_recommendations']}")
        print(f"   • 澄清问题: {self.stats['clarification_questions']}")
        print(f"   • 成功率: {self.stats['successful_recommendations']/max(1, self.stats['total_requests'])*100:.1f}%")
        print(f"   • 平均处理时间: {self.stats['average_processing_time']:.2f}秒")
        print(f"   • 平均Schema完整性: {self.stats['schema_completeness_avg']:.2f}")
        
        uptime = datetime.now() - self.stats['start_time']
        print(f"   • 运行时间: {uptime.total_seconds()/3600:.1f}小时")
    
    def _show_conversation_history(self, session_id: str):
        """显示对话历史"""
        history = self.conversation_histories.get(session_id, [])
        
        if not history:
            print("\n📝 暂无对话历史")
            return
        
        print(f"\n📝 对话历史 (会话ID: {session_id}):")
        print("-" * 40)
        
        for i, msg in enumerate(history, 1):
            role = "👤 用户" if msg['role'] == 'user' else "🤖 系统"
            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            print(f"{i}. {role}: {content}")
    
    def _show_current_schema(self, session_id: str):
        """显示当前Schema"""
        history = self.conversation_histories.get(session_id, [])
        
        if not history:
            print("\n📋 暂无Schema信息")
            return
        
        # 找到最新的Schema
        latest_schema = None
        for msg in reversed(history):
            if msg.get('role') == 'assistant' and msg.get('schema'):
                latest_schema = msg['schema']
                break
        
        if latest_schema:
            print("\n📋 当前Schema信息:")
            print("-" * 40)
            print(f"需求片段: {len(latest_schema.get('segments', []))} 个")
            print(f"预算范围: {latest_schema.get('budget_range', '未指定')}")
            print(f"品牌偏好: {latest_schema.get('brand_preferences', '无偏好')}")
            print(f"使用场景: {latest_schema.get('usage_scenarios', '未指定')}")
            print(f"完整性评分: {latest_schema.get('completeness_score', 0):.2f}")
            print(f"置信度: {latest_schema.get('confidence_score', 0):.2f}")
        else:
            print("\n📋 暂无Schema信息")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n📖 使用帮助:")
        print("=" * 40)
        print("💡 需求描述技巧:")
        print("   • 明确主要需求: '拍照好'、'性能强'、'续航久'")
        print("   • 提供预算信息: '3000-4000元'、'5000左右'、'不超过6000'")
        print("   • 说明使用场景: '玩游戏'、'商务办公'、'日常使用'")
        print("   • 品牌偏好: '喜欢苹果'、'不要小米'、'华为不错'")
        print("   • 组合需求: '喜欢苹果，拍照要好，预算5000左右'")
        print("\n🔄 交互流程:")
        print("   1. 描述您的需求")
        print("   2. 系统解析为Schema")
        print("   3. 基于Schema智能推荐")
        print("   4. 回答澄清问题（如有）")
        print("   5. 获得更精确的推荐")
        print("\n🔧 系统特性:")
        print("   • Schema抽象: 标准化需求结构")
        print("   • 大模型理解: 语义理解和参数提取")
        print("   • 向量匹配: 智能匹配需求片段")
        print("   • 动态权重: 根据需求调整权重")
        print("   • 智能引导: 主动询问缺失信息")
        print("\n📊 Schema系统:")
        print("   • 需求片段: 最小可匹配单元")
        print("   • 优先级: 关键/重要/一般/可选")
        print("   • 约束条件: 具体的参数要求")
        print("   • 完整性评估: 需求信息完整度")
    
    def run_demo(self):
        """运行演示"""
        print("🎬 运行基于Schema的智能推荐系统演示...")
        
        demo_queries = [
            "我想要拍照好的手机",
            "需要性能强劲的游戏手机",
            "预算3000-4000，轻薄便携",
            "喜欢苹果，拍照要好，预算5000左右",
            "不要小米，续航久，商务办公用"
        ]
        
        session_id = str(uuid.uuid4())
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{'='*60}")
            print(f"演示 {i}/{len(demo_queries)}: {query}")
            print(f"{'='*60}")
            
            result = self._process_user_input(session_id, query)
            self._display_recommendation_result(result)
            
            if i < len(demo_queries):
                input("\n按回车键继续下一个演示...")
        
        print(f"\n🎉 演示完成！")
    
    def test_recommendation(self, test_demand: str):
        """测试特定需求"""
        print(f"🧪 测试需求: {test_demand}")
        print("-" * 40)
        
        session_id = str(uuid.uuid4())
        result = self._process_user_input(session_id, test_demand)
        self._display_recommendation_result(result)


def main():
    """主函数"""
    system = SchemaBasedRecommendationSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'demo':
            system.run_demo()
        elif command == 'test':
            if len(sys.argv) > 2:
                test_demand = ' '.join(sys.argv[2:])
                system.test_recommendation(test_demand)
            else:
                print("请提供测试需求，例如: python main_schema_based.py test '我想要拍照好的手机'")
        else:
            print("未知命令。可用命令:")
            print("  python main_schema_based.py demo    - 运行演示")
            print("  python main_schema_based.py test <需求> - 测试特定需求")
            print("  python main_schema_based.py         - 启动交互模式")
    else:
        # 默认启动交互模式
        system.start_interactive_mode()


if __name__ == "__main__":
    main() 
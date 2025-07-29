from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from core.demand_analyzer import UserDemand, DemandParser
from core.recommendation_engine import RecommendationEngine, RecommendationResult

class DialogueState(Enum):
    """对话状态"""
    INITIAL = "initial"           # 初始状态
    COLLECTING_DEMAND = "collecting_demand"  # 收集需求
    CLARIFYING = "clarifying"     # 澄清需求
    RECOMMENDING = "recommending" # 推荐中
    FOLLOW_UP = "follow_up"       # 后续跟进

@dataclass
class DialogueContext:
    """对话上下文"""
    session_id: str
    state: DialogueState = DialogueState.INITIAL
    current_demand: Optional[UserDemand] = None
    conversation_history: List[Dict] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)
    current_recommendations: List[RecommendationResult] = field(default_factory=list)
    user_preferences: Dict = field(default_factory=dict)

class DialogueManager:
    """对话管理器"""
    
    def __init__(self):
        self.demand_parser = DemandParser()
        self.recommendation_engine = RecommendationEngine()
        self.sessions: Dict[str, DialogueContext] = {}
        
        # 澄清问题模板
        self.clarification_templates = {
            'budget': [
                "您的预算大概是多少呢？",
                "请问您能接受的价格范围是？",
                "您希望购买什么价位的手机？"
            ],
            'camera_preference': [
                "您更注重夜景拍摄还是广角拍摄？",
                "拍照方面，您更看重哪个功能？",
                "您主要用手机拍什么类型的照片？"
            ],
            'performance_preference': [
                "您主要用手机做什么？游戏、工作还是日常使用？",
                "您对手机性能有什么特殊要求吗？",
                "您会玩大型游戏吗？"
            ],
            'portability_preference': [
                "您更偏好大屏还是小屏手机？",
                "便携性对您来说重要吗？",
                "您希望手机轻便一些还是功能更全面？"
            ],
            'battery_preference': [
                "您对续航有什么要求？",
                "您希望手机能用多久？",
                "快充功能对您重要吗？"
            ]
        }
    
    def create_session(self, session_id: str) -> DialogueContext:
        """创建新的对话会话"""
        context = DialogueContext(session_id=session_id)
        self.sessions[session_id] = context
        return context
    
    def get_session(self, session_id: str) -> Optional[DialogueContext]:
        """获取对话会话"""
        return self.sessions.get(session_id)
    
    def _detect_clarification_needs(self, demand: UserDemand, context: DialogueContext) -> List[str]:
        """检测需要澄清的需求点，避免重复"""
        clarification_needs = []
        
        # 检查预算是否明确
        if demand.budget_min is None and demand.budget_max is None:
            # 检查是否已经问过预算问题
            if not any('预算' in q or '价格' in q or '价位' in q for q in context.clarification_questions):
                clarification_needs.append('budget')
        
        # 检查偏好是否明确
        if not demand.preferences:
            # 检查是否已经问过一般偏好问题
            if not any('主要用' in q or '做什么' in q or '场景' in q for q in context.clarification_questions):
                clarification_needs.append('usage_scenario')
        else:
            # 检查具体偏好是否需要澄清
            if '拍照' in demand.preferences and not any('拍照' in q or '相机' in q for q in context.clarification_questions):
                clarification_needs.append('camera_preference')
            if ('性能' in demand.preferences or '游戏' in demand.preferences) and not any('性能' in q or '游戏' in q for q in context.clarification_questions):
                clarification_needs.append('performance_preference')
            if ('轻薄' in demand.preferences or '大屏' in demand.preferences) and not any('大屏' in q or '小屏' in q or '便携' in q for q in context.clarification_questions):
                clarification_needs.append('portability_preference')
            if '续航' in demand.preferences and not any('续航' in q or '电池' in q for q in context.clarification_questions):
                clarification_needs.append('battery_preference')
        
        return clarification_needs
    
    def _generate_clarification_question(self, clarification_type: str, context: DialogueContext) -> str:
        """生成智能澄清问题"""
        import random
        
        # 检查已经问过的问题，避免重复
        asked_questions = context.clarification_questions
        
        # 根据问题类型和已问过的问题生成新的问题
        if clarification_type == 'budget':
            questions = [
                "您的预算大概是多少呢？",
                "请问您能接受的价格范围是？",
                "您希望购买什么价位的手机？",
                "价格方面您有什么考虑吗？",
                "您觉得什么价位的手机比较合适？"
            ]
        elif clarification_type == 'camera_preference':
            questions = [
                "您更注重夜景拍摄还是广角拍摄？",
                "拍照方面，您更看重哪个功能？",
                "您主要用手机拍什么类型的照片？",
                "您对拍照有什么特殊需求吗？",
                "您希望手机拍照效果怎么样？"
            ]
        elif clarification_type == 'performance_preference':
            questions = [
                "您主要用手机做什么呢？游戏、工作还是日常使用？",
                "您对手机性能有什么特殊要求吗？",
                "您会玩大型游戏吗？",
                "平时使用手机主要是哪些场景？",
                "您希望手机运行速度怎么样？"
            ]
        elif clarification_type == 'portability_preference':
            questions = [
                "您更偏好大屏还是小屏手机？",
                "便携性对您来说重要吗？",
                "您希望手机轻便一些还是功能更全面？",
                "您平时会把手机放在哪里？",
                "您对手机尺寸有什么偏好吗？"
            ]
        elif clarification_type == 'battery_preference':
            questions = [
                "您对续航有什么要求？",
                "您希望手机能用多久？",
                "快充功能对您重要吗？",
                "您平时使用手机的时间长吗？",
                "您希望电池续航怎么样？"
            ]
        elif clarification_type == 'usage_scenario':
            questions = [
                "您主要用手机做什么呢？",
                "您平时使用手机的场景有哪些？",
                "您希望手机能满足哪些需求？",
                "您使用手机的主要目的是什么？",
                "您希望手机在哪些方面表现突出？"
            ]
        else:
            questions = ["能详细说明一下您的需求吗？"]
        
        # 过滤掉已经问过的问题
        available_questions = [q for q in questions if not any(q in asked for asked in asked_questions)]
        
        if not available_questions:
            # 如果所有问题都问过了，生成一个通用但个性化的问题
            if clarification_type == 'budget':
                return "关于价格方面，您还有什么特殊考虑吗？"
            elif clarification_type == 'camera_preference':
                return "关于拍照功能，您还有什么其他要求吗？"
            elif clarification_type == 'performance_preference':
                return "关于性能方面，您还有什么特殊需求吗？"
            elif clarification_type == 'portability_preference':
                return "关于便携性，您还有什么考虑吗？"
            elif clarification_type == 'battery_preference':
                return "关于续航方面，您还有什么要求吗？"
            else:
                return "您还有什么其他需求需要我了解的吗？"
        
        # 随机选择一个未问过的问题
        return random.choice(available_questions)
    
    def _update_demand_from_clarification(self, context: DialogueContext, 
                                        clarification_type: str, user_response: str) -> None:
        """根据澄清回答更新需求"""
        if context.current_demand is None:
            return
        
        # 解析用户回答中的新信息
        new_demand = self.demand_parser.parse_demand(user_response)
        
        # 更新当前需求
        if new_demand.budget_min is not None or new_demand.budget_max is not None:
            context.current_demand.budget_min = new_demand.budget_min
            context.current_demand.budget_max = new_demand.budget_max
        
        # 更新偏好
        if new_demand.preferences:
            context.current_demand.preferences.extend(new_demand.preferences)
            context.current_demand.preferences = list(set(context.current_demand.preferences))
        
        # 更新权重
        context.current_demand.performance_weight = new_demand.performance_weight
        context.current_demand.camera_weight = new_demand.camera_weight
        context.current_demand.battery_weight = new_demand.battery_weight
        context.current_demand.portability_weight = new_demand.portability_weight
        context.current_demand.price_weight = new_demand.price_weight
        context.current_demand.appearance_weight = new_demand.appearance_weight
    
    def process_user_input(self, session_id: str, user_input: str, 
                          available_phones: List) -> Dict:
        """处理用户输入"""
        
        # 获取或创建会话
        context = self.get_session(session_id)
        if context is None:
            context = self.create_session(session_id)
        
        # 记录对话历史
        context.conversation_history.append({
            'user': user_input,
            'timestamp': 'now'  # 实际应用中应该使用真实时间戳
        })
        
        response = {
            'session_id': session_id,
            'message': '',
            'recommendations': [],
            'clarification_question': None,
            'state': context.state.value
        }
        
        if context.state == DialogueState.INITIAL:
            # 初始状态，解析用户需求
            demand = self.demand_parser.parse_demand(user_input)
            context.current_demand = demand
            context.state = DialogueState.COLLECTING_DEMAND
            
            # 检查是否需要澄清
            clarification_needs = self._detect_clarification_needs(demand, context)
            
            if clarification_needs:
                context.state = DialogueState.CLARIFYING
                clarification_type = clarification_needs[0]
                clarification_question = self._generate_clarification_question(clarification_type, context)
                context.clarification_questions.append(clarification_question)
                
                response['clarification_question'] = clarification_question
                response['message'] = f"我理解您的需求，让我为您推荐合适的手机。{clarification_question}"
            else:
                # 需求明确，直接推荐
                context.state = DialogueState.RECOMMENDING
                recommendations = self.recommendation_engine.recommend(
                    available_phones, demand, top_n=3
                )
                context.current_recommendations = recommendations
                
                summary = self.recommendation_engine.get_recommendation_summary(recommendations)
                response['recommendations'] = summary
                response['message'] = f"根据您的需求，我为您推荐以下手机：\n{self._format_recommendations(summary)}"
        
        elif context.state == DialogueState.CLARIFYING:
            # 澄清状态，处理用户回答
            self._update_demand_from_clarification(context, 'general', user_input)
            
            # 再次检查是否需要澄清
            clarification_needs = self._detect_clarification_needs(context.current_demand, context)
            
            if clarification_needs:
                clarification_type = clarification_needs[0]
                clarification_question = self._generate_clarification_question(clarification_type, context)
                context.clarification_questions.append(clarification_question)
                
                response['clarification_question'] = clarification_question
                response['message'] = clarification_question
            else:
                # 需求已明确，进行推荐
                context.state = DialogueState.RECOMMENDING
                recommendations = self.recommendation_engine.recommend(
                    available_phones, context.current_demand, top_n=3
                )
                context.current_recommendations = recommendations
                
                summary = self.recommendation_engine.get_recommendation_summary(recommendations)
                response['recommendations'] = summary
                response['message'] = f"好的，根据您的需求，我为您推荐以下手机：\n{self._format_recommendations(summary)}"
        
        elif context.state == DialogueState.RECOMMENDING:
            # 推荐状态，处理用户反馈
            if any(keyword in user_input for keyword in ['换', '其他', '还有', '更多']):
                # 用户想要更多推荐
                context.state = DialogueState.FOLLOW_UP
                response['message'] = "您希望我为您推荐其他类型的手机吗？或者您有什么特殊要求？"
            elif any(keyword in user_input for keyword in ['详细', '参数', '对比']):
                # 用户想要详细信息
                response['message'] = self._get_detailed_info(context.current_recommendations)
            else:
                # 默认回复
                response['message'] = "如果您需要更多信息或有其他问题，请告诉我！"
        
        elif context.state == DialogueState.FOLLOW_UP:
            # 后续跟进状态
            new_demand = self.demand_parser.parse_demand(user_input)
            if new_demand.preferences or new_demand.budget_min or new_demand.budget_max:
                # 用户提供了新的需求信息
                context.current_demand = new_demand
                context.state = DialogueState.RECOMMENDING
                
                recommendations = self.recommendation_engine.recommend(
                    available_phones, new_demand, top_n=3
                )
                context.current_recommendations = recommendations
                
                summary = self.recommendation_engine.get_recommendation_summary(recommendations)
                response['recommendations'] = summary
                response['message'] = f"根据您的新需求，我为您推荐：\n{self._format_recommendations(summary)}"
            else:
                response['message'] = "请告诉我您的具体需求，比如预算、偏好等。"
        
        # 更新状态
        response['state'] = context.state.value
        
        return response
    
    def _format_recommendations(self, summary: Dict) -> str:
        """格式化推荐结果"""
        if 'message' in summary:
            return summary['message']
        
        formatted = ""
        for rec in summary['all_recommendations']:
            formatted += f"{rec['rank']}. {rec['name']} - ¥{rec['price']} (匹配度: {rec['score']})\n"
            formatted += f"   推荐理由: {', '.join(rec['reasons'])}\n\n"
        
        return formatted
    
    def _get_detailed_info(self, recommendations: List[RecommendationResult]) -> str:
        """获取详细信息"""
        if not recommendations:
            return "暂无推荐信息"
        
        detailed = "详细参数对比：\n\n"
        for rec in recommendations:
            phone = rec.phone
            detailed += f"【{phone.name}】\n"
            detailed += f"价格: ¥{phone.original_data['price']}\n"
            detailed += f"CPU: {phone.original_data['cpu']}\n"
            detailed += f"内存: {phone.original_data['ram_gb']}GB\n"
            detailed += f"存储: {phone.original_data['storage_gb']}GB\n"
            detailed += f"屏幕: {phone.original_data['screen_size_inch']}英寸\n"
            detailed += f"摄像头: {phone.original_data['camera_mp']}MP\n"
            detailed += f"电池: {phone.original_data['battery_mah']}mAh\n"
            detailed += f"重量: {phone.original_data['weight_g']}g\n"
            detailed += f"评分: {phone.original_data['rating']}/5.0\n"
            detailed += f"销量: {phone.original_data['sales']}\n"
            detailed += f"亮点: {', '.join(phone.original_data['highlights'])}\n\n"
        
        return detailed 
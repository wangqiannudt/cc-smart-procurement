import os
import uuid
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

# LLM客户端 - 延迟加载
_openai_client = None
_llm_available = None

# 支持的LLM提供商配置
LLM_PROVIDERS = {
    "glm": {
        "env_key": "GLM_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "default_model": "glm-4-flash"
    },
    "dashscope": {
        "env_key": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus"
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": None,
        "default_model": "gpt-3.5-turbo"
    }
}


def _get_openai_client():
    """获取OpenAI兼容客户端（延迟加载）"""
    global _openai_client, _llm_available

    if _llm_available is not None:
        return _openai_client if _llm_available else None

    try:
        from openai import OpenAI

        # 按优先级检测API Key：GLM > DASHSCOPE > OPENAI
        api_key = None
        base_url = None
        provider_name = None

        # 检测GLM（智谱AI）
        if os.getenv("GLM_API_KEY"):
            api_key = os.getenv("GLM_API_KEY")
            base_url = os.getenv("GLM_BASE_URL") or LLM_PROVIDERS["glm"]["base_url"]
            provider_name = "GLM(智谱AI)"
        # 检测通义千问
        elif os.getenv("DASHSCOPE_API_KEY"):
            api_key = os.getenv("DASHSCOPE_API_KEY")
            base_url = os.getenv("DASHSCOPE_BASE_URL") or LLM_PROVIDERS["dashscope"]["base_url"]
            provider_name = "通义千问"
        # 检测OpenAI
        elif os.getenv("OPENAI_API_KEY"):
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_BASE_URL")
            provider_name = "OpenAI"

        if not api_key:
            print("未配置LLM API密钥，将使用关键词匹配模式")
            print("支持的配置: GLM_API_KEY, DASHSCOPE_API_KEY, OPENAI_API_KEY")
            _llm_available = False
            return None

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        _openai_client = OpenAI(**client_kwargs)
        _llm_available = True
        print(f"LLM客户端初始化成功 - 提供商: {provider_name}")
        return _openai_client

    except ImportError:
        print("openai库未安装，将使用关键词匹配模式")
        _llm_available = False
        return None
    except Exception as e:
        print(f"LLM初始化失败: {e}，将使用关键词匹配模式")
        _llm_available = False
        return None


class ChatAgent:
    """AI聊天智能体 - 支持真实LLM的增强版"""

    # 系统提示词 - 定义AI助手的专业角色
    SYSTEM_PROMPT = """你是智慧采购系统的AI助手，专门为研究机构提供采购服务支持。

你的职责：
1. 协助用户进行采购需求分析和审查
2. 提供价格查询和比价建议
3. 识别合同中的风险条款
4. 解答采购流程相关问题
5. 提供供应商评估建议

你的特点：
- 专业、准确、高效
- 熟悉政府采购法规和企业采购流程
- 能够识别需求文档中的模糊表述和风险点
- 了解IT设备（服务器、网络设备、存储等）的选型建议

回答要求：
- 回答简洁明了，重点突出
- 对于专业问题，提供具体可操作的建议
- 如果用户的问题不明确，主动询问澄清
- 使用中文回答，适当使用表情符号增加亲和力
- 对于超出范围的问题，诚实告知并提供替代建议"""

    def __init__(self):
        # 多会话管理
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.default_session_id = "default"

        # 初始化默认会话
        self._create_session(self.default_session_id)

        # 采购相关关键词和回复模板（作为降级方案）
        self._init_keyword_responses()

        # 尝试初始化LLM
        self.llm_client = _get_openai_client()
        self.llm_model = os.getenv("LLM_MODEL") or self._get_default_model()

    def _get_default_model(self) -> str:
        """根据配置的API Key自动选择默认模型"""
        if os.getenv("GLM_API_KEY"):
            return "glm-4-flash"  # GLM默认模型
        elif os.getenv("DASHSCOPE_API_KEY"):
            return "qwen-plus"  # 通义千问默认模型
        else:
            return "gpt-3.5-turbo"  # OpenAI默认模型

    def _init_keyword_responses(self):
        """初始化关键词响应映射（降级方案）"""
        self.keyword_responses = {
            "greetings": {
                "keywords": ["你好", "您好", "hi", "hello", "早上好", "下午好", "晚上好"],
                "response": "您好！我是智慧采购系统的AI助手，可以帮您处理采购相关的问题。\n\n我可以协助您进行：\n• 需求审查与分析\n• 价格查询与比较\n• 合同风险识别\n• 采购方案建议\n\n请问有什么可以帮您？"
            },
            "price": {
                "keywords": ["价格", "报价", "多少钱", "费用", "成本", "预算", "比价", "询价", "定价"],
                "response": "关于价格查询，我可以帮您：\n\n1. **历史价格参考** - 查询同类产品的历史采购价格\n2. **价格趋势分析** - 了解价格波动和走势\n3. **多供应商比价** - 对比不同供应商的报价\n\n您想查询哪类产品的价格信息？"
            },
            "requirements": {
                "keywords": ["需求", "采购需求", "需求文档", "需求分析", "规格", "参数", "技术要求"],
                "response": "关于需求审查，我可以帮您：\n\n1. **需求完整性检查** - 确认是否包含必要的六要素\n2. **模糊表述识别** - 检测\"等\"、\"约\"等不明确表达\n3. **技术参数审核** - 验证规格参数是否合理\n\n请上传您的需求文档，或直接描述您的采购需求。"
            },
            "contract": {
                "keywords": ["合同", "协议", "条款", "签约", "签署", "合同分析", "风险条款"],
                "response": "关于合同分析，我可以帮您：\n\n1. **风险条款识别** - 检测免责条款、无限期条款等风险点\n2. **模糊表述检测** - 发现可能导致歧义的表述\n3. **修改建议** - 提供条款优化建议\n\n请上传您的合同文档，我将为您进行全面分析。"
            },
            "server": {
                "keywords": ["服务器", "机架式", "塔式", "dell", "hp", "华为", "联想", "cpu", "内存", "存储"],
                "response": "关于服务器采购：\n\n**选型建议：**\n- 机架式服务器：适合机房环境，密度高，易管理\n- 塔式服务器：适合办公室，噪音低，扩展性好\n\n**关键配置：**\n- CPU：Intel Xeon Silver/Gold/Platinum 系列\n- 内存：64GB-512GB（根据负载选择）\n- 存储：SSD系统盘 + HDD数据盘 + NVMe高速存储\n\n请告诉我您的具体用途和预算范围。"
            },
            "analysis": {
                "keywords": ["分析", "评估", "审查", "审核", "检查", "诊断", "报告"],
                "response": "我可以提供多种采购分析服务：\n\n1. **需求分析** - 评估需求完整性和合理性\n2. **价格分析** - 对比历史价格和市场行情\n3. **供应商评估** - 分析供应商资质和能力\n4. **合同风险分析** - 识别潜在法律和商务风险\n\n请告诉我您需要进行哪类分析？"
            },
            "supplier": {
                "keywords": ["供应商", "厂商", "厂家", "供应商选择", "供应商评估", "资质"],
                "response": "关于供应商管理，我可以帮您：\n\n1. **资质审核** - 检查供应商的营业执照、资质证书等\n2. **能力评估** - 评估技术能力、交付能力、服务水平\n3. **历史业绩** - 查询过往合作记录和客户评价\n4. **风险预警** - 识别潜在的合作风险\n\n您想了解哪个供应商的信息？"
            },
            "process": {
                "keywords": ["流程", "采购流程", "步骤", "怎么采购", "如何采购", "程序"],
                "response": "标准采购流程：\n\n1. **需求确认** - 明确用途、功能、预算、交付时间\n2. **方案制定** - 确定技术规格和采购方式\n3. **供应商筛选** - 资质审核和初步评估\n4. **询价比价** - 获取报价并对比分析\n5. **合同签订** - 条款审核和正式签署\n6. **履约验收** - 交付验收和付款\n\n您目前在哪个环节？"
            },
            "help": {
                "keywords": ["帮助", "功能", "能做什么", "怎么用", "使用", "帮助我", "介绍一下"],
                "response": "智慧采购系统可以为您提供以下服务：\n\n📋 **需求审查** - 上传需求文档，自动检查完整性和风险点\n💰 **价格参考** - 查询历史价格，分析价格趋势\n📑 **合同分析** - 识别合同风险条款，提供修改建议\n💬 **智能问答** - 回答采购相关问题，提供建议\n\n您可以直接描述需求，或上传相关文档进行分析。"
            },
            "thanks": {
                "keywords": ["谢谢", "感谢", "多谢", "辛苦了", "太好了"],
                "response": "不客气！很高兴能帮到您。如果还有其他采购相关的问题，随时可以问我。"
            }
        }

    def _create_session(self, session_id: str) -> str:
        """创建新会话"""
        self.sessions[session_id] = {
            "memory": ConversationBufferMemory(return_messages=True),
            "history": [],
            "created_at": None
        }
        return session_id

    def create_new_session(self) -> str:
        """创建新会话并返回session_id"""
        session_id = str(uuid.uuid4())
        self._create_session(session_id)
        return session_id

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """获取或创建会话"""
        if session_id and session_id in self.sessions:
            return session_id
        if session_id:
            self._create_session(session_id)
            return session_id
        return self.default_session_id

    def chat(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, str]:
        """处理用户输入并返回回复"""
        actual_session_id = self.get_or_create_session(session_id)
        session = self.sessions[actual_session_id]

        # 存储用户消息
        session["history"].append(HumanMessage(content=user_input))

        # 尝试使用LLM生成回复
        response = self._generate_llm_response(user_input, session["history"])

        # 如果LLM失败，降级到关键词匹配
        if not response:
            response = self._generate_response(user_input, session["history"])

        # 存储AI回复
        session["history"].append(AIMessage(content=response))

        return {
            "response": response,
            "session_id": actual_session_id
        }

    def _generate_llm_response(self, user_input: str, history: List[BaseMessage]) -> Optional[str]:
        """使用LLM生成回复"""
        if not self.llm_client:
            return None

        try:
            # 构建消息列表
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]

            # 添加历史消息（最近10轮对话）
            recent_history = history[-20:] if len(history) > 20 else history
            for msg in recent_history:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})

            # 调用LLM API
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM调用失败: {e}")
            return None

    def _generate_response(self, user_input: str, history: List[BaseMessage]) -> str:
        """生成回复（关键词匹配降级方案）"""
        user_input_lower = user_input.lower()
        context = self._get_context_from_history(history)
        matched_response = self._match_intent(user_input_lower)

        if matched_response:
            return matched_response

        return self._get_default_response(user_input, context)

    def _match_intent(self, user_input: str) -> Optional[str]:
        """意图匹配"""
        priority_order = ["greetings", "help", "price", "requirements", "contract",
                         "server", "analysis", "supplier", "process", "thanks"]

        for category in priority_order:
            if category in self.keyword_responses:
                config = self.keyword_responses[category]
                for keyword in config["keywords"]:
                    if keyword.lower() in user_input:
                        return config["response"]

        return None

    def _get_context_from_history(self, history: List[BaseMessage]) -> str:
        """从历史消息获取上下文"""
        if len(history) <= 1:
            return ""

        recent_messages = history[-4:] if len(history) >= 4 else history[:-1]
        context_parts = []
        for msg in recent_messages:
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            context_parts.append(f"{role}: {msg.content[:50]}...")

        return "\n".join(context_parts)

    def _get_default_response(self, user_input: str, context: str) -> str:
        """获取默认回复"""
        return f"""感谢您的咨询！

我理解您的问题是关于「{user_input[:30]}{'...' if len(user_input) > 30 else ''}」

作为采购智能助手，我可以帮助您：

• 📋 **需求审查** - 检查需求文档的完整性和合理性
• 💰 **价格参考** - 查询历史价格和进行价格分析
• 📑 **合同分析** - 识别合同中的风险条款
• 💬 **采购咨询** - 回答采购相关问题

请告诉我您具体需要哪方面的帮助，或者上传相关文档进行分析。"""

    def clear_session(self, session_id: Optional[str] = None):
        """清空指定会话的历史"""
        target_session = session_id or self.default_session_id
        if target_session in self.sessions:
            self.sessions[target_session]["history"] = []
            self.sessions[target_session]["memory"].clear()

    def clear_all_sessions(self):
        """清空所有会话"""
        self.sessions.clear()
        self._create_session(self.default_session_id)

    def get_history(self, session_id: Optional[str] = None) -> List[Dict[str, str]]:
        """获取指定会话的对话历史"""
        target_session = session_id or self.default_session_id
        if target_session not in self.sessions:
            return []

        history = []
        for msg in self.sessions[target_session]["history"]:
            history.append({
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            })
        return history

    def get_session_ids(self) -> List[str]:
        """获取所有会话ID"""
        return list(self.sessions.keys())

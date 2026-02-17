"""
规则引擎模块 - 加载和管理YAML规则配置
"""
import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class RuleEngine:
    """规则引擎：加载和管理品类规则配置"""

    def __init__(self, rules_dir: str = None):
        """
        初始化规则引擎

        Args:
            rules_dir: 规则文件目录路径，默认为 backend/data/rules
        """
        if rules_dir is None:
            # 默认规则目录
            backend_dir = Path(__file__).parent.parent.parent
            rules_dir = backend_dir / "data" / "rules"

        self.rules_dir = Path(rules_dir)
        self._category_rules_cache: Dict[str, Dict] = {}
        self._main_config: Optional[Dict] = None

    def _load_yaml(self, file_path: Path) -> Dict:
        """加载YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Failed to load {file_path}: {e}")
            return {}

    def _load_main_config(self) -> Dict:
        """加载主配置文件 category_rules.yaml"""
        if self._main_config is None:
            config_path = self.rules_dir / "category_rules.yaml"
            if config_path.exists():
                self._main_config = self._load_yaml(config_path)
            else:
                self._main_config = {"categories": {}}
        return self._main_config

    def load_category_rules(self, category_id: str) -> Dict:
        """
        加载品类规则配置

        Args:
            category_id: 品类ID，如 'server', 'workstation'

        Returns:
            品类规则配置字典
        """
        if category_id in self._category_rules_cache:
            return self._category_rules_cache[category_id]

        # 从主配置获取品类信息
        main_config = self._load_main_config()
        categories = main_config.get("categories", {})

        if category_id not in categories:
            return {}

        category_info = categories[category_id]
        rule_file = category_info.get("rule_file")

        if not rule_file:
            return {}

        # 加载品类规则文件
        rule_path = self.rules_dir / "rules" / rule_file
        if rule_path.exists():
            rules = self._load_yaml(rule_path)
            self._category_rules_cache[category_id] = rules
            return rules

        return {}

    def get_fields(self, category_id: str, subtype_id: str = None) -> List[Dict]:
        """
        获取品类字段定义

        Args:
            category_id: 品类ID
            subtype_id: 子类型ID（可选）

        Returns:
            字段定义列表
        """
        rules = self.load_category_rules(category_id)
        if not rules:
            return []

        fields = []
        field_groups = rules.get("fields", [])

        for group in field_groups:
            group_items = group.get("items", [])
            for item in group_items:
                field_info = {
                    "field_id": item.get("field_id"),
                    "label": item.get("label_cn", item.get("field_id")),
                    "priority": item.get("priority", "P2"),
                    "type": item.get("type", "text"),
                    "required_for": item.get("required_for", ["all"]),
                    "keywords_cn": item.get("keywords_cn", []),
                    "keywords_en": item.get("keywords_en", []),
                    "validation": item.get("validation", {}),
                    "unit": item.get("unit"),
                    "enums": item.get("enums", []),
                    "group_id": group.get("group_id"),
                    "group_label": group.get("group_label_cn", "")
                }

                # 如果指定了子类型，检查字段是否适用于该子类型
                if subtype_id:
                    required_for = item.get("required_for", ["all"])
                    if "all" not in required_for and subtype_id not in required_for:
                        continue

                fields.append(field_info)

        return fields

    def get_risk_rules(self, category_id: str) -> List[Dict]:
        """
        获取品类风险规则

        Args:
            category_id: 品类ID

        Returns:
            风险规则列表
        """
        rules = self.load_category_rules(category_id)
        if not rules:
            # 返回默认风险规则
            return self._get_default_risk_rules()

        return rules.get("risk_rules", self._get_default_risk_rules())

    def _get_default_risk_rules(self) -> List[Dict]:
        """获取默认风险规则"""
        return [
            {
                "rule_id": "risk.explicit_brand",
                "priority": "P0",
                "description_cn": "检测到明确品牌名称，存在采购指向性风险",
                "trigger_patterns": {
                    "cn_keywords": ["戴尔", "惠普", "联想", "华为", "浪潮"],
                    "regex": [
                        r"(?i)\b(dell|hp|hpe|lenovo|huawei|inspur|ibm|cisco)\b"
                    ]
                },
                "action": {
                    "report_message_cn": "出现品牌名称属于高风险表达，建议改为性能与能力参数描述"
                }
            },
            {
                "rule_id": "risk.explicit_model",
                "priority": "P0",
                "description_cn": "检测到明确型号，存在采购指向性风险",
                "trigger_patterns": {
                    "regex": [
                        r"(?i)\b(geforce|quadro|rtx|tesla|radeon|instinct|xeon|epyc|threadripper)\b",
                        r"(?i)\b(poweredge|proliant|thinksystem|altros|fusionserver)\b",
                        r"(?i)\b(a\d{2,4}|h\d{2,4}|v\d{2,4}|mi\d{2,4})\b"
                    ]
                },
                "action": {
                    "report_message_cn": "出现型号属于高风险表达，建议改为性能与能力参数描述"
                }
            },
            {
                "rule_id": "risk.benchmark_model_reference",
                "priority": "P1",
                "description_cn": "检测到'性能不低于某型号'类表述",
                "trigger_patterns": {
                    "cn_phrases": ["性能不低于", "不弱于", "不差于", "与XX同等"]
                },
                "action": {
                    "report_message_cn": "建议将标杆式型号引用改为参数化表达"
                }
            },
            {
                "rule_id": "risk.vague_expression",
                "priority": "P1",
                "description_cn": "检测到模糊表述",
                "trigger_patterns": {
                    "cn_keywords": ["大约", "大概", "左右", "尽可能", "尽量", "高性能", "高性能计算机",
                                   "先进水平", "国际领先", "国内领先", "性能优异", "高端"]
                },
                "action": {
                    "report_message_cn": "建议使用具体、可量化的表述替代模糊表达"
                }
            }
        ]

    def get_available_categories(self) -> List[Dict]:
        """
        获取可用品类列表

        Returns:
            品类信息列表
        """
        main_config = self._load_main_config()
        categories = main_config.get("categories", {})

        result = []
        for cat_id, cat_info in categories.items():
            category = {
                "id": cat_id,
                "name": cat_info.get("name_cn", cat_id),
                "description": cat_info.get("description_cn", ""),
                "subtypes": []
            }

            # 添加子类型
            subtypes = cat_info.get("subtypes", {})
            for sub_id, sub_info in subtypes.items():
                category["subtypes"].append({
                    "id": sub_id,
                    "name": sub_info.get("name_cn", sub_id),
                    "description": sub_info.get("description_cn", "")
                })

            result.append(category)

        return result

    def get_category_info(self, category_id: str) -> Optional[Dict]:
        """
        获取品类详细信息

        Args:
            category_id: 品类ID

        Returns:
            品类信息字典
        """
        main_config = self._load_main_config()
        categories = main_config.get("categories", {})

        if category_id not in categories:
            return None

        cat_info = categories[category_id]
        return {
            "id": category_id,
            "name": cat_info.get("name_cn", category_id),
            "description": cat_info.get("description_cn", ""),
            "rule_file": cat_info.get("rule_file"),
            "subtypes": cat_info.get("subtypes", {})
        }

    def get_unit_normalization(self, category_id: str = None) -> Dict:
        """
        获取单位归一化规则

        Args:
            category_id: 品类ID（可选，用于获取品类特定规则）

        Returns:
            单位归一化规则字典
        """
        # 默认单位归一化规则
        default_units = {
            "ghz": {"aliases": ["GHz", "ghz", "Ghz", "吉赫兹", "G"], "normalize_to": "GHz"},
            "gb": {"aliases": ["GB", "G", "gb", "GiB", "吉字节"], "normalize_to": "GB"},
            "tb": {"aliases": ["TB", "tb", "TiB", "太字节", "T"], "normalize_to": "TB"},
            "gbe": {"aliases": ["GbE", "gbe", "Gbe", "千兆以太", "万兆", "25G", "40G", "100G", "200G", "400G"], "normalize_to": "GbE"},
            "watt": {"aliases": ["W", "w", "瓦", "瓦特"], "normalize_to": "W"},
            "u_height": {"aliases": ["U", "u", "机架U数", "U高"], "normalize_to": "U"},
            "cores": {"aliases": ["核", "核心", "cores", "Core", "Cores"], "normalize_to": "cores"},
            "mm": {"aliases": ["mm", "毫米", "MM"], "normalize_to": "mm"},
            "inch": {"aliases": ["英寸", "inch", "in", "\""], "normalize_to": "inch"},
            "kg": {"aliases": ["kg", "KG", "千克", "公斤"], "normalize_to": "kg"},
            "hour": {"aliases": ["小时", "h", "H", "hr", "hour", "hours"], "normalize_to": "h"},
            "watt_hour": {"aliases": ["Wh", "wh", "瓦时"], "normalize_to": "Wh"}
        }

        if category_id:
            rules = self.load_category_rules(category_id)
            if rules:
                global_config = rules.get("global", {})
                custom_units = global_config.get("unit_normalization", {})
                # 合并自定义规则
                for unit, config in custom_units.items():
                    if unit in default_units:
                        default_units[unit]["aliases"].extend(config.get("aliases", []))
                    else:
                        default_units[unit] = config

        return default_units

    def get_comparator_patterns(self) -> Dict:
        """获取比较符模式"""
        return {
            "gte": ["≥", ">=", "不少于", "不低于", "至少", "大于等于", "以上"],
            "lte": ["≤", "<=", "不高于", "至多", "小于等于", "以下"],
            "gt": [">", "大于", "超过"],
            "lt": ["<", "小于"],
            "range": ["-", "—", "～", "~", "至", "范围"]
        }

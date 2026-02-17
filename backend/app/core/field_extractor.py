"""
字段提取器模块 - 基于jieba分词提取字段
"""
import re
import jieba
from typing import Dict, List, Any, Optional, Tuple


class FieldExtractor:
    """字段提取器：基于jieba分词和正则表达式提取字段值"""

    def __init__(self):
        """初始化字段提取器"""
        jieba.initialize()

        # 比较符映射
        self.comparator_map = {
            "≥": "gte", ">=": "gte", "不少于": "gte", "不低于": "gte",
            "至少": "gte", "大于等于": "gte", "以上": "gte",
            "≤": "lte", "<=": "lte", "不高于": "lte", "至多": "lte",
            "小于等于": "lte", "以下": "lte",
            ">": "gt", "大于": "gt", "超过": "gt",
            "<": "lt", "小于": "lt"
        }

        # 单位归一化映射
        self.unit_normalize_map = {
            # 频率
            "ghz": "GHz", "ghz": "GHz", "Ghz": "GHz", "吉赫兹": "GHz",
            # 容量
            "gb": "GB", "g": "GB", "GiB": "GB", "吉字节": "GB",
            "tb": "TB", "tb": "TB", "TiB": "TB", "太字节": "TB",
            # 功率
            "w": "W", "瓦": "W", "瓦特": "W",
            # 网络
            "gbe": "GbE",
            # 核心
            "cores": "cores", "core": "cores", "核": "cores", "核心": "cores",
            # 长度
            "mm": "mm", "毫米": "mm",
            "inch": "inch", "英寸": "inch", "in": "inch",
            # 重量
            "kg": "kg", "千克": "kg", "公斤": "kg",
            # 时间
            "h": "h", "小时": "h", "hr": "h"
        }

    def extract_field(self, content: str, field_def: Dict) -> Dict:
        """
        提取单个字段

        Args:
            content: 文档内容
            field_def: 字段定义

        Returns:
            提取结果字典，包含 value, confidence, span 等信息
        """
        field_id = field_def.get("field_id")
        field_type = field_def.get("type", "text")
        keywords_cn = field_def.get("keywords_cn", [])
        keywords_en = field_def.get("keywords_en", [])

        # 定位候选片段
        span = self._locate_span(content, keywords_cn, keywords_en)
        if not span:
            return {
                "field_id": field_id,
                "value": None,
                "confidence": 0,
                "found": False
            }

        span_text, start_pos, end_pos = span

        # 根据字段类型解析值，传递field_id作为上下文
        if field_type == "integer":
            value = self._parse_integer(span_text, field_id)
        elif field_type == "integer_with_comparator":
            value = self._parse_integer_with_comparator(span_text, field_def)
        elif field_type == "float":
            value = self._parse_float(span_text, field_id)
        elif field_type == "float_with_comparator":
            value = self._parse_float_with_comparator(span_text, field_def)
        elif field_type == "enum":
            value = self._parse_enum(span_text, field_def.get("enums", []))
        elif field_type == "enum_or_text":
            value = self._parse_enum_or_text(span_text, field_def.get("enums", []))
        elif field_type == "storage_spec":
            value = self._parse_storage_spec(span_text, field_id)
        elif field_type == "list_or_text":
            value = self._parse_list_or_text(span_text)
        else:  # text
            value = self._parse_text(span_text)

        return {
            "field_id": field_id,
            "label": field_def.get("label_cn", field_def.get("label", field_id)),
            "value": value,
            "confidence": self._calculate_confidence(span_text, value, field_type),
            "found": value is not None and value != "",
            "span_text": span_text[:200] if span_text else None,  # 限制长度
            "position": {"start": start_pos, "end": end_pos}
        }

    def extract_all_fields(self, content: str, fields: List[Dict]) -> Dict[str, Dict]:
        """
        批量提取所有字段

        Args:
            content: 文档内容
            fields: 字段定义列表

        Returns:
            字段ID到提取结果的映射
        """
        results = {}
        for field_def in fields:
            field_id = field_def.get("field_id")
            results[field_id] = self.extract_field(content, field_def)
        return results

    def _locate_span(self, content: str, keywords_cn: List[str],
                     keywords_en: List[str], window_chars: int = 80) -> Optional[Tuple[str, int, int]]:
        """
        定位包含关键词的文本片段

        Args:
            content: 文档内容
            keywords_cn: 中文关键词列表
            keywords_en: 英文关键词列表
            window_chars: 窗口字符数

        Returns:
            (片段文本, 起始位置, 结束位置) 或 None
        """
        all_keywords = keywords_cn + keywords_en

        for keyword in all_keywords:
            # 查找关键词位置
            idx = content.find(keyword)
            if idx != -1:
                # 向前扩展20字符以捕获关键词前的数字，向后扩展window_chars字符
                backward_chars = 20
                start = max(0, idx - backward_chars)
                end = min(len(content), idx + len(keyword) + window_chars)
                return (content[start:end], start, end)

        return None

    def _parse_integer(self, text: str, field_id: str = None) -> Optional[int]:
        """
        解析整数值

        Args:
            text: 文本片段
            field_id: 字段ID，用于确定解析上下文
        """
        # 根据field_id确定优先模式
        if field_id:
            if 'core' in field_id.lower() or 'cpu' in field_id.lower():
                # CPU核心数优先
                patterns = [
                    r'(?:不少于|不低于|至少|≥|>=)\s*(\d+)\s*核(?:心)?(?:以上|以下)?',
                    r'(\d+)\s*核(?:心)?(?:以上|以下)?(?:，|,|\s|$)',
                    r'(?:核心数|核数)\s*[:：]?\s*(\d+)',
                ]
            elif 'memory' in field_id.lower() or 'capacity' in field_id.lower():
                # 内存/容量优先
                patterns = [
                    r'(?:内存(?:容量)?)\s*[:：]?\s*(\d+)\s*(?:GB|TB)',
                    r'(?:容量)\s*[:：]?\s*(\d+)\s*(?:GB|TB)',
                ]
            elif 'quantity' in field_id.lower() or 'count' in field_id.lower():
                # 数量优先
                patterns = [
                    r'(?:采购)?数量\s*[:：]?\s*(\d+)\s*(?:台|套|节点|个)?',
                    r'(\d+)\s*(?:台|套|节点|个)(?:\s|$|,|，)',
                ]
            elif 'battery' in field_id.lower() or 'life' in field_id.lower():
                # 电池续航优先
                patterns = [
                    r'(?:续航|电池(?:续航)?)\s*[:：]?\s*(\d+)\s*(?:小时|h)',
                    r'(\d+)\s*(?:小时|h)\s*(?:以上|以上)?',
                ]
            elif 'storage' in field_id.lower() or 'disk' in field_id.lower():
                # 存储容量优先
                patterns = [
                    r'(?:硬盘|SSD|存储)\s*[:：]?\s*(\d+)\s*(?:GB|TB)',
                    r'(\d+)\s*(?:GB|TB)\s*(?:SSD)?',
                ]
            else:
                # 通用模式
                patterns = [
                    r'(\d+)\s*核(?:心)?(?:以上|以下)?',
                    r'(?:内存(?:容量)?)\s*[:：]?\s*(\d+)\s*(?:GB|TB)',
                    r'(?:采购)?数量\s*[:：]?\s*(\d+)',
                    r'(\d+)',
                ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        return int(match.group(1))
                    except (ValueError, AttributeError):
                        continue

        # 通用模式作为降级
        patterns_priority = [
            r'(\d+)\s*核(?:心)?(?:以上|以下)?(?:，|,|\s|$)',
            r'(?:不少于|不低于|至少|≥|>=)\s*(\d+)\s*核(?:心)?',
            r'(?:内存(?:容量)?)\s*[:：]?\s*(\d+)\s*(?:GB|TB)',
            r'(?:采购)?数量\s*[:：]?\s*(\d+)\s*(?:台|套|节点|个)',
            r'(\d+)\s*(?:台|套|节点)(?:\s|$|,|，)',
        ]

        for pattern in patterns_priority:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, AttributeError):
                    continue

        return None

    def _parse_integer_with_comparator(self, text: str, field_def: Dict) -> Optional[Dict]:
        """解析带比较符的整数值"""
        unit = field_def.get("unit", "")

        # 首先尝试特定模式
        specific_patterns = [
            # 内存/容量: 数字 + GB
            r'(?:内存|内存容量|容量)\s*[:：]?\s*(?:≥|>=|不少于|不低于|至少)?\s*(\d+)\s*(GB|G|gb)',
            # 核心: 数字 + 核
            r'(?:核心数|核数)\s*[:：]?\s*(?:≥|>=|不少于|不低于|至少)?\s*(\d+)\s*(?:核|核心)?',
            # 通用: 比较符 + 数字 + 单位
            r'(≥|>=|不少于|不低于|至少|大于等于|以上)?\s*(\d+)\s*(' + '|'.join(re.escape(u) for u in self.unit_normalize_map.keys()) + '|' + unit + r')?',
        ]

        for pattern in specific_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                # 如果是第一个模式（内存），直接取值
                if len(groups) == 2 and groups[0] and groups[0].isdigit():
                    return {
                        "comparator": "gte" if "不" in text[:match.start()] else "eq",
                        "value": int(groups[0]),
                        "unit": self._normalize_unit(groups[1]) if groups[1] else unit
                    }
                # 如果是第二个模式（核心）
                elif len(groups) == 1 and groups[0] and groups[0].isdigit():
                    return {
                        "comparator": "gte" if "不" in text[:match.start()] else "eq",
                        "value": int(groups[0]),
                        "unit": "cores"
                    }
                # 通用模式
                elif len(groups) == 3:
                    comparator_str = groups[0] or ""
                    value_str = groups[1]
                    unit_str = groups[2] or unit
                    if value_str and value_str.isdigit():
                        return {
                            "comparator": self.comparator_map.get(comparator_str, "eq"),
                            "value": int(value_str),
                            "unit": self._normalize_unit(unit_str)
                        }

        return None

    def _parse_float(self, text: str, field_id: str = None) -> Optional[float]:
        """
        解析浮点数值

        Args:
            text: 文本片段
            field_id: 字段ID，用于确定解析上下文
        """
        # 根据field_id确定优先模式
        if field_id:
            if 'frequency' in field_id.lower() or 'ghz' in field_id.lower():
                # 频率优先 - 数字+GHz
                match = re.search(r'(\d+(?:\.\d+)?)\s*(?:GHz|Ghz)', text, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        pass
                # 或者 主频+数字
                match = re.search(r'主频\s*[:：]?\s*(\d+(?:\.\d+)?)', text)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        pass
            elif 'weight' in field_id.lower():
                # 重量优先 - 数字+kg
                match = re.search(r'(?:不超过|不超过|≤|<=)?\s*(\d+(?:\.\d+)?)\s*(?:kg|千克|公斤)', text, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        pass
            elif 'size' in field_id.lower() or 'inch' in field_id.lower():
                # 尺寸优先 - 数字+英寸
                match = re.search(r'(\d+(?:\.\d+)?)\s*(?:英寸|inch)', text, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        pass
            elif 'battery' in field_id.lower() or 'life' in field_id.lower():
                # 电池续航优先 - 数字+小时
                match = re.search(r'(?:续航|电池)?\s*(\d+(?:\.\d+)?)\s*(?:小时|h)', text, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        pass

        # 通用模式：数字+单位
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:GHz|GB|TB|kg|mm|inch|小时|h)',
            r'(\d+(?:\.\d+)?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None

    def _parse_float_with_comparator(self, text: str, field_def: Dict) -> Optional[Dict]:
        """解析带比较符的浮点数值"""
        unit = field_def.get("unit", "")

        pattern = r'(≥|>=|不少于|不低于|至少|大于等于|以上|≤|<=|不高于|至多|小于等于|以下|>|大于|超过|<|小于)?\s*(\d+(?:\.\d+)?)\s*(' + '|'.join(self.unit_normalize_map.keys()) + '|' + unit + r')?'

        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            comparator_str = match.group(1) or ""
            value_str = match.group(2)
            unit_str = match.group(3) or unit

            comparator = self.comparator_map.get(comparator_str, "eq")

            try:
                return {
                    "comparator": comparator,
                    "value": float(value_str),
                    "unit": self._normalize_unit(unit_str)
                }
            except ValueError:
                pass

        return None

    def _parse_enum(self, text: str, enums: List[str]) -> Optional[str]:
        """解析枚举值"""
        text_lower = text.lower()
        for enum in enums:
            if enum.lower() in text_lower:
                return enum
        return None

    def _parse_enum_or_text(self, text: str, enums: List[str]) -> str:
        """解析枚举值或返回文本"""
        enum_value = self._parse_enum(text, enums)
        if enum_value:
            return enum_value

        # 尝试提取关键信息
        keywords = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z0-9]+', text)
        if keywords:
            return ' '.join(keywords[:5])  # 限制长度
        return text[:50].strip()

    def _parse_storage_spec(self, text: str, field_id: str = None) -> Optional[Dict]:
        """解析存储规格（系统盘等）"""
        # 匹配介质类型
        media = None
        if re.search(r'NVMe|nvme', text, re.IGNORECASE):
            media = "NVMe"
        elif re.search(r'SSD|ssd|固态', text, re.IGNORECASE):
            media = "SSD"
        elif re.search(r'HDD|hdd|机械|SATA', text, re.IGNORECASE):
            media = "HDD"

        # 匹配容量 - 优先匹配存储关键词附近的容量
        # 优先模式1: 数字+单位+SSD/NVMe (如 "512GB SSD")
        priority_patterns = [
            r'(\d+)\s*(GB|TB|G|T)\s*(?:SSD|NVMe|固态)',  # 512GB SSD
            r'(?:硬盘|系统盘|存储|SSD|NVMe)\s*[:：]?\s*(\d+)\s*(GB|TB|G|T)',  # 硬盘：512GB
            r'(?:硬盘|系统盘|存储)\s*[:：]?\s*(\d+)\s*(GB|TB|G|T)\s*(?:SSD|NVMe)?',  # 硬盘：512GB SSD
        ]

        capacity_match = None
        for pattern in priority_patterns:
            capacity_match = re.search(pattern, text, re.IGNORECASE)
            if capacity_match:
                break

        # 降级模式：任意数字+单位
        if not capacity_match:
            capacity_pattern = r'(≥|>=|不少于|不低于|至少)?\s*(\d+)\s*(GB|TB|G|T)'
            capacity_match = re.search(capacity_pattern, text, re.IGNORECASE)

        result = {}
        if media:
            result["media"] = media

        if capacity_match:
            groups = capacity_match.groups()
            # 处理不同模式的匹配组
            if len(groups) == 2:
                # 优先模式: (数字, 单位)
                value = int(groups[0])
                unit = groups[1].upper()
                comparator_str = ""
            elif len(groups) == 3:
                # 降级模式: (比较符, 数字, 单位)
                comparator_str = groups[0] or ""
                value = int(groups[1])
                unit = groups[2].upper()
            else:
                return result if result else None

            if unit in ['G']:
                unit = 'GB'
            elif unit in ['T']:
                unit = 'TB'

            result["comparator"] = self.comparator_map.get(comparator_str, "eq")
            result["value"] = value
            result["unit"] = unit

        return result if result else None

    def _parse_list_or_text(self, text: str) -> Any:
        """解析列表或文本"""
        # 尝试提取逗号或顿号分隔的项
        items = re.split(r'[,，、;；\n]', text)
        items = [item.strip() for item in items if item.strip()]

        if len(items) > 1:
            return items
        return text[:100].strip()

    def _parse_text(self, text: str) -> str:
        """解析文本字段"""
        # 清理文本
        text = re.sub(r'\s+', ' ', text)  # 合并空白
        text = re.sub(r'^[\d\.\、\)\）\s]+', '', text)  # 移除开头的序号

        # 在章节边界处截断（如 "一、", "二、", "1.", "2." 等）
        section_patterns = [
            r'[一二三四五六七八九十]+、',  # 中文数字章节
            r'\d+[\.\、]',  # 阿拉伯数字章节
            r'\([一二三四五六七八九十\d]+\)',  # 括号数字
            r'\n\s*\n',  # 空行
        ]

        for pattern in section_patterns:
            # 从第二个匹配开始截断（保留第一个章节的内容）
            matches = list(re.finditer(pattern, text))
            if len(matches) > 1:
                text = text[:matches[1].start()]
                break

        return text[:300].strip()  # 限制长度

    def _normalize_unit(self, unit: str) -> str:
        """归一化单位"""
        if not unit:
            return ""
        unit_lower = unit.lower().strip()
        return self.unit_normalize_map.get(unit_lower, unit)

    def _calculate_confidence(self, span_text: str, value: Any, field_type: str) -> float:
        """计算置信度"""
        if value is None or value == "":
            return 0.0

        base_confidence = 0.5

        # 根据字段类型调整
        if field_type in ["integer", "float", "integer_with_comparator", "float_with_comparator"]:
            if isinstance(value, dict) and value.get("value"):
                base_confidence = 0.8
            elif isinstance(value, (int, float)):
                base_confidence = 0.8
        elif field_type == "enum":
            base_confidence = 0.9
        elif field_type == "storage_spec":
            if isinstance(value, dict):
                if value.get("media") and value.get("value"):
                    base_confidence = 0.85
                elif value.get("media") or value.get("value"):
                    base_confidence = 0.7
        else:  # text
            if len(str(value)) > 20:
                base_confidence = 0.7

        return base_confidence

    def extract_numbers(self, content: str) -> List[Dict]:
        """
        从内容中提取所有数字及其上下文

        Args:
            content: 文档内容

        Returns:
            数字信息列表
        """
        numbers = []

        # 匹配数字模式（整数或小数）
        pattern = r'(\d+(?:\.\d+)?)\s*(GHz|GB|TB|G|T|W|瓦|核|台|套|个|mm|英寸|kg|h|小时)?'

        for match in re.finditer(pattern, content, re.IGNORECASE):
            value = match.group(1)
            unit = match.group(2) or ""

            # 获取上下文
            start = max(0, match.start() - 30)
            end = min(len(content), match.end() + 30)
            context = content[start:end]

            numbers.append({
                "value": value,
                "unit": self._normalize_unit(unit),
                "context": context,
                "position": match.start()
            })

        return numbers

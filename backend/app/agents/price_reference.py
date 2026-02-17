from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import random
import math

class PriceReference:
    """价格参考与审价支持智能体 - 增强版（含价格预测）"""

    def __init__(self):
        # 初始化模拟价格数据
        self.price_database = self._init_price_database()
        # 缓存预测结果
        self._prediction_cache: Dict[str, Dict] = {}

    def _init_price_database(self) -> List[Dict[str, Any]]:
        """初始化模拟价格数据"""
        # 根据实际产品分类重新组织的价格数据
        categories = {
            "服务器": [
                {"name": "Dell PowerEdge R750", "specs": "2U机架式, 2×Intel Xeon Gold 6348, 256GB RAM, 4×2.4TB SAS", "base_price": 68000},
                {"name": "HP ProLiant DL380 Gen10 Plus", "specs": "2U机架式, 2×Intel Xeon Silver 4314, 128GB RAM, 8×1.2TB SAS", "base_price": 52000},
                {"name": "浪潮英信 NF5280M6", "specs": "2U机架式, 2×Intel Xeon Gold 5318Y, 192GB RAM, 10×2.4TB SAS", "base_price": 58000},
                {"name": "华为 FusionServer 2288H V6", "specs": "2U机架式, 2×Intel Xeon Gold 6348, 384GB RAM, 12×3.84TB SSD", "base_price": 125000},
                {"name": "联想 ThinkSystem SR650 V2", "specs": "2U机架式, 2×Intel Xeon Silver 4310, 96GB RAM, 6×1.8TB SAS", "base_price": 42000},
                {"name": "曙光 I620-G40", "specs": "2U机架式, 2×Intel Xeon Platinum 8358, 512GB RAM, 8×7.68TB NVMe", "base_price": 185000},
                {"name": "Dell PowerEdge T350", "specs": "塔式服务器, Intel Xeon E-2378, 32GB ECC, 4×2TB SATA", "base_price": 18500},
                {"name": "超聚变 FusionServer 2488H V6", "specs": "2U高密度, 4×Intel Xeon Gold 6338, 1TB RAM, 24×2.4TB SAS", "base_price": 285000},
            ],
            "工作站": [
                {"name": "Dell Precision 3660 Tower", "specs": "Intel i9-13900K, 64GB DDR5, RTX A4500 20GB, 2TB NVMe", "base_price": 28000},
                {"name": "HP Z4 G4", "specs": "Intel Xeon W-3345, 128GB DDR4, RTX A5000 24GB, 4TB NVMe + 8TB HDD", "base_price": 45000},
                {"name": "联想 ThinkStation P620", "specs": "AMD Threadripper Pro 5955WX, 256GB DDR4, 2×RTX A6000, 8TB NVMe", "base_price": 98000},
                {"name": "曙光 W330", "specs": "Intel Xeon W-3275, 192GB DDR4, RTX A4000 16GB, 3TB NVMe SSD", "base_price": 62000},
                {"name": "仰联图形工作站", "specs": "Intel i7-13700K, 32GB DDR5, RTX 4060Ti, 1TB NVMe + 2TB HDD", "base_price": 15800},
                {"name": "HP Z6 G5 A", "specs": "AMD Threadripper Pro 5965WX, 192GB DDR5, 2×RTX A4000, 6TB NVMe", "base_price": 76000},
                {"name": "Dell Precision 3470", "specs": "Intel i7-12700H, 32GB DDR5, RTX A1000, 1TB SSD", "base_price": 18500},
            ],
            "终端": [
                {"name": "联想 ThinkPad X1 Carbon Gen11", "specs": "Intel i7-1365U, 32GB LPDDR5, 1TB PCIe 4.0 SSD, 14英寸 2.8K OLED", "base_price": 18500},
                {"name": "Dell Latitude 5440", "specs": "Intel i7-1355U, 16GB DDR5, 512GB PCIe 4.0 SSD, 14英寸 FHD", "base_price": 8500},
                {"name": "华为 MateBook 14s", "specs": "Intel i7-13700H, 32GB LPDDR5, 1TB SSD, 14.2英寸 2.5K触控", "base_price": 9800},
                {"name": "联想 ThinkCentre M950t", "specs": "Intel i7-13700, 32GB DDR5, 1TB NVMe + 2TB HDD, RTX 3050", "base_price": 12800},
                {"name": "HP EliteBook 840 G9", "specs": "Intel i5-1245U, 16GB LPDDR5, 512GB SSD, 14英寸 FHD", "base_price": 7500},
                {"name": "同方超锐 T550", "specs": "Intel i5-1240P, 16GB DDR4, 512GB SSD, 14英寸 FHD", "base_price": 6200},
                {"name": "升腾 C92", "specs": "Intel Celeron J6412, 8GB RAM, 64GB SSD, 瘦客户机", "base_price": 2300},
                {"name": "深信服桌面云瘦终端", "specs": "ARM处理器, 2GB RAM, 16GB存储, 零维护终端", "base_price": 1800},
            ],
            "无人平台": [
                {"name": "大疆 Matrice 300 RTK", "specs": "工业级无人机, 55分钟续航, 15公里图传, IP45防护", "base_price": 45000},
                {"name": "大疆 DJI FlyCart 30", "specs": "运载无人机, 30kg载重, 28分钟续航, 16公里图传", "base_price": 185000},
                {"name": "云洲 ME70", "specs": "测量无人船, 50kg载荷, 20节航速, 100km续航", "base_price": 280000},
                {"name": "FINEBOT X20无人车", "specs": "地面无人平台, 100kg载重, 8小时续航, 10km遥控距离", "base_price": 95000},
                {"name": "云洲安防无人艇", "specs": "智能巡逻艇, AI识别, 50km/h航速, 12小时续航", "base_price": 380000},
                {"name": "普宙 S400", "specs": "行业无人机, 61分钟续航, 1.2km升限, 15km图传", "base_price": 62000},
            ],
            "通信": [
                {"name": "海能达 PD980", "specs": "数字集群对讲机, 5W功率, IP68防护, GPS定位", "base_price": 3800},
                {"name": "海格通信 B-1000背负站", "specs": "车载/背负双用, 30W功率, 512-2M自适应, 单兵通信", "base_price": 85000},
                {"name": "华为 AirEngine 6761S-21", "specs": "企业级AP, Wi-Fi 6, 10Gbps速率, 256用户并发", "base_price": 6800},
                {"name": "中兴 iMacro 5G基站", "specs": "5G小基站, 2.6GHz频段, 4T4R, 10Gbps回传", "base_price": 350000},
                {"name": "量子加密通信终端", "specs": "量子密钥分发, 百公里传输, BB84协议, 军工级", "base_price": 580000},
                {"name": "海能达 SmartOne DCS", "specs": "调度控制系统, 支持3000用户, GIS地图, 录音回放", "base_price": 125000},
                {"name": "华为 S5731S-H48T4X", "specs": "企业级交换机, 48口千兆电口, 4口万兆光口, 三层交换", "base_price": 8500},
                {"name": "星状组网数传电台", "specs": "800MHz频段, 10W功率, 100km通信距离, 自组网", "base_price": 12000},
            ],
            "显示": [
                {"name": "BenQ RP6502", "specs": "65英寸交互平板, 4K分辨率, 20点触控, 内置Android", "base_price": 18500},
                {"name": "海信 98U7H-PRO", "specs": "98英寸4K电视, 256分区背光, 120Hz刷新, HDMI 2.1", "base_price": 45000},
                {"name": "利亚德 TXP系列", "specs": "P1.25小间距LED屏, 3840Hz刷新, 14bit灰度, 640x480mm", "base_price": 38000},
                {"name": "TCL会议平板 98Y20", "specs": "98英寸会议平板, 4K触控, 内置摄像头麦克风", "base_price": 58000},
                {"name": "飞利浦 275E1S", "specs": "27英寸2K显示器, IPS面板, 75Hz, HDMI+DP", "base_price": 1500},
                {"name": "AOC U34P2C", "specs": "34英寸曲面显示器, 3440x1440, 100Hz, Type-C 65W供电", "base_price": 3800},
                {"name": "爱普生 CB-L730U", "specs": "激光工程投影, 7000流明, WUXGA分辨率, 激光光源", "base_price": 85000},
                {"name": "NEC P525UL", "specs": "激光投影机, 5200流明, WUXGA, 20000小时寿命", "base_price": 68000},
                {"name": "巴可 F80-4K12", "specs": "4K投影机, 12000流明, 激光光源, 影院级", "base_price": 380000},
            ],
            "仪器仪表": [
                {"name": "Fluke DSX-8000", "specs": "线缆分析仪, CAT8测试, 30秒自动测试, 云存储", "base_price": 85000},
                {"name": "是德科技 DSOX4022A", "specs": "示波器, 200MHz带宽, 5GSa/s采样, 4通道", "base_price": 58000},
                {"name": "R&S FPC1000频谱仪", "specs": "频谱分析仪, 5kHz-1GHz, 分辨率1Hz, 跟踪源", "base_price": 38000},
                {"name": "福禄克 TiX580", "specs": "红外热像仪, 640x480分辨率, -20°C至800°C, 5.7英寸屏", "base_price": 128000},
                {"name": "创远仪器 T5260A", "specs": "矢量网络分析仪, 100kHz-20GHz, 动态范围125dB", "base_price": 185000},
                {"name": "固纬 GPP-3323", "specs": "可编程直流电源, 3通道, 195W总功率, USB/LAN", "base_price": 8500},
                {"name": "泰克 MSO2024B", "specs": "混合信号示波器, 200MHz, 1GS/s, 4+16通道", "base_price": 45000},
                {"name": "普源精电 DSA815-TG", "specs": "频谱分析仪, 9kHz-1.5GHz, 分辨率1Hz, 跟踪源", "base_price": 15800},
                {"name": "安东帕 MCP5000", "specs": "智能微波消解仪, 40位转子, 温度压力控制", "base_price": 380000},
            ]
        }

        # 生成历史价格数据
        price_records = []
        base_date = datetime(2024, 1, 1)

        for category, items in categories.items():
            for item in items:
                # 为每个商品生成6个月的历史价格
                for month in range(6):
                    # 模拟价格波动（5%-15%的波动）
                    fluctuation = random.uniform(0.95, 1.15)
                    month_price = round(item["base_price"] * fluctuation, 2)

                    record = {
                        "id": f"{category}-{item['name']}-{month}",
                        "category": category,
                        "name": item["name"],
                        "specs": item["specs"],
                        "price": month_price,
                        "date": base_date.replace(month=(base_date.month + month - 1) % 12 + 1,
                                                 year=base_date.year + (base_date.month + month - 1) // 12).strftime("%Y-%m"),
                        "source": random.choice(["采购平台", "政府采购网", "供应商报价"])
                    }
                    price_records.append(record)

        return price_records

    def query_price(self, category: Optional[str] = None, keyword: Optional[str] = None,
                    min_price: Optional[float] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
        """查询价格信息"""
        # 筛选价格数据
        filtered = self.price_database.copy()

        if category:
            filtered = [p for p in filtered if p["category"] == category]

        if keyword:
            filtered = [p for p in filtered if keyword.lower() in p["name"].lower() or keyword.lower() in p["specs"].lower()]

        if min_price:
            filtered = [p for p in filtered if p["price"] >= min_price]

        if max_price:
            filtered = [p for p in filtered if p["price"] <= max_price]

        # 如果没有筛选结果，返回空
        if not filtered:
            return {
                "records": [],
                "categories": self._get_categories(),
                "total": 0,
                "trend_data": [],
                "price_range": {"min": 0, "max": 0}
            }

        # 获取最新价格记录（按日期去重）
        latest_records = self._get_latest_records(filtered)

        # 生成价格趋势数据
        trend_data = self._generate_trend_data(latest_records)

        # 计算价格范围
        prices = [r["price"] for r in latest_records]
        price_range = {
            "min": min(prices),
            "max": max(prices),
            "avg": round(sum(prices) / len(prices), 2)
        }

        return {
            "records": latest_records,
            "categories": self._get_categories(),
            "total": len(latest_records),
            "trend_data": trend_data,
            "price_range": price_range
        }

    def get_price_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取价格信息"""
        records = [p for p in self.price_database if name.lower() in p["name"].lower()]
        if records:
            # 返回最新记录
            latest = sorted(records, key=lambda x: x["date"], reverse=True)[0]

            # 获取历史价格
            history = [r for r in records if r["name"] == latest["name"]]
            history = sorted(history, key=lambda x: x["date"])

            return {
                "product": latest,
                "history": history,
                "price_change": {
                    "absolute": round(history[-1]["price"] - history[0]["price"], 2),
                    "percent": round(((history[-1]["price"] - history[0]["price"]) / history[0]["price"]) * 100, 2)
                }
            }
        return None

    def _get_categories(self) -> List[str]:
        """获取所有分类"""
        return sorted(set(p["category"] for p in self.price_database))

    def _get_latest_records(self, records: List[Dict]) -> List[Dict]:
        """获取每个商品的最新记录"""
        latest = {}
        for record in records:
            key = f"{record['category']}-{record['name']}"
            if key not in latest or record["date"] > latest[key]["date"]:
                latest[key] = record

        return list(latest.values())

    def _generate_trend_data(self, records: List[Dict]) -> List[Dict]:
        """生成价格趋势数据"""
        # 按分类聚合价格数据
        category_data = {}
        for record in records:
            category = record["category"]
            if category not in category_data:
                category_data[category] = {}
            if record["date"] not in category_data[category]:
                category_data[category][record["date"]] = []
            category_data[category][record["date"]].append(record["price"])

        # 计算每个分类每月的平均价格
        trend_data = []
        months = sorted(set(r["date"] for r in records))

        for month in months:
            data_point = {"date": month}
            for category, monthly_data in category_data.items():
                if month in monthly_data:
                    avg_price = round(sum(monthly_data[month]) / len(monthly_data[month]), 2)
                    data_point[category] = avg_price
            trend_data.append(data_point)

        return trend_data

    def analyze_price(self, product_name: str, quoted_price: float) -> Dict[str, Any]:
        """分析报价合理性"""
        reference = self.get_price_by_name(product_name)

        if not reference:
            return {
                "product_name": product_name,
                "quoted_price": quoted_price,
                "analysis": "未找到参考价格数据",
                "recommendation": "建议收集更多价格信息后再做判断"
            }

        latest_price = reference["product"]["price"]
        price_diff = quoted_price - latest_price
        price_diff_percent = (price_diff / latest_price) * 100

        if price_diff_percent <= -10:
            assessment = "报价偏低"
            recommendation = "建议核实产品质量和服务条款，警惕低价陷阱"
        elif price_diff_percent >= 20:
            assessment = "报价偏高"
            recommendation = "建议与供应商协商降价，或提供额外增值服务"
        else:
            assessment = "报价合理"
            recommendation = "报价处于合理区间，可以接受"

        return {
            "product_name": product_name,
            "quoted_price": quoted_price,
            "reference_price": latest_price,
            "price_difference": round(price_diff, 2),
            "price_difference_percent": round(price_diff_percent, 2),
            "assessment": assessment,
            "recommendation": recommendation,
            "market_trend": reference["price_change"]
        }

    def predict_price(self, keyword: str, months_ahead: int = 3) -> Dict[str, Any]:
        """
        预测未来价格趋势

        Args:
            keyword: 产品关键词
            months_ahead: 预测未来几个月

        Returns:
            预测结果，包含预测价格、趋势、建议等
        """
        # 获取相关产品的历史数据
        records = [p for p in self.price_database if
                   keyword.lower() in p["name"].lower() or keyword.lower() in p["category"].lower()]

        if not records:
            return {
                "success": False,
                "message": f"未找到与 '{keyword}' 相关的价格数据",
                "predictions": []
            }

        # 按产品分组进行预测
        product_groups = self._group_by_product(records)
        predictions = []

        for product_name, product_records in product_groups.items():
            prediction = self._predict_single_product(product_name, product_records, months_ahead)
            if prediction:
                predictions.append(prediction)

        # 汇总预测结果
        if predictions:
            avg_trend = self._calculate_average_trend(predictions)
            best_buy_timing = self._analyze_best_buy_timing(predictions)

            return {
                "success": True,
                "keyword": keyword,
                "products_analyzed": len(predictions),
                "predictions": predictions[:5],  # 最多返回5个产品预测
                "overall_trend": avg_trend,
                "buying_advice": best_buy_timing,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        return {
            "success": False,
            "message": "无法生成有效预测",
            "predictions": []
        }

    def _group_by_product(self, records: List[Dict]) -> Dict[str, List[Dict]]:
        """按产品名分组"""
        groups = {}
        for record in records:
            name = record["name"]
            if name not in groups:
                groups[name] = []
            groups[name].append(record)

        # 按日期排序
        for name in groups:
            groups[name] = sorted(groups[name], key=lambda x: x["date"])

        return groups

    def _predict_single_product(self, product_name: str, records: List[Dict],
                                 months_ahead: int) -> Optional[Dict[str, Any]]:
        """对单个产品进行价格预测"""
        if len(records) < 3:
            return None

        # 提取价格序列
        prices = [r["price"] for r in records]
        dates = [r["date"] for r in records]

        # 计算趋势（使用线性回归）
        trend_slope, trend_intercept = self._linear_regression(prices)

        # 计算季节性因素
        seasonality = self._calculate_seasonality(prices)

        # 计算置信区间
        std_dev = self._calculate_std_dev(prices, trend_slope, trend_intercept)
        confidence_margin = std_dev * 1.96  # 95% 置信区间

        # 生成预测
        last_price = prices[-1]
        predictions = []
        current_date = datetime.strptime(dates[-1], "%Y-%m")

        for i in range(1, months_ahead + 1):
            future_date = self._add_months(current_date, i)
            trend_value = trend_intercept + trend_slope * (len(prices) + i - 1)
            seasonal_factor = seasonality[(len(prices) + i - 1) % len(seasonality)] if seasonality else 1.0

            predicted_price = trend_value * seasonal_factor
            lower_bound = predicted_price - confidence_margin
            upper_bound = predicted_price + confidence_margin

            predictions.append({
                "date": future_date.strftime("%Y-%m"),
                "predicted_price": round(max(predicted_price, 0), 2),
                "lower_bound": round(max(lower_bound, 0), 2),
                "upper_bound": round(max(upper_bound, 0), 2),
                "confidence": "95%"
            })

        # 判断趋势方向
        if trend_slope < -0.01 * last_price:
            trend_direction = "下降"
            trend_strength = "强" if abs(trend_slope) > 0.03 * last_price else "弱"
        elif trend_slope > 0.01 * last_price:
            trend_direction = "上升"
            trend_strength = "强" if trend_slope > 0.03 * last_price else "弱"
        else:
            trend_direction = "稳定"
            trend_strength = "中等"

        return {
            "product_name": product_name,
            "category": records[0]["category"],
            "current_price": last_price,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "trend_slope": round(trend_slope, 4),
            "predictions": predictions
        }

    def _linear_regression(self, values: List[float]) -> Tuple[float, float]:
        """简单线性回归"""
        n = len(values)
        x = list(range(n))

        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0, y_mean

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        return slope, intercept

    def _calculate_seasonality(self, values: List[float]) -> List[float]:
        """计算季节性因子"""
        if len(values) < 4:
            return [1.0]

        # 使用4期移动平均计算季节性
        n = len(values)
        period = min(4, n // 2)

        # 计算移动平均
        moving_avg = []
        for i in range(period - 1, n):
            avg = sum(values[i - period + 1:i + 1]) / period
            moving_avg.append(avg)

        # 计算季节性比率
        ratios = []
        for i in range(len(moving_avg)):
            if moving_avg[i] != 0:
                ratios.append(values[i + period - 1] / moving_avg[i])

        if not ratios:
            return [1.0]

        # 归一化
        avg_ratio = sum(ratios) / len(ratios)
        seasonality = [r / avg_ratio for r in ratios]

        return seasonality

    def _calculate_std_dev(self, values: List[float], slope: float, intercept: float) -> float:
        """计算残差标准差"""
        n = len(values)
        if n < 2:
            return 0

        residuals = []
        for i, v in enumerate(values):
            predicted = intercept + slope * i
            residuals.append((v - predicted) ** 2)

        variance = sum(residuals) / (n - 2)
        return math.sqrt(variance)

    def _add_months(self, date: datetime, months: int) -> datetime:
        """添加月份"""
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        return date.replace(year=year, month=month)

    def _calculate_average_trend(self, predictions: List[Dict]) -> Dict[str, Any]:
        """计算平均趋势"""
        if not predictions:
            return {"direction": "未知", "confidence": 0}

        up_count = sum(1 for p in predictions if p["trend_direction"] == "上升")
        down_count = sum(1 for p in predictions if p["trend_direction"] == "下降")
        stable_count = sum(1 for p in predictions if p["trend_direction"] == "稳定")

        total = len(predictions)
        if up_count > down_count and up_count > stable_count:
            return {"direction": "上升", "confidence": round(up_count / total * 100, 1)}
        elif down_count > up_count and down_count > stable_count:
            return {"direction": "下降", "confidence": round(down_count / total * 100, 1)}
        else:
            return {"direction": "稳定", "confidence": round(stable_count / total * 100, 1)}

    def _analyze_best_buy_timing(self, predictions: List[Dict]) -> Dict[str, Any]:
        """分析最佳购买时机"""
        if not predictions:
            return {"recommendation": "数据不足，无法提供建议"}

        # 分析价格走势
        downward_products = [p for p in predictions if p["trend_direction"] == "下降"]
        stable_products = [p for p in predictions if p["trend_direction"] == "稳定"]
        upward_products = [p for p in predictions if p["trend_direction"] == "上升"]

        if len(downward_products) > len(upward_products):
            return {
                "recommendation": "建议延后购买",
                "reason": "多数产品价格呈下降趋势，预计未来1-3个月价格可能更低",
                "suggested_delay": "1-3个月"
            }
        elif len(upward_products) > len(downward_products):
            return {
                "recommendation": "建议尽快购买",
                "reason": "多数产品价格呈上升趋势，延迟采购可能导致成本增加",
                "urgency": "高"
            }
        else:
            return {
                "recommendation": "可根据需求灵活安排",
                "reason": "市场价格相对稳定，建议根据项目进度安排采购",
                "urgency": "中"
            }

    def get_market_insights(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        获取市场洞察

        Returns:
            市场分析报告，包含热门产品、价格变化、采购建议等
        """
        records = self.price_database
        if category:
            records = [r for r in records if r["category"] == category]

        if not records:
            return {"success": False, "message": "无数据"}

        # 获取最新记录
        latest_records = self._get_latest_records(records)

        # 计算市场统计
        categories = {}
        for r in latest_records:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = {"count": 0, "total_price": 0, "products": []}
            categories[cat]["count"] += 1
            categories[cat]["total_price"] += r["price"]
            categories[cat]["products"].append(r["name"])

        # 计算各分类平均价格
        for cat in categories:
            categories[cat]["avg_price"] = round(
                categories[cat]["total_price"] / categories[cat]["count"], 2
            )

        # 生成采购建议
        insights = []
        for cat, data in categories.items():
            # 预测该分类的趋势
            cat_records = [r for r in records if r["category"] == cat]
            if len(cat_records) >= 3:
                prices = [r["price"] for r in sorted(cat_records, key=lambda x: x["date"])]
                slope, _ = self._linear_regression(prices)

                if slope < -0.02 * (sum(prices) / len(prices)):
                    insight = f"{cat}类产品价格呈下降趋势，建议关注"
                elif slope > 0.02 * (sum(prices) / len(prices)):
                    insight = f"{cat}类产品价格呈上升趋势，建议尽早采购"
                else:
                    insight = f"{cat}类产品价格稳定"

                insights.append({
                    "category": cat,
                    "insight": insight,
                    "trend_slope": round(slope, 4),
                    "product_count": data["count"],
                    "avg_price": data["avg_price"]
                })

        return {
            "success": True,
            "categories": categories,
            "insights": sorted(insights, key=lambda x: abs(x["trend_slope"]), reverse=True),
            "total_products": len(latest_records),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

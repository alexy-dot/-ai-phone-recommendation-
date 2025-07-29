from dataclasses import dataclass, field
from typing import List, Set

@dataclass
class PhoneSpec:
    name: str
    cpu: str
    ram_gb: int
    storage_gb: int
    screen_size_inch: float
    camera_mp: int
    battery_mah: int
    weight_g: int
    price: int
    highlights: List[str]
    rating: float
    sales: int
    # 新增维度
    heat_control_score: float = 3.0  # 发热控制评分 (1-5, 越高越好)
    network_stability_score: float = 3.0 # 网络稳定性评分 (1-5, 越高越好)

# 样例数据
sample_phones = [
    PhoneSpec(
        name="小米13",
        cpu="骁龙8 Gen2",
        ram_gb=12,
        storage_gb=256,
        screen_size_inch=6.36,
        camera_mp=50,
        battery_mah=4500,
        weight_g=189,
        price=3999,
        highlights=["轻薄", "高性能", "快充"],
        rating=4.7,
        sales=12000,
        heat_control_score=4.0,
        network_stability_score=4.2
    ),
    PhoneSpec(
        name="iPhone 14",
        cpu="A15",
        ram_gb=6,
        storage_gb=128,
        screen_size_inch=6.1,
        camera_mp=12,
        battery_mah=3279,
        weight_g=172,
        price=5999,
        highlights=["影像", "系统流畅", "品牌"],
        rating=4.8,
        sales=20000,
        heat_control_score=4.5,
        network_stability_score=3.5 # 模拟用户反馈的网络问题
    ),
    PhoneSpec(
        name="华为P60",
        cpu="骁龙8+ Gen1",
        ram_gb=8,
        storage_gb=256,
        screen_size_inch=6.67,
        camera_mp=48,
        battery_mah=4815,
        weight_g=197,
        price=4999,
        highlights=["拍照", "续航", "快充"],
        rating=4.6,
        sales=15000,
        heat_control_score=4.2,
        network_stability_score=4.8
    ),
    PhoneSpec(
        name="OPPO Find X6",
        cpu="天玑9200",
        ram_gb=12,
        storage_gb=256,
        screen_size_inch=6.74,
        camera_mp=50,
        battery_mah=4800,
        weight_g=207,
        price=4499,
        highlights=["影像", "快充", "大屏"],
        rating=4.5,
        sales=8000,
        heat_control_score=3.8,
        network_stability_score=4.1
    ),
    PhoneSpec(
        name="vivo X90",
        cpu="天玑9200",
        ram_gb=8,
        storage_gb=128,
        screen_size_inch=6.78,
        camera_mp=50,
        battery_mah=4810,
        weight_g=200,
        price=3999,
        highlights=["拍照", "快充", "大屏"],
        rating=4.4,
        sales=10000,
        heat_control_score=3.9,
        network_stability_score=4.0
    ),
    PhoneSpec(
        name="一加11",
        cpu="骁龙8 Gen2",
        ram_gb=16,
        storage_gb=256,
        screen_size_inch=6.7,
        camera_mp=50,
        battery_mah=5000,
        weight_g=205,
        price=3999,
        highlights=["性能", "快充", "大内存"],
        rating=4.6,
        sales=6000,
        heat_control_score=4.3,
        network_stability_score=4.3
    ),
    PhoneSpec(
        name="Redmi K60",
        cpu="骁龙8+ Gen1",
        ram_gb=12,
        storage_gb=256,
        screen_size_inch=6.67,
        camera_mp=64,
        battery_mah=5500,
        weight_g=204,
        price=2499,
        highlights=["性价比", "续航", "快充"],
        rating=4.3,
        sales=18000,
        heat_control_score=3.5,
        network_stability_score=3.8
    ),
    PhoneSpec(
        name="iPhone 14 Pro",
        cpu="A16",
        ram_gb=6,
        storage_gb=128,
        screen_size_inch=6.1,
        camera_mp=48,
        battery_mah=3200,
        weight_g=206,
        price=7999,
        highlights=["影像", "性能", "品牌"],
        rating=4.9,
        sales=25000,
        heat_control_score=4.6,
        network_stability_score=3.6 # 模拟用户反馈的网络问题
    ),
    PhoneSpec(
        name="小米13 Ultra",
        cpu="骁龙8 Gen2",
        ram_gb=16,
        storage_gb=512,
        screen_size_inch=6.73,
        camera_mp=50,
        battery_mah=5000,
        weight_g=227,
        price=5999,
        highlights=["影像", "性能", "大存储"],
        rating=4.7,
        sales=5000,
        heat_control_score=4.4,
        network_stability_score=4.4
    ),
    PhoneSpec(
        name="华为Mate 60",
        cpu="麒麟9000S", # CPU名称修正
        ram_gb=12,
        storage_gb=256,
        screen_size_inch=6.69,
        camera_mp=50,
        battery_mah=4750,
        weight_g=209,
        price=6999,
        highlights=["拍照", "续航", "品牌", "信号"],
        rating=4.8,
        sales=12000,
        heat_control_score=4.1,
        network_stability_score=5.0
    ),
    PhoneSpec(
        name="OPPO Reno 10",
        cpu="骁龙778G",
        ram_gb=8,
        storage_gb=128,
        screen_size_inch=6.7,
        camera_mp=64,
        battery_mah=4600,
        weight_g=180,
        price=2499,
        highlights=["轻薄", "拍照", "性价比"],
        rating=4.2,
        sales=15000,
        heat_control_score=3.7,
        network_stability_score=3.9
    ),
    PhoneSpec(
        name="vivo S17",
        cpu="骁龙778G",
        ram_gb=8,
        storage_gb=128,
        screen_size_inch=6.78,
        camera_mp=50,
        battery_mah=4600,
        weight_g=186,
        price=2299,
        highlights=["轻薄", "拍照", "颜值"],
        rating=4.3,
        sales=12000,
        heat_control_score=3.8,
        network_stability_score=4.0
    )
] 
import os
import csv
from typing import Dict, List
from dataclasses import asdict

from model.enum.category import Category
from model.memory.wing_model_para import WingModelPara

MEMORY_ROOT = "config"
WING_MODEL_PARA = "customized_wing_model_para.csv"


def load_customized_wing_model() -> Dict[str, WingModelPara]:
    """加载自定义 Wing Model 参数，并返回一个以 Category 为键的字典。"""
    file_path = os.path.join(MEMORY_ROOT, WING_MODEL_PARA)
    wing_model_data = {}

    if not os.path.exists(file_path):
        return wing_model_data

    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row["category"]  # 假设 category 存储为枚举名称
            wing_model_data[category] = WingModelPara(
                v=float(row["v"]),
                k1=float(row["k1"]),
                k2=float(row["k2"]),
                b=float(row["b"]),
            )

    return wing_model_data


def save_customized_wing_model(category: str, customized_wing_model: WingModelPara):
    """如果 category 已存在则更新，否则追加到 CSV 文件。"""
    file_path = os.path.join(MEMORY_ROOT, WING_MODEL_PARA)
    fieldnames = ["category", "v", "k1", "k2", "b"]

    # 读取 CSV 文件内容
    rows: List[Dict[str, str]] = []
    updated = False  # 标记是否更新了数据

    if os.path.exists(file_path):
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["category"] == category:
                    # 更新已有 category 的数据
                    row.update({
                        "v": customized_wing_model.v,
                        "k1": customized_wing_model.k1,
                        "k2": customized_wing_model.k2,
                        "b": customized_wing_model.b,
                    })
                    updated = True
                rows.append(row)
    else:
        os.makedirs(MEMORY_ROOT, exist_ok=True)

    # 如果 category 不存在，则追加新行
    if not updated:
        rows.append({
            "category": category,
            "v": customized_wing_model.v,
            "k1": customized_wing_model.k1,
            "k2": customized_wing_model.k2,
            "b": customized_wing_model.b,
        })

    # 重新写入 CSV 文件（覆盖写入）
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    save_customized_wing_model(Category.SSE50.name, WingModelPara(v=0.15, k1=0.01, k2=0.02, b=0.03))
    print(load_customized_wing_model())
    save_customized_wing_model(Category.CSI500.name, WingModelPara(v=0.16, k1=0.02, k2=0.03, b=0.04))
    save_customized_wing_model(Category.CSI1000.name, WingModelPara(v=0.17, k1=0.03, k2=0.04, b=0.05))

    print(load_customized_wing_model())

    save_customized_wing_model(Category.CSI1000.name, WingModelPara(v=0.18, k1=0.03, k2=0.04, b=0.05))

    print(load_customized_wing_model())


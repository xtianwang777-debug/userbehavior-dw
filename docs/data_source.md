# 数据来源

真实项目使用阿里天池公开的淘宝 UserBehavior 数据集：<https://tianchi.aliyun.com/dataset/649>。

原始文件为无表头 CSV，字段顺序为：`user_id,item_id,category_id,behavior_type,timestamp`。下载并解压后，将文件重命名为 `UserBehavior.csv`，放入 `data/raw/`。当前仓库中的 `data/raw/UserBehavior.csv` 是用于本地验收的可重复演示数据，不能替代真实数据。

-- 示例：DAU
SELECT dt, COUNT(DISTINCT user_id) AS dau
FROM dwd.user_behavior_detail
GROUP BY dt;

-- 示例：次日留存（分母使用当日活跃用户）
SELECT a.dt,
       COUNT(DISTINCT a.user_id) AS dau,
       COUNT(DISTINCT b.user_id) AS next_day_uv,
       COUNT(DISTINCT b.user_id) * 1.0 / COUNT(DISTINCT a.user_id) AS retention_1d
FROM dwd.user_behavior_detail a
LEFT JOIN dwd.user_behavior_detail b
  ON a.user_id = b.user_id
 AND b.dt = date_add(a.dt, 1)
GROUP BY a.dt;

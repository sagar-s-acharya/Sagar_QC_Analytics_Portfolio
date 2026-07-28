-- Q1: Batch Status Distribution
SELECT
  batch_status,
  COUNT(*) AS total_batches,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM batches), 2) AS percentage
FROM batches
GROUP BY batch_status
ORDER BY total_batches DESC;

-- Q2: Product-wise Batch Production
SELECT
  product_name,
  COUNT(*) AS total_batches
FROM batches
GROUP BY product_name
ORDER BY total_batches DESC;

-- Q3: Production Line Utilization
SELECT
  production_line,
  COUNT(*) AS total_batches
FROM batches
GROUP BY production_line
ORDER BY total_batches DESC;

-- Q4: Shift-wise Production
SELECT
  shift,
  COUNT(*) AS total_batches
FROM batches
GROUP BY shift
ORDER BY total_batches DESC;

-- Q5: Monthly Production Trend
SELECT
  month_year,
  COUNT(*) AS total_batches
FROM batches
GROUP BY month_year
ORDER BY month_year ASC;

-- Q6: Deviation Severity Distribution
SELECT
  severity,
  COUNT(*) AS total_deviations
FROM deviations
GROUP BY severity
ORDER BY total_deviations DESC;

-- Q7: Root Cause Analysis
SELECT
  root_cause_category,
  COUNT(*) AS total_deviations
FROM deviations
GROUP BY root_cause_category
ORDER BY total_deviations DESC;

-- Q8: Deviations Detected By Department/Role
SELECT
  detected_by,
  COUNT(*) AS total_detected
FROM deviations
GROUP BY detected_by
ORDER BY total_detected DESC;

-- Q9: CAPA Generation Rate
SELECT
  capa_raised,
  COUNT(*) AS total_deviations
FROM deviations
GROUP BY capa_raised;

-- Q10: Product-wise Deviations (Requires JOIN to get product name)
SELECT
  b.product_name,
  COUNT(d.deviation_id) AS total_deviations
FROM deviations d
JOIN batches b ON d.batch_id = b.batch_id
GROUP BY b.product_name
ORDER BY total_deviations DESC;

-- Q11: CAPA Effectiveness Summary
SELECT
  effectiveness_status,
  COUNT(*) AS total_capa
FROM capa_actions
GROUP BY effectiveness_status
ORDER BY total_capa DESC;

-- Q12: CAPA On-Time Closure Rate
SELECT
  on_time,
  COUNT(*) AS total_capa
FROM capa_actions
GROUP BY on_time;

-- Q13: Average CAPA Turnaround Time (TAT) by Product
SELECT
  b.product_name,
  ROUND(AVG(c.tat_days), 2) AS avg_tat_days
FROM capa_actions c
JOIN deviations d ON c.deviation_id = d.deviation_id
JOIN batches b ON d.batch_id = b.batch_id
GROUP BY b.product_name
ORDER BY avg_tat_days DESC;

-- Q14: Microbial Overall Pass/Fail Status
SELECT
  result_status,
  COUNT(*) AS total_tests
FROM microbial_results
GROUP BY result_status;

-- Q15: Product-wise Microbial Failures
SELECT
  b.product_name,
  COUNT(m.micro_id) AS microbial_failures
FROM microbial_results m
JOIN batches b ON m.batch_id = b.batch_id
WHERE m.result_status != 'Pass'
GROUP BY b.product_name
ORDER BY microbial_failures DESC;

-- Q16: Physicochemical Overall Pass/Fail Status
SELECT
  result_status,
  COUNT(*) AS total_tests
FROM test_results
GROUP BY result_status;

-- Q17: Product-wise Physicochemical Failures
SELECT
  b.product_name,
  COUNT(t.test_id) AS pc_failures
FROM test_results t
JOIN batches b ON t.batch_id = b.batch_id
WHERE t.result_status != 'Pass'
GROUP BY b.product_name
ORDER BY pc_failures DESC;
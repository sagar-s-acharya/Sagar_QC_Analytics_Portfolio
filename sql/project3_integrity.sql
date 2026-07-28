-- Check 1: Data Completeness (Finds test results missing values)
SELECT COUNT(*) AS missing_values_count
FROM test_results 
WHERE result_value IS NULL;

-- Check 2: Timeliness (Finds backdated test entries where testing predates batch creation)
SELECT COUNT(t.test_id) AS anachronistic_tests_count
FROM test_results t
JOIN batches b ON t.batch_id = b.batch_id
WHERE t.test_date < b.batch_date;

-- Check 3: Consistency & Compliance (Finds illegal data states: Batch marked 'PASS' despite containing a 'FAIL' test)
SELECT COUNT(DISTINCT b.batch_id) AS non_compliant_pass_batches
FROM batches b
JOIN test_results t ON b.batch_id = t.batch_id
WHERE b.batch_status = 'PASS' 
  AND t.result_status = 'FAIL';
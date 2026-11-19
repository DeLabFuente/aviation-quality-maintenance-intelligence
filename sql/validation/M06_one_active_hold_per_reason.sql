-- rule: M06
-- title: At most one active hold per reason on each order
-- severity: CRITICAL
-- type: N
-- enforced_by: PARTIAL UNIQUE INDEX + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref, COUNT(*) || ' active ' || h.hold_reason || ' holds' AS detail
FROM Maintenance_Order_Holds h JOIN Maintenance_Orders o USING (mo_id)
WHERE h.end_date IS NULL GROUP BY h.mo_id, h.hold_reason HAVING COUNT(*) > 1;

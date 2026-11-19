-- rule: M05
-- title: ON_HOLD if and only if the order has an active hold
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref,
       'Status ' || o.status || ' with ' ||
       (SELECT COUNT(*) FROM Maintenance_Order_Holds h WHERE h.mo_id = o.mo_id AND h.end_date IS NULL) || ' active holds' AS detail
FROM Maintenance_Orders o
WHERE (o.status = 'ON_HOLD') <> EXISTS (SELECT 1 FROM Maintenance_Order_Holds h
                                        WHERE h.mo_id = o.mo_id AND h.end_date IS NULL);

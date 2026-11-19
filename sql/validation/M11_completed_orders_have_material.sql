-- rule: M11
-- title: A COMPLETED or CLOSED order received all its material, net of returns
-- severity: CRITICAL
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT o.mo_number AS record_ref,
       m.part_number || ': required ' || l.qty_required || ', issued ' || COALESCE(x.net_issued, 0) AS detail
FROM Maintenance_Order_Materials l
JOIN Maintenance_Orders o USING (mo_id)
JOIN Materials m ON m.material_id = l.material_id
LEFT JOIN (SELECT mo_id, material_id,
                  SUM(CASE movement_type WHEN 'ISSUE' THEN quantity ELSE -quantity END) AS net_issued
           FROM Inventory_Movements WHERE movement_type IN ('ISSUE', 'RETURN')
           GROUP BY mo_id, material_id) x ON x.mo_id = l.mo_id AND x.material_id = l.material_id
WHERE o.status IN ('COMPLETED', 'CLOSED') AND COALESCE(x.net_issued, 0) < l.qty_required;

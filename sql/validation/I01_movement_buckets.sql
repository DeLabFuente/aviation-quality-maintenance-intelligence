-- rule: I01
-- title: Each movement type moves stock between its own pair of states
-- severity: CRITICAL
-- type: N
-- enforced_by: CHECK + validation
-- returns: one row per record that breaks the rule (record_ref, detail)
SELECT movement_number AS record_ref,
       movement_type || ' from ' || COALESCE(from_bucket, '-') || ' to ' || COALESCE(to_bucket, '-') AS detail
FROM Inventory_Movements
WHERE NOT (
       (movement_type = 'RECEIPT'            AND from_bucket IS NULL            AND to_bucket = 'QUARANTINE')
    OR (movement_type = 'INSPECTION_RELEASE' AND from_bucket = 'QUARANTINE'     AND to_bucket = 'AVAILABLE')
    OR (movement_type = 'RESERVE'            AND from_bucket = 'AVAILABLE'      AND to_bucket = 'RESERVED')
    OR (movement_type = 'UNRESERVE'          AND from_bucket = 'RESERVED'       AND to_bucket = 'AVAILABLE')
    OR (movement_type = 'ISSUE'              AND from_bucket = 'RESERVED'       AND to_bucket IS NULL)
    OR (movement_type = 'RETURN'             AND from_bucket IS NULL            AND to_bucket = 'QUARANTINE')
    OR (movement_type = 'BLOCK'              AND from_bucket = 'AVAILABLE'      AND to_bucket = 'BLOCKED')
    OR (movement_type = 'UNBLOCK'            AND from_bucket = 'BLOCKED'        AND to_bucket = 'AVAILABLE')
    OR (movement_type = 'NONCONFORM'         AND from_bucket IN ('QUARANTINE', 'AVAILABLE', 'BLOCKED')
                                             AND to_bucket = 'NON_CONFORMING')
    OR (movement_type = 'SCRAP'              AND from_bucket = 'NON_CONFORMING' AND to_bucket IS NULL)
    OR (movement_type = 'ADJUSTMENT_IN'      AND from_bucket IS NULL            AND to_bucket = 'AVAILABLE')
    OR (movement_type = 'ADJUSTMENT_OUT'     AND from_bucket = 'AVAILABLE'      AND to_bucket IS NULL));

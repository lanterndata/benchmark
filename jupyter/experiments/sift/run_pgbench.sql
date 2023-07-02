\set id random(1, 10000)

SELECT *
FROM sift_base:N
ORDER BY v <-> (
    SELECT v
    FROM sift_base:N
    WHERE id = :id
)
LIMIT :K;
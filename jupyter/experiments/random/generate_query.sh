D=$1
K=$2
N=$3

cat << EOF
  \set id random(1, ${N})

  SELECT * 
  FROM test_table2
  ORDER BY vector${D} <-> (
    SELECT
      vector${D}
    FROM
      test_table2
    WHERE
      id = :id
  ) 
  LIMIT ${K};
EOF
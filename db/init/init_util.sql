CREATE OR REPLACE FUNCTION random_integer(max_value INT) RETURNS INT AS $$
  BEGIN
    RETURN floor(random() * max_value)::INT;
  END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION random_array(n INT) RETURNS float[] AS $$
  DECLARE
    result float[] := ARRAY[]::float[];
  BEGIN
    FOR i IN 1..n LOOP
      result := array_append(result, random());
    END LOOP;
    RETURN result;
  END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION random_vector(n INT) RETURNS vector AS $$
  BEGIN
    RETURN random_array(n)::vector;
  END
$$ LANGUAGE plpgsql;

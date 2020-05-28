--
-- Copyright 2020 The Android Open Source Project
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     https://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

CREATE TABLE {{output_table}} AS
SELECT
  utid,
  cpu,
  (
    SELECT
      CASE
        WHEN layout = 'big_little_bigger' AND cpu < 4 THEN 'little'
        WHEN layout = 'big_little_bigger' AND cpu < 7 THEN 'big'
        WHEN layout = 'big_little_bigger' AND cpu = 7 THEN 'bigger'
        WHEN layout = 'big_little' AND cpu < 4 THEN 'little'
        WHEN layout = 'big_little' AND cpu < 8 THEN 'big'
        ELSE 'unknown'
      END
    FROM core_layout_type
  ) AS core_type,
  -- We divide by 1e3 here as dur is in ns and freq_khz in khz. In total
  -- this means we need to divide the duration by 1e9 and multiply the
  -- frequency by 1e3 then multiply again by 1e3 to get millicycles
  -- i.e. divide by 1e3 in total.
  -- We use millicycles as we want to preserve this level of precision
  -- for future calculations.
  SUM(dur * freq_khz / 1000) AS millicycles,
  CAST(SUM(dur * freq_khz / 1000000 / 1000000) AS INT) AS mcycles,
  SUM(dur) AS runtime_ns,
  MIN(freq_khz) AS min_freq_khz,
  MAX(freq_khz) AS max_freq_khz,
  -- We choose to work in micros space in both the numerator and
  -- denominator as this gives us good enough precision without risking
  -- overflows.
  CAST(SUM(dur * freq_khz / 1000) / SUM(dur / 1000) AS INT) AS avg_freq_khz
FROM {{input_table}}
GROUP BY utid, cpu;

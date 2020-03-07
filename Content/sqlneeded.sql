-- staff usercase all_sql

-- View Flights:
-- 1. defaults: view all future flights operated by the airline she/he works for the next 30 days 
SELECT * FROM flight WHERE airline_name = %s AND DATE(dept_time) BETWEEN DATE(CURRENT_TIMESTAMP) 
    AND DATE(CURRENT_TIMESTAMP) + INTERVAL 30 DAY

-- 2. general: view all past/current/future flights based on "range of dates" & "source/destination airports" 
SELECT * FROM flight WHERE airline_name = %s AND DATE(dept_time) BETWEEN DATE(CURRENT_TIMESTAMP) 
    AND DATE(CURRENT_TIMESTAMP) + INTERVAL 30 DAY AND dept_from = %s AND arr_at = %s

-- 3. see all the customer of a particular flight
SELECT airline_name, flight_num, dep_time, email, name FROM ticket NATURAL JOIN customer WHERE (airline_name, flight_num, dep_time) = (%s, %s, %s)

-- 4. Dummy

-- 5. Create New Flights
-- foreign key constraint!!!
SELECT airline_name, airpline_id 
FROM airplane

INSERT INTO flight 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

-- 6. Change Status of Flights
UPDATE flight 
   SET flight_status = %s
   WHERE (airline_name, flight_num, dep_time) = (%s, %s, %s)

-- 7. Add Airplane
INSERT INTO airplane
    VALUES (%s, %s, %s)

-- 8. Add Airport
INSERT INTO airport
    VALUES (%s, %s)

-- 9. View Flight ratings
SELECT * from rate NATURAL JOIN (SELECT airline_name,flight_num, AVG(rate) AS avg_rate) 
    WHERE airline_name = %s;


-- 10. View  All booking agents
-- Part I sales past month
SELECT  agent_email, COUNT(*) AS total_sales
    FROM ticket 
    WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 30 DAY AND NOW() 
    GROUP BY agent_email ORDER BY total_sales DESC
    LIMIT 5
-- Part II sales past year
SELECT  agent_email, COUNT(*) AS total_sales
    FROM ticket 
    WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() 
    GROUP BY agent_email ORDER BY total_sales DESC
    LIMIT 5
-- Part III commission past year
SELECT  agent_email, SUM(sold_price) * 0.1 AS commission FROM ticket 
    WHERE agent_email IS NOT NULL AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR AND NOW() 
    ORDER BY commission DESC
    LIMIT 5
    
-- 11. View frequent customers
-- Part I most frequent customer
CREATE VIEW travel_freq AS 
    SELECT cust_email, COUNT(*) AS travel_times FROM ticket WHERE airline_name = %s;

SELECT cust_email FROM travel_freq WHERE travel_times in (SELECT MAX(travel_times) FROM travel_freq)

-- Part II see the flight a customer taken on that airline
SELECT airline_name, flight_num, dept_time FROM ticket WHERE cust_email = %s 

-- 12. Ticket Sales Report 
-- Part I Sales based on specific DATE (Monthwise Sales)
SELECT YEAR(purchase_time), MONTH(purchase_time), COUNT(*) FROM ticket 
WHERE DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR and NOW()
GROUP BY YEAR(purchase_time), MONTH(purchase_time)
 
-- Part II 


-- 13. Comparison of Revenue
SELECT SUM(sold_price)
from ticket 
WHERE agent_email IS NULL and DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR and NOW(); 

SELECT SUM(sold_price)
from ticket 
WHERE agent_email IS NOT NULL and DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR and NOW(); 

-- 14. View Top Destinations

SELECT arr_at, city, count(*) as visit_time 
    FROM ticket NATURAL JOIN flight as S, airport
    WHERE S.arr_at  = airport.name AND DATE(purchase_time) BETWEEN NOW() - INTERVAL 3 MONTH and NOW()
    GROUP BY arr_at 
    ORDER BY visit_time DESC
    LIMIT 3

SELECT arr_at, count(*) as visit_time 
    FROM ticket NATURAL JOIN flight 
    WHERE DATE(purchase_time) BETWEEN NOW() - INTERVAL 1 YEAR and NOW()
    GROUP BY arr_at 
    ORDER BY visit_time
    LIMIT 3











-- COVID-19 Data Analysis with SQL, Tableau: 
-- Link to dashboard: https://public.tableau.com/app/profile/sean6667/viz/COVID-19DataExplorationdashboard/ISACOUNTRYSAFETOTRAVELTO

-- What could stakeholders want from the COVID-19 dataset? Let's try to ask questions and answer them.
-- 1) Is the COVID situation getting better or worse in a certain country? How does a country fare compared to the others? 
-- 2) Which countries can I safely travel to?
-- To answer these questions, I wrote 3 queries and showed the results in Tableau Public.

-- Data cleaning
UPDATE covid19.covid
	SET reproduction_rate = 0
    WHERE reproduction_rate<0;

-- Query 1:
-- Pit country against continent averages
-- Show deaths per 100 cases, deaths per 100 persons, and reproduction rate (R0)

WITH continent_averages(date, location, r0, dpc, dpm) AS
(
	SELECT date, location,
    AVG(reproduction_rate) OVER (PARTITION BY continent,date),
    AVG(total_deaths_per_million/total_cases_per_million) OVER (PARTITION BY continent,date),
    AVG(total_deaths_per_million) OVER (PARTITION BY continent,date)
    FROM covid19.covid
    WHERE date > (SELECT MAX(date) - INTERVAL 6 MONTH FROM covid19.covid) -- Last 6 months
		AND continent NOT LIKE ''
    ORDER BY date
)
SELECT c.date, c.continent, c.location,
c.reproduction_rate as Country_R0, 
ROUND(a.r0,2) as Avg_Continent_R0,
ROUND(c.total_deaths_per_million/c.total_cases_per_million*100,2) as Country_DeathPer100Case, 
ROUND(a.dpc/100,2) as Avg_Continent_DeathPerCase,
ROUND(c.total_deaths_per_million/10000,4) as Country_DeathPer100People, 
ROUND(a.dpm/10000,4) as Avg_Continent_DeathPer100People
    FROM covid19.covid c
    LEFT JOIN continent_averages a 
    ON c.location = a.location AND c.date = a.date
    WHERE continent not like '' 
		AND c.date > (SELECT MAX(date) - INTERVAL 6 MONTH FROM covid19.covid) -- Last 6 months
        AND c.total_cases_per_million IS NOT NULL
    GROUP BY date, c.location
    ORDER BY date, c.continent, c.location
;

-- Query 2:
-- Average the monthly new cases and reproduction rate, and show the trend for the last 6 months.

SELECT YEAR(date) as Year, MONTH(date) as Month, WEEK(date) as Week, location, 
	ROUND(AVG(reproduction_rate),3) as r0,
	ROUND(SUM(new_cases_per_million)/1000,2) as nc
FROM covid19.covid
WHERE total_cases>0
	AND (continent NOT LIKE ''  OR location LIKE 'European Union') -- include the EU for ease of interpretation
	AND date > (SELECT MAX(date) - INTERVAL 6 MONTH FROM covid19.covid) -- Last 6 months
GROUP BY Week, Location
ORDER BY 1,2,3,4
;

-- Query 3: 
-- Proportion of population vaccinated and % of total population infected.
-- The idea is that the greater these proportions, the safer you will be in these countries.
-- For aesthetic reasons I decided not to show % of total population infected in the dashboard.
-- Some data shows >100% population vaccinated, in which case I relabelled the proportion as 99.99% instead.

SELECT location,
	ROUND(MAX(total_cases_per_million)/1000000,4) as total_infected,
	ROUND(MAX(CASE 
			WHEN people_fully_vaccinated_per_hundred>=100 THEN 99.99 
			ELSE people_fully_vaccinated_per_hundred END
		)/100, 4) as vaccination_rate
FROM covid19.covid
WHERE date > (SELECT MAX(date) - INTERVAL 12 MONTH FROM covid19.covid)
GROUP BY location
;
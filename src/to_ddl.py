from typing import NamedTuple, List
import csv
import pandas as pd

def init_tables(output_sql_file):
    """
    initialize the tables
    """
    with open(output_sql_file, 'w') as outfile:
        outfile.write(f"CREATE TABLE MonitorStation (CentroidLongitude DECIMAL, CentroidLatitude DECIMAL, Year INTEGER, AverageTemperature DECIMAL, PRIMARY KEY (CentroidLongitude, CentroidLatitude, Year));\n")
        outfile.write(f"CREATE TABLE Bee ( State VARCHAR(255), Year INTEGER, MaxColony INTEGER, LostColony INTEGER, PercentLost DECIMAL, Colony INTEGER, AddColony INTEGER, PercentRenovated DECIMAL, PercentLostByDisease DECIMAL, PRIMARY KEY (State, Year));\n")
        outfile.write(f"CREATE TABLE Detect ( CentroidLongitude DECIMAL, CentroidLatitude DECIMAL, StationYear INTEGER, BeeState VARCHAR(255), BeeYear INTEGER, PRIMARY KEY (CentroidLongitude, CentroidLatitude, StationYear, BeeState, BeeYear), FOREIGN KEY (BeeState, BeeYear) REFERENCES Bee(State, Year), FOREIGN KEY (CentroidLongitude, CentroidLatitude, StationYear) REFERENCES MonitorStation(CentroidLongitude, CentroidLatitude, Year));\n")
        outfile.write(f"CREATE ASSERTION totalBee CHECK (NOT EXITS ((SELECT State, Year FROM Bee) EXCEPT (SELECT BeeState, BeeYear FROM Detect)));\n")
        outfile.write(f"CREATE TABLE GasConditions ( Name VARCHAR(255), State VARCHAR(255), Year INTEGER, MeanValue DECIMAL, AverageAQI DECIMAL, PRIMARY KEY (Name, State, Year));\n")
        outfile.write(f"CREATE TABLE Influence ( GasPollutantsYearAffected INTEGER, GasPollutantsStateAffected VARCHAR(255), BeeState VARCHAR(255), BeeYear INTEGER, GasPollutantsName VARCHAR(255), PRIMARY KEY (GasPollutantsYearAffected, GasPollutantsStateAffected, BeeState, BeeYear, GasPollutantsName), FOREIGN KEY (BeeState, BeeYear) REFERENCES Bee(State, Year), FOREIGN KEY (GasPollutantsYearAffected, GasPollutantsStateAffected, GasPollutantsName) REFERENCES GasConditions(Year, State, Name));\n")
        outfile.write(f"CREATE TABLE RiskFactors ( State VARCHAR(255), Year INTEGER, Name VARCHAR(255), PRIMARY KEY (State, Year)); \n")        
        outfile.write(f"CREATE TABLE Monitor ( CentroidLongitude DECIMAL, CentroidLatitude DECIMAL, StationYear INTEGER, RiskFactorsReportedYear INTEGER, RiskFactorsReportedState VARCHAR(255), PRIMARY KEY (CentroidLongitude, CentroidLatitude, StationYear, RiskFactorsReportedYear, RiskFactorsReportedState), FOREIGN KEY (RiskFactorsReportedYear, RiskFactorsReportedState) REFERENCES RiskFactors(Year, State), FOREIGN KEY (CentroidLongitude, CentroidLatitude, StationYear) REFERENCES MonitorStation(CentroidLongitude, CentroidLatitude, Year));\n")
        outfile.write(f"CREATE TABLE Kill ( BeeState VARCHAR(255), BeeYear INTEGER, RiskFactorsReportedYear INTEGER, RiskFactorsReportedState VARCHAR(255), PRIMARY KEY (BeeState, BeeYear, RiskFactorsReportedYear, RiskFactorsReportedState), FOREIGN KEY (BeeState, BeeYear) REFERENCES Bee(State, Year), FOREIGN KEY (RiskFactorsReportedYear, RiskFactorsReportedState) REFERENCES RiskFactors(Year, State));\n")
        outfile.write(f"CREATE TABLE Parasite ( Year INTEGER, State VARCHAR(255), PercentAffected DECIMAL, PRIMARY KEY (Year, State), FOREIGN KEY (Year, State) REFERENCES RiskFactors(Year, State));\n")
        outfile.write(f"CREATE TABLE Pesticide ( Year INTEGER, State VARCHAR(255), LowEstimate DECIMAL, HighEstimate DECIMAL, PRIMARY KEY (Year, State), FOREIGN KEY (Year, State) REFERENCES RiskFactors(Year, State));\n")
        return True

def create_sql_MonitorStation(input_csv_file, output_sql_file):
    """
    insert processed data into the MonitorStation table 
    """
    try:
        with open(input_csv_file, 'r', newline='') as csvfile, open(output_sql_file, 'a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)
            stationcheck = set()
            
            for row in reader:
                centroid_longitude = float(row[4])
                centroid_latitude = float(row[5])
                year = int(row[1])
                average_temperature = float(row[3])
                
                station_key = (centroid_longitude, centroid_latitude, year)
                
                if station_key not in stationcheck:
                    stationcheck.add(station_key)
                    statement = f"INSERT INTO MonitorStation (CentroidLongitude, CentroidLatitude, Year, AverageTemperature) VALUES ({centroid_longitude}, {centroid_latitude}, {year}, {average_temperature});\n"
                    statement = outfile.write(statement)
            return True 
    except:
        return False


def create_sql_Bee(input_csv_file3, output_sql_file):
    """
    insert processed data into the Bee table 
    """
    try:
        with open(input_csv_file3) as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header
            bee_check = []
            
            for row in reader:
                State = row[1].replace('"', "'")
                Year = row[2]
                numColony = row[3]
                MaxColony = row[4]
                LostColony = row[5]
                pctLost = row[6]
                AddColony = row[7]
                pctRenovated = row[9]
                pctlostbydisease = row[11]
                
                if (State, Year) not in bee_check:
                    bee_check.append((State, Year))
                    statement = f"INSERT INTO Bee (State, Year, Colony, MaxColony, LostColony, PercentLost, AddColony, PercentRenovated, PercentLostByDisease) VALUES ('{State}', {Year}, {numColony}, {MaxColony}, {LostColony}, {pctLost}, {AddColony}, {pctRenovated}, {pctlostbydisease});\n"
                    outfile.write(statement)
            return True
    except:
        return False
            

def create_sql_detect(monitor_csv_file, bee_csv_file, output_sql_file):
    """
    insert processed data into the Detect table 
    """
    monitor_data = []
    bee_data = []
    helper_1 = []
    helper_2 = []
    
    # Read MonitorStation data
    try:
        with open(monitor_csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                monitor_data.append({
                    'CentroidLongitude': row['centroid_lon'],
                    'CentroidLatitude': row['centroid_lat'],
                    'Year': row['year']
                })
    except:
        return False

    try:    
        # Read Bee data
        with open(bee_csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                bee_data.append({
                    'State': row['state'],
                    'Year': row['year']
                })
    except:
        return False
    
    try:
        # Write to output SQL file
        with open(output_sql_file, 'a') as sqlfile:
            for monitor in monitor_data:
                for bee in bee_data:
                    if ((monitor['Year'] == bee['Year']) & ((monitor["Year"], monitor["CentroidLongitude"], monitor["CentroidLatitude"]) not in helper_1) & ((bee["Year"], bee["State"]) not in helper_2)):
                        helper_1.append((monitor["Year"], monitor["CentroidLongitude"], monitor["CentroidLatitude"]))
                        helper_2.append((bee["Year"], bee["State"]))
                        statement = f"INSERT INTO Detect (CentroidLongitude, CentroidLatitude, StationYear, BeeState, BeeYear) VALUES ({monitor['CentroidLongitude']}, {monitor['CentroidLatitude']}, {monitor['Year']}, '{bee['State']}', {bee['Year']});\n"
                        sqlfile.write(statement)
            
            return True
    except:
        return False



def create_sql_GasConditions(input_csv_file4, output_sql_file):
    """
    insert processed data into the GasConditions table 
    """
    try:
        with open(input_csv_file4) as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)

            for row in reader:
                Name = row[3].replace("'", "''")
                State = row[2].replace("'", "''")
                Year = row[1]
                MeanValue = row[5]
                AverageAQI = row[4]
                
                statement = f"INSERT INTO GasConditions (Name, State, Year, MeanValue, AverageAQI) VALUES ('{Name}', '{State}', {Year}, {MeanValue}, {AverageAQI});\n"
                outfile.write(statement)
            
            return True
    except Exception as e:
        return False



def create_sql_Influence(gas_csv_file, bee_csv_file, output_sql_file):
    """
    insert processed data into the Influence table 
    """
    bee_data = []
    try:
        with open(bee_csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                bee_data.append((row[1], row[2]))
    except:
        return False
            
    try:
        with open(gas_csv_file, 'r') as gasfile, open(output_sql_file, mode='a') as outfile:
            gas_reader = csv.reader(gasfile)
            next(gas_reader)
            checker = []
            for row in gas_reader:
                gas_year = row[1]
                gas_state = row[2].replace("'", "''")
                pollutant = row[3].replace("'", "''")
                if [gas_year,gas_state,pollutant] not in checker:
                    checker.append([gas_year, gas_state,pollutant])
                    for bee_state, bee_year in bee_data:
                        if (gas_year == bee_year) & (gas_state == bee_state):
                            statement = f"INSERT INTO Influence (GasPollutantsYearAffected, GasPollutantsStateAffected, BeeState, BeeYear, GasPollutantsName) VALUES ({gas_year}, '{gas_state}', '{bee_state}', {bee_year}, '{pollutant}');\n"
                            outfile.write(statement)
            return True
    except:
        return False 


def create_sql_RiskFactors(input_csv_file, output_sql_file):
    """
    insert processed data into the RiskFactors table 
    """
    try:
        with open(input_csv_file, 'r') as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)
            risk_factors_check = []

            for row in reader:
                state = row[3].replace("'", "''")
                year = row[2]
                name = row[1].replace("'", "''")
                identifier = (state, year)
                
                if identifier not in risk_factors_check:
                    risk_factors_check.append(identifier)
                    statement = f"INSERT INTO RiskFactors (State, Year, Name) VALUES ('{state}', {year}, '{name}');\n"
                    outfile.write(statement)
            return True
    except:
        return False


def create_sql_Monitor(monitor_csv_file, risk_factors_csv_file, output_sql_file):
    """
    insert processed data into the Monitor table 
    """
    monitor_data = []
    try:
        with open(monitor_csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                monitor_data.append((row[4], row[5], row[1],row[2]))  # (CentroidLongitude, CentroidLatitude, Year)
    except:
        return False
    
    try:    
        with open(risk_factors_csv_file, 'r') as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)
            checker = []
            for row in reader:
                risk_state = row[3].strip().replace("'", "''")
                risk_year = row[2].strip()
                if [risk_state,risk_year] not in checker:
                    checker.append([risk_state,risk_year])
                    for centroid_long, centroid_lat, year,state in monitor_data:
                        if (year == risk_year) & (state == risk_state) :
                            statement = f"INSERT INTO Monitor (CentroidLongitude, CentroidLatitude, StationYear, RiskFactorsReportedYear, RiskFactorsReportedState) VALUES ({centroid_long}, {centroid_lat}, {year}, {risk_year}, '{risk_state}');\n"
                            outfile.write(statement)
            return True
    except:
        return False


def create_sql_Kill(bee_csv_file, risk_factors_csv_file, output_sql_file):
    """
    insert processed data into the Kill table 
    """
    # Bee data
    bee_data = []
    try:
        with open(bee_csv_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                bee_state = row[1].replace("'", "''")
                bee_year = row[2]
                bee_data.append((bee_state, bee_year))
    except:
        return False
    
    # RiskFactors data
    try:
        with open(risk_factors_csv_file, 'r') as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)
            checker = []
            for row in reader:
                risk_state = row[2].strip().replace("'", "''")
                risk_year = row[1].strip()
                if [risk_state,risk_year] not in checker:
                    checker.append([risk_state,risk_year])
                    # Check for matches with Bee data
                    for bee_state, bee_year in bee_data:
                        if (bee_year == risk_year) and (bee_state == risk_state):
                            statement = f"INSERT INTO Kill (BeeState, BeeYear, RiskFactorsReportedYear, RiskFactorsReportedState) VALUES ('{bee_state}', {bee_year}, {risk_year}, '{risk_state}');\n"
                            outfile.write(statement)
            return True
    except:
        return False


def create_sql_Parasite(input_csv_file, output_sql_file):
    """
    insert processed data into the Parasite table 
    """
    try:
        with open(input_csv_file, 'r') as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)
            parasite_check = []

            for row in reader:
                year = row[2]
                state = row[1].replace("'", "''")
                percentAffected = row[-2]

                identifier = (year, state)
                
                if identifier not in parasite_check:
                    parasite_check.append(identifier)
                    statement = f"INSERT INTO Parasite (Year, State, PercentAffected) VALUES ({year}, '{state}', {percentAffected});\n"
                    outfile.write(statement)
            return True
    except:
        return False


def create_sql_Pesticide(input_csv_file, output_sql_file):
    """
    insert processed data into the Pesticide table 
    """
    try:
        with open(input_csv_file, 'r') as csvfile, open(output_sql_file, mode='a') as outfile:
            reader = csv.reader(csvfile)
            next(reader)
            pesticide_check = []

            for row in reader:
                year = row[2]
                state = row[5].replace("'", "''")
                lowEstimate = row[3]
                highEstimate = row[4]

                if (year, state) not in pesticide_check:
                    pesticide_check.append((year, state))
                    statement = f"INSERT INTO Pesticide (Year, State, LowEstimate, HighEstimate) VALUES ({year}, '{state}', {lowEstimate}, {highEstimate});\n"
                    outfile.write(statement)
            return True
    except:
        return False
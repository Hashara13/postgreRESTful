from models import AirQualityIndex, TrafficDensity
from app import db
import numpy as np

def air_quality_index(sensor_readings):
    pm25 = np.mean([r.value for r in sensor_readings if r.sensor.sensor_type == 'PM2.5'])
    o3 = np.mean([r.value for r in sensor_readings if r.sensor.sensor_type == 'O3'])
    
    aqi = (pm25 * 10 + o3 * 5) / 15 
    
    return min(max(aqi, 0), 500) 

def update_air_quality_index(location, sensor_readings):
    aqi = air_quality_index(sensor_readings)
    new_aqi = AirQualityIndex(location=location, aqi=aqi)
    db.session.add(new_aqi)
    db.session.commit()

def traffic_density(sensor_readings):
    vehicle_count = sum([r.value for r in sensor_readings if r.sensor.sensor_type == 'vehicle_counter'])
    road_capacity = 1000 
    
    density = min(vehicle_count / road_capacity, 1)  
    
    return density

def update_traffic_density(location, sensor_readings):
    density = traffic_density(sensor_readings)
    new_density = TrafficDensity(location=location, density=density)
    db.session.add(new_density)
    db.session.commit()
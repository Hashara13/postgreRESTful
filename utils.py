from models import AirQualityIndex, TrafficData, NoiseLevel, WaterQuality, EnergyConsumption, WeatherData
from app import db
import numpy as np
from scipy import stats
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

def calc_aqi(readings):
    pm25 = np.mean([r.value for r in readings if r.sensor.sensor_type == 'PM2.5'])
    pm10 = np.mean([r.value for r in readings if r.sensor.sensor_type == 'PM10'])
    o3 = np.mean([r.value for r in readings if r.sensor.sensor_type == 'O3'])
    co = np.mean([r.value for r in readings if r.sensor.sensor_type == 'CO'])
    no2 = np.mean([r.value for r in readings if r.sensor.sensor_type == 'NO2'])
    so2 = np.mean([r.value for r in readings if r.sensor.sensor_type == 'SO2'])
    
    aqi = (pm25 * 5 + pm10 * 5 + o3 * 5 + co * 4 + no2 * 3 + so2 * 3) / 25
    
    return min(max(aqi, 0), 500), pm25, pm10, o3, co, no2, so2

def update_aqi(loc, readings):
    aqi, pm25, pm10, o3, co, no2, so2 = calc_aqi(readings)
    new_aqi = AirQualityIndex(location=loc, aqi=aqi, pm25=pm25, pm10=pm10, o3=o3, co=co, no2=no2, so2=so2)
    db.session.add(new_aqi)
    db.session.commit()

def calc_traffic(readings):
    vc = sum([r.value for r in readings if r.sensor.sensor_type == 'vehicle_counter'])
    speeds = [r.value for r in readings if r.sensor.sensor_type == 'vehicle_speed']
    avg_speed = np.mean(speeds) if speeds else 0
    
    road_capacity = 1000
    density = min(vc / road_capacity, 1)
    
    congestion_level = 1 - (avg_speed / 60)  # Assuming 60 km/h is free flow
    
    return density, vc, avg_speed, congestion_level

def update_traffic(loc, readings):
    density, vc, avg_speed, congestion = calc_traffic(readings)
    new_traffic = TrafficData(location=loc, density=density, vehicle_count=vc, average_speed=avg_speed, congestion_level=congestion)
    db.session.add(new_traffic)
    db.session.commit()

def calc_noise(readings):
    noise_readings = [r.value for r in readings if r.sensor.sensor_type == 'noise']
    frequency_readings = [r.value for r in readings if r.sensor.sensor_type == 'noise_frequency']
    avg_decibel = np.mean(noise_readings)
    avg_frequency = np.mean(frequency_readings) if frequency_readings else 0
    return avg_decibel, avg_frequency

def update_noise(loc, readings):
    decibel, frequency = calc_noise(readings)
    new_noise = NoiseLevel(location=loc, decibel=decibel, frequency=frequency)
    db.session.add(new_noise)
    db.session.commit()

def calc_water(readings):
    ph = np.mean([r.value for r in readings if r.sensor.sensor_type == 'pH'])
    turbidity = np.mean([r.value for r in readings if r.sensor.sensor_type == 'turbidity'])
    do = np.mean([r.value for r in readings if r.sensor.sensor_type == 'dissolved_oxygen'])
    conductivity = np.mean([r.value for r in readings if r.sensor.sensor_type == 'conductivity'])
    temperature = np.mean([r.value for r in readings if r.sensor.sensor_type == 'water_temperature'])
    return ph, turbidity, do, conductivity, temperature

def update_water(loc, readings):
    ph, turbidity, do, conductivity, temperature = calc_water(readings)
    new_water = WaterQuality(location=loc, ph=ph, turbidity=turbidity, dissolved_oxygen=do, conductivity=conductivity, temperature=temperature)
    db.session.add(new_water)
    db.session.commit()

def calc_energy(readings):
    cons = sum([r.value for r in readings if r.sensor.sensor_type == 'energy_consumption'])
    renew = sum([r.value for r in readings if r.sensor.sensor_type == 'renewable_energy'])
    total = cons + renew
    renew_pct = (renew / total) * 100 if total > 0 else 0
    peak = max([r.value for r in readings if r.sensor.sensor_type == 'energy_consumption'])
    freq = np.mean([r.value for r in readings if r.sensor.sensor_type == 'grid_frequency'])
    return cons, renew_pct, peak, freq

def update_energy(loc, readings):
    cons, renew_pct, peak, freq = calc_energy(readings)
    new_energy = EnergyConsumption(location=loc, consumption=cons, renewable_percentage=renew_pct, peak_demand=peak, grid_frequency=freq)
    db.session.add(new_energy)
    db.session.commit()

def calc_weather(readings):
    temp = np.mean([r.value for r in readings if r.sensor.sensor_type == 'temperature'])
    humidity = np.mean([r.value for r in readings if r.sensor.sensor_type == 'humidity'])
    wind_speed = np.mean([r.value for r in readings if r.sensor.sensor_type == 'wind_speed'])
    wind_dir = np.mean([r.value for r in readings if r.sensor.sensor_type == 'wind_direction'])
    precip = sum([r.value for r in readings if r.sensor.sensor_type == 'precipitation'])
    return temp, humidity, wind_speed, wind_dir, precip

def update_weather(loc, readings):
    temp, humidity, wind_speed, wind_dir, precip = calc_weather(readings)
    new_weather = WeatherData(location=loc, temperature=temp, humidity=humidity, wind_speed=wind_speed, wind_direction=wind_dir, precipitation=precip)
    db.session.add(new_weather)
    db.session.commit()

def detect_anomalies(readings, sensor_type):
    values = [r.value for r in readings if r.sensor.sensor_type == sensor_type]
    z_scores = stats.zscore(values)
    anomalies = np.abs(z_scores) > 3
    return [values[i] for i in range(len(values)) if anomalies[i]]

def calc_corr(readings, type1, type2):
    values1 = [r.value for r in readings if r.sensor.sensor_type == type1]
    values2 = [r.value for r in readings if r.sensor.sensor_type == type2]
    if len(values1) == len(values2) and len(values1) > 1:
        return stats.pearsonr(values1, values2)[0]
    return None

def gen_report(loc):
    aqi = AirQualityIndex.query.filter_by(location=loc).order_by(AirQualityIndex.timestamp.desc()).first()
    traffic = TrafficData.query.filter_by(location=loc).order_by(TrafficData.timestamp.desc()).first()
    noise = NoiseLevel.query.filter_by(location=loc).order_by(NoiseLevel.timestamp.desc()).first()
    water = WaterQuality.query.filter_by(location=loc).order_by(WaterQuality.timestamp.desc()).first()
    energy = EnergyConsumption.query.filter_by(location=loc).order_by(EnergyConsumption.timestamp.desc()).first()
    weather = WeatherData.query.filter_by(location=loc).order_by(WeatherData.timestamp.desc()).first()

    report = f"""
    Daily Report for {loc} - {datetime.now().strftime('%Y-%m-%d')}
    
    Air Quality Index: {aqi.aqi:.2f}
    - PM2.5: {aqi.pm25:.2f}
    - PM10: {aqi.pm10:.2f}
    - O3: {aqi.o3:.2f}
    - CO: {aqi.co:.2f}
    - NO2: {aqi.no2:.2f}
    - SO2: {aqi.so2:.2f}
    
    Traffic Data:
    - Density: {traffic.density:.2f}
    - Vehicle Count: {traffic.vehicle_count}
    - Average Speed: {traffic.average_speed:.2f} km/h
    - Congestion Level: {traffic.congestion_level:.2f}
    
    Noise Level:
    - Decibel: {noise.decibel:.2f} dB
    - Frequency: {noise.frequency:.2f} Hz
    
    Water Quality:
    - pH: {water.ph:.2f}
    - Turbidity: {water.turbidity:.2f} NTU
    - Dissolved Oxygen: {water.dissolved_oxygen:.2f} mg/L
    - Conductivity: {water.conductivity:.2f} µS/cm
    - Temperature: {water.temperature:.2f} °C
    
    Energy Consumption:
    - Total Consumption: {energy.consumption:.2f} kWh
    - Renewable Percentage: {energy.renewable_percentage:.2f}%
    - Peak Demand: {energy.peak_demand:.2f} kW
    - Grid Frequency: {energy.grid_frequency:.2f} Hz
    
    Weather Data:
    - Temperature: {weather.temperature:.2f} °C
    - Humidity: {weather.humidity:.2f}%
    - Wind Speed: {weather.wind_speed:.2f} m/s
    - Wind Direction: {weather.wind_direction:.2f}°
    - Precipitation: {weather.precipitation:.2f} mm
    """

    return report

def pdf_report(loc):
    aqi = AirQualityIndex.query.filter_by(location=loc).order_by(AirQualityIndex.timestamp.desc()).first()
    traffic = TrafficData.query.filter_by(location=loc).order_by(TrafficData.timestamp.desc()).first()
    noise = NoiseLevel.query.filter_by(location=loc).order_by(NoiseLevel.timestamp.desc()).first()
    water = WaterQuality.query.filter_by(location=loc).order_by(WaterQuality.timestamp.desc()).first()
    energy = EnergyConsumption.query.filter_by(location=loc).order_by(EnergyConsumption.timestamp.desc()).first()
    weather = WeatherData.query.filter_by(location=loc).order_by(WeatherData.timestamp.desc()).first()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"Daily Report for {loc} - {datetime.now().strftime('%Y-%m-%d')}", styles['Title'])
    elements.append(title)

    data = [
        ['Air Quality Index', f"{aqi.aqi:.2f}"],
        ['PM2.5', f"{aqi.pm25:.2f}"],
        ['PM10', f"{aqi.pm10:.2f}"],
        ['O3', f"{aqi.o3:.2f}"],
        ['CO', f"{aqi.co:.2f}"],
        ['NO2', f"{aqi.no2:.2f}"],
        ['SO2', f"{aqi.so2:.2f}"],
        ['Traffic Density', f"{traffic.density:.2f}"],
        ['Vehicle Count', f"{traffic.vehicle_count}"],
        ['Average Speed', f"{traffic.average_speed:.2f} km/h"],
        ['Congestion Level', f"{traffic.congestion_level:.2f}"],
        ['Noise Level', f"{noise.decibel:.2f} dB"],
        ['Noise Frequency', f"{noise.frequency:.2f} Hz"],
        ['Water pH', f"{water.ph:.2f}"],
        ['Water Turbidity', f"{water.turbidity:.2f} NTU"],
        ['Dissolved Oxygen', f"{water.dissolved_oxygen:.2f} mg/L"],
        ['Water Conductivity', f"{water.conductivity:.2f} µS/cm"],
        ['Water Temperature', f"{water.temperature:.2f} °C"],
        ['Energy Consumption', f"{energy.consumption:.2f} kWh"],
        ['Renewable Energy', f"{energy.renewable_percentage:.2f}%"],
        ['Peak Energy Demand', f"{energy.peak_demand:.2f} kW"],
        ['Grid Frequency', f"{energy.grid_frequency:.2f} Hz"],
        ['Air Temperature', f"{weather.temperature:.2f} °C"],
        ['Humidity', f"{weather.humidity:.2f}%"],
        ['Wind Speed', f"{weather.wind_speed:.2f} m/s"],
        ['Wind Direction', f"{weather.wind_direction:.2f}°"],
        ['Precipitation', f"{weather.precipitation:.2f} mm"]
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer
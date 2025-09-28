#!/usr/bin/env python3
"""
Procesador de datos del ciclo menstrual desde Apple Health
y generador de calendario iCal para compartir
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pandas as pd
import uuid

class MenstrualCycleProcessor:
    def __init__(self):
        self.periods = []
        self.cycle_data = []
        
    def parse_health_data(self, xml_file_path):
        """
        Parsea el archivo XML exportado de Apple Health
        y extrae los datos del ciclo menstrual
        """
        print("📱 Procesando datos de Apple Health...")
        
        # Cargar XML
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Buscar registros de menstruación
        menstrual_flow_records = []
        
        for record in root.findall('.//Record'):
            record_type = record.get('type')
            
            # Buscar datos de flujo menstrual
            if record_type == 'HKCategoryTypeIdentifierMenstrualFlow':
                date_str = record.get('startDate')
                value = record.get('value')
                
                # Convertir fecha
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                
                menstrual_flow_records.append({
                    'date': date,
                    'flow_intensity': value,
                    'raw_date': date_str
                })
        
        print(f"✅ Encontrados {len(menstrual_flow_records)} registros de flujo menstrual")
        
        # Convertir a DataFrame para facilitar el análisis
        df = pd.DataFrame(menstrual_flow_records)
        if not df.empty:
            df = df.sort_values('date')
            self.periods = df
            
        return menstrual_flow_records
    
    def identify_periods(self):
        """
        Identifica períodos menstruales agrupando días consecutivos
        """
        if self.periods.empty:
            return []
        
        print("🩸 Identificando períodos menstruales...")
        
        periods = []
        current_period = []
        
        sorted_dates = self.periods['date'].sort_values()
        
        for i, date in enumerate(sorted_dates):
            if i == 0:
                current_period = [date]
            else:
                prev_date = sorted_dates.iloc[i-1]
                # Si hay más de 2 días de diferencia, es un nuevo período
                if (date - prev_date).days > 2:
                    if current_period:
                        periods.append({
                            'start': min(current_period),
                            'end': max(current_period),
                            'duration': len(current_period)
                        })
                    current_period = [date]
                else:
                    current_period.append(date)
        
        # Añadir el último período
        if current_period:
            periods.append({
                'start': min(current_period),
                'end': max(current_period),
                'duration': len(current_period)
            })
        
        print(f"✅ Identificados {len(periods)} períodos")
        return periods
    
    def calculate_cycle_phases(self, periods):
        """
        Calcula las fases del ciclo basándose en los períodos identificados
        """
        print("📊 Calculando fases del ciclo...")
        
        cycle_phases = []
        
        for i in range(len(periods) - 1):
            current_period = periods[i]
            next_period = periods[i + 1]
            
            # Calcular duración del ciclo
            cycle_length = (next_period['start'] - current_period['start']).days
            
            # Estimar ovulación (14 días antes del siguiente período)
            ovulation_date = next_period['start'] - timedelta(days=14)
            fertile_window_start = ovulation_date - timedelta(days=5)
            fertile_window_end = ovulation_date + timedelta(days=1)
            
            # Semana de alerta antes del período
            pms_alert_start = next_period['start'] - timedelta(days=7)
            
            cycle_phases.append({
                'cycle_number': i + 1,
                'period_start': current_period['start'],
                'period_end': current_period['end'],
                'period_duration': current_period['duration'],
                'cycle_length': cycle_length,
                'ovulation_date': ovulation_date,
                'fertile_window_start': fertile_window_start,
                'fertile_window_end': fertile_window_end,
                'pms_alert_date': pms_alert_start,
                'next_period_date': next_period['start']
            })
        
        self.cycle_data = cycle_phases
        print(f"✅ Calculadas {len(cycle_phases)} fases de ciclo")
        return cycle_phases
    
    def generate_ical_calendar(self, cycle_phases, months_future=6):
        """
        Genera un calendario iCal con todos los eventos del ciclo
        """
        print("📅 Generando calendario iCal...")
        
        cal = Calendar()
        cal.add('prodid', '-//Ciclo Menstrual App//ES')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', 'Ciclo Menstrual')
        cal.add('x-wr-caldesc', 'Calendario del ciclo menstrual compartido')
        
        # Añadir eventos históricos
        for cycle in cycle_phases:
            # Evento: Período menstrual
            period_event = Event()
            period_event.add('uid', str(uuid.uuid4()))
            period_event.add('dtstart', cycle['period_start'])
            period_event.add('dtend', cycle['period_end'] + timedelta(days=1))
            period_event.add('summary', '🩸 Menstruación')
            period_event.add('description', f"Duración: {cycle['period_duration']} días")
            period_event.add('categories', 'MENSTRUATION')
            cal.add_component(period_event)
            
            # Evento: Ovulación
            ovulation_event = Event()
            ovulation_event.add('uid', str(uuid.uuid4()))
            ovulation_event.add('dtstart', cycle['ovulation_date'])
            ovulation_event.add('summary', '🥚 Ovulación (estimada)')
            ovulation_event.add('description', 'Día de ovulación estimado')
            ovulation_event.add('categories', 'OVULATION')
            cal.add_component(ovulation_event)
            
            # Evento: Ventana fértil
            fertile_event = Event()
            fertile_event.add('uid', str(uuid.uuid4()))
            fertile_event.add('dtstart', cycle['fertile_window_start'])
            fertile_event.add('dtend', cycle['fertile_window_end'] + timedelta(days=1))
            fertile_event.add('summary', '💚 Ventana fértil')
            fertile_event.add('description', 'Período de mayor fertilidad')
            fertile_event.add('categories', 'FERTILITY')
            cal.add_component(fertile_event)
            
            # Evento: Alerta pre-menstrual
            pms_event = Event()
            pms_event.add('uid', str(uuid.uuid4()))
            pms_event.add('dtstart', cycle['pms_alert_date'])
            pms_event.add('summary', '⚠️ Semana pre-menstrual')
            pms_event.add('description', 'El período comenzará aproximadamente en una semana')
            pms_event.add('categories', 'PMS_ALERT')
            cal.add_component(pms_event)
        
        # Proyectar eventos futuros basándose en el ciclo promedio
        if cycle_phases:
            avg_cycle_length = sum(c['cycle_length'] for c in cycle_phases) / len(cycle_phases)
            last_period = max(cycle_phases, key=lambda x: x['period_start'])
            
            print(f"📈 Proyectando {months_future} meses futuros (ciclo promedio: {avg_cycle_length:.1f} días)")
            
            current_date = last_period['next_period_date']
            future_cycles = 0
            
            while future_cycles < months_future * 30 / avg_cycle_length:
                # Período futuro
                period_start = current_date
                period_end = current_date + timedelta(days=last_period['period_duration'])
                
                future_period = Event()
                future_period.add('uid', str(uuid.uuid4()))
                future_period.add('dtstart', period_start)
                future_period.add('dtend', period_end + timedelta(days=1))
                future_period.add('summary', '🩸 Menstruación (predicción)')
                future_period.add('description', f"Predicción basada en ciclo promedio de {avg_cycle_length:.1f} días")
                future_period.add('categories', 'MENSTRUATION_PREDICTED')
                cal.add_component(future_period)
                
                # Ovulación futura
                ovulation_future = period_start - timedelta(days=14)
                if ovulation_future > datetime.now().date():
                    ovul_event = Event()
                    ovul_event.add('uid', str(uuid.uuid4()))
                    ovul_event.add('dtstart', ovulation_future)
                    ovul_event.add('summary', '🥚 Ovulación (predicción)')
                    ovul_event.add('description', 'Predicción de ovulación')
                    ovul_event.add('categories', 'OVULATION_PREDICTED')
                    cal.add_component(ovul_event)
                
                # Alerta pre-menstrual futura
                pms_future = period_start - timedelta(days=7)
                if pms_future > datetime.now().date():
                    pms_future_event = Event()
                    pms_future_event.add('uid', str(uuid.uuid4()))
                    pms_future_event.add('dtstart', pms_future)
                    pms_future_event.add('summary', '⚠️ Semana pre-menstrual (predicción)')
                    pms_future_event.add('description', 'El período comenzará aproximadamente en una semana')
                    pms_future_event.add('categories', 'PMS_ALERT_PREDICTED')
                    cal.add_component(pms_future_event)
                
                current_date += timedelta(days=int(avg_cycle_length))
                future_cycles += 1
        
        return cal
    
    def save_calendar(self, calendar, filename='ciclo_menstrual.ics'):
        """
        Guarda el calendario en un archivo iCal
        """
        with open(filename, 'wb') as f:
            f.write(calendar.to_ical())
        
        print(f"💾 Calendario guardado como: {filename}")
        return filename
    
    def print_summary(self):
        """
        Muestra un resumen de los datos procesados
        """
        if not self.cycle_data:
            print("❌ No hay datos de ciclo para mostrar")
            return
        
        print("\n" + "="*50)
        print("📊 RESUMEN DEL CICLO MENSTRUAL")
        print("="*50)
        
        avg_cycle = sum(c['cycle_length'] for c in self.cycle_data) / len(self.cycle_data)
        avg_period = sum(c['period_duration'] for c in self.cycle_data) / len(self.cycle_data)
        
        print(f"📅 Total de ciclos analizados: {len(self.cycle_data)}")
        print(f"⏱️  Duración promedio del ciclo: {avg_cycle:.1f} días")
        print(f"🩸 Duración promedio del período: {avg_period:.1f} días")
        
        if self.cycle_data:
            last_period = max(self.cycle_data, key=lambda x: x['period_start'])
            next_predicted = last_period['next_period_date'] + timedelta(days=int(avg_cycle))
            
            print(f"📍 Último período: {last_period['period_start']}")
            print(f"🔮 Próximo período estimado: {next_predicted}")


def main():
    """
    Función principal
    """
    print("🌸 PROCESADOR DE CICLO MENSTRUAL 🌸")
    print("=" * 50)
    
    # DIAGNÓSTICO: Ver dónde estamos y qué archivos hay
    import os
    print(f"📍 Directorio actual: {os.getcwd()}")
    print(f"📂 Archivos en directorio actual: {os.listdir('.')}")
    
    if os.path.exists('datos'):
        print(f"📂 Archivos en carpeta datos: {os.listdir('datos')}")
    else:
        print("❌ No existe la carpeta 'datos'")
    
    # Inicializar procesador
    processor = MenstrualCycleProcessor()
    
    # Usar la ruta por defecto o solicitar archivo XML
    xml_file = "datos/exportación.xml"  # Ruta por defecto
    
    print(f"🔍 Buscando archivo: {xml_file}")
    print(f"🔍 ¿Existe el archivo? {os.path.exists(xml_file)}")
    
    # Verificar si existe el archivo
    if not os.path.exists(xml_file):
        xml_file = input("📁 Ruta al archivo exportación.xml de Apple Health: ").strip()
    
    try:
        # Procesar datos
        processor.parse_health_data(xml_file)
        periods = processor.identify_periods()
        cycle_phases = processor.calculate_cycle_phases(periods)
        
        # Mostrar resumen
        processor.print_summary()
        
        # Generar calendario
        calendar = processor.generate_ical_calendar(cycle_phases)
        filename = processor.save_calendar(calendar)
        
        print(f"\n✅ ¡Proceso completado!")
        print(f"📧 Puedes enviar el archivo '{filename}' a tu chico")
        print(f"📱 Él puede importarlo en su calendario o suscribirse al enlace")
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo XML")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()

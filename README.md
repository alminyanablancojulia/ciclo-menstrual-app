# 🌸 Procesador de Ciclo Menstrual

Aplicación en Python que procesa datos del ciclo menstrual exportados desde Apple Health y genera un calendario iCal (.ics) para compartir.

## 📋 Características

- ✅ Procesa datos históricos de Apple Health
- ✅ Identifica períodos menstruales automáticamente
- ✅ Calcula fases del ciclo (ovulación, ventana fértil)
- ✅ Genera alertas pre-menstruales
- ✅ Predice ciclos futuros
- ✅ Exporta calendario iCal compatible con cualquier app de calendario

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
   git clone https://github.com/TU_USUARIO/ciclo-menstrual-app.git
   cd ciclo-menstrual-app

 python3 -m venv venv
   source venv/bin/activate
   pip install pandas icalendar
   📱 Uso

Exportar datos de Apple Health:

App Salud → Perfil → "Exportar todos los datos de salud"
Descomprimir el archivo ZIP
Colocar exportación.xml en la carpeta datos/


Ejecutar el programa:

bash   python ciclo_menstrual.py

Resultado:

Se genera ciclo_menstrual.ics
Importar en cualquier app de calendario



📊 Información del ciclo

Duración promedio del ciclo
Duración promedio del período
Predicciones de próximos períodos
Fechas de ovulación estimadas
Ventanas fértiles
Alertas pre-menstruales

🔒 Privacidad

Los datos de salud NO se suben al repositorio
Solo se incluye el código fuente
Cada usuario debe añadir sus propios datos

  
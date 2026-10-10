# SolarBI Pascual · Power BI, Grafana, Gobernanza de Datos, ETL e IoT

Repositorio del trabajo de consulta de **Inteligencia de Negocios — Grupo 01**, 
Institución Universitaria Pascual Bravo, semestre 2026-II.

El proyecto construye un flujo de datos para el monitoreo operativo de una planta 
solar simulada: datos crudos, limpieza y validación, carga en PostgreSQL, 
resumen diario y visualización en **Power BI** y **Grafana**.

> One governed dataset, two views: Grafana for real-time operations and Power BI for business decisions.

## Integrantes

| Nombre | Rol |
|---|---|
| Sebastian Cifuentes Moncada | Data engineer / ETL / PostgreSQL / Grafana |
| Josue Penagos Amaya | Data modeler / Power BI / documentación |

* Ajusten los roles según quien realmente hizo cada parte.

## Curso

- **Asignatura:** Inteligencia de Negocios  
- **Grupo:** 01  
- **Semestre:** 2026-II  
- **Docente:** Ramiro Grisales Montoya  
- **Proyecto:** SolarBI Pascual  

## Objetivo

Implementar un pipeline ETL idempotente que procese telemetría simulada de un 
inversor solar, aplique reglas de calidad, cargue los datos en PostgreSQL y 
permita analizarlos desde Power BI y Grafana.

## Tecnologías utilizadas

- Python 3
- Pandas
- PostgreSQL
- Power BI Desktop
- Grafana OSS
- Git y GitHub
- Variables de entorno con `.env`

## Estructura del repositorio

```text
solarbi-apellido1-apellido2/
├── README.md
├── .gitignore
├── docs/                  # PDF de la consulta y evidencias
├── data/
│   ├── bronze/            # Datos crudos simulados
│   └── silver/            # Datos limpios y validados
├── etl/
│   ├── simulador.py       # Genera datos crudos
│   ├── silver.py          # Limpieza y reglas de calidad
│   ├── gold.py            # Agregación diaria
│   ├── load_postgres.py   # Carga con UPSERT
│   ├── load_silver.py
│   ├── load_gold.py
│   └── run_etl.py         # Punto único de ejecución
├── sql/
│   ├── 01_schema.sql      # Creación de tablas
│   └── 02_upsert.sql      # Consultas UPSERT de referencia
├── powerbi/               # Archivo .pbix o proyecto .pbip
└── grafana/
    └── dashboard.json     # Dashboard exportado
```

## Reglas de calidad aplicadas

1. **Duplicados:** se conserva la primera lectura para cada combinación de `ts` y `dispositivo_id`.
2. **Datos faltantes:** se marcan las filas sin fecha o sin alguna medida principal.
3. **Rango físico válido:** se validan los valores de potencia, irradiancia y temperatura.
4. **Porcentaje de datos válidos:** se calcula como:

```text
% datos válidos = (lecturas válidas / lecturas totales) × 100
```

## Modelo de datos

- `silver.lectura_5min`: lecturas limpias cada 5 minutos.
- `dwh.fact_energia_dia`: resumen diario con energía y porcentaje de datos válidos.
- La energía por intervalo se calcula así:

```text
energia_kwh = p_ac_kw × (5 / 60)
```

## Cómo ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone [https://github.com/usuario/solarbi-apellido1-apellido2.git](https://github.com/usuario/solarbi-apellido1-apellido2.git)
cd solarbi-apellido1-apellido2
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz, basado en `.env.example`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=solarbi
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

> **Importante:** no subir el archivo `.env`, credenciales ni cadenas de conexión al repositorio.

### 5. Crear las tablas en PostgreSQL

Ejecutar en pgAdmin o psql:

```sql
-- Contenido de sql/01_schema.sql
```

### 6. Ejecutar el pipeline completo

Desde la raíz del proyecto:

```bash
python -m etl.run_etl
```

El comando ejecuta:

1. Generación o lectura de datos Bronze.
2. Limpieza y validación hacia Silver.
3. Agregación diaria hacia Gold.
4. Carga idempotente en PostgreSQL.

## Idempotencia

El pipeline puede ejecutarse varias veces sin duplicar registros.

```bash
python -m etl.run_etl
python -m etl.run_etl
```

Después de ambas ejecuciones, los conteos en PostgreSQL deben permanecer iguales:

```sql
SELECT COUNT(*) FROM silver.lectura_5min;
SELECT COUNT(*) FROM dwh.fact_energia_dia;
```

La carga usa `INSERT ... ON CONFLICT ... DO UPDATE`, por lo que si el registro ya existe se actualiza en lugar de duplicarse.

## Tableros

### Power BI

El tablero se conecta a PostgreSQL y presenta indicadores como:

- Energía generada.
- Yield.
- Performance Ratio.
- Ahorro.
- Disponibilidad.
- Alarmas.
- Porcentaje de datos válidos.

### Grafana

El tablero incluye:

- Serie de tiempo de potencia cada 5 minutos.
- Umbral o alerta cuando la potencia sea cero entre 9:00 y 15:00.
- Indicador tipo *stat* con la energía del día seleccionado.

El dashboard exportado se encuentra en:

```text
grafana/dashboard.json
```

## Automatización propuesta

Para ejecutar el ETL todos los días a medianoche en Linux o macOS:

```bash
0 0 * * * cd /ruta/al/repo/solarbi-apellido1-apellido2 && /ruta/al/venv/bin/python -m etl.run_etl >> logs/etl.log 2>&1
```

## Aportes por integrante

| Integrante | Actividades realizadas |
|---|---|
| Sebastian Cifuentes Moncada | Simulador de datos, reglas de calidad, ETL, carga en PostgreSQL, UPSERT, Grafana |
| Josue Penagos Amaya | Modelo de datos, Power BI, medidas DAX, documentación, control de versiones |

* Personalicen esta tabla con los aportes reales de cada uno.

## Buenas prácticas de seguridad

- No subir contraseñas ni cadenas de conexión.
- Usar `.env` y agregarlo a `.gitignore`.
- No publicar datos personales de operadores.
- Mantener credenciales y configuración sensible fuera del repositorio.

## Licencia

Este repositorio es un trabajo académico para la Institución Universitaria Pascual Bravo.

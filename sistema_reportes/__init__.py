"""
Archivo de Inicialización del Paquete de Configuración 'sistema_reportes'.
Se ejecuta al cargar el proyecto y configura los controladores de base de datos MySQL.
"""

# Importar pymysql para usarlo como el conector de MySQL por defecto de Django
import pymysql

# Registrar pymysql como el módulo de compatibilidad MySQLdb nativo
pymysql.install_as_MySQLdb()

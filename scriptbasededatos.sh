#!/bin/bash

echo "Conectando a MySQL y recreando bases de datos..."

mysql -u root <<EOF
DROP DATABASE IF EXISTS UVLHUBDB;
DROP DATABASE IF EXISTS UVLHUBDB_TEST;

CREATE DATABASE UVLHUBDB;
CREATE DATABASE UVLHUBDB_TEST;

GRANT ALL PRIVILEGES ON uvlhubdb.* TO 'uvlhubdb_user'@'localhost';
GRANT ALL PRIVILEGES ON uvlhubdb_test.* TO 'uvlhubdb_user'@'localhost';

FLUSH PRIVILEGES;
EOF

echo "Bases de datos recreadas correctamente."

echo "Ejecutando migraciones de Flask..."
flask db upgrade

echo "Ejecutando seed de la base de datos..."
rosemary db:seed

echo "Proceso completado ✅"
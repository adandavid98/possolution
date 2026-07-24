@echo off
echo Creando base de datos POS_LaRuta_DB en SQL Server SQLEXPRESS...
sqlcmd -S .\SQLEXPRESS -Q "IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'POS_LaRuta_DB') CREATE DATABASE POS_LaRuta_DB;"
sqlcmd -S .\SQLEXPRESS -Q "IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'SMS-ADAN\Adan') CREATE LOGIN [SMS-ADAN\Adan] FROM WINDOWS;"
sqlcmd -S .\SQLEXPRESS -Q "ALTER SERVER ROLE sysadmin ADD MEMBER [SMS-ADAN\Adan];"
sqlcmd -S .\SQLEXPRESS -d POS_LaRuta_DB -Q "IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'SMS-ADAN\Adan') CREATE USER [SMS-ADAN\Adan] FOR LOGIN [SMS-ADAN\Adan]; ALTER ROLE db_owner ADD MEMBER [SMS-ADAN\Adan];"
echo Proceso finalizado.

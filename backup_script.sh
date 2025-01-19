BACKUP_DIR='/app/backup'
FILE_NAME=$BACKUP_DIR/$(date +'%d-%m-%Y-%H-%M-%S').tar
PGPASSWORD='1'
docker exec -e PGPASSWORD=$PGPASSWORD pg pg_dump -U postgres -h localhost -p 5432 -d idk -F tar -f /tmp/db_backup.tar
docker cp pg:/tmp/db_backup.tar $FILE_NAME
echo $FILE_NAME

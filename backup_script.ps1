
$BACKUP_DIR = 'C:\Users\User\PycharmProjects\XOLODILNIK\backup'
$FILE_NAME = $BACKUP_DIR + '\' + (Get-Date -Format 'dd-MM-yyyy-hh-mm-ss') + '.tar'
$PGPASSWORD = '1'
docker exec -e PGPASSWORD=$PGPASSWORD pg pg_dump -U postgres -h localhost -p 5432 -d idk -F tar -f '/tmp/db_backup.tar'
docker cp pg:/tmp/db_backup.tar $FILE_NAME

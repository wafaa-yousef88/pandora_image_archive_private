maysara modification to db
===============================
UPDATE archive_file set wanted=True;
alter table archive_file add COLUMN is_image boolean;
UPDATE archive_file set is_image=True ;
alter table archive_file ALTER COLUMN is_image boolean NOT NULL;


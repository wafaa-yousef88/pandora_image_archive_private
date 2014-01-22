maysara modification to db
===============================
UPDATE archive_file set wanted=True;
alter table archive_file add COLUMN is_image boolean;
UPDATE archive_file set is_image=True ;
alter table archive_file ALTER COLUMN is_image SET NOT NULL;

wafaa made these columns accept null cuz we may remove dar later:
===================================================================
ALTER TABLE archive_file ALTER COLUMN display_aspect_ratio DROP NOT NULL;
 ALTER TABLE item_item ALTER COLUMN stream_aspect DROP NOT NULL;
 ALTER TABLE clip_clip ALTER COLUMN aspect_ratio DROP NOT NULL;
 ALTER TABLE archive_stream ALTER COLUMN aspect_ratio DROP NOT NULL;
ALTER TABLE clip_clip ALTER COLUMN aspect_ratio DROP NOT NULL;

/*Adding Field to title table to hold collection value for future usage*/
alter table title_title  add COLUMN collection character varying(1000);
alter table title_title   ALTER   COLUMN collection set   NOT NULL;

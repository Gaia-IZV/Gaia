sudo -u hdfs hdfs dfs -chown -R root:hdfsadmingroup /user/hive/warehouse/gaia.db/plant_recognition_events
sudo -u hdfs hdfs dfs -chown -R root:hdfsadmingroup /user/hive/warehouse/gaia.db/plant_care_queries
sudo -u hdfs hdfs dfs -chown -R root:hdfsadmingroup /user/hive/warehouse/gaia.db/plant_care_responses

sudo -u hdfs hdfs dfs -chmod -R 775 /user/hive/warehouse/gaia.db/plant_recognition_events
sudo -u hdfs hdfs dfs -chmod -R 775 /user/hive/warehouse/gaia.db/plant_care_queries
sudo -u hdfs hdfs dfs -chmod -R 775 /user/hive/warehouse/gaia.db/plant_care_responses

sudo -u hdfs hdfs dfs -ls -d /user/hive/warehouse/gaia.db/plant_recognition_events
sudo -u hdfs hdfs dfs -ls -d /user/hive/warehouse/gaia.db/plant_care_queries
sudo -u hdfs hdfs dfs -ls -d /user/hive/warehouse/gaia.db/plant_care_responses
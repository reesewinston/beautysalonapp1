create user 'appuser'@'localhost' identified by 'AppPass123!';
grant all privileges on beauty_booking_system.* to 'appuser'@'localhost';
flush privileges;
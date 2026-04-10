-- remove the database if it already exists
drop database if exists beauty_booking_system;

-- create the database
create database if not exists beauty_booking_system;

-- use the database
use beauty_booking_system;

-- drop tables in the correct order to avoid foreign key issues
drop table if exists reviews;
drop table if exists appointments;
drop table if exists stylist_services;
drop table if exists services;
drop table if exists stylists;
drop table if exists clients;

-- create the clients table
create table if not exists clients (
    client_id int auto_increment primary key,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    phone varchar(20) not null unique,
    email varchar(100) not null unique
);

-- create the stylists table
create table if not exists stylists (
    stylist_id int auto_increment primary key,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    specialty varchar(100),
    phone varchar(20) not null unique,
    email varchar(100) not null unique
);

-- create the services table
create table if not exists services (
    service_id int auto_increment primary key,
    service_name varchar(100) not null,
    category varchar(50) not null,
    duration int not null,
    addOn varchar(100)
);

-- create the stylist_services table to connect stylists and services
create table if not exists stylist_services (
    stylist_id int not null,
    service_id int not null,
    price decimal(8,2) not null,
    primary key (stylist_id, service_id),
    foreign key (stylist_id) references stylists(stylist_id)
        on delete cascade
        on update cascade,
    foreign key (service_id) references services(service_id)
        on delete cascade
        on update cascade
);

-- create the appointments table
create table if not exists appointments (
    appointment_id int auto_increment primary key,
    client_id int not null,
    stylist_id int not null,
    service_id int not null,
    appointment_date date not null,
    appointment_time time not null,
    appointment_status varchar(20) not null,
    foreign key (client_id) references clients(client_id)
        on delete cascade
        on update cascade,
    foreign key (stylist_id) references stylists(stylist_id)
        on delete cascade
        on update cascade,
    foreign key (service_id) references services(service_id)
        on delete cascade
        on update cascade,
    check (appointment_status in ('scheduled', 'completed', 'cancelled', 'no-show'))
);

-- create the reviews table
create table if not exists reviews (
    review_id int auto_increment primary key,
    appointment_id int not null unique,
    rating int not null,
    client_review varchar(255),
    review_date date not null,
    foreign key (appointment_id) references appointments(appointment_id)
        on delete cascade
        on update cascade,
    check (rating between 1 and 5)
);

-- insert sample data into clients
insert into clients (first_name, last_name, phone, email)
values
('Aaliyah', 'Washington', '404-555-0101', 'aaliyah.washington@gmail.com'),
('Brianna', 'Thompson', '678-555-0102', 'brianna.thompson@gmail.com'),
('Camille', 'Jackson', '770-555-0103', 'camille.jackson@yahoo.com'),
('Destiny', 'Harris', '404-555-0104', 'destiny.harris@outlook.com'),
('Ebony', 'Martin', '678-555-0105', 'ebony.martin@gmail.com'),
('Fatima', 'Robinson', '770-555-0106', 'fatima.robinson@gmail.com'),
('Gabrielle', 'Lewis', '404-555-0107', 'gabrielle.lewis@yahoo.com'),
('Hailey', 'Walker', '678-555-0108', 'hailey.walker@gmail.com'),
('Imani', 'Hall', '770-555-0109', 'imani.hall@outlook.com'),
('Jasmine', 'Allen', '404-555-0110', 'jasmine.allen@gmail.com');

-- insert sample data into stylists
insert into stylists (first_name, last_name, specialty, phone, email)
values
('Tiana', 'Brooks', 'hair', '404-555-0201', 'tiana.brooks@salonmail.com'),
('Monique', 'Davis', 'hair', '678-555-0202', 'monique.davis@salonmail.com'),
('Simone', 'Edwards', 'nails', '770-555-0203', 'simone.edwards@salonmail.com'),
('Nia', 'Graham', 'lashes', '678-555-0205', 'nia.graham@salonmail.com'),
('Jade', 'Phillips', 'hair', '678-555-0211', 'jade.phillips@salonmail.com');

-- insert sample data into services
insert into services (service_name, category, duration, addOn)
values
('Braids', 'hair', 240, 'beads'),
('Wigs', 'hair', 180, 'custom styling'),
('Quickweave', 'hair', 120, 'closure install'),
('Silk Press', 'hair', 90, 'trim'),
('Acrylic Full Set', 'nails', 90, 'design'),
('GelX Full Set', 'nails', 90, 'design'),
('Classic Lashes', 'lashes', 90, 'bottom lashes'),
('Hybrid Lashes', 'lashes', 100, 'bottom lashes');

-- insert sample data into stylist_services
insert into stylist_services (stylist_id, service_id, price)
values
(1, 1, 175.00),
(1, 2, 150.00),
(1, 4, 85.00),
(2, 1, 165.00),
(2, 3, 95.00),
(2, 4, 80.00),
(3, 5, 65.00),
(3, 6, 70.00),
(4, 7, 85.00),
(4, 8, 100.00),
(5, 1, 170.00),
(5, 2, 145.00),
(5, 4, 75.00);

-- insert sample data into appointments
insert into appointments (client_id, stylist_id, service_id, appointment_date, appointment_time, appointment_status)
values
(1, 1, 1, '2025-03-01', '09:00:00', 'completed'),
(2, 1, 2, '2025-03-03', '11:00:00', 'completed'),
(3, 2, 3, '2025-03-05', '10:00:00', 'completed'),
(4, 2, 1, '2025-03-07', '13:00:00', 'no-show'),
(5, 3, 5, '2025-03-10', '09:30:00', 'completed'),
(6, 3, 6, '2025-03-12', '14:00:00', 'completed'),
(7, 4, 7, '2025-03-14', '10:00:00', 'completed'),
(8, 4, 8, '2025-03-15', '11:30:00', 'cancelled'),
(9, 5, 1, '2025-03-17', '09:00:00', 'completed'),
(10, 1, 4, '2025-03-18', '10:30:00', 'scheduled');

-- insert sample data into reviews
insert into reviews (appointment_id, rating, client_review, review_date)
values
(1, 5, 'Tiana did an amazing job on my braids! Super neat and lasted weeks.', '2025-03-02'),
(2, 4, 'Love my wig install! Will definitely be back.', '2025-03-04'),
(3, 5, 'Monique is so talented. My quickweave looked so natural.', '2025-03-06'),
(5, 5, 'Simone is the best nail tech! My acrylics are flawless.', '2025-03-11'),
(6, 4, 'GelX set came out beautiful. Lasted over 3 weeks with no lifting.', '2025-03-13'),
(7, 5, 'Nia is incredible. My lashes look so natural and full.', '2025-03-15'),
(9, 5, 'Jade is so precise and professional. I loved my style.', '2025-03-18');

-- ==================================================
-- 5 basic queries 
-- ==================================================

-- 1. retrieve a list of all services
select * 
from services;

-- 2. find clients who had appointments within a specific date range
select c.client_id, c.first_name, c.last_name, a.appointment_date
from clients c
join appointments a
on c.client_id = a.client_id
where a.appointment_date between '2025-03-01' and '2025-03-10';

-- 3. insert a new client record
insert into clients (first_name, last_name, phone, email)
values ('Kayla', 'Moore', '404-555-0111', 'kayla.moore@gmail.com');

-- 4. update a client record
update clients
set phone = '404-999-0000'
where client_id = 1;

-- 5. delete a client record
delete from clients
where client_id = 10;

-- ==================================================
-- extra queries
-- ==================================================

-- show all clients
select * from clients;

-- show all stylists
select * from stylists;

-- show all appointments
select * from appointments;

-- show all reviews
select * from reviews;

-- show each appointment with client name and service name
select c.first_name, c.last_name, s.service_name, a.appointment_date, a.appointment_time, a.appointment_status
from appointments a
join clients c on a.client_id = c.client_id
join services s on a.service_id = s.service_id;

-- show stylists and the services they offer with prices
select st.first_name, st.last_name, sv.service_name, ss.price
from stylist_services ss
join stylists st on ss.stylist_id = st.stylist_id
join services sv on ss.service_id = sv.service_id;
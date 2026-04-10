create database beauty_booking_system;
use beauty_booking_system;

create table clients (
    client_id int auto_increment primary key,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    phone varchar(20) not null,
    email varchar(100) not null unique
);

create table stylists (
    stylist_id int auto_increment primary key,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    specialty varchar(100),
    phone varchar(20) not null,
    email varchar(100) not null unique
);

create table services (
    service_id int auto_increment primary key,
    service_name varchar(100) not null,
    price decimal(8,2) not null,
    duration int not null,
    stylist_id int not null,
    foreign key (stylist_id) references stylists(stylist_id)
        on delete cascade
        on update cascade
);

create table appointments (
    appointment_id int auto_increment primary key,
    client_id int not null,
    stylist_id int not null,
    service_id int not null,
    appointment_date date not null,
    appointment_time time not null,
    status varchar(20) not null,
    foreign key (client_id) references clients(client_id)
        on delete cascade
        on update cascade,
    foreign key (stylist_id) references stylists(stylist_id)
        on delete cascade
        on update cascade,
    foreign key (service_id) references services(service_id)
        on delete cascade
        on update cascade
);

create table reviews (
    review_id int auto_increment primary key,
    client_id int not null,
    stylist_id int not null,
    rating int not null,
    comment varchar(255),
    review_date date not null,
    foreign key (client_id) references clients(client_id)
        on delete cascade
        on update cascade,
    foreign key (stylist_id) references stylists(stylist_id)
        on delete cascade
        on update cascade,
    check (rating between 1 and 5)
);
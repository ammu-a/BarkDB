CREATE DATABASE BarkDB;
SHOW DATABASES;
USE BarkDB;

## Create Tables
-- 1. UserSignup

CREATE TABLE UserSignup (
  UserID INT AUTO_INCREMENT PRIMARY KEY,
  UserType ENUM('Owner', 'Provider') NOT NULL,
  Email VARCHAR(100) UNIQUE NOT NULL,
  UserName VARCHAR(100) NOT NULL,
  Password VARCHAR(100) NOT NULL
);
ALTER TABLE UserSignup 
MODIFY COLUMN UserType VARCHAR(20) NOT NULL;

-- 2. Location
CREATE TABLE Location (
  LocationID INT AUTO_INCREMENT PRIMARY KEY,
  Zipcode VARCHAR(10),
  City VARCHAR(100),
  Province VARCHAR(100)
);

-- 3. PetOwner
CREATE TABLE PetOwner (
  PetOwnerID INT AUTO_INCREMENT PRIMARY KEY,
  UserID INT,
  OwnerName VARCHAR(100),
  PetType VARCHAR(50),
  Breed VARCHAR(50),
  PetName VARCHAR(50),
  FOREIGN KEY (UserID) REFERENCES UserSignup(UserID)
);

-- 4. ServiceProvider
CREATE TABLE ServiceProvider (
  ProviderID INT AUTO_INCREMENT PRIMARY KEY,
  UserID INT,
  ProviderName VARCHAR(100),
  LocationID INT,
  HomeType VARCHAR(50),
  TotalReviews INT,
  YearsExperience INT,
  RepeatClients INT,
  PetsAtHome BOOLEAN,
  ChildrenAtHome BOOLEAN,
  AboutMe TEXT,
  FOREIGN KEY (UserID) REFERENCES UserSignup(UserID),
  FOREIGN KEY (LocationID) REFERENCES Location(LocationID)
);

-- 5. Services
CREATE TABLE Services (
  ServiceID INT AUTO_INCREMENT PRIMARY KEY,
  ServiceName VARCHAR(100),
  ServiceDescription TEXT,
  Active BOOLEAN DEFAULT TRUE
);

-- 6. Rate
CREATE TABLE Rate (
  RateID INT AUTO_INCREMENT PRIMARY KEY,
  ProviderID INT,
  ServiceID INT,
  Rate DECIMAL(6,2),
  RateType ENUM('Hourly', 'Daily', 'Per Visit'),
  EffectiveDate DATE,
  FOREIGN KEY (ProviderID) REFERENCES ServiceProvider(ProviderID),
  FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID)
);

ALTER TABLE Rate MODIFY COLUMN RateType VARCHAR(50);

-- 7. Booking
CREATE TABLE Booking (
  BookingID INT AUTO_INCREMENT PRIMARY KEY,
  PetOwnerID INT,
  ServiceID INT,
  ProviderID INT,
  RateID INT,
  DiscountRate DECIMAL(5,2),
  StartDate DATE,
  EndDate DATE,
  BookingDate DATE,
  BookingStatus ENUM('Pending', 'Confirmed', 'Cancelled', 'Completed'),
  FOREIGN KEY (PetOwnerID) REFERENCES PetOwner(PetOwnerID),
  FOREIGN KEY (ServiceID) REFERENCES Services(ServiceID),
  FOREIGN KEY (ProviderID) REFERENCES ServiceProvider(ProviderID),
  FOREIGN KEY (RateID) REFERENCES Rate(RateID)
);

-- 8. Reviews
CREATE TABLE Reviews (
  ReviewID INT AUTO_INCREMENT PRIMARY KEY,
  BookingID INT,
  Rating INT CHECK (Rating BETWEEN 1 AND 5),
  CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  Comment TEXT,
  FOREIGN KEY (BookingID) REFERENCES Booking(BookingID)
);


-- LOAD DATA
LOAD DATA LOCAL INFILE '/data/UserSignup.csv'
INTO TABLE UserSignup
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(UserID, UserType, email, UserName, Password);

LOAD DATA LOCAL INFILE '/data/Location.csv'
INTO TABLE Location
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(LocationID, Zipcode, City, Province);

LOAD DATA LOCAL INFILE '/data/ServiceProvider.csv'
INTO TABLE ServiceProvider
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(ProviderID, UserID, ProviderName, LocationID, HomeType, TotalReviews, YearsExperience, RepeatClients, PetsAtHome, ChildrenAtHome, AboutMe);
LOAD DATA LOCAL INFILE '/data/PetOwner.csv'
INTO TABLE PetOwner
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(PetOwnerID, UserID, OwnerName, PetType, Breed, PetName);

LOAD DATA LOCAL INFILE '/data/Services.csv'
INTO TABLE Services
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(ServiceID, ServiceName, ServiceDescription, Active);

LOAD DATA LOCAL INFILE '/data/Rate.csv'
INTO TABLE Rate
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(RateID, ProviderID, ServiceID, Rate, RateType, EffectiveDate);

LOAD DATA LOCAL INFILE '/data/Booking.csv'
INTO TABLE Booking
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(BookingID, PetOwnerID, ServiceID, ProviderID, RateID, DiscountRate, StartDate, EndDate, BookingDate, BookingStatus);

LOAD DATA LOCAL INFILE '/data/Reviews.csv'
INTO TABLE Reviews
FIELDS TERMINATED BY ';' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(ReviewID, BookingID, Rating, CreatedAt, Comment);

-- Create indexes
-- create an index on BookingID in Reviews table 
CREATE INDEX idx_reviews_provider ON Reviews (BookingID);
 SHOW INDEX FROM Reviews;
 
 -- Create View
CREATE VIEW `providers with yard` AS
SELECT ProviderID,
    ProviderName,
    HomeType,
    LocationID,
    TotalReviews,
    YearsExperience,
    RepeatClients,
    PetsAtHome,
    ChildrenAtHome,
    AboutMe
FROM ServiceProvider
WHERE HomeType LIKE '%yard%';

SELECT * FROM `providers with yard`;

-- Temperory tables
CREATE TEMPORARY TABLE TempDogBoarders1 AS
SELECT 
    sp.ProviderID,
    sp.ProviderName,
    s.ServiceName,
    r.Rate,
    r.RateType,
    r.EffectiveDate
FROM 
    ServiceProvider sp
JOIN 
    Rate r ON sp.ProviderID = r.ProviderID
JOIN 
    Services s ON r.ServiceID = s.ServiceID
WHERE 
    s.ServiceName IN ('Dog Boarding', 'Overnight Boarding with Medication Admin');
    
SELECT * FROM TempDogBoarders;

CREATE TEMPORARY TABLE VancouverProviders (
ProviderID int PRIMARY KEY, 
ProviderName varchar(20),
YearsExperience int);

INSERT INTO VancouverProviders(ProviderID, ProviderName, YearsExperience)
SELECT ProviderID, ProviderName, YearsExperience
FROM ServiceProvider SP
JOIN Location l ON sp.LocationID = l.LocationID
WHERE l.city = 'Vancouver';

SELECT * 
FROM VancouverProviders;


-- Stored Procedure
-- calculate the total price of a booking

DELIMITER //

CREATE PROCEDURE TotalPrice (IN inputBookingID INT)
BEGIN
  DECLARE baseRate DECIMAL(10,2);
  DECLARE discount DECIMAL(10,2);
  DECLARE totalDays INT;
  DECLARE totalPrice DECIMAL(10,2);
  DECLARE rateType VARCHAR(50);
  -- Get base rate, discount, number of days, and rate type
  SELECT 
    r.Rate, 
    b.DiscountRate, 
    DATEDIFF(b.EndDate, b.StartDate) + 1,
    r.RateType
  INTO 
    baseRate, discount, totalDays, rateType
  FROM Booking b
  JOIN Rate r ON b.RateID = r.RateID
  WHERE b.BookingID = inputBookingID;
  -- Calculate total price based on rate type
  IF rateType IN ('Per Night', 'Per Day') THEN
    SET totalPrice = (baseRate * totalDays) - discount;
  ELSE
    SET totalPrice = baseRate - discount;
  END IF;

  -- Return the total price
  SELECT ROUND(GREATEST(totalPrice, 0), 2) AS TotalBookingPrice;
END //
DELIMITER ;
CALL TotalPrice(2);


-- SQL Function-- 
-- compute the number of services offered by a provider
DELIMITER //
CREATE FUNCTION CountServicesByProvider(p_ProviderID INT)
RETURNS INT
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE serviceCount INT;

    SELECT COUNT(DISTINCT ServiceID)
    INTO serviceCount
    FROM Rate
    WHERE ProviderID = p_ProviderID;

    RETURN serviceCount;
END //

DELIMITER ;

SELECT CountServicesByProvider(15);

 -- Create Trigger
 -- After a new review is inserted, update the avg rating and total review counts for the corresponding service provider
 
ALTER TABLE ServiceProvider
ADD COLUMN AvgRating DECIMAL(3,2);

 DELIMITER //

CREATE TRIGGER UpdateAvgAndTotalReviews
AFTER INSERT ON Reviews
FOR EACH ROW
BEGIN
  DECLARE providerId INT;
-- Get the ProviderID from the Booking table using the new Review's BookingID
  SELECT ProviderID INTO providerId
  FROM Booking
  WHERE BookingID = NEW.BookingID;

  -- Update the average rating
  UPDATE ServiceProvider
  SET AvgRating = (
    SELECT ROUND(AVG(R.Rating), 2)
    FROM Reviews R
    JOIN Booking B ON R.BookingID = B.BookingID
    WHERE B.ProviderID = providerId
  ),
  -- Update the total number of reviews
  TotalReviews = (
    SELECT COUNT(*)
    FROM Reviews R
    JOIN Booking B ON R.BookingID = B.BookingID
    WHERE B.ProviderID = providerId
  )
  WHERE ProviderID = providerId;
END;
//

DELIMITER ;
 


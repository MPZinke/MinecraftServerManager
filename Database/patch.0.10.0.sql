

-- Add the favorited field to the Locations table.
ALTER TABLE "Locations" ADD COLUMN "favorited" TIMESTAMP DEFAULT NULL;

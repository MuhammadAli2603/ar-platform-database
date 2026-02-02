-- Fix Storage Permissions for ar-models bucket
-- Run this in Supabase SQL Editor if you want to keep RLS enabled

-- Allow anyone to insert (upload) files
CREATE POLICY IF NOT EXISTS "Public Access - INSERT"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'ar-models');

-- Allow anyone to select (read) files
CREATE POLICY IF NOT EXISTS "Public Access - SELECT"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'ar-models');

-- Allow anyone to update files
CREATE POLICY IF NOT EXISTS "Public Access - UPDATE"
ON storage.objects FOR UPDATE
TO public
USING (bucket_id = 'ar-models');

-- Allow anyone to delete files (optional, enable if needed)
CREATE POLICY IF NOT EXISTS "Public Access - DELETE"
ON storage.objects FOR DELETE
TO public
USING (bucket_id = 'ar-models');

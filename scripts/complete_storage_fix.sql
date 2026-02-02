-- Complete Storage Fix for ar-models bucket
-- Run this entire script in Supabase SQL Editor

-- Step 1: Disable RLS on storage.objects table
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;

-- Step 2: Make sure bucket is public
UPDATE storage.buckets
SET public = true
WHERE id = 'ar-models';

-- Step 3: Drop existing policy and create a new one
DROP POLICY IF EXISTS "Allow all operations on ar-models" ON storage.objects;

-- Create permissive policy for all operations
CREATE POLICY "Allow all operations on ar-models"
ON storage.objects
FOR ALL
TO public
USING (bucket_id = 'ar-models')
WITH CHECK (bucket_id = 'ar-models');

-- Step 4: Grant necessary permissions
GRANT ALL ON storage.objects TO anon;
GRANT ALL ON storage.objects TO authenticated;
GRANT ALL ON storage.buckets TO anon;
GRANT ALL ON storage.buckets TO authenticated;

-- Verify configuration
SELECT
    id,
    name,
    public,
    file_size_limit,
    allowed_mime_types
FROM storage.buckets
WHERE id = 'ar-models';

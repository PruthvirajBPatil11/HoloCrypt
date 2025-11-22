import { createClient } from '@supabase/supabase-js'

// Get Supabase credentials from environment variables
// IMPORTANT: Add your Supabase URL and Anon Key in the .env file
// Copy .env.example to .env and fill in your values
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// Validate that environment variables are set
if (!supabaseUrl || !supabaseAnonKey || 
    supabaseUrl.includes('placeholder') || 
    supabaseAnonKey.includes('placeholder')) {
  console.error('⚠️ Supabase credentials not configured. Please add real credentials to .env file.')
}

// Create Supabase client (will work with placeholder for UI testing)
export const supabase = createClient(
  supabaseUrl || 'https://placeholder.supabase.co', 
  supabaseAnonKey || 'placeholder'
)

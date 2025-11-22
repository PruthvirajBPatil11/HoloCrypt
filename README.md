# React Authentication App with Supabase

A React authentication application with login, registration, and protected routes using Supabase as the backend.

## Features

- ✅ User Registration
- ✅ User Login with attempt limits (3 max attempts)
- ✅ Protected Routes
- ✅ Session Management
- ✅ Logout Functionality
- ✅ Easy-to-modify UI (all styles in one CSS file)

## Prerequisites

Before you begin, make sure you have:
- Node.js (v16 or higher) installed
- A Supabase account (free tier works fine)

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Fill in your project details:
   - Project name
   - Database password (save this!)
   - Region (choose closest to you)
4. Wait for the project to be created (takes ~2 minutes)

### 2. Get Your Supabase Credentials

1. In your Supabase project dashboard, go to **Settings** (gear icon in sidebar)
2. Click on **API** in the settings menu
3. You'll see:
   - **Project URL** - looks like `https://xxxxxxxxxxxxx.supabase.co`
   - **anon/public key** - a long string starting with `eyJ...`

### 3. Configure Environment Variables

1. In your project folder, copy the `.env.example` file to create `.env`:
   ```
   Copy-Item .env.example .env
   ```

2. Open the `.env` file and add your Supabase credentials:
   ```
   VITE_SUPABASE_URL=https://your-project-id.supabase.co
   VITE_SUPABASE_ANON_KEY=your-anon-key-here
   ```

   **IMPORTANT:** Replace the placeholder values with your actual Supabase URL and anon key from step 2.

### 4. Configure Supabase Authentication (Optional)

By default, Supabase requires email confirmation. To change this:

1. In your Supabase dashboard, go to **Authentication** → **Settings**
2. Under "Email Auth", you can:
   - Enable/disable "Confirm email"
   - Customize email templates
   - Set redirect URLs

For development, you might want to disable email confirmation.

### 5. Install Dependencies

Open your terminal in the project folder and run:

```powershell
npm install
```

### 6. Run the Application

Start the development server:

```powershell
npm run dev
```

The app will open in your browser at `http://localhost:3000`

## Project Structure

```
BMSCE/
├── src/
│   ├── components/
│   │   ├── Login.jsx          # Login page with attempt limits
│   │   ├── Register.jsx       # Registration page
│   │   ├── Dashboard.jsx      # Protected dashboard
│   │   └── ProtectedRoute.jsx # Route protection wrapper
│   ├── context/
│   │   └── AuthContext.jsx    # Authentication state management
│   ├── lib/
│   │   └── supabaseClient.js  # Supabase client configuration
│   ├── App.jsx                # Main app with routing
│   ├── App.css                # All styles (easy to modify)
│   └── main.jsx               # React entry point
├── .env                       # YOUR SUPABASE CREDENTIALS (don't commit!)
├── .env.example               # Template for .env file
├── package.json               # Dependencies
├── vite.config.js            # Vite configuration
└── index.html                # HTML entry point
```

## Key Features Explained

### Login Attempt Limits

- Users have **3 attempts** to login
- After 3 failed attempts, login is disabled
- Attempts reset on successful login
- Clear feedback on remaining attempts

### Protected Routes

The `/dashboard` route is protected and only accessible to authenticated users. Unauthenticated users are automatically redirected to `/login`.

### Easy-to-Modify UI

All styles are in `src/App.css` with:
- Simple, semantic class names
- Clear section comments
- No complex CSS frameworks
- Easy to replace entirely

To change the UI:
1. Modify classes in `App.css`, OR
2. Replace `App.css` with your own styles, OR
3. Add a CSS framework like Tailwind/Bootstrap

## Customization

### Change Max Login Attempts

In `src/components/Login.jsx`, change:
```javascript
const maxAttempts = 3  // Change to your desired number
```

### Modify Password Requirements

In `src/components/Register.jsx`, adjust the validation:
```javascript
if (password.length < 6) {  // Change minimum length
  setError('Password must be at least 6 characters long')
  return
}
```

### Change Styling

Edit `src/App.css` - all styles are organized by section with clear comments.

## Troubleshooting

### "Missing Supabase environment variables"

- Make sure you created the `.env` file
- Check that the variable names start with `VITE_`
- Restart the dev server after changing `.env`

### Email confirmation required

- Check your email for the confirmation link from Supabase
- Or disable email confirmation in Supabase dashboard (Authentication → Settings)

### Login not working

- Check browser console for errors
- Verify your Supabase credentials in `.env`
- Make sure the user is registered and confirmed

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- The anon key is safe to use in the frontend (it's public by design)
- Supabase handles all security through Row Level Security (RLS) policies

## Next Steps

- Set up Row Level Security (RLS) policies in Supabase
- Add password reset functionality
- Implement social authentication (Google, GitHub, etc.)
- Add user profile management
- Customize the email templates in Supabase

## Support

For Supabase documentation: [https://supabase.com/docs](https://supabase.com/docs)
  
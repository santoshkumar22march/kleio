/**
 * Firebase configuration and initialization
 * Handles authentication ONLY (no Firestore)
 */

import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// Firebase configuration from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

// Validate configuration
if (!firebaseConfig.apiKey || !firebaseConfig.authDomain || !firebaseConfig.projectId) {
  console.error('❌ Firebase configuration is missing!');
  console.error('Please create a .env file with:');
  console.error('VITE_FIREBASE_API_KEY=...');
  console.error('VITE_FIREBASE_AUTH_DOMAIN=...');
  console.error('VITE_FIREBASE_PROJECT_ID=...');
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Google Auth Provider
export const googleProvider = new GoogleAuthProvider();

// Configure Google provider
googleProvider.setCustomParameters({
  prompt: 'select_account', // Always show account selection
});

export default app;

